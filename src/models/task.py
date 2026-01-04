from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, Enum, DateTime, ForeignKey, Table, Column, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
import enum
from src.utils.db_base import Base

# 任务状态枚举
class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

# 任务优先级枚举
class TaskPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

# 任务依赖关联表 (多对多)
task_dependencies = Table(
    "task_dependencies",
    Base.metadata,
    Column("parent_task_id", Integer, ForeignKey("tasks.id"), primary_key=True),
    Column("child_task_id", Integer, ForeignKey("tasks.id"), primary_key=True),
)

class Task(Base):
    __tablename__ = "tasks"
    
    # 字段说明：
    # - id: 主键，自增
    # - title: 任务标题（必填）
    # - description: 任务描述（可选）
    # - status: 任务状态（pending/in_progress/completed）
    # - priority: 任务优先级（low/medium/high）
    # - tags: 标签数组（JSON格式存储）
    # - created_at: 创建时间（自动生成）
    # - updated_at: 更新时间（自动更新）
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), index=True)
    description: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    status: Mapped[TaskStatus] = mapped_column(Enum(TaskStatus), default=TaskStatus.PENDING, index=True)
    priority: Mapped[TaskPriority] = mapped_column(Enum(TaskPriority), default=TaskPriority.MEDIUM, index=True)
    
    # 使用 JSON 存储标签，适合轻量级标签系统
    tags: Mapped[List[str]] = mapped_column(JSON, default=list)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    # 关系定义
    # dependencies: 该任务依赖的任务 (parents)
    # dependants: 依赖该任务的任务 (children/downstream)
    dependencies: Mapped[List["Task"]] = relationship(
        "Task",
        secondary=task_dependencies,
        primaryjoin=id == task_dependencies.c.child_task_id,
        secondaryjoin=id == task_dependencies.c.parent_task_id,
        backref="dependants",
        lazy="selectin" # 优化查询，避免 N+1
    )
    @property
    def dependency_ids(self) -> List[int]:
        return [t.id for t in self.dependencies]

