import urllib.parse

from django.conf import settings

GOOGLE_OAUTH_STATE_KEY = "google_oauth_state"
GOOGLE_OAUTH_STATE_SALT = "google-oauth-state"
GOOGLE_OAUTH_STATE_MAX_AGE_SECONDS = 600
GOOGLE_OAUTH_FRONTEND_ORIGIN_KEY = "google_oauth_frontend_origin"
LOCAL_DEV_HOSTS = {"127.0.0.1", "localhost"}


def _is_allowed_frontend_origin(origin):
    parsed = urllib.parse.urlsplit((origin or "").strip())
    return (
        parsed.scheme in {"http", "https"}
        and parsed.hostname in LOCAL_DEV_HOSTS
        and parsed.port == 5173
    )


def _get_frontend_base_url(request):
    session_origin = request.session.get(GOOGLE_OAUTH_FRONTEND_ORIGIN_KEY, "").strip()
    if _is_allowed_frontend_origin(session_origin):
        return session_origin.rstrip("/")
    return getattr(settings, "FRONTEND_APP_URL", "http://127.0.0.1:5173").rstrip("/")


def _build_frontend_redirect(request, path, **params):
    base_url = _get_frontend_base_url(request)
    query = urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
    return f"{base_url}{path}?{query}" if query else f"{base_url}{path}"


def _resolve_google_redirect_uri(request):
    configured = getattr(settings, "GOOGLE_OAUTH_REDIRECT_URI", "").strip()
    if not configured:
        return ""

    parsed = urllib.parse.urlsplit(configured)
    current_host = request.get_host().strip()
    current_hostname = urllib.parse.urlsplit(f"{request.scheme}://{current_host}").hostname

    if parsed.hostname in LOCAL_DEV_HOSTS and current_hostname in LOCAL_DEV_HOSTS:
        return urllib.parse.urlunsplit((
            request.scheme,
            current_host,
            parsed.path or "/auth/google/callback/",
            "",
            "",
        ))

    return configured
