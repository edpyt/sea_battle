from beanie import PydanticObjectId
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from src.api.di.services import get_game_services
from src.domain.lobby.dto import GameDTO
from src.domain.lobby.usecases import GameServices
from src.domain.user.interfaces import current_active_user
from src.infrastructure.db.models.game import Game, GameStatusesEnum
from src.infrastructure.db.models.user import User

router = APIRouter()


@router.get(
    '/', response_description='Get all games lobbies'
)
async def get_free_games(
    game_services: GameServices = Depends(get_game_services)
) -> list[Game]:
    return await game_services.get_free_games()


@router.get('/change-status/')
async def change_status(
    id_: PydanticObjectId,
    game_services: GameServices = Depends(get_game_services)
):
    await game_services.update_game(id_, status=GameStatusesEnum.IN_GAME)
    return await game_services.get_game_by_id(id_)


# FIXME: fix route
@router.post('/create/', response_description='Create game lobby')
async def create_game(
    new_game: GameDTO,
    game_services: GameServices = Depends(get_game_services),
    user: User = Depends(current_active_user)
):
    new_game.player_1 = await User.get_by_id(new_game.player_1)
    new_game.player_2 = await User.get_by_id(new_game.player_2)
    await game_services.create_game(new_game)
    return JSONResponse({'is_created': True}, status_code=200)
