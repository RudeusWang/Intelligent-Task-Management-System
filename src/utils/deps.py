from typing import AsyncGenerator
from redis.asyncio import Redis
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.utils.db_session import get_db
from src.utils.config import settings

async def get_redis() -> AsyncGenerator[Redis, None]:
    redis = Redis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)
    try:
        yield redis
    finally:
        await redis.close()

