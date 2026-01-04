# 智能任务管理系统 (Intelligent Task Management System)

## Role Track
Backend

## Tech Stack
- **Language**: Python 3.10
- **Framework**: FastAPI 0.109.0
- **Database**: MySQL (使用 aiomysql 异步驱动)
- **Cache**: Redis 5.0.1
- **ORM**: SQLAlchemy 2.0.25
- **Validation**: Pydantic 2.5.3
- **Other tools**: 
  - uvicorn (ASGI 服务器)
  - python-dotenv (环境变量管理)
  - cryptography (加密支持)

## Features Implemented
- [x] 任务的 CRUD 操作（创建、读取、更新、删除）
- [x] 任务状态管理（pending/in_progress/completed）
- [x] 任务优先级管理（low/medium/high）
- [x] 任务标签系统（支持多个标签）
- [x] 任务依赖管理（多对多关系，支持任务间的依赖链）
- [x] 任务列表查询（支持分页、状态筛选、优先级筛选）
- [x] Redis 缓存机制（任务详情缓存，60秒过期）
- [x] 依赖验证（完成任务前检查所有依赖是否已完成）
- [x] 异步数据库操作（使用 SQLAlchemy 异步模式）
- [x] RESTful API 设计
- [x] 自动 API 文档（FastAPI 自动生成 OpenAPI/Swagger 文档）

## Setup Instructions

### 1. Prerequisites
- Python 3.8+
- MySQL 5.7+ 或 MySQL 8.0+
- Redis 5.0+

### 2. Installation steps

```bash
# 克隆项目（如果适用）
git clone <repository-url>
cd intelligent_task_management_system

# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 3. Configuration

创建 `.env` 文件在项目根目录，配置以下环境变量：

```env
# 数据库配置（必须使用 aiomysql 异步驱动）
DATABASE_URL=mysql+aiomysql://username:password@localhost:3306/dbname

# Redis 配置
REDIS_URL=redis://localhost:6379/0

# 可选配置（已在代码中设置默认值）
PROJECT_NAME=Intelligent Task System
API_V1_STR=/api/v1
```

**重要提示**：
- `DATABASE_URL` 必须以 `mysql+aiomysql://` 开头以支持异步操作
- 确保 MySQL 数据库已创建
- 确保 Redis 服务正在运行

### 4. Running the application

```bash
# 方式1: 直接运行
python -m src.main

# 方式2: 使用 uvicorn（推荐，支持热重载）
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

应用启动后，访问以下地址：
- API 文档（Swagger UI）: http://localhost:8000/docs
- API 文档（ReDoc）: http://localhost:8000/redoc
- 健康检查: http://localhost:8000/health

## API Documentation

### Base URL
```
http://localhost:8000/api/v1
```

### Endpoints

#### 1. 创建任务
**POST** `/tasks`

**Request Body:**
```json
{
  "title": "完成项目文档",
  "description": "编写项目的 README 和 API 文档",
  "status": "pending",
  "priority": "high",
  "tags": ["文档", "重要"],
  "dependency_ids": [1, 2]
}
```

**Response:** `201 Created`
```json
{
  "id": 3,
  "title": "完成项目文档",
  "description": "编写项目的 README 和 API 文档",
  "status": "pending",
  "priority": "high",
  "tags": ["文档", "重要"],
  "dependency_ids": [1, 2],
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

#### 2. 获取任务详情
**GET** `/tasks/{task_id}`

**Response:** `200 OK`
```json
{
  "id": 3,
  "title": "完成项目文档",
  "description": "编写项目的 README 和 API 文档",
  "status": "pending",
  "priority": "high",
  "tags": ["文档", "重要"],
  "dependency_ids": [1, 2],
  "dependencies": [
    {
      "id": 1,
      "title": "任务1",
      "status": "completed",
      ...
    }
  ],
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

#### 3. 更新任务
**PUT** `/tasks/{task_id}`

**Request Body:**
```json
{
  "status": "in_progress",
  "priority": "high",
  "dependency_ids": [1]
}
```

**Response:** `200 OK`
```json
{
  "id": 3,
  "title": "完成项目文档",
  "status": "in_progress",
  "priority": "high",
  "dependency_ids": [1],
  ...
}
```

#### 4. 删除任务
**DELETE** `/tasks/{task_id}`

**Response:** `204 No Content`

#### 5. 获取任务列表
**GET** `/tasks`

**Query Parameters:**
- `status` (optional): 任务状态筛选 (pending/in_progress/completed)
- `priority` (optional): 优先级筛选 (low/medium/high)
- `page` (optional): 页码，从 1 开始，默认 1
- `page_size` (optional): 每页数量，最大 100，默认 20

**Example:**
```
GET /tasks?status=pending&priority=high&page=1&page_size=10
```

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "title": "任务1",
    "status": "pending",
    "priority": "high",
    "dependency_ids": [],
    ...
  },
  {
    "id": 2,
    "title": "任务2",
    "status": "in_progress",
    "priority": "medium",
    "dependency_ids": [1],
    ...
  }
]
```

#### 6. 获取任务依赖
**GET** `/tasks/{task_id}/dependencies`

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "title": "依赖任务1",
    "status": "completed",
    ...
  }
]
```

#### 7. 健康检查
**GET** `/health`

**Response:** `200 OK`
```json
{
  "status": "ok"
}
```

## Design Decisions

### 1. 架构设计
- **分层架构**: 采用 Controller → Service → Repository 三层架构，职责清晰，便于维护和测试
- **依赖注入**: 使用 FastAPI 的依赖注入系统，便于管理和测试
- **异步编程**: 全面使用异步 I/O（async/await），提高并发性能

### 2. 数据库设计
- **异步驱动**: 使用 `aiomysql` 而非同步的 `pymysql`，充分利用异步优势
- **关系设计**: 任务依赖使用多对多关系表，支持复杂的依赖链
- **索引优化**: 在常用查询字段（id, title, status, priority, created_at）上建立索引

### 3. 缓存策略
- **缓存粒度**: 仅缓存任务详情（单个任务），列表查询不缓存（数据变化频繁）
- **缓存过期**: 60秒过期时间，平衡数据一致性和性能
- **缓存失效**: 任务更新或删除时主动清除缓存，保证数据一致性

### 4. 业务规则
- **依赖验证**: 完成任务前必须确保所有依赖任务已完成，防止逻辑错误
- **状态枚举**: 使用 Python Enum 确保状态值的类型安全
- **数据验证**: 使用 Pydantic 进行请求/响应数据验证，提供清晰的错误信息

### 5. 性能优化
- **N+1 查询优化**: 使用 `selectinload` 预加载依赖关系，避免 N+1 查询问题
- **分页支持**: 列表查询支持分页，防止大数据量查询导致性能问题

## Challenges & Solutions

### 挑战1: 异步数据库驱动配置
**问题**: 初始配置时容易使用同步的 `pymysql` 驱动，导致异步操作失败。

**解决方案**: 
- 在配置验证中强制检查 `DATABASE_URL` 必须以 `mysql+aiomysql://` 开头
- 提供清晰的错误提示信息

### 挑战2: 任务依赖的循环依赖检测
**问题**: 当前实现未检测循环依赖（如任务 A 依赖任务 B，任务 B 又依赖任务 A）。

**解决方案**: 
- 当前版本允许循环依赖（由业务层决定是否合理）
- 未来改进：可以在 Service 层添加循环依赖检测算法（DFS）

### 挑战3: 缓存与数据库一致性
**问题**: 缓存数据可能与数据库不一致。

**解决方案**:
- 采用缓存失效策略：更新/删除操作时主动清除缓存
- 设置合理的缓存过期时间（60秒）
- 详情查询采用 Cache-Aside 模式

### 挑战4: 任务依赖关系的序列化
**问题**: 在 API 响应中，任务依赖关系可能导致无限递归序列化。

**解决方案**:
- 列表视图返回 `dependency_ids`（ID 列表）而非完整对象
- 详情视图使用 `TaskResponseWithRelations` 包含完整的依赖对象
- 使用 Pydantic 的 `from_attributes=True` 简化序列化

## Future Improvements

1. **循环依赖检测**: 在创建/更新任务时检测并阻止循环依赖
2. **任务搜索**: 添加全文搜索功能，支持按标题、描述搜索任务
3. **任务排序**: 支持更多排序选项（按优先级、状态、更新时间等）
4. **批量操作**: 支持批量创建、更新、删除任务
5. **任务统计**: 添加任务统计 API（按状态、优先级统计等）
6. **用户认证**: 添加用户认证和授权，支持多用户任务管理
7. **任务历史**: 记录任务状态变更历史
8. **通知系统**: 任务状态变更时发送通知（邮件、WebSocket 等）
9. **任务模板**: 支持任务模板，快速创建相似任务
10. **单元测试**: 添加完整的单元测试和集成测试
11. **API 限流**: 添加请求限流，防止 API 滥用
12. **日志系统**: 完善日志记录，便于问题排查和监控
13. **数据库迁移**: 使用 Alembic 进行数据库版本管理
14. **Docker 支持**: 添加 Docker 和 Docker Compose 配置，简化部署

## Time Spent
Approximately 3 hours

