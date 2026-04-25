from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from ._session_auth import logout_session_user


@method_decorator(csrf_exempt, name="dispatch")
class AuthSessionLogoutView(View):
    def post(self, request):
        logout_session_user(request)
        request.session.flush()
        return JsonResponse({"message": "Logged out"})
