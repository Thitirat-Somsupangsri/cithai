import json
import secrets
import urllib.error
import urllib.parse
import urllib.request

from django.conf import settings
from django.http import HttpResponseRedirect, JsonResponse
from django.views import View

from ..models import Library, User


GOOGLE_OAUTH_STATE_KEY = "google_oauth_state"


def _frontend_redirect(path, **params):
    base_url = getattr(settings, "FRONTEND_APP_URL", "http://127.0.0.1:5173").rstrip("/")
    query = urllib.parse.urlencode({key: value for key, value in params.items() if value is not None})
    if query:
        return f"{base_url}{path}?{query}"
    return f"{base_url}{path}"


class GoogleLoginView(View):
    def get(self, request):
        client_id = getattr(settings, "GOOGLE_OAUTH_CLIENT_ID", "").strip()
        redirect_uri = getattr(settings, "GOOGLE_OAUTH_REDIRECT_URI", "").strip()
        auth_uri = getattr(settings, "GOOGLE_OAUTH_AUTH_URI", "").strip()
        scopes = getattr(settings, "GOOGLE_OAUTH_SCOPES", [])

        if not client_id or not redirect_uri or not auth_uri:
            return JsonResponse({"error": "Google OAuth is not configured."}, status=500)

        state = secrets.token_urlsafe(32)
        request.session[GOOGLE_OAUTH_STATE_KEY] = state

        query = urllib.parse.urlencode(
            {
                "client_id": client_id,
                "redirect_uri": redirect_uri,
                "response_type": "code",
                "scope": " ".join(scopes),
                "access_type": "online",
                "include_granted_scopes": "true",
                "prompt": "select_account",
                "state": state,
            }
        )
        return HttpResponseRedirect(f"{auth_uri}?{query}")


class GoogleCallbackView(View):
    def get(self, request):
        error = request.GET.get("error")
        if error:
            return HttpResponseRedirect(_frontend_redirect("/login", oauth_error=error))

        code = request.GET.get("code", "").strip()
        state = request.GET.get("state", "").strip()
        expected_state = request.session.pop(GOOGLE_OAUTH_STATE_KEY, "")

        if not code or not state or not expected_state or state != expected_state:
            return HttpResponseRedirect(_frontend_redirect("/login", oauth_error="invalid_oauth_state"))

        try:
            profile = self._fetch_google_profile(code)
            user = self._get_or_create_user(profile)
        except Exception as exc:
            return HttpResponseRedirect(_frontend_redirect("/login", oauth_error=str(exc)))

        return HttpResponseRedirect(_frontend_redirect("/auth/google/callback", user_id=user.id))

    def _fetch_google_profile(self, code):
        redirect_uri = getattr(settings, "GOOGLE_OAUTH_REDIRECT_URI", "").strip()
        token_uri = getattr(settings, "GOOGLE_OAUTH_TOKEN_URI", "").strip()
        userinfo_uri = getattr(settings, "GOOGLE_OAUTH_USERINFO_URI", "").strip()
        client_id = getattr(settings, "GOOGLE_OAUTH_CLIENT_ID", "").strip()
        client_secret = getattr(settings, "GOOGLE_OAUTH_CLIENT_SECRET", "").strip()

        token_request = urllib.request.Request(
            token_uri,
            data=urllib.parse.urlencode(
                {
                    "code": code,
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "redirect_uri": redirect_uri,
                    "grant_type": "authorization_code",
                }
            ).encode("utf-8"),
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(token_request, timeout=30) as response:
                token_payload = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="ignore")
            raise Exception(f"google_token_error:{exc.code}:{detail}")
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
            with urllib.request.urlopen(profile_request, timeout=30) as response:
                profile = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="ignore")
            raise Exception(f"google_userinfo_error:{exc.code}:{detail}")
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
