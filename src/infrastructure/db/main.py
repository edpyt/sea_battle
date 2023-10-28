from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from src.core.config import settings
from src.infrastructure.db.models import Game, User


def make_client() -> AsyncIOMotorClient:
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    return client


async def initiate_database() -> None:
    client: AsyncIOMotorClient = make_client()
    await init_beanie(
        database=client.seabattledb, document_models=[Game, User]
    )
