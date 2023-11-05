from fastapi import WebSocket

from src.api.ws.managers.redis import RedisPubSubManager
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
        self.pubsub_client = RedisPubSubManager(host="localhost", port=6379)

    async def add_user_to_room(
        self, room_id: str, username: str, websocket: WebSocket
    ) -> bool:
        """
        Adds a user's WebSocket connection to a room.

        Args:
            room_id (str): Room id for channel,
            username (str): Username,
            websocket (WebSocket): WebSocket connection object.
        """
        await self._set_default_connection(room_id, username, websocket)

        if is_connected := (await self.is_user_in_room(room_id, username)):
            await self.pubsub_client.connect()
            await self.pubsub_client.subscribe(room_id)

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

    async def remove_room(self, room_id: str) -> None:
        """
        Removes a user's WebSocket connection from a room.

        Args:
            room_id (PydanticObjectId): Room id for channel.
        """
        if self.rooms.get(room_id):
            del self.rooms[room_id]
            await self.pubsub_client.unsubscribe(room_id)

    async def _set_default_connection(
        self, room_id: str, username: str, websocket: WebSocket
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
            self.rooms[room_id][username].setdefault('game_board', GameBoard())


sea_battle_ws_manager = SeaBattleManager()
