from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, WebSocket

from src.api.di.services import get_game_services
from src.core.services.ws import sea_battle_ws
from src.domain.game.usecases.game import GameServices

router = APIRouter(prefix='/ws')


@router.websocket('/sea-battle/{room_id}/{username}/')
async def ws_connection(
    websocket: WebSocket,
    room_id: PydanticObjectId,
    username: str,
    game_services: GameServices = Depends(get_game_services)
) -> None:
    """Main route for sea battle websockets connection"""
    await sea_battle_ws(websocket, username, room_id, game_services)
