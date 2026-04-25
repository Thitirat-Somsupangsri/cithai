from dataclasses import dataclass

from .user_payload_validation_error import UserPayloadValidationError


@dataclass(frozen=True)
class UserCreatePayload:
    username: str
    email: str
    password: str = ''

    @classmethod
    def from_dict(cls, data):
        username = str(data.get('username', '')).strip()
        email = str(data.get('email', '')).strip()
        password = str(data.get('password', '')).strip()
        if not username or not email:
            raise UserPayloadValidationError('username and email are required')
        if not password:
            raise UserPayloadValidationError('password is required')
        if len(password) < 6:
            raise UserPayloadValidationError('password must be at least 6 characters')
        return cls(username=username, email=email, password=password)
