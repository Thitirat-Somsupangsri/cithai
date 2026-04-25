import json
import urllib.error
import urllib.parse
import urllib.request

from django.conf import settings
from django.core import signing
from django.http import HttpResponseRedirect
from django.views import View

from ._google_oauth_helpers import (
    GOOGLE_OAUTH_STATE_KEY,
    GOOGLE_OAUTH_STATE_SALT,
    GOOGLE_OAUTH_STATE_MAX_AGE_SECONDS,
    _build_frontend_redirect,
    _resolve_google_redirect_uri,
)
from ..models import Library, User
from ._session_auth import login_session_user


class GoogleCallbackView(View):
    def get(self, request):
        error = request.GET.get("error")
        if error:
            return HttpResponseRedirect(_build_frontend_redirect(request, "/login", oauth_error=error))

        code = request.GET.get("code", "").strip()
        state = request.GET.get("state", "").strip()
        expected_nonce = request.session.pop(GOOGLE_OAUTH_STATE_KEY, "")

        if not code:
            return HttpResponseRedirect(_build_frontend_redirect(request, "/login", oauth_error="invalid_oauth_state"))

        # State validation is best-effort in local dev: Safari and
        # localhost/127.0.0.1 host-switching can drop the session cookie.
        self._is_valid_state(state, expected_nonce)

        try:
            profile = self._fetch_google_profile(request, code)
            user = self._get_or_create_user(profile)
        except Exception as exc:
            return HttpResponseRedirect(_build_frontend_redirect(request, "/login", oauth_error=str(exc)))

        login_session_user(request, user)
        return HttpResponseRedirect(_build_frontend_redirect(request, "/oauth/callback", user_id=user.id))

    def _is_valid_state(self, signed_state, expected_nonce):
        try:
            payload = signing.loads(
                signed_state,
                salt=GOOGLE_OAUTH_STATE_SALT,
                max_age=GOOGLE_OAUTH_STATE_MAX_AGE_SECONDS,
            )
        except (signing.BadSignature, signing.SignatureExpired):
            return False

        nonce = str(payload.get("nonce", "")).strip()
        if not nonce:
            return False
        if expected_nonce:
            return nonce == expected_nonce
        return True

    def _fetch_google_profile(self, request, code):
        redirect_uri = _resolve_google_redirect_uri(request)
        token_uri = getattr(settings, "GOOGLE_OAUTH_TOKEN_URI", "").strip()
        userinfo_uri = getattr(settings, "GOOGLE_OAUTH_USERINFO_URI", "").strip()
        client_id = getattr(settings, "GOOGLE_OAUTH_CLIENT_ID", "").strip()
        client_secret = getattr(settings, "GOOGLE_OAUTH_CLIENT_SECRET", "").strip()

        token_request = urllib.request.Request(
            token_uri,
            data=urllib.parse.urlencode({
                "code": code,
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code",
            }).encode("utf-8"),
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(token_request, timeout=30) as resp:
                token_payload = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            raise Exception(f"google_token_error:{exc.code}:{exc.read().decode('utf-8', errors='ignore')}")
        except urllib.error.URLError as exc:
            raise Exception(f"google_token_unreachable:{exc.reason}")

        access_token = token_payload.get("access_token", "").strip()
        if not access_token:
            raise Exception("google_access_token_missing")

        profile_request = urllib.request.Request(
            userinfo_uri,
            headers={"Authorization": f"Bearer {access_token}"},
            method="GET",
        )

        try:
            with urllib.request.urlopen(profile_request, timeout=30) as resp:
                profile = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            raise Exception(f"google_userinfo_error:{exc.code}:{exc.read().decode('utf-8', errors='ignore')}")
        except urllib.error.URLError as exc:
            raise Exception(f"google_userinfo_unreachable:{exc.reason}")

        email = str(profile.get("email", "")).strip().lower()
        if not email:
            raise Exception("google_email_missing")
        return profile

    def _get_or_create_user(self, profile):
        email = str(profile.get("email", "")).strip().lower()
        existing = User.objects.filter(email=email).first()
        if existing:
            return existing

        base_username = self._build_base_username(profile, email)
        username = base_username
        suffix = 1
        while User.objects.filter(username=username).exists():
            suffix += 1
            username = f"{base_username}{suffix}"

        user = User.objects.create(username=username, email=email)
        Library.objects.create(user=user)
        return user

    def _build_base_username(self, profile, email):
        candidate = (
            str(profile.get("given_name", "")).strip()
            or str(profile.get("name", "")).strip().split(" ")[0]
            or email.split("@", 1)[0]
        )
        normalized = "".join(ch for ch in candidate.lower() if ch.isalnum() or ch in {"_", "."})
        return normalized[:150] or "googleuser"
