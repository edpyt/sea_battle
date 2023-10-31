from datetime import datetime
from enum import Enum
from typing import Optional

from beanie import Document, Indexed, Link

from src.infrastructure.db.models.user import User


class GameStatusesEnum(str, Enum):
    FREE: str = 'free'
    IN_GAME: str = 'in_game'
    ENDED: str = 'ended'


class Game(Document):
    dt_started: datetime
    game_name: Indexed(str, unique=True)  # type: ignore
    status: GameStatusesEnum = GameStatusesEnum.FREE
    player_1: Optional[Link[User]] = None
    player_2: Optional[Link[User]] = None

    class Config:
        use_enum_values = True

    class Settings:
        name = 'game'
