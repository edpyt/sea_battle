from fastapi import APIRouter, WebSocket

from src.core.services.ws import sea_ws
from src.infrastructure.db.models.user import User
from src.ws.managers.sea_battle import sea_battle_ws_manager

router = APIRouter(prefix='/ws')


@router.websocket('/sea-battle/{room_name}/{user}/')
async def sea_battle_ws(
    websocket: WebSocket, room_name: str, user: User
) -> None:
    """Main route for sea battle websockets connection"""
    await sea_ws(websocket)
