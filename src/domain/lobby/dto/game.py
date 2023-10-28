from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from src.infrastructure.db.models.user import User


class GameDTO(BaseModel):
    dt_started: datetime = Field(default_factory=datetime.utcnow)
    player_1: Optional[User] = None
    player_2: Optional[User] = None

    class Collection:
        name = 'game'