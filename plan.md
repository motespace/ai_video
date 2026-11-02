# AI 影视生产平台开发学习计划

> **项目名称：** AI Film Studio  
> **学习周期：** 14 天  
> **每日投入：** 约 2 小时  
> **学习方向：** Python 后端 + AI 应用开发 + 前后端协作  
> **核心目标：** 看懂 AI 影视生产系统的业务流程、技术架构和核心代码，具备参与实际项目开发的基础能力。

---

## 一、学习背景与目标

### 1. 当前技术基础

| 技术方向 | 当前基础 | 学习目标 |
|---|---|---|
| JavaScript / TypeScript | 熟悉 | 继续发挥前端优势 |
| React / Vue / Next.js | 熟悉 | 完成 AI 影视业务前端 |
| Python | 基础语法、爬虫入门 | 掌握 FastAPI 基础开发 |
| 数据库 | 需要补充 | 理解数据建模和 CRUD |
| Redis | 需要学习 | 理解缓存和消息机制 |
| Celery | 需要学习 | 理解异步任务执行 |
| AI API | 需要学习 | 掌握模型调用和结果处理 |
| AI 工作流 | 需要学习 | 理解 Dify、ComfyUI |

### 2. 核心学习目标

本次学习不以成为 Python 后端专家为目标，而是以理解真实 AI 影视项目为核心。

完成学习后，应该能够：

1. 看懂 FastAPI 项目的基本目录结构。
2. 理解 Router、Schema、Service、Model 的职责。
3. 能够开发简单的 Python API。
4. 理解影视项目、剧本、角色、场景、分镜和素材之间的关系。
5. 理解第三方 AI 模型 API 的调用流程。
6. 理解 Redis、Celery、Worker 和异步任务。
7. 理解 SSE 如何向前端推送生成进度。
8. 理解 AI 图片、视频生成和文件存储流程。
9. 能够阅读 AI 影视平台的整体架构。
10. 能够与项目负责人、后端工程师和 AI 工程师讨论技术方案。

---

## 二、项目实战：AI Film Studio

### 1. 项目定位

开发一个简化版 AI 影视生产管理平台。

用户输入故事或剧本，系统通过 AI 模型进行剧本分析、角色提取、场景拆解、分镜生成，并支持提交图片或视频生成任务。

第一阶段重点实现业务流程和任务管理，不追求完整的视频编辑能力。

### 2. 核心业务流程

```text
创建影视项目
    ↓
输入剧本
    ↓
AI 剧本解析
    ↓
提取角色和场景
    ↓
生成分镜
    ↓
生成角色参考图
    ↓
生成场景素材
    ↓
提交视频生成任务
    ↓
异步执行生成任务
    ↓
获取生成结果
    ↓
保存图片和视频素材
    ↓
完成影视项目
```

### 3. 核心功能模块

| 模块 | 功能 | 优先级 |
|---|---|---|
| 项目管理 | 创建、查询、编辑项目 | P0 |
| 剧本管理 | 保存和编辑剧本文本 | P0 |
| AI 剧本解析 | 提取人物、场景、故事内容 | P0 |
| 角色管理 | 管理人物信息和参考素材 | P1 |
| 场景管理 | 管理场景描述和参考素材 | P1 |
| 分镜管理 | 创建和编辑分镜 | P0 |
| AI 图片生成 | 生成角色和场景参考图 | P1 |
| AI 视频生成 | 提交视频生成任务 | P1 |
| 任务管理 | 任务状态、进度、失败处理 | P0 |
| 素材管理 | 图片、视频和文件记录 | P1 |
| 视频合成 | 将多个视频片段组合 | P2 |

### 4. 项目架构

```text
                  React + TypeScript
                          |
                  HTTP API / SSE
                          |
                       FastAPI
                          |
          ┌───────────────┼───────────────┐
          |               |               |
       Router          Service          Schema
          |               |
          |          业务逻辑处理
          |               |
          └───────────────┼───────────────┐
                          |
                     Database
                    PostgreSQL
                          |
                        Redis
                          |
                    Celery Worker
                          |
             ┌────────────┴────────────┐
             |                         |
          AI 模型 API               OSS / S3
             |
      图片生成 / 视频生成
```

说明：

- FastAPI：负责接收请求和处理业务。
- PostgreSQL：保存项目、剧本、分镜和任务数据。
- Redis：负责缓存或任务消息传递。
- Celery：负责异步任务执行。
- AI API：调用第三方模型或本地模型服务。
- OSS / S3：存储生成的图片和视频。
- SSE：向前端推送任务进度。

这是一套学习用参考架构，实际项目可以采用其他消息队列和任务调度技术。

---

## 三、技术栈规划

| 技术 | 用途 | 学习深度 |
|---|---|---|
| React | 前端业务开发 | 熟练使用 |
| TypeScript | 前端类型管理 | 熟练使用 |
| Python | 后端业务开发 | 掌握基础 |
| FastAPI | 后端 API 框架 | 能编写接口 |
| Pydantic | 请求参数校验 | 理解并使用 |
| SQLAlchemy | ORM 数据库操作 | 掌握基础 |
| PostgreSQL | 业务数据持久化 | 掌握基础 |
| Redis | 缓存、消息中间件 | 理解原理 |
| Celery | 异步任务 | 能运行和调试 |
| SSE | 实时进度通知 | 能够实现 |
| Dify | AI 工作流 | 能搭建基础流程 |
| ComfyUI | AI 图片生成工作流 | 理解节点流程 |
| Docker | 环境部署 | 理解基础 |
| OSS / S3 | 文件存储 | 理解基本流程 |

### AI 模型接入策略

采用两条路线。

**路线 A：第三方 API**

- 先通过 API 调用大语言模型。
- 实现剧本解析和结构化输出。
- 了解图片、视频模型的调用方式。
- 理解 API Key、请求参数、响应数据、错误处理。

**路线 B：本地开源模型**

- 了解开源模型的运行方式。
- 使用 ComfyUI 观察图片生成工作流。
- 了解模型、节点、参数和输出文件。
- 后续再尝试本地部署和 API 接入。

优先完成路线 A，再逐步探索路线 B。

---

## 四、项目目录规划

```text
ai-film-studio/
│
├── docs/
│   ├── business-flow.md
│   ├── database-design.md
│   └── architecture.md
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   │
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   └── database.py
│   │   │
│   │   ├── schemas/
│   │   ├── routers/
│   │   ├── services/
│   │   ├── models/
│   │   ├── tasks/
│   │   ├── integrations/
│   │   │   ├── llm/
│   │   │   ├── image/
│   │   │   └── video/
│   │   │
│   │   └── utils/
│   │
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   ├── components/
│   │   ├── services/
│   │   └── types/
│   └── package.json
│
├── storage/
│   ├── images/
│   └── videos/
│
├── docker/
│
└── README.md
```

前期可以先使用精简目录，随着学习进度再补充模块，不需要第一天就创建所有文件。

---

# 五、14 天详细学习计划

## 第一阶段：理解 AI 影视业务与 AI 工作流

**时间：第 1～3 天**

### Day 1：理解业务流程，搭建 FastAPI 项目

学习目标：

- 理解 AI 影视生产的完整流程。
- 理解项目、剧本、角色、场景、分镜、素材的关系。
- 创建 Python 项目。
- 启动第一个 FastAPI 服务。

学习内容：

1. 理解影视生产业务流程。
2. 了解项目管理和分镜管理。
3. 创建项目目录。
4. 安装 Python 虚拟环境。
5. 安装 FastAPI 和 Uvicorn。
6. 编写项目创建和查询 API。
7. 使用 Swagger 测试接口。

环境安装：

```bash
mkdir ai-film-studio
cd ai-film-studio

mkdir -p docs backend/app/{schemas,routers,services,models,tasks} frontend storage

cd backend

python3 -m venv .venv
source .venv/bin/activate

pip install fastapi "uvicorn[standard]"

pip freeze > requirements.txt
```

第一个接口：

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="AI Film Studio")

projects = []


class ProjectCreate(BaseModel):
    name: str
    description: str | None = None


@app.get("/")
def root():
    return {"message": "Welcome to AI Film Studio"}


@app.post("/api/projects")
def create_project(data: ProjectCreate):
    project = {
        "id": len(projects) + 1,
        "name": data.name,
        "description": data.description,
        "status": "draft"
    }

    projects.append(project)
    return project


@app.get("/api/projects")
def get_projects():
    return {
        "total": len(projects),
        "items": projects
    }
```

启动：

```bash
uvicorn app.main:app --reload
```

访问：

```text
http://127.0.0.1:8000/docs
```

验收标准：

- 成功启动 FastAPI。
- 成功创建影视项目。
- 成功查询影视项目。
- 理解 API、Schema 和数据库的基本区别。
- 能够说明影视项目的业务流程。

产出：

- 项目目录。
- FastAPI 服务。
- 项目创建和查询接口。
- 业务流程图。

### Day 2：学习 Dify，完成 AI 剧本解析

学习目标：

理解大语言模型如何通过工作流完成业务任务。

学习内容：

1. 了解 Dify 的基本界面。
2. 理解模型节点。
3. 理解 Prompt。
4. 理解变量传递。
5. 理解工作流节点之间的关系。
6. 创建剧本解析工作流。

实战任务：

输入一段故事：

```text
一个年轻人在雨夜的城市街道上行走，
发现一只受伤的小猫，决定帮助它。
```

期望 AI 返回：

```json
{
  "title": "雨夜的小猫",
  "characters": [
    {
      "name": "年轻人",
      "description": "一名在雨夜行走的年轻人"
    },
    {
      "name": "小猫",
      "description": "一只受伤的流浪猫"
    }
  ],
  "scenes": [
    {
      "name": "雨夜街道",
      "description": "城市街道，夜晚，下雨"
    }
  ]
}
```

重点理解：

- Prompt 如何影响输出。
- 为什么要使用结构化 JSON。
- 如何校验模型返回的数据。
- 如何处理模型输出不符合预期的情况。

验收标准：

- 能够创建一个 Dify 工作流。
- 能够输入剧本并获得 AI 解析结果。
- 能解释模型调用和工作流的区别。

产出：

- 一个剧本解析工作流。
- 一份结构化剧本数据。

### Day 3：学习 ComfyUI，理解 AI 图片生成

学习目标：

理解 AI 图片生成的基本工作流程。

学习内容：

1. 了解 ComfyUI。
2. 理解节点式工作流。
3. 了解模型、Prompt、采样器和输出节点。
4. 理解图片生成任务的输入和输出。
5. 观察生成结果如何保存。

实战任务：

- 选择一个人物描述。
- 生成一张人物参考图。
- 选择一个场景描述。
- 生成一张场景参考图。
- 观察不同参数对生成结果的影响。

重点理解：

```text
Prompt
  ↓
模型
  ↓
图片生成流程
  ↓
输出图片
  ↓
保存文件
```

验收标准：

- 能够看懂 ComfyUI 的基础节点。
- 能够理解节点之间的数据传递。
- 能够说明图片生成结果如何被后端管理。

产出：

- 一份 ComfyUI 工作流观察记录。
- 人物和场景参考图。

---

## 第二阶段：Python 后端基础

**时间：第 4～7 天**

### Day 4：深入 FastAPI 项目结构

学习目标：

从单文件接口转变为模块化项目结构。

学习内容：

- Router：路由管理。
- Schema：请求和响应结构。
- Service：业务逻辑。
- Model：数据库模型。
- Dependency：依赖注入。
- Middleware：中间件。

实战任务：

将项目创建接口拆分为：

```text
app/
├── main.py
├── schemas/
│   └── project.py
├── routers/
│   └── project.py
└── services/
    └── project.py
```

理解请求流程：

```text
前端请求
  ↓
Router
  ↓
Schema 校验
  ↓
Service
  ↓
返回响应
```

验收标准：

- 能够独立编写一个 Router。
- 能够理解 Service 的职责。
- 能够理解 Schema 和 Model 的区别。

产出：

- 模块化 FastAPI 项目。

### Day 5：数据库与 ORM

学习目标：

理解 AI 影视平台如何保存业务数据。

学习内容：

- 关系型数据库。
- 表、字段、主键、外键。
- SQL 基础。
- CRUD。
- SQLAlchemy ORM。
- 数据库连接。

先使用 SQLite，减少环境配置成本，后续切换 PostgreSQL。

初步设计数据表：

| 表名 | 主要字段 |
|---|---|
| projects | id、name、description、status |
| scripts | id、project_id、content |
| characters | id、project_id、name、description |
| scenes | id、project_id、name、description |
| storyboards | id、project_id、sequence、prompt |
| assets | id、project_id、type、file_path |
| generation_tasks | id、project_id、task_type、status |

实战任务：

- 安装 SQLAlchemy。
- 建立数据库连接。
- 创建 projects 表。
- 实现项目新增、查询、修改、删除。

验收标准：

- 能够理解 ORM。
- 能够完成基本 CRUD。
- 理解数据表之间的关联关系。

产出：

- 数据库设计文档。
- 项目数据持久化功能。

### Day 6：Redis

学习目标：

理解 Redis 在 AI 任务系统中的作用。

学习内容：

- Redis 是什么。
- Key-Value 数据结构。
- String、List、Hash、Set。
- 缓存。
- 消息队列基础。
- Redis 与数据库的区别。

理解场景：

```text
PostgreSQL：
保存项目、剧本、任务等正式业务数据。

Redis：
保存缓存、临时数据，也可以作为任务消息中间件。
```

实战任务：

- 安装 Redis。
- 连接 Redis。
- 写入和读取测试数据。
- 理解 Redis 在任务队列中的角色。

验收标准：

- 能够连接 Redis。
- 能够执行基本读写。
- 能够说明 Redis 和 PostgreSQL 的区别。

产出：

- Redis 测试代码。
- Redis 基础笔记。

### Day 7：Celery 异步任务

学习目标：

理解耗时任务为什么需要异步执行。

学习内容：

- Broker。
- Worker。
- Task。
- Queue。
- Retry。
- Concurrency。
- 任务状态。

理解任务执行流程：

```text
前端提交请求
    ↓
FastAPI 创建任务
    ↓
Redis Broker
    ↓
Celery Worker
    ↓
执行任务
    ↓
更新数据库
```

实战任务：

- 安装 Celery。
- 创建 Celery 实例。
- 编写一个模拟视频生成任务。
- 启动 Worker。
- 提交任务并观察执行过程。

验收标准：

- 能够启动 Worker。
- 能够提交异步任务。
- 能够理解 API 和 Worker 的区别。
- 能够解释为什么不能让 HTTP 接口一直等待视频生成。

产出：

- Celery 异步任务 Demo。

---

## 第三阶段：前后端与 AI 业务整合

**时间：第 8～11 天**

### Day 8：实现项目管理前端

学习目标：

将现有 React 技术与 Python 后端连接。

学习内容：

- React 项目搭建。
- API 请求封装。
- TypeScript 类型定义。
- 项目列表。
- 项目创建表单。
- 加载和错误状态。

实战任务：

实现：

- 项目列表页。
- 创建项目弹窗。
- 项目详情页。
- FastAPI 接口调用。

验收标准：

- React 能成功请求 FastAPI。
- 创建项目后能够显示。
- 刷新页面后数据仍然存在。

产出：

- 项目管理页面。

### Day 9：AI 剧本解析

学习目标：

让后端真正调用 AI 模型。

学习内容：

- HTTP 请求。
- API Key。
- 模型请求参数。
- Prompt。
- JSON 结构化输出。
- 超时和错误处理。

实战任务：

```text
前端输入剧本
    ↓
FastAPI 接收请求
    ↓
调用 AI 模型 API
    ↓
获取结构化结果
    ↓
解析人物、场景、分镜
    ↓
保存数据库
    ↓
返回前端
```

验收标准：

- 能够通过后端调用第三方 AI API。
- 能够处理模型返回结果。
- 能够保存解析结果。
- 能够处理 API 失败情况。

产出：

- AI 剧本解析接口。
- 结构化剧本数据。

### Day 10：AI 视频生成任务

学习目标：

理解 AI 视频生成的异步业务流程。

学习内容：

- 生成任务创建。
- task_id。
- 任务状态。
- Celery Worker。
- 模型服务调用。
- provider_task_id。

实战任务：

实现：

```text
用户点击生成视频
    ↓
FastAPI 创建业务任务
    ↓
返回 task_id
    ↓
Celery Worker 执行任务
    ↓
调用模型服务
    ↓
获取生成结果
    ↓
更新数据库
```

先使用模拟任务，不要求真的生成视频。

任务状态：

```text
queued
processing
success
failed
cancelled
```

注意：

业务系统自己的 task_id 和第三方模型的 provider_task_id 是两个不同的标识。

验收标准：

- 能够创建生成任务。
- 能够返回 task_id。
- 能够通过 Worker 执行任务。
- 能够查询任务状态。

产出：

- 视频生成任务 Demo。

### Day 11：SSE 任务进度通知

学习目标：

理解前端如何获取任务实时进度。

学习内容：

- HTTP 轮询。
- SSE。
- WebSocket。
- 断线重连。
- 任务状态恢复。

实战任务：

```text
前端提交任务
    ↓
获得 task_id
    ↓
建立 SSE 连接
    ↓
后端推送任务状态
    ↓
前端更新进度
```

重点理解：

| 技术 | 适用场景 |
|---|---|
| 轮询 | 简单状态查询 |
| SSE | 服务端向前端推送进度 |
| WebSocket | 实时双向通信 |

验收标准：

- 能够实现一个 SSE 接口。
- 前端能接收任务状态变化。
- 断开页面后，重新进入仍能通过 task_id 查询任务。

产出：

- 实时任务进度页面。

---

## 第四阶段：存储、异常处理与项目复盘

**时间：第 12～14 天**

### Day 12：文件存储与素材管理

学习目标：

理解 AI 生成图片和视频如何保存。

学习内容：

- 文件上传。
- 本地文件存储。
- OSS / S3。
- 文件元数据。
- 文件访问地址。
- 文件与业务数据的关系。

实战任务：

- 上传图片。
- 保存图片文件。
- 数据库保存文件路径。
- 将素材关联到对应项目和分镜。

理解：

```text
图片 / 视频文件
       ↓
OSS / S3
       ↓
返回文件地址或对象 Key
       ↓
数据库保存元数据
       ↓
前端展示素材
```

验收标准：

- 能够上传文件。
- 能够保存文件信息。
- 能够在前端展示素材。

产出：

- 素材管理基础功能。

### Day 13：任务异常处理

学习目标：

理解生产环境中的任务可靠性。

学习内容：

- 模型 API 超时。
- 任务失败。
- 任务重试。
- 幂等性。
- 重复提交。
- Worker 异常退出。
- 任务恢复。

重点场景：

1. 用户重复点击生成按钮。
2. AI 模型请求超时。
3. Worker 执行过程中退出。
4. 模型生成成功，但文件上传失败。
5. 用户关闭浏览器后重新进入。

验收标准：

- 能够区分任务失败和任务超时。
- 能够理解重试机制。
- 能够理解幂等设计。
- 能够解释任务状态为什么需要持久化。

产出：

- 任务异常处理方案。
- 任务生命周期说明。

### Day 14：系统复盘与面试准备

学习目标：

能够从业务、架构、技术和项目交付角度介绍系统。

复盘内容：

1. 业务流程图。
2. 系统架构图。
3. 数据库 ER 图。
4. API 接口文档。
5. AI 模型调用流程。
6. 异步任务执行流程。
7. 文件存储流程。
8. 异常处理方案。

准备面试问题：

- 为什么 AI 视频生成需要异步任务？
- Redis 和数据库分别负责什么？
- Celery Worker 是如何执行任务的？
- SSE 和 WebSocket 有什么区别？
- 为什么业务 task_id 和 provider_task_id 要分开？
- AI 模型 API 超时如何处理？
- 如何防止用户重复提交生成任务？
- 用户关闭浏览器后，任务是否还会继续？
- 生成的视频文件应该保存在哪里？
- 如何设计一个 AI 影视生产平台？

验收标准：

能够不依赖教程，独立讲清楚整个系统的业务流程和技术架构。

产出：

- 完整项目文档。
- 项目架构图。
- 面试问题与回答。
- 可运行的项目 Demo。

---

# 六、每日时间安排

每天约 2 小时，不建议连续观看教程。

| 时间 | 内容 | 时长 |
|---|---|---|
| 第一部分 | 理解技术原理和业务场景 | 30 分钟 |
| 第二部分 | 阅读文档、查看示例代码 | 30 分钟 |
| 第三部分 | 动手编码 | 50 分钟 |
| 第四部分 | 复盘和记录 | 10 分钟 |

学习原则：

- 每天至少写一段代码。
- 每天至少解决一个具体问题。
- 不要求一次掌握全部原理。
- 遇到不懂的概念，先结合当前项目理解。
- 不要为了学习而安装过多工具。
- 先让最小 Demo 跑通，再逐步完善。

---

# 七、学习优先级

考虑到目前主要目标是理解 AI 影视项目、参与实际开发，建议按照以下优先级投入精力。

| 优先级 | 技术 | 达成要求 |
|---|---|---|
| P0 | FastAPI | 能看懂并编写基础接口 |
| P0 | Python | 能理解函数、类、模块、异常处理 |
| P0 | 数据库 | 能理解表结构和 CRUD |
| P0 | AI API | 能理解模型调用和数据处理 |
| P0 | React + TypeScript | 能完成业务页面 |
| P1 | Redis | 理解消息和缓存机制 |
| P1 | Celery | 能理解和调试异步任务 |
| P1 | SSE | 能实现任务进度推送 |
| P1 | Dify | 能看懂基础 AI 工作流 |
| P1 | ComfyUI | 能看懂图片生成工作流 |
| P2 | Docker | 能看懂基本部署配置 |
| P2 | OSS / S3 | 能理解文件存储方案 |
| P2 | 本地模型部署 | 了解运行方式和资源要求 |

---

# 八、推荐学习资源

## Python 后端

- FastAPI：https://fastapi.tiangolo.com/
- Python：https://docs.python.org/3/
- Pydantic：https://docs.pydantic.dev/latest/
- SQLAlchemy：https://docs.sqlalchemy.org/

## 数据库和任务队列

- PostgreSQL：https://www.postgresql.org/docs/
- Redis：https://redis.io/docs/
- Celery：https://docs.celeryq.dev/
- Flower：https://flower.readthedocs.io/

## AI 应用和工作流

- Dify：https://docs.dify.ai/
- Dify GitHub：https://github.com/langgenius/dify
- ComfyUI：https://docs.comfy.org/
- ComfyUI GitHub：https://github.com/comfyanonymous/ComfyUI

## AI 模型

- Hugging Face：https://huggingface.co/docs
- OpenAI API：https://platform.openai.com/docs

---

# 九、最终项目验收清单

完成 14 天后，按照下面的标准检查学习成果。

## 业务能力

- [ ] 能够讲清楚 AI 影视生产流程。
- [ ] 理解剧本、角色、场景、分镜之间的关系。
- [ ] 理解图片、视频素材的管理方式。
- [ ] 理解 AI 视频生成的业务流程。

## Python 后端能力

- [ ] 能够启动 FastAPI 服务。
- [ ] 能够编写基本 API。
- [ ] 能够理解 Router、Schema、Service、Model。
- [ ] 能够连接数据库。
- [ ] 能够完成基本 CRUD。
- [ ] 能够调用第三方 AI API。

## 异步任务能力

- [ ] 理解 Redis 的基本用途。
- [ ] 理解 Celery 的任务执行机制。
- [ ] 理解 Worker 的职责。
- [ ] 理解 task_id 的用途。
- [ ] 理解 SSE 的进度推送机制。
- [ ] 理解任务失败、重试和幂等。

## AI 应用能力

- [ ] 能够搭建简单 Dify 工作流。
- [ ] 理解 Prompt 和结构化输出。
- [ ] 能够看懂 ComfyUI 基础节点。
- [ ] 理解第三方模型和本地模型的区别。

## 项目交付能力

- [ ] 有一个可运行的 AI 影视平台 Demo。
- [ ] 有一张系统架构图。
- [ ] 有一份数据库设计文档。
- [ ] 有一份 API 接口说明。
- [ ] 能够介绍核心技术流程。
- [ ] 能够说明当前系统的不足和后续优化方向。

---

# 十、后续学习路线

14 天只是第一阶段，不意味着已经具备独立承担完整 AI 后端系统的能力。

建议后续分为三个阶段：

### 阶段一：理解项目（第 1～14 天）

目标：看懂系统架构、业务流程和核心代码。

### 阶段二：独立开发（第 15～30 天）

目标：

- 完善 FastAPI 项目结构。
- 使用 PostgreSQL。
- 完善任务队列和任务状态。
- 接入真实 AI 模型。
- 实现素材管理。
- 增加用户、权限和项目隔离。
- 完善 Docker 部署。

### 阶段三：工程化能力（第 31～45 天）

目标：

- 学习日志和监控。
- 学习接口鉴权。
- 学习任务重试与恢复。
- 学习模型服务适配层。
- 学习文件存储和 CDN。
- 学习基础部署和性能优化。
- 阅读真实 AI 应用项目源码。

---

# 十一、执行原则

本计划最重要的原则：

**不要把自己变成一个只会调用 AI API 的前端开发者，而是逐步成长为理解 AI 产品、前后端协作、模型接入和任务系统的应用开发工程师。**

学习过程中，重点建立三种能力：

1. **业务理解能力：** 知道 AI 影视产品解决什么问题。
2. **技术理解能力：** 知道系统各个模块为什么存在、如何协作。
3. **工程交付能力：** 能够将一个业务需求拆解成接口、数据、任务和前端页面。

最终目标不是记住多少框架，而是拿到一个真实 AI 影视项目时，能够快速理解它、定位代码、参与开发，并逐步承担更完整的业务模块。

> 学习策略：先理解业务，再理解架构，最后通过代码验证原理。每个技术都要放在实际业务场景中学习。