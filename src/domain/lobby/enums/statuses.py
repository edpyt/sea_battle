from enum import Enum


class GameStatusesEnum(str, Enum):
    FREE: str = 'free'
    IN_GAME: str = 'in_game'
    ENDED: str = 'ended'
