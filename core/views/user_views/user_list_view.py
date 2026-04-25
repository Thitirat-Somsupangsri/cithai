import json

from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from ...presenters import present_user
from .._session_auth import require_authenticated_user
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
        user, err = require_authenticated_user(request)
        if err:
            return err
        users = [present_user(user)]
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
