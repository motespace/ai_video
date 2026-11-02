# 后端知识速查手册（写给前端出身的你）

> 目标不是"学会后端"，是**能在面试里画对图、说对话、并诚实说出 demo 与生产的差距**。
> 学习顺序：🔴 必会 → 🟡 懂概念 → 🟢 先不管

---

## 一、一张图看懂"生产版 AI 短剧流水线"

```
                        ┌─────────────────────────────┐
   用户浏览器  ───────►  │  前端 (React/Vue)           │
                        │  工作台 / 播放端             │
                        └──────────┬──────────────────┘
                                   │ REST + SSE
                        ┌──────────▼──────────────────┐
                        │  FastAPI (Web 层)           │  ← 你 demo 里的 main.py
                        │  鉴权 / 参数校验 / 编排      │
                        └───┬──────────────────────┬──┘
                            │ 写状态              │ 投递任务
              ┌─────────────▼──────┐   ┌──────────▼────────────┐
              │  PostgreSQL        │   │  Redis                │
              │  项目/镜头/候选    │   │  ① Broker（任务队列）  │
              │  /用户/成本账单    │   │  ② 缓存 / 计数器      │
              │  （本 demo 用      │   │  ③ 进度 / 幂等键      │
              │    SQLite）        │   └──────────┬────────────┘
              └─────────────▲──────┘              │
                            │                ┌─────▼──────────────┐
                            │                │  Celery Worker 池  │
                            │                │  （跑在 GPU 机器）  │
                            │                │  调模型 / 渲染      │
                            │                └─────┬──────────────┘
                            │                      │
                            │                ┌─────▼──────────────┐
                            │                │  生成服务          │
                            │                │  可灵/即梦/自研     │
                            │                │  （可插拔）        │
                            │                └─────┬──────────────┘
                            │                      │
              ┌─────────────▼──────────────────────▼───┐
              │  对象存储 (OSS/S3/MinIO) + CDN           │
              │  视频 / 图片 / 音频 / 字幕文件            │
              └─────────────────────────────────────────┘
```

**记忆口诀**（背这个就够）：
- **数据库存"状态"，对象存储存"文件"**
- **Redis 既排队又加速**
- **Celery 让"提交"和"执行"分居两台机器**
- **GPU 机器只干重活，Web 层绝不碰推理**

---

## 二、🔴 必会：只有 2.5 天

### 2.1 FastAPI 四个用法（1.5 天）

```python
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel

app = FastAPI()

# ① 路由装饰器 ≈ Express 的 app.post()
class ShotCreate(BaseModel):        # ② Pydantic 契约（≈ TS interface + zod）
    project_id: int
    prompts: list[str]

@app.post("/api/shots")
def create_shots(body: ShotCreate, background: BackgroundTasks):
    ids = save(body)                          # ③ 同步落库
    background.add_task(run_generation, ids)  # ③ BackgroundTasks：先返回，后台跑
    return {"shot_ids": ids}
```

**② Pydantic 到底做了什么**（面试常问）：
前端传 `{"prompts": "abc"}`（字符串不是数组），FastAPI 在**进函数之前**就返回 422。
好处：接口契约是**运行时强制的**，不靠口头对齐、不靠前端自觉。

**③ BackgroundTasks 到底怎么用**：
- 传 `background: BackgroundTasks` 参数
- `background.add_task(fn, *args)`
- 接口**立刻返回**，fn 在响应之后才执行
- ⚠️ 它是**进程内**的：进程重启任务就没了。生产必须换 Celery

**④ SSE 是什么**：
```python
async def stream():
    while True:
        yield f"data: {json.dumps(payload)}\n\n"   # SSE 报文格式
        await asyncio.sleep(1)
```
前端：
```js
const es = new EventSource('/api/events')
es.onmessage = e => setState(JSON.parse(e.data))
```
为什么不用 WebSocket：我们只要**单向**推，SSE 走 HTTP、自带断线重连，更简单。

**async 的唯一铁律**：
> 耗时操作必须 `await asyncio.sleep()`，**绝不能** `time.sleep()`。
> `time.sleep` 会把整个事件循环卡死，其他请求全部排队。
> `await` 的意思是"我这段时间让出线程，你先去处理别的请求"。

### 2.2 五条 SQL（半天）

```sql
CREATE TABLE shots (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_id INTEGER NOT NULL,
  prompt TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'pending',
  cost REAL NOT NULL DEFAULT 0
);

SELECT * FROM shots WHERE project_id = ?;        -- 查
INSERT INTO shots(project_id, prompt) VALUES (?,?);  -- 增
UPDATE shots SET status = ? WHERE id = ?;        -- 改
DELETE FROM shots WHERE id = ?;                 -- 删
```

SQLite 的连接用法（Python 标准库自带）：
```python
import sqlite3
conn = sqlite3.connect("pipeline.db")
conn.row_factory = sqlite3.Row      # 让结果能按列名取
cur = conn.execute("SELECT * FROM shots WHERE id=?", (sid,))
row = cur.fetchone()
conn.commit()                        # 写操作要提交
conn.close()
```

⚠️ **面试要说的话**：这个 demo 每次操作都新建连接 + 用线程锁，是为了简单。
生产环境绝不会这么写——那会变成吞吐瓶颈。生产是**连接池**。

---

## 三、🟡 懂概念（2 小时，不用会写）

### PostgreSQL vs SQLite
| | SQLite | PostgreSQL |
|---|---|---|
| 形态 | 单个文件 | 独立服务 |
| 并发 | 写操作串行（库级锁） | MVCC，真并发 |
| 权限 | 无 | 用户 / 角色 / 行级权限 |
| 备份 | 复制文件 | 逻辑备份 / 流复制 |
| 适用 | 本地工具、demo、边缘设备 | 生产服务 |

**面试话术**："我 demo 用 SQLite 是为了零依赖能跑起来；生产上这一层会换成 Postgres，因为要并发写、要备份、要按租户做数据隔离。分层就是为了这一天。"

### Redis
一句话：**用内存换速度的键值存储。**
四种典型用途：
1. **缓存**：热点数据（项目配置、模型参数）放内存，DB 只做兜底
2. **计数器**：调用量、QPS、积分
3. **限流**：一个 IP 每分钟最多 N 次
4. **消息中间件**：Celery 的 Broker（最常见的用法）

**面试话术**："Redis 在我们这套架构里主要当两用：一是 Celery 的 Broker，任务往队列里扔，GPU worker 那边取；二是存进度和幂等键——幂等键特别重要，因为生成任务重试很容易重复扣费。"

### Celery 四个角色
| 概念 | 是什么 | 面试用词 |
|---|---|---|
| Broker | 任务队列 | "Redis 当中转站" |
| Worker | 干活的进程 | "跑在 GPU 机器上" |
| Result Backend | 结果存放地 | "结果回传存 Redis/DB" |
| 路由 | 任务分队列 | "GPU 任务单独一个队列，防止拖垮普通接口" |

**为什么不用 FastAPI 的 BackgroundTasks 上生产**：
1. 任务在 Web 进程里，重启就丢
2. Web 机器和 GPU 机器不是同一台，BackgroundTasks 跨不过去
3. 没有失败重试、死信、限速、优先级
4. Web 进程被长任务占住，接口变慢

**面试话术**："我 demo 里用的是 FastAPI 的 BackgroundTasks，因为它零依赖。但我知道生产必须换 Celery：任务要能跨机器、要在重启后恢复、要区分可重试和不可重试的错误、要能限流。我 demo 里任务状态是存在 SQLite 的，生产会存 Postgres，这样进程挂了任务状态还在，可以做恢复。"

### 对象存储（OSS / S3 / MinIO）
- 大文件（视频、图片、音频）**不进数据库**
- 数据库只存 URL 和元数据
- 配 CDN 做分发（你的播放端第一帧速度就靠它）

**AI 影视特别重要**：一部短剧几十个镜头，每个几 MB 到几十 MB，全塞数据库会炸。

### GPU 调度
- 真实瓶颈是**显存**，不是 CPU 核数
- 并发上限 = 显存能装下几个模型实例
- 所以需要：排队、优先级（付费客户优先）、配额、超时释放

**面试话术**："我理解在这类公司里，GPU 就是最贵的资源，所有成本控制最终都落到'单位算力产出多少可用的成片'。这也是为什么我说抽卡率比推理单价更关键。"

---

## 四、🟢 先不管（别浪费时间）

PostgreSQL 调优 / SQL 优化 / 索引原理 / 分库分表 / Redis 集群哨兵 /
Celery 高级特性（链式、周期、saga）/ SQLAlchemy 进阶 / 异步 ORM

**这些是后端同事的活。你投的是前端岗。**

---

## 五、领导问「你了解我们后端吗」的答法

:::writing{variant="chat_message" id="58431"}
"了解个大概，细节还不熟，说说我现在的理解你看对不对。

我理解你们这套是：FastAPI 做 Web 层，负责鉴权、参数校验和编排；任务通过 Redis 排队，Celery 的 worker 在 GPU 机器上真正跑模型；状态和成本记在 PostgreSQL；产出的视频文件走对象存储，数据库只存地址。这几层之间是这么分的原因是——瓶颈在显存不在 CPU，所以要把重活从 Web 进程里踢出去。

我自己为了搞懂这条链路，写了一个小工具，就是这个 demo：FastAPI + SQLite + SSE 推送，前端是 React。生成层我抽象成了一个接口，mock 和真实模型可以随时换。

里面也有几个我清楚的取舍：我用的是 FastAPI 的 BackgroundTasks 而不是 Celery，因为它零依赖、方便我理解整条链路，但我知道上生产必须换——任务会跨机器、会在重启后丢、也需要重试和限流。数据库我用的 SQLite，同理，生产要换 Postgres，因为要并发写。

所以我的定位是：我不是来替后端同学写服务的，但接口契约怎么定、前端怎么把一个会失败、会耗时、会产生多个候选的异步过程表达清楚，这些是我的活。
:::

---

## 六、给 AI Tutor 的提问清单（每天用）

**不要问"帮我写完"，要问"解释 / 出题 / review"。**

FastAPI
- "解释 `main.py` 里 `events()` 这个生成器函数，每一步在做什么？"
- "`BackgroundTasks` 和 `asyncio.create_task` 有什么区别？什么时候必须用前者？"
- "为什么 SSE 在 nginx 后面要加 `X-Accel-Buffering: no`？"
- "FastAPI 里怎么做到请求体校验失败自动返回 422？它在哪一层拦的？"
- "出 5 道题考我 Pydantic 和 TypeScript interface 的区别"

SQL
- "我这段 SQL 有 N+1 查询问题吗？怎么改成一条 JOIN？"
- "为什么 SQLite 需要 `conn.commit()`？不 commit 会怎样？"

Celery / Redis（概念层面，别要代码）
- "Celery 的 prefork 和 gthread 两种 worker 模式分别适合什么场景？"
- "如果 Redis 挂了，正在排队的 Celery 任务会怎样？"
- "为什么很多公司会用 RabbitMQ 而不是 Redis 当 Celery 的 broker？"

Redis
- "缓存穿透、缓存击穿、缓存雪崩分别是什么？怎么防？"
- "用 Redis 做限流有哪几种实现方式？"

数据库
- "PostgreSQL 的 MVCC 是什么意思？为什么它能支持高并发写？"
- "什么情况下 SQLite 的写锁会成为瓶颈？"

代码 review（让它看你的代码）
- "看下我 `tasks.py` 里的状态机，有没有竞态条件？"
- "我这个 SSE 端点在有 nginx 反代的情况下会有什么问题？"
