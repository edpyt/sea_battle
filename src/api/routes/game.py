from beanie import PydanticObjectId
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from src.api.di.services import get_game_services
from src.domain.lobby.dto import GameDTO
from src.domain.lobby.usecases import GameServices
from src.infrastructure.db.models.game import Game, GameStatusesEnum

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
    # player_1_id: PydanticObjectId,
    # player_2_id: PydanticObjectId,
    new_game: GameDTO,
    game_services: GameServices = Depends(get_game_services)
):
    # await get_users_by_ids(player_1_id, player_2_id)
    await game_services.create_game(new_game)
    return JSONResponse({'is_created': True}, status_code=200)
