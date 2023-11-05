import pickle
from typing import Optional

import redis.asyncio as aioredis
from beanie import PydanticObjectId
from bson.errors import InvalidId
from fastapi import WebSocket

from src.api.ws.managers.sea_battle import sea_battle_ws_manager
from src.core.services.board import GameBoard, place_ship_to_board
from src.domain.game.exceptions.game import GameNotExists
from src.domain.game.usecases.game import GameServices
from src.infrastructure.db.models.game import Game
from src.infrastructure.db.models.user import User


async def connection_place_ship(
    websocket: WebSocket, game_board: GameBoard, ship_type: str
) -> None:
    """
    Placing ship to the game board

    Args:
        websocket (WebSocket): WebSocket connection object,
        game_board (GameBoard): Sea Battle user game board,
        ship_type (str): Which ship place to the game board.
    """
    message: str = await place_ship_to_board(game_board, ship_type)
    await websocket.send_text(message)


async def sea_battle_ws(
    websocket: WebSocket,
    user: User,
    game_services: GameServices,
    redis_session: aioredis.Redis
) -> None:
    """
    Main logic with sea battle websockets

    Args:
        websocket(WebSocket): WebSocket connection object,
        user(User): User model instance
    """
    await websocket.accept()

    active_game = await game_services.get_user_active_game(user)

    if active_game:
        ...
    else:
        await sea_battle_create_connection(
            websocket, user, game_services, redis_session
        )


async def sea_battle_create_connection(
    websocket: WebSocket,
    user: User,
    game_services: GameServices,
    redis_session: aioredis.Redis
) -> None:
    while True:
        free_rooms = ', '.join(map(str, await get_free_rooms(game_services)))
        await websocket.send_text(f'Select room id from the list: {free_rooms}')

        try:
            room_id = PydanticObjectId(await websocket.receive_text())
        except InvalidId:
            continue

        is_connected: bool = await add_websocket_to_room(
            str(room_id), user.username, websocket, game_services
        )
        if is_connected:
            await websocket.send_text("You're succesfully connected.")
            break
    await game_services.update_game(room_id, player_2=user)
    user_game_board: Optional[GameBoard] = await (
        sea_battle_ws_manager.get_game_board(
            room_id=str(room_id),
            username=user.username
        )
    )
    await set_saved_game(
        user_game_board, user.username, redis_session
    )


async def get_free_rooms(game_services: GameServices) -> list[PydanticObjectId]:
    free_games: list[Game] = await game_services.get_free_games()
    return [game.id for game in free_games]


async def add_websocket_to_room(
    room_id: str,
    username: str,
    websocket: WebSocket,
    game_services: GameServices
) -> bool:
    """
    Support function for main websocket connection function

    Args:
        room_id(str): Room MongoDB id,
        username(str): Username,
        websocket(WebSocket): WebSocket connection object,
        game_serivces(GameServices): Services usecases for model Game
    """
    is_connected: bool = False
    try:
        await game_services.get_game_by_id(room_id)
    except GameNotExists:
        await websocket.send_text(f"Not found game with id: {room_id}")
    else:
        is_connected = await sea_battle_ws_manager.add_user_to_room(
            room_id, username, websocket
        )
    return is_connected


async def get_saved_game(
    username: str, redis_session: aioredis.Redis
) -> Optional[GameBoard]:
    return await redis_session.get(username)


async def set_saved_game(
    game_board: GameBoard,
    username: str,
    redis_session: aioredis.Redis
) -> None:
    serialized_game_board = pickle.dumps(game_board)
    await redis_session.set(username, serialized_game_board)
