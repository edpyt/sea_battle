"""
Main services for initialize WebSocket connection.

Uses GameServices usecases.
So only here you can create a connection logic to WebSocket.
"""
from typing import Optional

from beanie import PydanticObjectId
from bson.errors import InvalidId
from fastapi import WebSocket, WebSocketDisconnect

from src.api.ws.managers.sea_battle import sea_battle_ws_manager
from src.core.services.board import GameBoard, place_ship_to_board
from src.domain.game.exceptions.game import GameNotExists
from src.domain.game.usecases.game import GameServices
from src.infrastructure.db.models.game import Game
from src.infrastructure.db.models.user import User


# TODO: Move to a sea battle WebSocket manager.
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
) -> None:
    """
    Main logic with sea battle websockets

    Args:
        websocket(WebSocket): WebSocket connection object,
        user(User): User model instance,
        game_services(GameServices): Services usecases for model Game,
        redis_session(redis.asyncio.Redis): Redis current session.
    """
    try:
        await websocket.accept()

        active_game = await game_services.get_user_active_game(user_id=user.id)
        cached_active_game = await sea_battle_ws_manager.get_saved_game(
            user.username
        )
        await sea_battle_connection(
            websocket, user, game_services, active_game, cached_active_game
        )
    except WebSocketDisconnect:
        ...


async def sea_battle_connection(
    websocket: WebSocket,
    user: User,
    game_services: GameServices,
    active_game: Optional[Game],
    cached_active_game: Optional[GameBoard]
) -> None:
    if active_game:
        await sea_battle_exist_connection(
            websocket, user, active_game, cached_active_game
        )
    else:
        await sea_battle_create_connection(websocket, user, game_services)


async def sea_battle_exist_connection(
    websocket: WebSocket,
    user: User,
    active_game: Game,
    cached_active_game: Optional[GameBoard]
) -> None:
    """
    Connect to exist cached lobby

    Args:
        websocket(WebSocket): WebSocket connection object,
        user(User): User model instance
    """
    await sea_battle_ws_manager.add_user_to_room(
        str(active_game.id),
        user.username,
        websocket,
        game_board=cached_active_game
    )
    await websocket.send_text("Your gaming session has been restored.")


async def sea_battle_create_connection(
    websocket: WebSocket,
    user: User,
    game_services: GameServices,
) -> None:
    while True:
        free_rooms = ', '.join(map(str, await get_free_rooms(game_services)))
        await websocket.send_text(f'Select room id from the list: {free_rooms}')

        ws_message = await websocket.receive_text()
        if 'reload' in ws_message.lower():
            continue

        try:
            room_id = PydanticObjectId(ws_message)
        except InvalidId:
            await websocket.send_text('Wrong room id')
            continue

        is_connected: bool = await add_websocket_to_room(
            str(room_id), user.username, websocket, game_services
        )
        if is_connected:
            await websocket.send_text("You're succesfully connected.")
            break
    await game_services.update_game(room_id, player_2=user)


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
