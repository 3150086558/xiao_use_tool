import redis.asyncio as aioredis
from loguru import logger
from .config import get_settings

settings = get_settings()

redis_client: aioredis.Redis = None


async def init_redis():
    global redis_client
    try:
        redis_client = aioredis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
        )
        await redis_client.ping()
        logger.info("Redis 连接成功")
    except Exception as e:
        logger.warning(f"Redis 连接失败: {e}（部分功能可能不可用）")
        redis_client = None


async def close_redis():
    global redis_client
    if redis_client:
        try:
            await redis_client.close()
        except Exception as e:
            logger.warning(f"关闭 Redis 连接失败: {e}")
        redis_client = None


def get_redis() -> aioredis.Redis:
    return redis_client
