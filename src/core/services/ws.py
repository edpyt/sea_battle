"""
Main services for initialize WebSocket connection.
"""
from typing import Optional

from beanie import PydanticObjectId
from bson.errors import InvalidId
from fastapi import WebSocket, WebSocketDisconnect

from src.api.ws.managers.sea_battle import sea_battle_ws_manager
from src.core.services.board import GameBoard
from src.core.services.ws_game import (
    close_connection_update_game,
    game,
    init_game_board,
    wait_all_users,
)
from src.core.utils import game_utils
from src.domain.game.exceptions.game import GameNotExists
from src.domain.game.usecases.game import GameServices
from src.infrastructure.db.models.game import Game
from src.infrastructure.db.models.user import User


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
        game_services(GameServices): Services usecases for model Game.
    """
    game_id: Optional[str] = None
    try:
        active_game = await game_services.get_user_active_game(user_id=user.id)
        cached_active_game = await sea_battle_ws_manager.get_saved_game(
            user.username
        )
        game_id = await sea_battle_connection(
            websocket, user, game_services, active_game, cached_active_game
        )

        game_board: GameBoard = await sea_battle_ws_manager.get_game_board(
            game_id, user.username
        )
        if not game_board.is_all_ships_placed_and_game_initialized:
            await init_game_board(websocket, game_board, user.username)

        if await wait_all_users(websocket, game_id, game_services):
            first_move: str = game_utils.WS_GAME_START_MESSAGE_SUCCES.format(
                username=await (
                    sea_battle_ws_manager.get_first_move_username(game_id)
                )
            )
            await websocket.send_text(first_move)
            await game(game_id, user.username)
            await close_connection_update_game(game_id, game_services)
    except WebSocketDisconnect:
        if (
            game_id
            and sea_battle_ws_manager.rooms.get(game_id)
            and not await sea_battle_ws_manager.get_users_from_room(game_id)
        ):
            await close_connection_update_game(game_id, game_services, True)


async def sea_battle_connection(
    websocket: WebSocket,
    user: User,
    game_services: GameServices,
    active_game: Optional[Game],
    cached_active_game: Optional[GameBoard]
) -> str:
    await websocket.accept()
    if active_game:
        game_id = await sea_battle_exist_connection(
            websocket, user, active_game, cached_active_game
        )
    else:
        game_id = await sea_battle_create_connection(
            websocket, user, game_services
        )
    return game_id


async def sea_battle_exist_connection(
    websocket: WebSocket,
    user: User,
    active_game: Game,
    cached_active_game: Optional[GameBoard] = None
) -> str:
    """
    Connect to exist cached lobby

    Args:
        websocket(WebSocket): WebSocket connection object,
        user(User): User model instance
    """
    if cached_active_game is None:
        cached_active_game = GameBoard()

    await sea_battle_ws_manager.add_user_to_room(
        str(active_game.id),
        user.username,
        websocket,
        game_board=cached_active_game
    )
    await websocket.send_text("Your gaming session has been restored.")
    return str(active_game.id)


async def sea_battle_create_connection(
    websocket: WebSocket,
    user: User,
    game_services: GameServices,
) -> str:
    while True:
        free_rooms = ', '.join(map(str, await get_free_rooms(game_services)))
        await websocket.send_text(f'Select room id from the list: {free_rooms}')

        ws_message = await websocket.receive_text()
        if 'reload' in ws_message.lower():
            active_game = (
                await game_services.get_user_active_game(user_id=user.id)
            )
            if active_game:
                return await sea_battle_exist_connection(
                    websocket, user, active_game
                )
            continue

        try:
            room_id = PydanticObjectId(ws_message)
        except InvalidId:
            await websocket.send_text('Wrong room id')
            continue

        is_connected, _ = await add_websocket_to_room(
            str(room_id), user.username, websocket, game_services
        )
        if is_connected:
            await websocket.send_text("You're succesfully connected.")
            break
    await game_services.update_game(room_id, player_2=user)
    return str(room_id)


async def get_free_rooms(game_services: GameServices) -> list[PydanticObjectId]:
    free_games: list[Game] = await game_services.get_free_games()
    return [game.id for game in free_games]


async def add_websocket_to_room(
    room_id: str,
    username: str,
    websocket: WebSocket,
    game_services: GameServices
) -> tuple[bool, GameBoard]:
    """
    Support function for main websocket connection function

    Args:
        room_id(str): Room MongoDB id,
        username(str): Username,
        websocket(WebSocket): WebSocket connection object,
        game_serivces(GameServices): Services usecases for model Game
    """
    is_connected: bool = False
    game_board: GameBoard = GameBoard()
    try:
        await game_services.get_game_by_id(PydanticObjectId(room_id))
    except GameNotExists:
        await websocket.send_text(f"Not found game with id: {room_id}")
    else:
        is_connected = await sea_battle_ws_manager.add_user_to_room(
            room_id, username, websocket, game_board=game_board
        )
    return is_connected, game_board
