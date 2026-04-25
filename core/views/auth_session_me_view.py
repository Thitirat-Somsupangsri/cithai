from django.http import JsonResponse
from django.views import View

from ..presenters import present_user
from ._session_auth import require_authenticated_user


class AuthSessionMeView(View):
    def get(self, request):
        user, err = require_authenticated_user(request)
        if err:
            return err
        return JsonResponse({"user": present_user(user)})
