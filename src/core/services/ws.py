from beanie import PydanticObjectId
from fastapi import WebSocket

from src.api.ws.managers.sea_battle import sea_battle_ws_manager
from src.core.services.board import GameBoard, place_ship_to_board
from src.domain.lobby.exceptions.game import GameNotExists
from src.domain.lobby.usecases.game import GameServices


async def sea_battle_ws(
    websocket: WebSocket,
    username: str,
    room_id: PydanticObjectId,
    game_services: GameServices
) -> None:
    """
    Main logic with sea battle websockets

    Args:
        websocket (WebSocket): WebSocket connection object,
        username (str): Username,
        room_id (PydanticObjectId): Room id from `Game` model.
    """
    try:
        await game_services.get_game_by_id(room_id)
    except GameNotExists:
        await websocket.accept()
        await websocket.send_text(f"Not found game with id: {room_id}")
        await websocket.close()
    else:
        await sea_battle_ws_manager.add_user_to_room(
            room_id, username, websocket
        )


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
