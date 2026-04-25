import json

from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from ._session_auth import require_owned_user
from ..services import UserPayloadValidationError, UserService


@method_decorator(csrf_exempt, name="dispatch")
class ChangePasswordView(View):
    user_service = UserService()

    def post(self, request, user_id):
        _, err = require_owned_user(request, user_id)
        if err:
            return err

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        current_password = str(data.get("current_password", "")).strip()
        new_password = str(data.get("new_password", "")).strip()

        if not new_password:
            return JsonResponse({"error": "new_password is required"}, status=400)

        try:
            self.user_service.change_password(user_id, current_password, new_password)
        except UserPayloadValidationError as exc:
            return JsonResponse({"error": str(exc)}, status=400)

        return JsonResponse({"message": "Password updated successfully"})
