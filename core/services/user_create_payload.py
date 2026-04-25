from dataclasses import dataclass

from .user_payload_validation_error import UserPayloadValidationError


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
