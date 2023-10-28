from beanie import PydanticObjectId

from src.domain.lobby.dto.game import GameDTO
from src.domain.lobby.exceptions import GameNotExists
from src.domain.lobby.interfaces import GameUseCase
from src.infrastructure.db.models import Game
from src.infrastructure.db.uow import UnitOfWork


class GetGameById(GameUseCase):
    async def __call__(self, id_: PydanticObjectId) -> Game:
        try:
            game = await self.uow.lobby_holder.game_repo.get_game_by_id(id_)
        except AssertionError:
            raise GameNotExists
        else:
            return game


class CreateGame(GameUseCase):
    async def __call__(self, new_game: GameDTO) -> Game:
        game = await self.uow.lobby_holder.game_repo.create_game(new_game)
        return game


class GetGames(GameUseCase):
    async def __call__(self) -> list[Game]:
        games = await self.uow.lobby_holder.game_repo.get_all_games()
        return games


class UpdateGame(GameUseCase):
    async def __call__(self, id_:PydanticObjectId, **kwargs) -> None:
        await self.uow.lobby_holder.game_repo.update_game(id_, **kwargs)


class DeleteGame(GameUseCase):
    async def __call__(self, id_: PydanticObjectId) -> None:
        try:
            await self.uow.lobby_holder.game_repo.delete_game(id_)
        except AssertionError:
            raise GameNotExists


class GameServices:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def create_game(self, new_game: GameDTO) -> Game:
        return await CreateGame(self.uow)(new_game)

    async def get_all_games(self) -> list[Game]:
        return await GetGames(self.uow)()

    async def get_game_by_id(self, id_: PydanticObjectId) -> Game:
        return await GetGameById(self.uow)(id_)

    async def update_game(self, id_: PydanticObjectId, **kwargs) -> Game:
        await UpdateGame(self.uow)(id_, **kwargs)
        return await GetGameById(self.uow)(id_)

    async def delete_game(self, id_: PydanticObjectId) -> None:
        await DeleteGame(self.uow)(id_)
