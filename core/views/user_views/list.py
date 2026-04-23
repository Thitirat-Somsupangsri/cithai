import json

from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from ...presenters import present_user
from ...services import (
    DuplicateEmailError,
    DuplicateUsernameError,
    UserCreatePayload,
    UserPayloadValidationError,
    UserService,
)


@method_decorator(csrf_exempt, name='dispatch')
class UserListView(View):
    user_service = UserService()

    def get(self, request):
        users = [present_user(user) for user in self.user_service.list_users()]
        return JsonResponse({'users': users})

    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        try:
            user = self.user_service.create_user(UserCreatePayload.from_dict(data))
        except (DuplicateUsernameError, DuplicateEmailError, UserPayloadValidationError) as exc:
            return JsonResponse({'error': str(exc)}, status=exc.status_code)

        return JsonResponse(present_user(user), status=201)
