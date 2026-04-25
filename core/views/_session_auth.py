from django.http import JsonResponse

from ..models import User

SESSION_USER_ID_KEY = "session_user_id"


def login_session_user(request, user):
    request.session.cycle_key()
    request.session[SESSION_USER_ID_KEY] = user.id


def logout_session_user(request):
    request.session.pop(SESSION_USER_ID_KEY, None)


def get_session_user(request):
    user_id = request.session.get(SESSION_USER_ID_KEY)
    if not user_id:
        return None
    return User.objects.filter(pk=user_id).first()


def require_authenticated_user(request):
    user = get_session_user(request)
    if user is None:
        return None, JsonResponse({"error": "Authentication required"}, status=401)
    return user, None


def require_owned_user(request, user_id):
    user, err = require_authenticated_user(request)
    if err:
        return None, err
    if user.id != user_id:
        return None, JsonResponse({"error": "Forbidden"}, status=403)
    return user, None
