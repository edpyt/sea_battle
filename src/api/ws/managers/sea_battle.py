import pickle
from typing import Any, Optional

from fastapi import WebSocket

from src.api.ws.managers.redis import RedisPubSubManager
from src.core.config import settings
from src.core.services.board import GameBoard


class SeaBattleManager:
    """WebSocket manager for game 'Sea Battle'"""

    def __init__(self) -> None:
        """
        Initializes the WebSocketManager.

        Attributes:
            rooms (dict): A dictionary to store WebSocket connections in
            different rooms
            self.pubsub_client: custom redis pub sub manager
        """
        self.rooms: dict = {}
        self.pubsub_client = RedisPubSubManager(
            host=settings.REDIS_HOST, port=int(settings.REDIS_PORT)
        )

    async def broadcast_to_room(
        self, room_id: str, message: str
    ) -> None:
        """
        Broadcasts a message to all connected WebSockets in a room.

        Args:
            room_id (PydanticObjectId): Room id for channel.
            message (str): Message to be broadcasted.
        """
        await self.pubsub_client._publish(room_id, message)

    @property
    def redis_connection(self) -> Any:
        return self.pubsub_client.redis_connection

    async def add_user_to_room(
        self,
        room_id: str,
        username: str,
        websocket: WebSocket,
        game_board: Optional[GameBoard] = None
    ) -> bool:
        """
        Adds a user's WebSocket connection to a room.

        Args:
            room_id (str): Room id for channel,
            username (str): Username,
            websocket (WebSocket): WebSocket connection object.
        """
        if not game_board:
            game_board = GameBoard()
        await self._setdefault_connection(
            room_id, username, websocket, game_board
        )

        if is_connected := (await self.is_user_in_room(room_id, username)):
            await self.pubsub_client.connect()
            await self.pubsub_client.subscribe(room_id)
            await self.set_saved_game(game_board, username)
        return is_connected

    async def is_user_in_room(
        self, room_id: str, username: str
    ) -> bool:
        """
        Check if user exists in room

        Args:
            room_id (str): Room id for channel,
            username (str): Username
        """
        return bool(self.rooms[room_id].get(username))

    async def get_game_board(
        self, room_id: str, username: str
    ) -> Optional[GameBoard]:
        game_board: Optional[GameBoard] = None
        try:
            game_board = self.rooms[room_id][username]['game_board']
        except KeyError:
            ...
        return game_board

    async def get_users_from_room(self, room_id: str) -> list[str]:
        return list(self.rooms[room_id].keys())

    async def get_other_user(
        self, room_id: str, username: str
    ) -> Optional[dict[str, GameBoard | WebSocket | str]]:
        """
        Get other user from rooms dictionary

        Args:
            room_id (str): Room id for channel,
            username (str): Username
        Returns:
            user_connection(dict): Dictionary with gameboard, connection and
                turn.
        """
        for username_other in self.rooms[room_id]:
            if username != username_other:
                self.rooms[room_id][username_other]['username'] = username_other
                return self.rooms[room_id][username_other]
        return None

    async def is_game_over(self, room_id: str) -> bool:
        return any(
            self.rooms[room_id][user]['game_board'].is_game_over
            for user in self.rooms[room_id]
        )

    async def get_winner(self, room_id: str) -> str:
        for username in self.rooms[room_id]:
            if not self.rooms[room_id][username]['game_board'].is_game_over:
                return username
        raise ValueError()

    async def get_first_move_username(self, room_id: str) -> str:
        return next(
            username for username in self.rooms[room_id]
            if self.rooms[room_id][username]['is_turn']
        )

    async def remove_room(self, room_id: str) -> None:
        """
        Removes a user's WebSocket connection from a room.

        Args:
            room_id (str): Room id for channel.
        """
        if self.rooms.get(room_id):
            for user_connection in self.rooms[room_id]:
                connection: WebSocket = (
                    self.rooms[room_id][user_connection]['connection']
                )
                await connection.close()
            del self.rooms[room_id]
            await self.pubsub_client.unsubscribe(room_id)

    async def all_users_initialized(self, room_id: str) -> bool:
        """
        Is all users initialized game.

        Args:
            room_id (str): Room id for channel.
        """
        if len(self.rooms[room_id]) != 2:
            return False
        user_ships_and_game_initialized = all(
            self.rooms
            [room_id][user]['game_board']
            .is_all_ships_placed_and_game_initialized
            for user in self.rooms[room_id]
        )
        return user_ships_and_game_initialized

    async def _setdefault_connection(
        self,
        room_id: str,
        username: str,
        websocket: WebSocket,
        game_board: GameBoard
    ) -> None:
        """
        Setup default fields for self.rooms

        Args:
            room_id (str): Room id for channel,
            username (str): Username,
            websocket (WebSocket): WebSocket connection object.
        """
        self.rooms.setdefault(room_id, {})
        self.rooms[room_id].setdefault(username, {})

        if len(self.rooms[room_id]) > 2:
            del self.rooms[room_id][username]
            await websocket.send_text('This room is full!')
        else:
            self.rooms[room_id][username].setdefault('connection', websocket)
            self.rooms[room_id][username].setdefault('game_board', game_board)

            other_user = await self.get_other_user(room_id, username)
            self.rooms[room_id][username].setdefault(
                'is_turn', not other_user or not other_user['is_turn']
            )

    async def get_saved_game(self, username: str) -> Optional[GameBoard]:
        """
        Get cached GameBoard instance

        Args:
            username(str): Key for a cache
        """
        serialized_game_board: Optional[GameBoard] = None
        cached_game_board: Optional[bytes] = await (
            self.redis_connection.get(username)
        )
        if cached_game_board:
            serialized_game_board = pickle.loads(cached_game_board)
        return serialized_game_board

    async def set_saved_game(
        self,
        game_board: GameBoard,
        username: str,
    ) -> None:
        """
        Set serialized GameBoard to a cache

        Args:
            game_board(GameBoard): GameBoard instance,
            username(str): Key for a cache.
        """
        serialized_game_board = pickle.dumps(game_board)
        await self.redis_connection.set(username, serialized_game_board)

    async def delete_saved_games(self, *usernames) -> None:
        """
        Delete cached serialized game board instances

        Args:
            usernames(args): args of usernames keys to delete cache.
        """
        await self.redis_connection.delete(*usernames)


sea_battle_ws_manager = SeaBattleManager()
