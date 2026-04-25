from dataclasses import dataclass

from .profile_payload_validation_error import ProfilePayloadValidationError


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
