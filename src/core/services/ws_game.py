import asyncio
from typing import Any, Callable, Optional

from beanie import PydanticObjectId
from fastapi import WebSocket

from src.api.ws.managers.sea_battle import sea_battle_ws_manager
from src.core.services.board import GameBoard, ShipsOver
from src.core.utils import game_utils
from src.domain.game.enums.statuses import GameStatusesEnum
from src.domain.game.usecases.game import GameServices
from src.infrastructure.db.models.game import GameEnds
from src.infrastructure.db.models.user import User


async def game(room_id: str, username: str) -> None:
    ws_game_user_1 = sea_battle_ws_manager.rooms[room_id][username]
    websocket_user_1: WebSocket = ws_game_user_1['connection']

    ws_game_user_2 = await sea_battle_ws_manager.get_other_user(
        room_id, username
    )
    websocket_user_2: WebSocket = ws_game_user_2['connection']
    game_board_user_2: GameBoard = ws_game_user_2['game_board']  # type: ignore

    while not await _is_game_over(room_id):
        ws_text = await websocket_user_1.receive_text()

        if ws_game_user_1['is_turn']:
            while True:
                cords = _validate_cords(ws_text)
                if not cords:
                    await websocket_user_1.send_text(
                        game_utils.VALID_COORDINATES_ERROR
                    )
                else:
                    is_hited = game_board_user_2.attack(*cords)
                    await sea_battle_ws_manager.set_saved_game(
                        game_board_user_2,
                        ws_game_user_2['username']  # type: ignore
                    )
                    if not is_hited:
                        ws_game_user_1['is_turn'] = False
                        ws_game_user_2['is_turn'] = True
                        break
                    await websocket_user_1.send_text(
                        game_utils.WS_GAME_HIT_SHIP_USER_1_INFO
                    )
                    await websocket_user_2.send_text(
                        game_utils
                        .WS_GAME_HITTED_SHIP_USER_2_INFO.format(cords=cords)
                    )
                if await _is_game_over(room_id):
                    break
                ws_text = await websocket_user_1.receive_text()
        else:
            await websocket_user_1.send_text(
                game_utils.WS_GAME_NOT_YOUR_MOVE_ERROR
            )
    await websocket_user_1.send_text(game_utils.WS_GAME_OVER_INFO)


async def _is_game_over(room_id: str) -> bool:
    return await sea_battle_ws_manager.is_game_over(room_id)


async def wait_all_users(
    websocket: WebSocket, room_id: str, game_services: GameServices
) -> bool:
    await websocket.send_text(game_utils.WS_GAME_WAIT_FOR_OTHER_USER_INFO)
    seconds_passed: int = game_utils.SECONDS_TO_CONNECT_AND_INITIALIZE_SHIPS

    while seconds_passed >= 0:
        if await sea_battle_ws_manager.all_users_initialized(room_id):
            return True
        await asyncio.sleep(1)
        if (seconds_passed % 5) == 0:
            await websocket.send_text(
                game_utils
                .WS_GAME_INITIALIZE_SECONDS_PASSED_INFO
                .format(seconds=seconds_passed)
            )
        seconds_passed -= 1
    await websocket.send_text(game_utils.WS_GAME_NOT_START_ERROR)
    usernames = await sea_battle_ws_manager.get_users_from_room(room_id)
    await sea_battle_ws_manager.delete_saved_games(*usernames)
    await close_connection_update_game(room_id, game_services, True)
    return False


async def close_connection_update_game(
    room_id: str,
    game_services: GameServices,
    delete: bool = False
) -> None:
    winner_username = await sea_battle_ws_manager.get_winner(room_id)
    await sea_battle_ws_manager.remove_room(room_id)

    if delete:
        await game_services.delete_game(PydanticObjectId(room_id))
    else:
        game = await game_services.update_game(
            PydanticObjectId(room_id), status=GameStatusesEnum.ENDED
        )
        winner = await User.get_by_username(winner_username)

        if winner:
            game = await game_services.get_game_by_id(PydanticObjectId(room_id))
            await (GameEnds(game=game, winner=winner)).create()


async def init_game_board(
    websocket: WebSocket, game_board: GameBoard, username: str
) -> None:
    while not game_board.is_all_ships_placed_and_game_initialized:
        ship_type: int = await validate_fields(
            websocket,
            _validate_ship_type,
            game_utils.VALID_SHIP_TYPE_ERROR
        )
        is_vertical: bool = True if ship_type == 1 else await validate_fields(
            websocket,
            _validate_is_vertical,
            game_utils.VALID_VERTICAL_FIELD_ERROR
        )
        cords: tuple[str, int] = await validate_fields(
            websocket,
            _validate_cords,
            game_utils.VALID_COORDINATES_ERROR
        )
        try:
            if not game_board.set_ship_into_game_board(
                ship_type, *cords, vertical=is_vertical
            ):
                await websocket.send_text(game_utils.WS_CORDS_NOT_FREE_ERROR)
            else:
                await sea_battle_ws_manager.set_saved_game(game_board, username)
                await websocket.send_text(game_utils.WS_USER_SHIP_PLACED_INFO)
        except ShipsOver:
            await websocket.send_text(
                game_utils
                .WS_GAME_SHIP_WITH_TYPE_ERROR.format(ship_type=ship_type)
            )


async def validate_fields(
    websocket: WebSocket, validate_func: Callable, error_message: str
) -> Any:
    await websocket.send_text(error_message)

    while (field := validate_func(await websocket.receive_text())) is None:
        await websocket.send_text(error_message)
    return field


def _validate_ship_type(ship_type: str) -> Optional[int]:
    try:
        ship_type = int(ship_type)  # type: ignore
        assert ship_type in range(1, 5)
    except (AssertionError, ValueError, TypeError):
        ship_type = None
    return ship_type  # type: ignore


def _validate_cords(cords: str) -> Optional[tuple[str, int]]:
    try:
        game_x, *game_y = list(cords)
        game_x = game_x.upper()
        game_y = int(''.join(game_y))  # type: ignore
        assert game_y in range(1, 11)
    except (ValueError, AssertionError):
        ...
    else:
        return game_x, game_y  # type: ignore
    return None


def _validate_is_vertical(is_vertical: str) -> Optional[bool]:
    if is_vertical == 'True':
        return True
    elif is_vertical == 'False' or is_vertical == '':
        return False
    return None
