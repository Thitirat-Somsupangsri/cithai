from .profile_service_error import ProfileServiceError


class ProfilePayloadValidationError(ProfileServiceError):
    status_code = 400
