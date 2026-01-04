from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from src.utils.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=False, pool_pre_ping=True)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# 获取数据库会话
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

