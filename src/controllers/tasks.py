from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from src.utils.deps import get_db, get_redis
from src.models.task_schema import TaskCreate, TaskResponse, TaskUpdate, TaskResponseWithRelations
from src.services.task_service import TaskService
from src.services.task_repo import TaskRepository
from src.models.task import TaskStatus, TaskPriority

# 创建任务路由
router = APIRouter()

# 获取任务服务
def get_task_service(
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis)
) -> TaskService:
    repo = TaskRepository(db)
    return TaskService(repo, redis)

# 创建任务路由
@router.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_in: TaskCreate,
    service: TaskService = Depends(get_task_service)
):
    # 创建新任务
    task = await service.create_task(task_in)
    # 手动处理 response 的依赖 ID 列表
    response = TaskResponse.model_validate(task)
    response.dependency_ids = [t.id for t in task.dependencies]
    return response

@router.get("/tasks/{task_id}", response_model=TaskResponseWithRelations)
async def get_task(
    task_id: int,
    service: TaskService = Depends(get_task_service)
):
    # 获取任务详情，包含依赖信息
    return await service.get_task(task_id)

@router.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_in: TaskUpdate,
    service: TaskService = Depends(get_task_service)
):
    # 更新任务状态或内容
    task = await service.update_task(task_id, task_in)
    response = TaskResponse.model_validate(task)
    response.dependency_ids = [t.id for t in task.dependencies]
    return response

@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    service: TaskService = Depends(get_task_service)
):
    # 删除任务
    await service.delete_task(task_id)

@router.get("/tasks", response_model=List[TaskResponse])
async def list_tasks(
    status: Optional[TaskStatus] = None,
    priority: Optional[TaskPriority] = None,
    page: int = Query(1, ge=1, description="Page number (starts from 1)"),
    page_size: int = Query(20, ge=1, le=100, description="Number of items per page (max 100)"),
    service: TaskService = Depends(get_task_service)
):
    # 任务列表，支持分页、状态筛选、优先级筛选。
    skip = (page - 1) * page_size
    tasks = await service.repo.get_list(skip=skip, limit=page_size, status=status, priority=priority)
    
    # 转换响应
    results = []
    for t in tasks:
        item = TaskResponse.model_validate(t)
        item.dependency_ids = [dep.id for dep in t.dependencies]
        results.append(item)
    return results

@router.get("/tasks/{task_id}/dependencies", response_model=List[TaskResponse])
async def get_task_dependencies(
    task_id: int,
    service: TaskService = Depends(get_task_service)
):
    # 查询任务的所有上游依赖
    task = await service.get_task(task_id)
    return task.dependencies

