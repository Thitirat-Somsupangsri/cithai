from dataclasses import dataclass

from ..models import Profile, User


class ProfileServiceError(Exception):
    status_code = 400


class ProfileUserNotFoundError(ProfileServiceError):
    status_code = 404


class ProfileNotFoundError(ProfileServiceError):
    status_code = 404


class ProfileAlreadyExistsError(ProfileServiceError):
    status_code = 409


class ProfilePayloadValidationError(ProfileServiceError):
    status_code = 400


@dataclass(frozen=True)
class ProfileCreatePayload:
    gender: str
    birthday: str

    @classmethod
    def from_dict(cls, data):
        gender = str(data.get('gender', '')).strip()
        birthday = str(data.get('birthday', '')).strip()
        if not gender or not birthday:
            raise ProfilePayloadValidationError('gender and birthday are required')
        return cls(gender=gender, birthday=birthday)


@dataclass(frozen=True)
class ProfileUpdatePayload:
    gender: str | None = None
    birthday: str | None = None

    @classmethod
    def from_dict(cls, data):
        payload = cls(
            gender=str(data['gender']).strip() if 'gender' in data else None,
            birthday=str(data['birthday']).strip() if 'birthday' in data else None,
        )
        if payload.gender == '' or payload.birthday == '':
            raise ProfilePayloadValidationError('gender and birthday cannot be blank')
        return payload


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
