# 学习日志 · AI Film Studio

> **每节课后必写三行：**
> 1. 今天真正学到的原理是什么（一句话）
> 2. 我踩了什么坑 / 哪里卡住了
> 3. 我能不能用大白话讲给同事听（能 → 抄在这里）
>
> 为什么写：看懂 ≠ 会用 ≠ 能讲。**能讲清楚才是真学会了。**
> 这个文件也是 14 天后做项目复盘和面试演示的原始素材。

---

## 第 1 课 · 一次请求的完整路径 & 后端分层

**日期：** 2026-11-02
**对应 plan.md：** Day 1（FastAPI 第一个接口）+ Day 4（Router / Schema / Service / Model 分层）
**代码范围：** `backend/app/main.py`、`backend/app/models.py`、`backend/app/store.py`

### 1.1 请求路径

以 `POST /api/projects`（前端传 `{"name": "雨夜的小猫"}`）为例：

```
① 前端发请求
   POST /api/projects  {"name": "雨夜的小猫"}
        ↓
② FastAPI 匹配路由
   找到 routers/project.py 里的 create_project
   （它挂在 APIRouter(prefix="/api/projects") 上，路径写 "",
     所以最终路径 = prefix + path = /api/projects）
        ↓
③ 【Schema 校验 —— 入站】
   用 schemas/project.py 的 ProjectCreate 检查这段 JSON
   ├─ name 不是 str / 字段缺失 / 超过 100 字 → 直接返回 422
   │  ★ 校验不通过，② 之后的代码【一行都不会执行】
   └─ 通过 → 把 JSON 转成 ProjectCreate 对象，交给路由函数
        ↓
④ Router → Service
   routers/project.py 把 payload.name 交给 services.create_project()
        ↓
⑤ Service 做业务判断
   services/project.py 里：
   ├─ name.strip() 去掉首尾空格
   ├─ 判空 → 空则 raise ValueError
   ├─ 查重 → 项目名已存在则 raise ValueError
   └─ 通过 → 调 store.create_project()
        ↓
⑥ Store 执行数据库操作
   store.py 里 db.add(Project(...)) → db.flush() → 拿到自增 id
   （事务由 FastAPI 依赖注入的 get_db 在请求结束时统一 commit）
        ↓
⑦ 出站校验 + 字段过滤
   回到 router，response_model=ProjectOut 做【出站校验】：
   ├─ 检查返回的数据是否符合 ProjectOut 的形状
   └─ 只保留 id / name / created_at，多余字段直接丢掉
        ↓
⑧ 序列化成 JSON → 返回前端
```

**出错的三条岔路：**

```
③ 入站校验失败 → 422   （前端传的数据不合法，用户的问题）
⑤ 业务判断失败 → 400   （router 捕获 ValueError 翻译而来，用户的问题）
⑦ 出站校验失败 → 500   （后端自己的 bug，返回了不合规的数据）
```

**★ 最关键的一点：③ 的入站校验和 ⑦ 的出站校验是两次校验，方向相反。**

- **入站（③）**：管「**进来的**数据合不合法」（前端传的）
- **出站（⑦）**：管「**出去的**数据会不会泄露 / 不合规」（后端产的）

同一个 `ProjectCreate` 管进、同一个 `ProjectOut` 管出——**这就是"对外契约"的意思。**

### 1.2 每一层的一句话职责

- **Schema（Pydantic）**：对外的数据契约——定义请求/响应**长什么样**，自动校验，生成接口文档。
  只描述"形状"，不做业务判断、不查数据库。
- **Router（路由）**：HTTP 层入口——认 URL 和参数，把 service 抛出的业务异常**翻译成 HTTP 状态码**。
  不写业务规则，不碰 SQL。
- **Service（业务）**：业务规则与决策——能不能创建、怎么算、状态怎么流转。
  规则要被 HTTP 接口 / Celery Worker / 脚本**多处复用**，所以必须独立成层。
- **Store / Repository（数据）**：只负责存取（SELECT / INSERT / UPDATE），**不做业务计算**。
  （现在 `cost_summary` 把业务统计混进来了，第 2 课拆掉。）

> 一句话串起来：**Schema 说"数据长什么样"，Router 说"HTTP 怎么表现"，
> Service 说"业务允不允许"，Store 说"数据存在哪"。**

### 1.3 我踩的坑

**坑 1 · 相对导入漏了点号**
- 报错：`ModuleNotFoundError: No module named 'schemas'`
- 原因：`from schemas.project import X` 会去 **sys.path 顶层**找 `schemas`，
  而它其实在 `app/` 里面。加一个点：`from .schemas.project import X`。
- **规则**：点数的含义 = 从当前包出发，先往上爬 N 层，再往下走到目标。
  - `.` = 当前包（同级）　`..` = 父包（**上一层，不是子级！**）　`...` = 再上一层
  - `app/main.py` 用 1 个点；`app/routers/shot.py` 用 2 个点。

**坑 2 · `services/__init__.py` 是空的（隐藏 bug，import 阶段不报错）**
- 报错：`AttributeError: module 'app.services' has no attribute 'create_project'`
- 原因：`from .. import services` 拿到的是**包**，不是包里的函数。
  Python 导入一个包时**只执行 `__init__.py`**，函数必须在里面"摆出来"才存在。
- 修法：`services/__init__.py` 里写 `from .project import create_project, list_projects`（显式写函数名，别用 `import *`）。

**坑 3 · 忘写路由装饰器（最隐蔽：什么都不报错，但功能失效）**
- 现象：`router` 存在，但 `len(router.routes) == 0`，接口 404。
- 原因：`APIRouter` 只是收集器，不写 `@router.get("")` 的函数不会被注册。
- 类比 Express：`const router = express.Router()` 之后必须写 `router.get(path, handler)`。
- 修法：补上装饰器；prefix 已经是 `/api/events` 时，路径写空字符串 `""`。

**坑 4 · 文件放错层**
- 报错：`ImportError: cannot import name 'router' from 'app.routers.cost'`
- 原因：把 service 的函数写进了 `routers/cost.py`，`main.py` 要的是 `router` 对象。
- **判断放哪层看"对外暴露什么"**：`routers/` 暴露 `router`，`services/` 暴露函数。

**坑 5 · Router 直接调 store**
- 写：`store.list_shots()`（在 routers/event.py 里）
- 为什么不行：违反分层禁令——Router 不该知道"数据怎么拼"，
  而且以后把统计逻辑从 store 搬到 service 时，router 就得跟着改。
- 修法：走 `services.list_shots()`。**这就是分层的复利。**

**坑 6 · service 抛的异常没人接 → 500**
- 现象：`services.create_project` 抛 `ValueError("项目名已存在")`，前端收到 500 而不是 400。
- 原因：router 没 try/except。
- 修法：router 里 `try/except ValueError as e: raise HTTPException(400, str(e))`。
  **service 只管抛业务异常，router 决定它变成 400 / 404 / 409。**

**坑 7 · SSE 接口不能用普通 GET 测试**
- 现象：测试脚本直接卡死。
- 原因：SSE 的响应**永不结束**（`while True`），连接不关闭。
- 修法：`curl -s --max-time 2.5 http://127.0.0.1:8011/api/events | head -c 400`

### 1.4 我能用一句话讲给同事听

**（1）这个后端是怎么组织的**

整个后端分成四块：

- **schema**：类型约束 + 入站出站参数约定（`ProjectCreate` 管进来的、`ProjectOut` 管出去的）
- **routers**：接口路由 + HTTP 异常处理（把 service 抛的 `ValueError` 翻译成 400 / 404）
- **services**：业务层，书写相关业务逻辑（判空、查重、状态怎么流转）
- **store**：进行数据库操作（只管存取，不管业务计算）

**关于 `__init__.py` 统一导出——实际有两种风格，用途不同：**

| 包 | 风格 | 例子 | 为什么 |
|---|---|---|---|
| `services/` | 包级汇总 | `from .. import services` → `services.create_project()` | 里面函数名各不相同，汇总不冲突，调用处更干净 |
| `schemas/` `routers/` | 精确指到模块 | `from ..schemas.shot import ShotCreate`<br>`from .routers.project import router as project_router` | **4 个 router 文件里都有一个叫 `router` 的东西**，必须精确指名否则冲突 |

**（2）一次生成任务是怎么跑完的**

```
前端提交一批镜头
  → 【schema 校验入参】不合法直接 422
  → router 收到，交给 service
  → service 做业务判断（项目存不存在、名字重不重复）
  → store 落库拿到 id
  → 接口【立刻返回】镜头列表（不等生成完）
  → 后台任务开始生成（失败会自动重试，最多 3 次）
  → 每生成出一版候选图，就落一条素材记录（assets + asset_versions）
  → 服务端通过 SSE 每秒把「当前所有镜头状态 + 累计成本」推给前端
  → 用户在候选图里挑一张，存为该镜头的默认素材
```

**（3）为什么这么分层**

1. **分工清楚**：改业务逻辑不会碰到 SQL，改接口不会碰到业务。
2. **关键理由**：这套业务规则**不只 HTTP 接口要用**——将来 Celery Worker、定时脚本都要用同一套逻辑，
   所以必须独立成 service 层，两边共用一份代码。
   （第 1 课实际遇到的例子：`tasks.py` 里也要判断"镜头存不存在"，
   如果这个判断写在 router 里，Worker 就得再抄一遍。）
3. **换存储层只改一层**：现在 SQLite，第 4 课换 PostgreSQL 只改一行 `create_engine()`。

**（4）我踩过的坑（印象最深的一个）**

`services/__init__.py` 一开始是空的，结果 `from .. import services` 之后调
`services.create_project()` 报：

```
AttributeError: module 'app.services' has no attribute 'create_project'
```

**原因**：`from .. import services` 拿到的是**包**，不是包里的函数。
Python 导入一个包时**只执行 `__init__.py`**，函数必须在里面显式"摆出来"才存在。

**修法**：`services/__init__.py` 里写
`from .project import create_project, list_projects`（写具体函数名，别用 `import *`）。

**这个坑最阴的地方是：import 阶段完全不报错，跑到接口才炸。**

**（5）同事可能会追问的三个问题（自检）**

| 追问 | 答案 |
|---|---|
| 为什么不让 HTTP 接口等生成完再返回？ | 视频生成要几十秒到几分钟，HTTP 连接会超时，而且用户不能一直卡在按钮上。所以"立刻返回 + 后台跑 + SSE 推进度" |
| 进度怎么推到前端的？前端怎么知道监听哪个接口？ | SSE，`new EventSource('/api/events')`，服务端每秒推一次当前所有镜头状态和累计成本 |
| 生成失败了怎么办？用户看到什么？ | 状态机转 `failed`，`error` 字段存原因；前端显示失败并给"重试"按钮，点重试就是调一次 retry 接口 |


---
