from .profile_service_error import ProfileServiceError


class ProfileUserNotFoundError(ProfileServiceError):
    status_code = 404
