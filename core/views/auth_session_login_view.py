import json

from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from ..presenters import present_user
from ..models import User
from ._session_auth import login_session_user


@method_decorator(csrf_exempt, name="dispatch")
class AuthSessionLoginView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        identifier = str(data.get("identifier", "")).strip().lower()
        if not identifier:
            return JsonResponse({"error": "identifier is required"}, status=400)

        password = str(data.get("password", "")).strip()

        user = User.objects.filter(email__iexact=identifier).first()
        if user is None:
            user = User.objects.filter(username__iexact=identifier).first()
        if user is None:
            return JsonResponse({"error": "Invalid username/email or password."}, status=401)

        if user.password:
            from django.contrib.auth.hashers import check_password
            if not password or not check_password(password, user.password):
                return JsonResponse({"error": "Invalid username/email or password."}, status=401)

        login_session_user(request, user)
        return JsonResponse({"user": present_user(user)})
