import json
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from ..presenters import present_profile
from ._session_auth import require_owned_user
from ..services import (
    ProfileAlreadyExistsError,
    ProfileCreatePayload,
    ProfileNotFoundError,
    ProfilePayloadValidationError,
    ProfileService,
    ProfileUpdatePayload,
    ProfileUserNotFoundError,
)


@method_decorator(csrf_exempt, name='dispatch')
class ProfileView(View):
    """
    One Profile per User — accessed via /users/<user_id>/profile/

    GET    → read profile
    POST   → create profile (if none exists)
    PUT    → update gender / birthday
    DELETE → delete profile only (User is preserved)
    """

    profile_service = ProfileService()

    def get(self, request, user_id):
        _, err = require_owned_user(request, user_id)
        if err:
            return err
        try:
            profile = self.profile_service.get_profile(user_id)
        except (ProfileNotFoundError, ProfileUserNotFoundError) as exc:
            return JsonResponse({'error': str(exc)}, status=exc.status_code)
        return JsonResponse(present_profile(profile))

    def post(self, request, user_id):
        _, err = require_owned_user(request, user_id)
        if err:
            return err
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        try:
            profile = self.profile_service.create_profile(user_id, ProfileCreatePayload.from_dict(data))
        except (
            ProfileAlreadyExistsError,
            ProfilePayloadValidationError,
            ProfileUserNotFoundError,
        ) as exc:
            return JsonResponse({'error': str(exc)}, status=exc.status_code)
        return JsonResponse(present_profile(profile), status=201)

    def put(self, request, user_id):
        _, err = require_owned_user(request, user_id)
        if err:
            return err
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        try:
            profile = self.profile_service.update_profile(user_id, ProfileUpdatePayload.from_dict(data))
        except (
            ProfileNotFoundError,
            ProfilePayloadValidationError,
            ProfileUserNotFoundError,
        ) as exc:
            return JsonResponse({'error': str(exc)}, status=exc.status_code)
        return JsonResponse(present_profile(profile))

    def delete(self, request, user_id):
        _, err = require_owned_user(request, user_id)
        if err:
            return err
        try:
            self.profile_service.delete_profile(user_id)
        except (ProfileNotFoundError, ProfileUserNotFoundError) as exc:
            return JsonResponse({'error': str(exc)}, status=exc.status_code)
        return JsonResponse({'message': f'Profile for user {user_id} deleted'})
