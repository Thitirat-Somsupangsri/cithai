from django.contrib.auth.hashers import check_password, make_password

from ..models import Library, User
from .duplicate_email_error import DuplicateEmailError
from .duplicate_username_error import DuplicateUsernameError
from .user_create_payload import UserCreatePayload
from .user_not_found_error import UserNotFoundError
from .user_payload_validation_error import UserPayloadValidationError
from .user_service_error import UserServiceError
from .user_update_payload import UserUpdatePayload


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

        hashed = make_password(payload.password) if payload.password else ''
        user = User.objects.create(username=payload.username, email=payload.email, password=hashed)
        Library.objects.create(user=user)
        return user

    def verify_password(self, user, raw_password):
        if not user.password:
            return True
        return check_password(raw_password, user.password)

    def change_password(self, user_id, current_password, new_password):
        user = self.get_user(user_id)
        if user.password and not check_password(current_password, user.password):
            raise UserPayloadValidationError('Current password is incorrect')
        if len(new_password) < 6:
            raise UserPayloadValidationError('New password must be at least 6 characters')
        user.password = make_password(new_password)
        user.save(update_fields=['password'])
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
