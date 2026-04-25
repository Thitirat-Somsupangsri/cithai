from .user_service_error import UserServiceError


class DuplicateUsernameError(UserServiceError):
    status_code = 409
