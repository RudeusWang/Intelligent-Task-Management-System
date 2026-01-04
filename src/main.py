from fastapi import FastAPI
from src.controllers import tasks
from src.utils.config import settings

# 创建 FastAPI 应用
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# 注册路由
app.include_router(tasks.router, prefix=settings.API_V1_STR, tags=["tasks"])



if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)

