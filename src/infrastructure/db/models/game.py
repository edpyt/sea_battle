from datetime import datetime
from typing import Optional

from beanie import Document, Link

from src.domain.game.enums.statuses import GameStatusesEnum
from src.infrastructure.db.models.user import User


class Game(Document):
    dt_started: datetime
    status: GameStatusesEnum
    player_1: Optional[Link[User]] = None
    player_2: Optional[Link[User]] = None

    class Settings:
        name = 'game'


class GameEnds(Document):
    game: Link[Game]
    winner: Link[User]

    class Settings:
        name = 'game_ends'
