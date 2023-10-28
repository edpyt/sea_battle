import asyncio

from fastapi import WebSocket
from src.ws.managers.redis import RedisPubSubManager

from src.core.services.board import GameBoard, ShipCountsOver


class SeaBattleManager:
    """WebSocket manager for game 'Sea Battle'"""

    def __init__(self) -> None:
        """
        Initializes the WebSocketManager.

        Attributes:
            rooms (dict): A dictionary to store WebSocket connections in
            different rooms
            self.pub
        """
        self.rooms: dict = {}
        self.pubsub_client = RedisPubSubManager()

    async def add_user_to_room(
        self, room_id: str, username: str, websocket: WebSocket
    ) -> None:
        """
        Adds a user's WebSocket connection to a room.

        Args:
            room_id (str): Room ID or channel name.
            websocket (WebSocket): WebSocket connection object.
        """
        await websocket.accept()

        if room_id not in self.rooms:
            await self.pubsub_client.connect()
            pubsub_subscriber = await self.pubsub_client.subscribe(room_id)
            await asyncio.create_task(
                self._pubsub_data_reader(pubsub_subscriber)
            )
        self.rooms.setdefault(room_id, {})

        self.rooms[room_id].setdefault(username, {})
        (
            self.rooms[room_id][username]
            .setdefault('connection', websocket)
        )
        if not self.rooms[room_id][username].get('game_board'):
            self.rooms[room_id][username]['game_board'] = GameBoard()

    async def _pubsub_data_reader(self, pubsub_subscriber):
        """
        Reads and broadcasts messages received from Redis PubSub.

        Args:
            pubsub_subscriber (aioredis.ChannelSubscribe):
                PubSub object for the subscribed channel.
        """
        while True:
            message = await pubsub_subscriber.get_message(
                ignore_subscribe_messages=True
            )
            if message is not None:
                room_id = message['channel'].decode('utf-8')
                all_sockets = self.rooms[room_id]
                for socket in all_sockets:
                    data = message['data'].decode('utf-8')
                    await socket.send_text(data)

    async def broadcast_to_room(self, room_id: str, message: str) -> None:
        """
        Broadcasts a message to all connected WebSockets in a room.

        Args:
            room_id (str): Room ID or channel name.
            message (str): Message to be broadcasted.
        """
        await self.pubsub_client._publish(room_id, message)

    async def remove_user_from_room(
        self, room_id: str, websocket: WebSocket
    ) -> None:
        """
        Removes a user's WebSocket connection from a room.

        Args:
            room_id (str): Room ID or channel name.
            websocket (WebSocket): WebSocket connection object.
        """
        self.rooms[room_id].remove(websocket)

        if len(self.rooms[room_id]) == 0:
            del self.rooms[room_id]
            await self.pubsub_client.unsubscribe(room_id)

    async def place_ship_to_a_board(
        self, room_id: str, username: str, ship_type: str
    ) -> None:
        """
        Placing ship to the game board

        Args:
            room_id (str): Room ID or channel name,
            ship_type (str): Ship type which place to a board.
        """
        connection: WebSocket = self.rooms[room_id][username]['connection']
        game_board: GameBoard = self.rooms[room_id][username]['game_board']

        try:
            await game_board.set_cell_into_game_board(ship_type)
        except ShipCountsOver:
            await connection.send_text('Ships over!')
        except TypeError:
            await connection.send_text(f'Not found ship with type: {ship_type}')
        else:
            await connection.send_text('Ok!')


sea_battle_ws_manager = SeaBattleManager()
