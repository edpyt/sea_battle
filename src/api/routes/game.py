from beanie import PydanticObjectId
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from src.api.di.services import get_game_services
from src.core.services.user import current_active_user
from src.domain.game.dto import GameDTO
from src.domain.game.usecases.game import GameServices
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


@router.post('/create/', response_description='Create game lobby')
async def create_game(
    new_game: GameDTO,
    user: User = Depends(current_active_user),
    game_services: GameServices = Depends(get_game_services)
) -> JSONResponse:
    """
    Route for creating game lobby. Only authorize route.

    Args:
        new_game(GameDTO): Data Transfer Object for model Game

    Kwargs:
        game_serivces(GameServices): Services usecases for model Game,
        user(User): Current user which is creating game,
        user_services(UserServices): Services usecases for model User
    """
    new_game.player_1 = user
    await game_services.create_game(new_game)
    return JSONResponse({'is_created': True}, status_code=200)
