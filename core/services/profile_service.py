from ..models import Profile, User
from .profile_already_exists_error import ProfileAlreadyExistsError
from .profile_create_payload import ProfileCreatePayload
from .profile_not_found_error import ProfileNotFoundError
from .profile_payload_validation_error import ProfilePayloadValidationError
from .profile_service_error import ProfileServiceError
from .profile_update_payload import ProfileUpdatePayload
from .profile_user_not_found_error import ProfileUserNotFoundError


class ProfileService:
    def get_profile(self, user_id):
        user = self._get_user(user_id)
        try:
            return user.profile
        except Profile.DoesNotExist as exc:
            raise ProfileNotFoundError('Profile not found') from exc

    def create_profile(self, user_id, payload):
        user = self._get_user(user_id)
        if Profile.objects.filter(user=user).exists():
            raise ProfileAlreadyExistsError('Profile already exists for this user')
        profile = Profile.objects.create(user=user, gender=payload.gender, birthday=payload.birthday)
        profile.refresh_from_db()
        return profile

    def update_profile(self, user_id, payload):
        profile = self.get_profile(user_id)
        if payload.gender is not None:
            profile.gender = payload.gender
        if payload.birthday is not None:
            profile.birthday = payload.birthday
        profile.save()
        profile.refresh_from_db()
        return profile

    def delete_profile(self, user_id):
        profile = self.get_profile(user_id)
        profile.delete()

    def _get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist as exc:
            raise ProfileUserNotFoundError('User not found') from exc
