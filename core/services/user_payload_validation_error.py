from .user_service_error import UserServiceError


class UserPayloadValidationError(UserServiceError):
    status_code = 400
