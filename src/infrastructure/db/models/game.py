from datetime import datetime

from beanie import Document, Link, TimeSeriesConfig
from pydantic import Field

from src.infrastructure.db.models.user import User


class Game(Document):
    player_1: Link[User]
    player_2: Link[User]

    class Config:
        json_schema_extra = {
            "example": {
                "player_1": "ab",
                "player_2": "dc"
            }
        }


class GameEnds(Game):
    winner: str
    dt_ended: datetime = Field(default_factory=datetime.now)

    class Config:
        json_schema_extra = {
            "example": {
                "player_1": "ab",
                "player_2": "dc",
                "winner": "player_1"
            }
        }

    class Settings:
        timeseries = TimeSeriesConfig(time_field='ts')