# 任务数据访问层 
# 负责与数据库交互，提供任务的增删改查操作

from typing import List, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, asc, or_
from sqlalchemy.orm import selectinload

from src.models.task import Task, TaskStatus, TaskPriority

class TaskRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    # 创建任务
    async def create(self, task: Task) -> Task:
        self.db.add(task)
        await self.db.commit()
        await self.db.refresh(task)
        return task

    # 根据任务ID获取任务
    async def get_by_id(self, task_id: int) -> Optional[Task]:

        # 使用 selectinload 预加载依赖，防止 N+1
        stmt = select(Task).options(selectinload(Task.dependencies)).where(Task.id == task_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    # 根据任务ID列表获取任务列表
    async def get_multi_by_ids(self, ids: List[int]) -> List[Task]:
        stmt = select(Task).where(Task.id.in_(ids))
        result = await self.db.execute(stmt)
        return result.scalars().all()

    # 更新任务
    async def update(self, task: Task, update_data: dict) -> Task:
        for key, value in update_data.items():
            setattr(task, key, value)
        self.db.add(task)
        await self.db.commit()
        await self.db.refresh(task)
        return task

    # 删除任务
    async def delete(self, task: Task) -> None:
        self.db.delete(task)
        await self.db.commit()

    # 获取任务列表
    async def get_list(
        self, 
        skip: int = 0, 
        limit: int = 100,
        status: Optional[TaskStatus] = None,
        priority: Optional[TaskPriority] = None,
        sort_by: str = "created_at_desc"
    ) -> List[Task]:
        
        stmt = select(Task).options(selectinload(Task.dependencies))

        # 过滤
        if status:
            stmt = stmt.where(Task.status == status)
        if priority:
            stmt = stmt.where(Task.priority == priority)
        
        # 排序
        if sort_by == "created_at_desc":
            stmt = stmt.order_by(desc(Task.created_at))
        elif sort_by == "priority_desc":
             # 利用 Enum 顺序或 Case 语句，这里简化处理
             stmt = stmt.order_by(Task.priority) 
        elif sort_by == "status":
             stmt = stmt.order_by(Task.status)
        
        stmt = stmt.offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()

