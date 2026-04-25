from .user_service_error import UserServiceError


class UserNotFoundError(UserServiceError):
    status_code = 404
