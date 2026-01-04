from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime
from src.models.task import TaskStatus, TaskPriority

# 任务基础模型
class TaskBase(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    tags: Optional[List[str]] = Field(default_factory=list)

# 创建任务模型
class TaskCreate(TaskBase):
    title: str
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.MEDIUM
    dependency_ids: Optional[List[int]] = Field(default_factory=list) # 仅接收 ID 列表

# 更新任务模型
class TaskUpdate(TaskBase):
    dependency_ids: Optional[List[int]] = None

# 任务响应模型
class TaskResponse(TaskBase):
    id: int
    created_at: datetime
    updated_at: datetime
    # 为了避免无限递归，列表视图通常不返回嵌套的完整对象，或者使用特定模型
    dependency_ids: List[int] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)

    # 解析依赖ID
    @staticmethod
    def resolve_dependency_ids(task):
        return [t.id for t in task.dependencies]

# 任务响应模型（包含关系）
class TaskResponseWithRelations(TaskResponse):
    # 详情页可以包含更多信息
    dependencies: List["TaskResponse"] = Field(default_factory=list)

