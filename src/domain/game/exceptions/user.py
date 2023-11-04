from src.domain.common.exceptions import AppException


class UserException(AppException):
    """Base user exception"""
    ...


class UserNotExists(UserException):
    """User not exists error"""
    ...
