import redis.asyncio as aioredis
from fastapi import APIRouter, Depends, WebSocket

from src.api.di.redis import get_redis_session
from src.api.di.services import get_game_services
from src.api.di.user import get_user_from_token
from src.core.services.ws import sea_battle_ws
from src.domain.game.usecases.game import GameServices
from src.infrastructure.db.models.user import User

router = APIRouter()


@router.websocket('/sea-battle/')
async def main_ws_connection(
    websocket: WebSocket,
    user: User = Depends(get_user_from_token),
    game_services: GameServices = Depends(get_game_services),
    redis_session: aioredis.Redis = Depends(get_redis_session)
):
    """
    Main route for sea battle websockets connection

    Args:
        websocket(WebSocket): WebSocket connection object,
        user(User): Current active user model

    Kwargs:
        game_services(GameServices): Services usecases for model Game
    """
    await sea_battle_ws(websocket, user, game_services, redis_session)
