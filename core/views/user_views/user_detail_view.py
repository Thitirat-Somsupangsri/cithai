import json

from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from ...presenters import present_user
from .._session_auth import require_owned_user
from ...services import (
    DuplicateEmailError,
    DuplicateUsernameError,
    UserNotFoundError,
    UserPayloadValidationError,
    UserService,
    UserUpdatePayload,
)


@method_decorator(csrf_exempt, name='dispatch')
class UserDetailView(View):
    user_service = UserService()

    def get(self, request, user_id):
        _, err = require_owned_user(request, user_id)
        if err:
            return err
        try:
            user = self.user_service.get_user(user_id)
        except UserNotFoundError as exc:
            return JsonResponse({'error': str(exc)}, status=exc.status_code)
        return JsonResponse(present_user(user))

    def put(self, request, user_id):
        _, err = require_owned_user(request, user_id)
        if err:
            return err
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        try:
            user = self.user_service.update_user(user_id, UserUpdatePayload.from_dict(data))
        except (
            DuplicateUsernameError,
            DuplicateEmailError,
            UserNotFoundError,
            UserPayloadValidationError,
        ) as exc:
            return JsonResponse({'error': str(exc)}, status=exc.status_code)
        return JsonResponse(present_user(user, include_created_at=False))

    def delete(self, request, user_id):
        _, err = require_owned_user(request, user_id)
        if err:
            return err
        try:
            self.user_service.delete_user(user_id)
        except UserNotFoundError as exc:
            return JsonResponse({'error': str(exc)}, status=exc.status_code)
        return JsonResponse({'message': f'User {user_id} deleted'}, status=200)
