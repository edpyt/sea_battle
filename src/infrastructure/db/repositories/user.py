from beanie import PydanticObjectId
from fastapi_users import BaseUserManager
from fastapi_users.schemas import BaseUserCreate
from motor.motor_asyncio import AsyncIOMotorClient

from src.infrastructure.db.models.game import Game
from src.infrastructure.db.models.user import User
from src.infrastructure.db.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository for model User"""
    def __init__(self, session: AsyncIOMotorClient) -> None:
        self.session = session
        super().__init__(Game, session)

    async def create_user(
        self, new_user: BaseUserCreate, user_manager: BaseUserManager
    ) -> User:
        return await user_manager.create(new_user)

    async def get_user_by_id(self, id_: PydanticObjectId) -> User:
        return await super().get_by_id(id_)

    async def get_all_users(self) -> list[User]:
        return await super().get_all()

    async def update_user(self, id_: PydanticObjectId, **kwargs) -> None:
        await super().update_obj(id_, **kwargs)

    async def delete_user(self, id_: PydanticObjectId) -> None:
        await super().delete_obj(id_)
