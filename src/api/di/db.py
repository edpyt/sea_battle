from typing import Generator
from fastapi import Depends

from motor.motor_asyncio import AsyncIOMotorClient

from src.infrastructure.db.main import make_client
from src.infrastructure.db.uow import UnitOfWork


def get_session() -> Generator[AsyncIOMotorClient, None, None]:
    mongo_client: AsyncIOMotorClient = make_client()
    yield mongo_client


def uow_provider(
    session: AsyncIOMotorClient = Depends(get_session)
) -> UnitOfWork:
    return UnitOfWork(session)
