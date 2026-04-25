from dataclasses import dataclass

from .profile_payload_validation_error import ProfilePayloadValidationError


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
