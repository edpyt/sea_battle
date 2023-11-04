from src.domain.common.exceptions import AppException


class GameException(AppException):
    """Base game exception"""
    ...


class GameNotExists(GameException):
    """Game not exists error"""
    ...
