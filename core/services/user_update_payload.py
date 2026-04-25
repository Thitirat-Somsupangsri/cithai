from dataclasses import dataclass

from .user_payload_validation_error import UserPayloadValidationError


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
