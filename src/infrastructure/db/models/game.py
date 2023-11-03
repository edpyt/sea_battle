from datetime import datetime
from enum import Enum
from typing import Optional

from beanie import Document, Link

from src.infrastructure.db.models.user import User


class GameStatusesEnum(str, Enum):
    FREE: str = 'free'
    IN_GAME: str = 'in_game'
    ENDED: str = 'ended'


class Game(Document):
    dt_started: datetime
    status: GameStatusesEnum
    player_1: Optional[Link[User]] = None
    player_2: Optional[Link[User]] = None

    class Settings:
        name = 'game'
