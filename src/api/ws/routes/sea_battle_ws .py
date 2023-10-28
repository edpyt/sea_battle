from fastapi import APIRouter, WebSocket

from src.core.services.ws import sea_ws

router = APIRouter(prefix='/ws')


@router.websocket('/sea-battle/{room_name}/{user}/')
async def sea_battle_ws(
    websocket: WebSocket, room_name: str, user: str
) -> None:
    """Main route for sea battle websockets connection"""
    await sea_ws(websocket, user, room_name)
