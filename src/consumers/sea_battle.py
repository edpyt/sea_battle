import asyncio
import json

import redis.asyncio as aioredis
from fastapi import WebSocket


class SeaBattleRedisManager:
    """
    WebSocket sea battle redis pub/sub manager
    
    Args:
        host (str): Redis server host.
        port (int): Redis server port.
    """
    def __init__(
        self, host: str = 'localhost', port: int = 6379
    ) -> None:
        self.redis_host = host
        self.redis_port = port
        self.pubsub = None

    async def connect(self) -> None:
        """
        Connects to the Redis server and initializes the pubsub client
        """
        self.redis_connection = await self._get_redis_connection()
        self.pubsub = self.redis_connection.pubsub()

    async def _get_redis_connection(self) -> aioredis.Redis:
        """
        Establishes a connection to Redis.

        Returns:
            aioredis.Redis: Redis connection object
        """
        return aioredis.Redis(
            host=self.redis_host,
            port=self.redis_port,
            auto_close_connection_pool=False
        )