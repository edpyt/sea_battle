from typing import Optional

from beanie import PydanticObjectId
from motor.motor_asyncio import AsyncIOMotorClient

from src.infrastructure.db.models.game import Game, GameStatusesEnum
from src.infrastructure.db.models.user import User
from src.infrastructure.db.repositories.base import BaseRepository


class GameRepository(BaseRepository[Game]):
    def __init__(self, session: AsyncIOMotorClient) -> None:
        self.session = session
        super().__init__(Game, session)

    async def create_game(self, new_game: Game) -> Game:
        await new_game.create()
        return new_game

    async def get_game_by_id(self, id_: PydanticObjectId) -> Game:
        return await super().get_by_id(id_)

    async def get_active_game_by_user(self, user: User) -> Optional[Game]:
        return await super().get_filtered_one(
            Game.player_1 == user | Game.player_2 == user
        )

    async def get_all_games(self) -> list[Game]:
        return await super().get_all()

    async def get_free_games(self) -> list[Game]:
        return await super().get_filtered(Game.status == GameStatusesEnum.FREE)

    async def update_game(self, id_: PydanticObjectId, **kwargs) -> None:
        await super().update_obj(id_, **kwargs)

    async def delete_game(self, id_: PydanticObjectId) -> None:
        await super().delete_obj(id_)
