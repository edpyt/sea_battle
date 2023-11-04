from datetime import datetime
from typing import Optional

from beanie import PydanticObjectId
from pydantic import BaseModel, Field

from src.infrastructure.db.models.game import GameStatusesEnum


class GameDTO(BaseModel):
    dt_started: datetime = Field(default_factory=datetime.utcnow)
    status: GameStatusesEnum = GameStatusesEnum.FREE
    player_1: Optional[PydanticObjectId] = None
    player_2: Optional[PydanticObjectId] = None

    class Config:
        use_enum_values = True

    class Collection:
        name = 'game'
