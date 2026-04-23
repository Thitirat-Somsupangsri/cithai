from dataclasses import dataclass

from ..models import Library, User


class UserServiceError(Exception):
    status_code = 400


class UserNotFoundError(UserServiceError):
    status_code = 404


class DuplicateUsernameError(UserServiceError):
    status_code = 409


class DuplicateEmailError(UserServiceError):
    status_code = 409


class UserPayloadValidationError(UserServiceError):
    status_code = 400


@dataclass(frozen=True)
class UserCreatePayload:
    username: str
    email: str

    @classmethod
    def from_dict(cls, data):
        username = str(data.get('username', '')).strip()
        email = str(data.get('email', '')).strip()
        if not username or not email:
            raise UserPayloadValidationError('username and email are required')
        return cls(username=username, email=email)


@dataclass(frozen=True)
class UserUpdatePayload:
    username: str | None = None
    email: str | None = None

    @classmethod
    def from_dict(cls, data):
        payload = cls(
            username=str(data['username']).strip() if 'username' in data else None,
            email=str(data['email']).strip() if 'email' in data else None,
        )
        if payload.username == '' or payload.email == '':
            raise UserPayloadValidationError('username and email cannot be blank')
        return payload


class UserService:
    def list_users(self):
        return User.objects.all()

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist as exc:
            raise UserNotFoundError('User not found') from exc

    def create_user(self, payload):
        if User.objects.filter(username=payload.username).exists():
            raise DuplicateUsernameError('username already taken')
        if User.objects.filter(email=payload.email).exists():
            raise DuplicateEmailError('email already registered')

        user = User.objects.create(username=payload.username, email=payload.email)
        Library.objects.create(user=user)
        return user

    def update_user(self, user_id, payload):
        user = self.get_user(user_id)

        if payload.username is not None:
            if User.objects.exclude(pk=user_id).filter(username=payload.username).exists():
                raise DuplicateUsernameError('username already taken')
            user.username = payload.username

        if payload.email is not None:
            if User.objects.exclude(pk=user_id).filter(email=payload.email).exists():
                raise DuplicateEmailError('email already registered')
            user.email = payload.email

        user.save()
        return user

    def delete_user(self, user_id):
        user = self.get_user(user_id)
        user.delete()
