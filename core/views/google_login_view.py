import secrets
import urllib.parse

from django.conf import settings
from django.core import signing
from django.http import HttpResponseRedirect, JsonResponse
from django.views import View

from ._google_oauth_helpers import (
    GOOGLE_OAUTH_FRONTEND_ORIGIN_KEY,
    GOOGLE_OAUTH_STATE_KEY,
    GOOGLE_OAUTH_STATE_SALT,
    _is_allowed_frontend_origin,
    _resolve_google_redirect_uri,
)


class GoogleLoginView(View):
    def get(self, request):
        client_id = getattr(settings, "GOOGLE_OAUTH_CLIENT_ID", "").strip()
        redirect_uri = _resolve_google_redirect_uri(request)
        auth_uri = getattr(settings, "GOOGLE_OAUTH_AUTH_URI", "").strip()
        scopes = getattr(settings, "GOOGLE_OAUTH_SCOPES", [])
        frontend_origin = request.GET.get("frontend_origin", "").strip()

        if not client_id or not redirect_uri or not auth_uri:
            return JsonResponse({"error": "Google OAuth is not configured."}, status=500)

        nonce = secrets.token_urlsafe(32)
        state = signing.dumps({"nonce": nonce}, salt=GOOGLE_OAUTH_STATE_SALT)
        request.session[GOOGLE_OAUTH_STATE_KEY] = nonce

        if _is_allowed_frontend_origin(frontend_origin):
            request.session[GOOGLE_OAUTH_FRONTEND_ORIGIN_KEY] = frontend_origin
        else:
            request.session.pop(GOOGLE_OAUTH_FRONTEND_ORIGIN_KEY, None)

        query = urllib.parse.urlencode({
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": " ".join(scopes),
            "access_type": "online",
            "include_granted_scopes": "true",
            "prompt": "select_account",
            "state": state,
        })
        return HttpResponseRedirect(f"{auth_uri}?{query}")
