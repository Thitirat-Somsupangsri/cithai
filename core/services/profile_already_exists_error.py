from .profile_service_error import ProfileServiceError


class ProfileAlreadyExistsError(ProfileServiceError):
    status_code = 409
