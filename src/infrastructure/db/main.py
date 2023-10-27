from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from src.core.config import settings
from src.infrastructure.db.models import Game, GameEnds, User


async def initiate_database() -> None:
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    await init_beanie(
        database=client.seabattledb, document_models=[Game, GameEnds, User]
    )
