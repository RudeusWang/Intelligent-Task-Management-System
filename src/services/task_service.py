import json
from typing import List, Optional
from fastapi import HTTPException
from redis.asyncio import Redis

from src.models.task import Task, TaskStatus
from src.services.task_repo import TaskRepository
from src.models.task_schema import TaskCreate, TaskUpdate, TaskResponseWithRelations


# 任务服务层
# 负责处理任务的创建、更新、删除等业务逻辑
class TaskService:
    # 初始化
    def __init__(self, repo: TaskRepository, redis: Redis):
        self.repo = repo
        self.redis = redis

    # 清除单个任务缓存
    async def _invalidate_cache(self, task_id: int):
        await self.redis.delete(f"task:{task_id}")

    # 创建任务
    async def create_task(self, obj_in: TaskCreate) -> Task:
        # 1. 检查依赖是否存在
        dependencies = []
        if obj_in.dependency_ids:
            dependencies = await self.repo.get_multi_by_ids(obj_in.dependency_ids)
            if len(dependencies) != len(obj_in.dependency_ids):
                raise HTTPException(status_code=400, detail="One or more dependency IDs do not exist.")

        # 2. 创建实体
        task_data = obj_in.model_dump(exclude={"dependency_ids"})
        task = Task(**task_data)
        task.dependencies = list(dependencies)
        
        return await self.repo.create(task)

    # 获取任务
    # 返回类型统一为 Pydantic Model (TaskResponseWithRelations)
    async def get_task(self, task_id: int) -> TaskResponseWithRelations:
        cache_key = f"task:{task_id}"

        # 1. 尝试从缓存读取
        cached_data = await self.redis.get(cache_key)
        if cached_data:
            # 命中缓存：反序列化为字典，然后转为 Pydantic 对象
            # 这样做的好处是 Service 返回类型始终一致，方便调用方处理
            data_dict = json.loads(cached_data)
            return TaskResponseWithRelations(**data_dict)

        # 2. 缓存未命中：查询数据库
        task = await self.repo.get_by_id(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # 3. 转换为 Pydantic 对象
        # 依赖于步骤一中在 Model 添加的 @property dependency_ids
        task_pydantic = TaskResponseWithRelations.model_validate(task)
        
        # 4. 写入缓存
        # 存入 Redis (序列化为 JSON)
        serialized_data = task_pydantic.model_dump(mode='json')
        await self.redis.set(cache_key, json.dumps(serialized_data), ex=60)

        return task_pydantic

    # 更新任务
    async def update_task(self, task_id: int, obj_in: TaskUpdate) -> Task:
        task = await self.repo.get_by_id(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        # 业务规则: 如果要更新为 Completed，检查依赖
        if obj_in.status == TaskStatus.COMPLETED:
            # 检查是否有未完成的依赖
            for dep in task.dependencies:
                if dep.status != TaskStatus.COMPLETED:
                    raise HTTPException(
                        status_code=400, 
                        detail=f"Cannot complete task. Dependency task {dep.id} ({dep.title}) is not completed."
                    )

        # 处理依赖更新
        if obj_in.dependency_ids is not None:
            new_deps = await self.repo.get_multi_by_ids(obj_in.dependency_ids)
            task.dependencies = list(new_deps)

        update_data = obj_in.model_dump(exclude={"dependency_ids"}, exclude_unset=True)
        updated_task = await self.repo.update(task, update_data)
        
        await self._invalidate_cache(task_id)
        return updated_task

    # 删除任务
    async def delete_task(self, task_id: int):
        task = await self.repo.get_by_id(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        await self.repo.delete(task)
        await self._invalidate_cache(task_id)

