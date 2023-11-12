import redis.asyncio as aioredis

from src.core.config import settings


async def get_redis_session() -> aioredis.Redis:
    return aioredis.Redis(
        host=settings.REDIS_HOST, port=int(settings.REDIS_PORT)
    )
