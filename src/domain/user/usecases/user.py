from typing import Optional

from beanie import PydanticObjectId

from src.domain.user.interfaces.manager import UserManager
from src.domain.user.interfaces.user import UserUseCase
from src.domain.user.schemas import UserCreate
from src.infrastructure.db.models.user import User
from src.infrastructure.db.uow import UnitOfWork


class CreateUser(UserUseCase):
    async def __call__(
        self, new_user: UserCreate, user_manager: UserManager
    ) -> User:
        return await self.uow.lobby_holder.user_repo.create_user(
            new_user, user_manager
        )


class GetUserById(UserUseCase):
    async def __call__(self, id_: PydanticObjectId) -> Optional[User]:
        user: Optional[User] = None
        try:
            user = await self.uow.lobby_holder.user_repo.get_user_by_id(id_)
        except AssertionError:
            ...
        return user


class UserServices:
    def __init__(
        self, uow: UnitOfWork, user_manager: UserManager
    ) -> None:
        self.uow = uow
        self.user_manager = user_manager

    async def create_user(self, new_user: UserCreate) -> User:
        return await CreateUser(self.uow)(new_user, self.user_manager)

    async def get_user_by_id(self, id_: PydanticObjectId) -> Optional[User]:
        return await GetUserById(self.uow)(id_)
