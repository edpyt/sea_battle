from datetime import datetime
from typing import Optional

from beanie import Document, Link

from src.infrastructure.db.models.user import User


class Game(Document):
    dt_started: datetime
    player_1: Optional[Link[User]]
    player_2: Optional[Link[User]]

    class Settings:
        name = 'game'
