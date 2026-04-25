from .profile_service_error import ProfileServiceError


class ProfileNotFoundError(ProfileServiceError):
    status_code = 404
