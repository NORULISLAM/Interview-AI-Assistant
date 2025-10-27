"""
Redis configuration and connection management
"""
import aioredis
from app.core.config import settings

# Global Redis client
redis_client = None


async def get_redis():
    """Get Redis client instance"""
    global redis_client
    if redis_client is None:
        redis_client = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
    return redis_client


async def close_redis():
    """Close Redis connection"""
    global redis_client
    if redis_client:
        await redis_client.close()
        redis_client = None
