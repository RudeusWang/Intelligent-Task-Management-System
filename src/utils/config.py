from pydantic import field_validator
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Intelligent Task System"
    API_V1_STR: str = "/api/v1"
    # 必填项，无默认值，启动时若缺失会报错
    DATABASE_URL: str
    REDIS_URL: str

    model_config = {
        "env_file": ".env",
        "case_sensitive": True
    }

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        if not v or not isinstance(v, str):
            raise ValueError("DATABASE_URL is required and must be a string")
        
        # 强制检查是否使用了异步驱动
        # SQLAlchemy 异步模式必须使用 aiomysql (或者 asyncmy)
        if not v.startswith("mysql+aiomysql://"):
            raise ValueError(
                "DATABASE_URL must start with 'mysql+aiomysql://' to support asyncio. "
                "Example: mysql+aiomysql://user:password@localhost/dbname"
            )
        return v

    @field_validator("REDIS_URL", mode="before")
    @classmethod
    def validate_redis_url(cls, v: str) -> str:
        if not v or not isinstance(v, str):
            raise ValueError("REDIS_URL is required and must be a string")
        
        # 简单检查协议头
        if not (v.startswith("redis://") or v.startswith("rediss://")):
            raise ValueError("REDIS_URL must start with 'redis://' or 'rediss://'")
        
        return v

settings = Settings()

