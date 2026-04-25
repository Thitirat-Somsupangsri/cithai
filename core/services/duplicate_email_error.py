from .user_service_error import UserServiceError


class DuplicateEmailError(UserServiceError):
    status_code = 409
