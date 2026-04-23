import json

from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from ...presenters import present_user
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
        try:
            user = self.user_service.get_user(user_id)
        except UserNotFoundError as exc:
            return JsonResponse({'error': str(exc)}, status=exc.status_code)
        return JsonResponse(present_user(user))

    def put(self, request, user_id):
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
        try:
            self.user_service.delete_user(user_id)
        except UserNotFoundError as exc:
            return JsonResponse({'error': str(exc)}, status=exc.status_code)
        return JsonResponse({'message': f'User {user_id} deleted'}, status=200)
