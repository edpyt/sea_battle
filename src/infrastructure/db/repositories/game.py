from typing import Optional

from beanie import PydanticObjectId, WriteRules
from beanie.odm.operators.find.logical import Or
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

    async def get_user_current_game(
        self, user_id: PydanticObjectId
    ) -> Optional[Game]:
        return await super().get_filtered_one(
            Or(Game.player_1.id == user_id, Game.player_2.id == user_id),
            Or(
                Game.status == GameStatusesEnum.IN_GAME,
                Game.status == GameStatusesEnum.FREE
            )
        )

    async def get_all_games(self) -> list[Game]:
        return await super().get_all()

    async def get_free_games(self) -> list[Game]:
        return await super().get_filtered(Game.status == GameStatusesEnum.FREE)

    async def update_game(self, id_: PydanticObjectId, **kwargs) -> None:
        game = await super().update_obj(id_, **kwargs)
        await self.set_link_players(game, **kwargs)

    async def set_link_players(self, game: Game, **kwargs) -> None:
        player_1: Optional[User] = kwargs.get('player_1')
        player_2: Optional[User] = kwargs.get('player_2')

        if player_1 or player_2:
            if player_1:
                game.player_1 = player_1
            if player_2:
                game.player_2 = player_2
            await game.save(link_rule=WriteRules.WRITE)

    async def delete_game(self, id_: PydanticObjectId) -> None:
        await super().delete_obj(id_)
