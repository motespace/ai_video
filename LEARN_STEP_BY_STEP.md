# 从「Python 只会语法」到「能讲清楚整个 demo」

> 面向对象：**有 7 年前端经验，但 Python 只有基础语法**的人。
> 学习目标不是变成 Python 工程师，而是——**能独立跑通、能改动、能在面试里被问到时讲 5 分钟**。
>
> 总时长：约 20 小时，按每天 2-3 小时算，**两周**。
> 每天只需要完成一个"动手任务"，不追求全部看懂。

---

## 📖 怎么用这份文档

- **一次只做一章**，做完动手任务再进下一章
- 每章末尾有 **「动手任务」**（必须做，看不懂也要照做）和 **「自测题」**（答案在文末，先做后看）
- 卡住了：翻到最后一章 **「卡住时的提问模板」**，直接复制去问 Codex / Claude Code
- 每章开头有 **「学完你能回答什么问题」**——这是唯一需要记住的东西
- 全文用 ✅ 标记你已经会的东西，跳过

**进度表**（自己打勾）：

```
□ 第 0 章  建立地图
□ 第 1 章  补齐写这个项目需要的 Python
□ 第 2 章  FastAPI 四个用法
□ 第 3 章  SQL 与 SQLite
□ 第 4 章  asyncio 与任务队列
□ 第 5 章  SSE 实时推送
□ 第 6 章  读懂状态机（tasks.py）
□ 第 7 章  读懂生成抽象层（generator.py）
□ 第 8 章  生产版架构（Redis / Celery / PG）
□ 第 9 章  成本模型与抽卡率
□ 第 10 章 面试怎么讲
```

---

# 第 0 章 · 建立地图

**学完你能回答：这个东西到底在解决什么问题？**

## 0.1 故事版理解

想象一个 AI 短剧公司的一条产线。编剧写完剧本，运营把它拆成 30 个镜头。
每个镜头交给 AI 生成，AI 会返回 3 个候选，运营挑一个。30 个镜头跑完，还要算这集花了多少钱。

这条产线跟前传统影视产线有本质区别：

| | 传统影视 | AI 影视 |
|---|---|---|
| 一个镜头要多久 | 拍一天 | 生成 1-5 分钟（可能失败） |
| 结果唯一吗 | 是（拍完就是那样） | 否（每次都不一样） |
| 会失败吗 | 不会 | **会**，而且是常态 |
| 成本在哪 | 演员、场地、后期 | **GPU 调用次数** |

这张表推出全部四个设计：

1. **会失败** → 系统必须内建"失败"状态，能重试、能观测
2. **结果不唯一** → 必须多候选并存 + 人工挑选
3. **耗时长** → 不能让用户干等，要异步 + 实时推进度
4. **成本在调用次数** → 必须精确记账，不能只算"每分钟"

## 0.2 三个角色，三层代码

```
用户看到的东西     →  frontend/    （你的主场）
调度和状态         →  backend/app/tasks.py + main.py
真正干活的（假的）  →  backend/app/generator.py
```

**动手任务**
1. 启动服务：`cd /Users/lvsj/Desktop/ai-short-drama-pipeline && ./start.sh`
2. 浏览器打开 http://localhost:5173
3. 点「批量生成 6 个镜头」，盯着表格看状态变化 30 秒
4. 找一个「失败」的行，点「重试」
5. 找一个「已完成」的行，点「候选」，在抽屉里切换选中的候选
6. 看完底部的成本面板，找那个"抽卡率"的数字

**自测题**
1. 这个 demo 里，"生成"这一步是真的调了 AI 吗？在哪个文件控制？
2. 失败率大概是多少？在哪里配置？
3. 一次生成会产生几个候选？在哪个文件配置？

<details><summary>答案</summary>

1. 不是，是 mock。`backend/app/generator.py` 里的 `_mock_generate`，用 `asyncio.sleep` 模拟耗时，用随机数模拟失败率。
2. 25%。`backend/app/tasks.py` 里 `if attempt < config.MAX_ATTEMPTS and random.random() < 0.25`。
3. 3 个。`backend/app/config.py` 的 `CANDIDATES_PER_SHOT = 3`。

</details>

---

# 第 1 章 · 补齐写这个项目需要的 Python

**学完你能回答：这个项目用到的 Python 语法有哪些？我还缺什么？**

✅ = 你大概已经会了，可以快速扫一眼。

## 1.1 你已经会的（扫一眼就行）

✅ 变量、字符串、数字、列表、字典的基本用法
✅ `print`、运算符、条件、循环
✅ 函数定义、参数、返回值
✅ `import`

## 1.2 需要补的（这些是真正卡住你的）

### ① f-string —— 最常用，先掌握

```python
name = "小雨"
age = 24
print(f"角色 {name} 今年 {age} 岁")
print(f"成本 {cost:.2f} 元")      # 保留 2 位小数
print(f"{items[0]}")             # 字典/列表取值也可以塞进去
```

**为什么前端对应**：`${name}`、`${cost.toFixed(2)}` —— 一模一样。

### ② 列表推导式 —— 后端到处都是

```python
# 传统写法
urls = []
for c in candidates:
    urls.append(c["url"])

# 推导式
urls = [c["url"] for c in candidates]

# 带条件
failed = [s for s in shots if s["status"] == "failed"]

# 带三元表达式
label = "成功" if s["cost"] > 0 else "待生成"
```

**为什么前端对应**：`candidates.map(c => c.url)`、`shots.filter(...)`。

### ③ 类：只要会"属性 + 方法"就够

```python
class Shot:
    def __init__(self, id, prompt):
        self.id = id
        self.prompt = prompt
        self.status = "pending"

    def mark_running(self):
        self.status = "running"

    def to_dict(self):
        return {"id": self.id, "prompt": self.prompt, "status": self.status}
```

**为什么前端对应**：`class Shot { id; status = 'pending'; markRunning() {} }`
Python 的 `__init__` ≈ TS 的 `constructor`。

**注意**：Python 里**一切都是对象**，函数、列表、字典都是。所以"静态方法"不需要专门记，
你写 `store.list_shots()` 就是 `store`（模块）上的一个函数。

### ④ 模块与导入：`from . import config`

```python
# backend/app/tasks.py 里
from . import config, generator, store

config.MAX_ATTEMPTS      # 读另一个文件里的变量
store.get_shot(shot_id)  # 调另一个文件里的函数
```

**为什么前端对应**：`import config from './config'` → `config.MAX_ATTEMPTS`
Python 的 `from . import x` 里的那个点 = **当前目录**。

### ⑤ `with` —— 自动关闭资源

```python
with sqlite3.connect("db.sqlite") as conn:
    conn.execute("INSERT INTO shots VALUES (?, ?)", (1, "hello"))
    conn.commit()
```

`with` 块结束时会自动关闭/提交。这等价于 JS 的 `try/finally { resource.close() }`，
但 Python 有语法糖，不用你写。

### ⑥ 异常：`try / except / raise`

```python
try:
    result = await generate(prompt)
except Exception as e:
    update_shot(shot_id, status="failed", error=str(e))
    raise            # 重新抛出（如果你想让它继续往上走）
```

**为什么前端对应**：`try { await generate() } catch (e) { ... }`
Python 的 `except Exception as e` ≈ `catch (e)`，`str(e)` ≈ `String(e)`。

### ⑦ 装饰器：`@app.post("/api/shots")`

**这是 FastAPI 的全部魔法来源。**

```python
@app.post("/api/shots")     # 把下面这个函数注册成 POST /api/shots
def create_shots(body: ShotCreate, background: BackgroundTasks):
    ...
```

它做的事：把这个函数**包装**成一个对象，包装后的对象被注册到 FastAPI 的路由表里。
调用它时，FastAPI 会先解析 HTTP 请求 → 校验参数 → 再调你的函数。

**为什么前端对应**：你写过 `app.get('/api/x', handler)`，
这里的 `@app.post` 是同一件事，只是换了个写法。

### ⑧ `async` / `await` —— 唯一真正要理解的新东西

```python
async def run_shot(shot_id):
    await asyncio.sleep(6)      # 等待 6 秒，但这 6 秒里线程让出去了
    shot = store.get_shot(shot_id)
```

**必须记住的一条铁律**：
> 耗时操作必须 `await asyncio.sleep()`，**绝对不能** `time.sleep()`。
> `time.sleep` 会把整个事件循环**卡死**，所有其他请求全部排队等着。

**为什么要让出线程**：
```
单线程事件循环（asyncio）
  ├─ 请求 A 到达 → 处理 → await（让出）→ 去处理请求 B
  ├─ 请求 B 到达 → 处理 → await（让出）→ A 醒来了 → 继续
```
所以你的服务能"同时"处理很多个**等 I/O** 的任务。
（注意：CPU 密集的活 asyncio 救不了，那种要开多进程。）

**为什么前端对应**：JS 的 `async/await` 就是一模一样的东西。
唯一区别是 JS 里没有"事件循环卡死"这个概念（因为 JS 本来就是单线程，
但你也不会在 JS 里写同步阻塞代码）。Python 是个通用语言，
所以你必须自己记住"别阻塞"。

## 1.3 Python 与 JS/TS 速查对照

| Python | JS / TS |
|---|---|
| `f"{x}"` | `` `${x}` `` |
| `[f(x) for x in items]` | `items.map(f)` |
| `{k: v for ...}` | `Object.fromEntries(...)` |
| `None` | `null` / `undefined` |
| `True / False` | `true / false` |
| `def f(x: int) -> str:` | `function f(x: number): string` |
| `class A: def __init__(self)` | `class A { constructor() }` |
| `list` / `dict` / `tuple` / `set` | `Array` / `Record` / `tuple` / `Set` |
| `str(e)` | `String(e)` |
| `a is b` | `a === b`（近似） |
| `**kwargs` | `{...rest}` |
| `import x` / `from x import y` | `import x` / `import { y } from 'x'` |

**动手任务**（都在 `backend/app/` 里）
1. 打开 `config.py`，把 `CANDIDATES_PER_SHOT` 从 3 改成 5，重启后端，看每个镜头出几个候选
2. 把 `MOCK_MIN_SECONDS` 改成 8，观察进度流转变慢
3. 在 `tasks.py` 里找到 `random.random() < 0.25`，改成 `0.6`，看失败率变化
4. 在 `generator.py` 的 `compute_cost` 里加一行 `print(f"本次生成成本 {cost} 元")`，看它打印什么

**自测题**
1. `from . import config` 里的 `.` 是什么意思？
2. `time.sleep(3)` 和 `await asyncio.sleep(3)` 在一个 FastAPI 服务里分别会导致什么？
3. `config.MAX_ATTEMPTS = 3` 和 `config.MAX_ATTEMPTS` 有什么区别？（提示：一个是赋值，一个是什么？）
4. Python 里函数是一等公民吗？（能不能 `f = some_func` 然后 `f()`？）

<details><summary>答案</summary>

1. 当前包目录。`backend/app/tasks.py` 里的 `.` 就是 `backend/app/`，所以它 import 的是同目录的 `config.py`。
2. `time.sleep` 会阻塞整个事件循环，这 3 秒内**所有**并发请求都停摆；`await asyncio.sleep` 只是让当前协程挂起，事件循环继续处理别的请求。
3. 左边是给变量赋值，右边是读取当前值。（`=` 是赋值，`==` 才是比较，这个坑 Python 新手常踩。）
4. 是的。Python 里函数、类都是对象，可以赋值给变量、当参数传、当返回值返回。

</details>

---

# 第 2 章 · FastAPI 四个用法

**学完你能回答：FastAPI 是怎么把一个 Python 函数变成 HTTP 接口的？**

对应代码：`backend/app/main.py`、`backend/app/models.py`

## 2.1 ① 路由装饰器

```python
@app.get("/api/projects")
def list_projects():
    return store.list_projects()

@app.get("/api/shots/{shot_id}")     # 路径参数
def get_shot(shot_id: int):          # 类型标注 → 自动转成 int 并校验
    shot = store.get_shot(shot_id)
    if not shot:
        raise HTTPException(status_code=404, detail="shot not found")
    return shot
```

**关键点**：
- 参数名 `shot_id` 会自动从路径里取
- `shot_id: int` 意味着如果有人传 `/api/shots/abc`，FastAPI 直接返回 422，**不进你的函数**
- `raise HTTPException(404, ...)` 是 FastAPI 的标准错误返回方式

**为什么前端对应**：`app.get('/api/shots/:id', handler)` + 参数校验。

**动手**：加一个 `GET /api/shots/{shot_id}/candidates`（返回该镜头的候选列表）

## 2.2 ② Pydantic —— 契约

```python
class ShotCreate(BaseModel):
    project_id: int
    prompts: list[str] = Field(..., min_length=1, description="每个元素是一个镜头的画面描述")
    character_ref: Optional[str] = None
```

- `project_id: int` —— **必填**，类型 int
- `prompts: list[str] = Field(..., min_length=1)` —— 必填，且数组至少 1 个元素
- `character_ref: Optional[str] = None` —— 可选，默认 None

**它到底做了什么**（面试高频）：
1. 收到请求 → 用这个类**校验**请求体
2. 不合格 → **自动返回 422**，附带每个字段的错误说明
3. 合格 → 把校验过的数据作为**一个对象**传给你的函数（不是一堆散参数）
4. 用 `response_model=ShotOut` 声明响应结构 → 自动**过滤掉没声明的字段**（安全）+ 生成文档

**动手**
1. 故意传错类型：`curl -X POST localhost:8011/api/shots -H 'Content-Type: application/json' -d '{"project_id":"abc","prompts":[]}'`，看返回什么
2. 把 `prompts` 的 `min_length` 改成 2，看什么时候开始报错
3. 在 `ShotOut` 里加一个 `new_field: str = "x"`，看列表接口返回里多了什么

## 2.3 ③ BackgroundTasks —— 长任务不能挡住接口

```python
@app.post("/api/shots", response_model=list[ShotOut])
def create_shots(payload: ShotCreate, background: BackgroundTasks):
    project = store.get_project(payload.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="project not found")

    ids = store.add_shots(payload.project_id, payload.prompts, payload.character_ref)
    background.add_task(tasks.run_shots, ids)      # ← 排队
    return [store.get_shot(i) for i in ids]        # ← 立刻返回
```

**执行顺序**：
```
① 收到请求
② 校验参数
③ 落库（status = pending）
④ 把 run_shots(ids) 挂到 background
⑤ 返回响应（用户已经看到镜头列表了）
⑥ 【响应之后】才开始执行 run_shots
```

**为什么这一步很重要**：
如果没有它，`POST /api/shots` 要等 30 个镜头全部生成完才返回，**几十秒到几分钟**。
用户体验是"页面卡死"。有了它，接口 10 毫秒返回，进度靠 SSE 推。

**⚠️ 必须知道的局限**（这正是面试要讲的）：
- `BackgroundTasks` 是**进程内**的，进程重启 → 任务全丢
- 任务跑在**处理 HTTP 请求的这台机器**上
- 没有重试策略、没有死信、没有优先级、不能限流

**动手**：故意在 `tasks.py` 里加一行 `time.sleep(5)`，然后同时提交 3 批镜头，看它们是不是串行卡住。（这就是第 1 章那条铁律的现实后果）

## 2.4 ④ SSE —— 服务端主动推

```python
@app.get("/api/events")
async def events():
    async def stream():
        while True:
            payload = {"shots": store.list_shots(), "cost": store.cost_summary()}
            yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"   # ← SSE 报文格式
            await asyncio.sleep(1.0)

    return StreamingResponse(
        stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive",
                 "X-Accel-Buffering": "no"},
    )
```

**SSE 报文格式**（就这个约定，没别的）：
```
data: {"a": 1}\n\n
```
`data:` 前缀 + 内容 + **两个换行**。浏览器看到两个换行就知道"这条消息结束了"。

**三个 header 的作用**：
| header | 为什么 |
|---|---|
| `Cache-Control: no-cache` | 别缓存，不然收不到新消息 |
| `X-Accel-Buffering: no` | **关掉 nginx 缓冲**——否则 nginx 会把 SSE 内容攒着不发，你前端看着像"不推送" |
| `Connection: keep-alive` | 别断开 |

**前端**（`frontend/src/App.tsx`）：
```tsx
const es = new EventSource('/api/events')
es.onopen = () => setConnected(true)
es.onerror = () => setConnected(false)
es.onmessage = (e) => {
  const data = JSON.parse(e.data)
  setShots(data.shots)
  setCost(data.cost)
}
```

**⚠️ 组件卸载必须 `es.close()`**，否则连接泄漏，页面切多了会卡。

**为什么不用 WebSocket**：
- 我们只需要**服务端 → 前端**单向推
- SSE 走普通 HTTP，穿透性好、自带断线重连
- WebSocket 要握手、要心跳、要处理双向、还可能被代理挡
- **只有需要双向实时协同编辑（两个人同时改一个剧本）才值得上 WebSocket**

**动手**：把 `await asyncio.sleep(1.0)` 改成 `0.3`，看前端刷新变快；再改成 `0`，看会不会把服务打满。

**自测题**
1. `response_model=ShotOut` 除了生成文档，还做了什么安全上的事？
2. 为什么 `create_shots` 里要先 `store.add_shots` 再 `background.add_task`？反过来会怎样？
3. 如果你的 FastAPI 服务前面有 nginx，SSE 推不动了，你会先查什么？
4. `BackgroundTasks` 和 Celery 的本质区别是什么？

<details><summary>答案</summary>

1. 自动**过滤掉响应里没有在模型中声明的字段**。这样即使你的 store 函数不小心多返回了 `password_hash` 这类字段，也不会泄露给前端。
2. 因为 `add_task` 传的是 `ids`，必须先有 ids 才能排队。反过来的话就没有 id 可传；更重要的是，先落库再排队保证了"任务一定会被创建"——如果先排队后落库，中间崩了就丢任务（这在生产里叫"消息丢失"，要用事务消息/outbox 模式解决）。
3. 查 nginx 有没有开 `proxy_buffering on`（默认是开的！），SSE 必须 `proxy_buffering off;` 或加 `X-Accel-Buffering: no` 响应头。然后查中间有没有别的代理/CDN。
4. `BackgroundTasks` 在**同一个进程内**跑，跟着 Web 进程生死；Celery 把任务**序列化后投递到 broker（Redis/RabbitMQ）**，由**独立的 worker 进程/机器**取走执行。所以 Celery 能跨机器、能扛重启、能做重试和限流。

</details>

---

# 第 3 章 · SQL 与 SQLite

**学完你能回答：数据存在哪？我怎么查/改？生产上为什么不能这么干？**

对应代码：`backend/app/store.py`

## 3.1 三张表

```sql
projects (id, name, created_at)
shots    (id, project_id, idx, prompt, character_ref,
          status, error, attempts, duration_seconds, cost,
          selected_candidate_id, created_at, updated_at)
candidates (id, shot_id, url, seed, is_selected, created_at)
```

关系：`projects 1 ── N shots 1 ── N candidates`

## 3.2 五条 SQL 够了

```sql
-- 增
INSERT INTO shots(project_id, idx, prompt, status, created_at, updated_at)
VALUES (?,?,?,?,?,?)

-- 查
SELECT * FROM shots WHERE project_id=? ORDER BY idx
SELECT * FROM shots WHERE id=?          -- 只查一个

-- 改
UPDATE shots SET status=?, updated_at=? WHERE id=?

-- 删
DELETE FROM shots WHERE id=?

-- 建表
CREATE TABLE IF NOT EXISTS shots (...);
```

**`?` 是参数占位符**（不是字符串拼接！）：
```python
_query("SELECT * FROM shots WHERE project_id=?", (project_id,))
```
参数用元组传，**永远不要**用 f-string 拼 SQL（SQL 注入）。

## 3.3 Python 的标准库 sqlite3

```python
import sqlite3

conn = sqlite3.connect(config.DB_PATH)     # 连上
conn.row_factory = sqlite3.Row              # 让结果能 ["列名"] 取
cur = conn.execute("SELECT * FROM shots WHERE id=?", (sid,))
row = cur.fetchone()                        # 取一行 / fetchall() 取全部
conn.commit()                               # 写操作必须提交
conn.close()                                # 关掉
```

**三个必须记住的点**：
1. `conn.execute(...)` 返回的是 cursor，要 `.fetchone()` / `.fetchall()` 才拿到数据
2. **写操作要 `commit()`**，否则不落盘
3. **这个 demo 每次操作都新建连接**，还用了 `threading.Lock`——这是为了让 demo 简单，
   真实生产绝不会这么写（那会成为吞吐瓶颈）。**这一点面试要主动说**，显得你知道差距在哪。

## 3.4 为什么生产用 PostgreSQL 而不是 SQLite

| | SQLite | PostgreSQL |
|---|---|---|
| 形态 | 一个文件 | 独立服务（可以远程连） |
| 并发写 | 库级写锁，基本串行 | MVCC，真并发 |
| 权限 | 无 | 用户 / 角色 / 行级权限 |
| 备份 | 复制文件 | 逻辑备份 / 流复制 |
| 类型 | 弱 | 丰富（JSONB、数组、地理类型） |
| 适合 | 本地工具、demo、边缘设备 | 生产服务 |

**这个 demo 的分层就是为了这一天**：`store.py` 是唯一碰数据库的地方，
将来换成 PG，只需要改这一个文件，`tasks.py` 和 `main.py` 一行不动。

**动手任务**
1. 用 `sqlite3` 命令行或 Python 打开 `backend/data/pipeline.db`，查一下 shots 表
2. 在 `store.py` 里加一个 `delete_shot(sid)`，并在 `main.py` 加一个 `DELETE /api/shots/{id}`
3. 把 `store.py` 里的 `_lock` 注释掉，同时开两个浏览器标签提交镜头，看会不会报错（并发写问题）

**自测题**
1. `conn.execute(...)` 之后为什么还要 `.fetchone()`？
2. 这个 demo 每次操作都 `sqlite3.connect()` 一次，生产这么干会有什么问题？
3. 如果要做"每个租户只能看到自己的镜头"，PostgreSQL 有什么 SQLite 不方便做的东西？
4. `ORDER BY idx` 里的 `idx` 是什么？为什么不直接用 `id`？

<details><summary>答案</summary>

1. `execute` 只把语句发给数据库并返回一个游标（cursor），游标上才有结果集，要从中取行。
2. 每次新建连接 = 每次 TCP 握手 + 认证 + 分配内存，是巨大开销；生产要用**连接池**（如 psycopg 的 pool、SQLAlchemy 的 engine）。而且大量短连接会让数据库的连接数限制被打满。
3. PostgreSQL 有**行级安全策略（RLS）**，可以直接在数据库层做租户隔离，配合 `SET LOCAL app.tenant_id` 就能让所有查询自动带上租户过滤；SQLite 没有这个能力，只能在应用层到处手写 `WHERE tenant_id = ?`，很容易漏。
4. `idx` 是镜头在**这一集里**的序号（0,1,2...），而 `id` 是全局自增主键。当一个项目有多个分镜批次时，`id` 的顺序不等于集内顺序，所以要单独一个 `idx`。

</details>

---

# 第 4 章 · asyncio 与任务队列思想

**学完你能回答：为什么一个任务失败不影响其他任务？并发上限是怎么控制的？**

对应代码：`backend/app/tasks.py`

## 4.1 状态机（本项目的核心）

```
pending ──► running ──► succeeded
   ▲            │
   │            ▼
   └── retry ── failed
```

**每个镜头完全独立**：
- 自己的 status
- 自己的 attempts（尝试次数）
- 自己的 cost（成本）
- 自己的 candidates（候选）

所以镜头 2 失败了，镜头 3、4 照常跑，镜头 2 单独重试。

**为什么这个设计重要**：
传统内容生产是串行的（一个环节卡住全卡住）。
AI 生成天然是**大量独立小任务**，所以状态必须是**每镜头粒度**而不是每批次粒度。

## 4.2 任务函数

```python
async def run_shot(shot_id: int) -> None:
    shot = store.get_shot(shot_id)
    attempt = shot["attempts"] + 1
    store.update_shot(shot_id, status="running", attempts=attempt, error=None)

    try:
        result = await generator.generate(shot["prompt"], shot_id, attempt)

        if attempt < config.MAX_ATTEMPTS and random.random() < 0.25:
            raise RuntimeError("生成超时：模型推理队列拥堵（模拟）")

        cand_ids = store.add_candidates(shot_id, result["candidates"])
        cost = generator.compute_cost(result["duration_seconds"], len(cand_ids))
        store.update_shot(shot_id, status="succeeded", duration_seconds=..., cost=cost, ...)
    except Exception as e:
        store.update_shot(shot_id, status="failed", error=str(e))
```

**注意几件事**：
1. 进函数第一件事是**把状态置为 running 并累加 attempts**——这样 UI 上立刻能看到"生成中"，而且重试次数可观测
2. **失败信息写进 `error` 字段**，前端能显示"生成超时：模型推理队列拥堵"。**失败必须可观测**，这是排查问题的前提
3. 失败不抛出到外层，只是记录——因为这是后台任务，抛出去也没人接

## 4.3 并发闸门

```python
async def run_shots(shot_ids: list[int], concurrency: int = 3) -> None:
    sem = asyncio.Semaphore(concurrency)

    async def guarded(sid: int) -> None:
        async with sem:
            await run_shot(sid)

    await asyncio.gather(*(guarded(s) for s in shot_ids))
```

- `Semaphore(3)` = 最多 3 个同时跑
- `async with sem` = 拿号 → 干活 → 还号
- `asyncio.gather(...)` = 等所有都完成（并发，不是串行）

**为什么这个 demo 要限并发**：
真实场景并发上限是**显存**（一个 GPU 只能同时装下 N 个模型实例）。
这个 demo 是 mock，所以用 3 演示"限流"这个概念。

## 4.4 从 asyncio 到 Celery（生产版）

```
asyncio（demo）                    Celery（生产）
────────────────                   ──────────────────
在同一个进程里跑                     worker 在独立进程/机器
进程挂了任务没了                     任务在 broker（Redis）里，重启后还在
没有重试策略                         支持重试 / 死信队列
没有优先级                             支持优先级、限流、路由
并发受限于代码                          并发受限于显存
接口返回就结束了                       任务状态可查（result backend）
```

**动手任务**
1. 把 `concurrency=3` 改成 `1`，提交 6 个镜头，看总时长变长
2. 在 `run_shot` 的 `except` 里加一行 `print(f"镜头 {shot_id} 失败: {e}")`，看日志
3. 思考题：如果 `run_shot` 里 `store.update_shot` 成功了但 `store.add_candidates` 失败了，状态会是什么？（提示：会卡在 running，变成"僵尸任务"）

**自测题**
1. `asyncio.gather` 和 `await` 逐个执行有什么区别？
2. `Semaphore(3)` 限制的是什么资源？在真实系统里这个"3"由什么决定？
3. 如果生成任务在 `running` 状态时服务进程挂了，会发生什么？生产怎么解决？

<details><summary>答案</summary>

1. `gather` 让所有协程**并发**开始（都跑到第一个 await 才让出），总耗时约等于最慢的那个；逐个 await 是**串行**，总耗时是所有之和。
2. 限制的是**同时进行的任务数**。在真实 GPU 系统里，这个数字由**显存能装下几个模型实例**决定，不由 CPU 核数决定。所以它是一个成本/吞吐的调节旋钮。
3. 会变成"僵尸任务"——永远停在 running，因为没人再更新它了。生产上的解法：① 任务状态存数据库（不存内存），重启后扫描 `status='running' AND updated_at < 10分钟前` 的任务重新投递；② Celery 配 `acks_late` + worker 优雅退出；③ 加心跳/超时看门狗。

</details>

---

# 第 5 章 · SSE 实时推送（前端视角）

**学完你能回答：SSE 和 WebSocket 怎么选？前端要注意什么？**

对应代码：`backend/app/main.py` 的 `events()`、`frontend/src/App.tsx` 的 `useEffect`

## 5.1 前端这一侧

```tsx
useEffect(() => {
  const es = new EventSource('/api/events')
  esRef.current = es
  es.onopen  = () => setConnected(true)
  es.onerror = () => setConnected(false)
  es.onmessage = (e) => {
    const data = JSON.parse(e.data)
    setShots(data.shots)
    setCost(data.cost)
  }
  return () => es.close()      // ← 卸载必须关闭，否则连接泄漏
}, [])
```

**前端要记住的 4 件事**：
1. `EventSource` 的 `onmessage` 里 `e.data` 是**字符串**，要 `JSON.parse`
2. **组件卸载必须 `es.close()`**。不关的话，切页面/切项目会不断累积连接
3. SSE **自带断线重连**，但 `onerror` 时状态会短暂变红，重连成功后 `onopen` 又会触发
4. **不要用 SSE 做高频双向交互**（比如打字协同），那个才需要 WebSocket

## 5.2 为什么不是轮询？

| | 轮询 | SSE |
|---|---|---|
| 请求数 | 每 N 秒一次，不管有没有变化 | 1 条长连接 |
| 延迟 | 最多 N 秒 | 立即 |
| 服务端压力 | 高（反复查库） | 低（变化才推） |
| 浏览器限制 | 无 | **每个域名最多 6 条 HTTP/1.1 连接** |

**什么时候该轮询**：
- 更新间隔不敏感（比如每分钟一次统计）
- 需要兼容不支持 SSE 的环境
- 想实现简单，不想维护长连接

**什么时候该 SSE**：状态变化频繁、要"快"、数据是单向的。
**AI 生成任务正好是 SSE 的典型场景**：服务端有持续变化的状态要推。

## 5.3 SSE 的三个坑

1. **nginx 缓冲** → 必须 `proxy_buffering off;`（默认开！）
2. **HTTP/1.1 的 6 连接限制** → 一个页面开太多 SSE 会把浏览器连接占满
3. **超时** → 很多网关/LB 默认 60 秒断开，要配 keepalive 或定期发心跳

**动手任务**
1. 在 `App.tsx` 里加一个"手动刷新"按钮，调 `GET /api/shots`，体会轮询和 SSE 的区别
2. 故意在 `useEffect` 里**不写** `return () => es.close()`，然后来回切项目 5 次，用 DevTools 的 Network 面板看 EventSource 连接数
3. 试着用 `curl -N http://localhost:8011/api/events` 直接看原始报文

**自测题**
1. `EventSource` 的 `onmessage` 收到的 `e.data` 是什么类型？
2. 为什么组件卸载时必须关掉 EventSource？
3. 你要做一个"多人同时编辑同一个剧本"的协同功能，该用 SSE 还是 WebSocket？

<details><summary>答案</summary>

1. 字符串。因为 SSE 传的是文本，前端要自己 `JSON.parse`。
2. 不关的话每次挂载都会新建一条连接，旧连接还挂着不放。轻则浪费服务端资源，重则浏览器对同一域名的连接数（HTTP/1.1 下 6 条）被占满，新连接发不出去，页面就"不推送"了。
3. WebSocket。因为 SSE 是单向的（只能服务端推），而协同编辑需要双向：我要把我的编辑发回去，同时接收别人的编辑。

</details>

---

# 第 6 章 · 读懂状态机（tasks.py）

**学完你能回答：一次生成的完整生命周期是怎样的？失败是怎么被处理和观测的？**

## 6.1 完整生命周期

```
① 用户点「批量生成 6 个镜头」
        ↓
② POST /api/shots → add_shots() 落库，6 条 status='pending', attempts=0
        ↓
③ background.add_task(run_shots, ids) → 立刻返回 6 条 pending 给前端
        ↓
④ run_shots 起 3 个并发（Semaphore），每个调 run_shot
        ↓
⑤ run_shot: status='running', attempts=1
        ↓
⑥ await generator.generate(...)   ← 耗时 3-8 秒（mock）
        ↓
   ┌────┴─────┐
   │ 成功       │ 失败（25% 概率）
   ↓            ↓
⑦ status='succeeded'   ⑧ status='failed', error='生成超时...'
   + 3 个候选     + cost 累加
   + cost 累加
        ↓            ↓
   前端 SSE 收到，表格实时刷新
        ↓
⑨ 用户点「重试」→ status='pending' → 再走一遍（attempts=2）
```

## 6.2 三个值得讲的工程细节

**① 状态写入时机**
进 `run_shot` 的第一件事就是置 `running` + 累加 `attempts`。
**为什么**：如果这一步放在生成之后，一旦进程崩溃，任务永远停在 `pending`，
你根本不知道它到底跑没跑过。先标记再执行，是"乐观记录"，
出问题时的 `running` 状态本身就是排查线索。

**② 失败必须留痕**
```python
store.update_shot(shot_id, status="failed", error=str(e))
```
`error` 字段写的是**人能看懂的业务原因**（"生成超时：模型推理队列拥堵"），
不是堆栈。生产上还需要：错误码、结构化日志、告警。

**③ 成本只在成功时记**
失败不记 cost（因为没成功消耗），但**重试的 attempts 会累加**。
所以成本放大系数 = 总生成次数 ÷ 成功镜头数。

## 6.3 这个状态机在真实产线里对应什么

| demo | 真实产线 |
|---|---|
| 镜头 pending | 待生成 |
| 镜头 running | GPU 队列里 |
| 镜头 succeeded + 候选 | 出片了，等人挑 |
| 镜头 failed | 生成失败，等重试或人工介入 |
| attempts | 这个镜头被"抽"了几次 |
| cost | 累计花了多少钱 |

**这就是为什么 AI 影视的前端工作量比传统影视大**：
传统影视里"生成"是剪辑师点一下就完事；
AI 影视里前端要处理一个**会失败、会耗时、会产生多个候选、需要人工确认**的过程。

**动手任务**
1. 在 `tasks.py` 的 `except` 分支里加一个 `print`，看失败时的日志
2. 给 `shots` 表加一个 `tags` 字段（需要改 `store.py` 的 SCHEMA 和 `add_shots`），提交时带上标签
3. **进阶**：实现"批量重试所有失败的镜头"按钮

**自测题**
1. 为什么 `attempts` 要在生成**之前**累加，而不是成功后？
2. 如果一个镜头永远卡在 running（进程崩了），用户会看到什么？你怎么修？
3. 真实生产里，"重试"应该由谁触发？用户点按钮，还是系统自动？各有什么问题？

<details><summary>答案</summary>

1. 因为"尝试过"这个事实必须先落盘，否则崩溃后你不知道它跑没跑过，attempts 永远停在 0，重试计数就失去了意义。
2. 用户看到"生成中"永远转圈。修法：① 状态存数据库（已做）；② 加一个看门狗定时任务，把 `status='running'` 且 `updated_at` 超过 N 分钟的任务判为超时，改成 failed 并允许重试。
3. 两种都要。**系统自动重试**用于瞬时错误（网络抖动、队列拥堵），有次数上限，且必须**幂等**（否则重复扣费）；**用户手动重试**用于参数错、需求变了这类需要人介入的情况。自动重试的关键是区分「可重试错误」和「不可重试错误」——比如参数非法重试一万次也没用。

</details>

---

# 第 7 章 · 读懂生成抽象层（generator.py）

**学完你能回答：为什么要把"生成"抽象成一个接口？这在真实公司里对应什么？**

## 7.1 抽象的形状

```python
async def generate(prompt: str, shot_id: int, attempt: int) -> dict:
    """统一入口。返回 {"candidates": [...], "duration_seconds": float}"""
    return await _mock_generate(prompt, shot_id, attempt)
```

**所有调用方（`tasks.py`）只认这个返回结构**，不关心底下是 mock 还是可灵还是自研模型。

## 7.2 换成真实模型要改什么

只改这一个文件，而且只改 `generate()` 里的分支：

```python
async def _kling_generate(prompt, shot_id, attempt):
    r = await httpx.AsyncClient().post(
        "https://api.klingai.com/v1/videos/image2video",
        headers={"Authorization": f"Bearer {API_KEY}"},
        json={"prompt": prompt, "model_name": "kling-v2"},
    )
    task_id = r.json()["data"]["task_id"]

    while True:                              # 真实生成是异步的，要轮询
        s = await httpx.AsyncClient().get(f".../image2video/{task_id}")
        status = s.json()["data"]["task_status"]
        if status == "succeed":
            url = s.json()["data"]["task_result"]["videos"][0]["url"]
            break
        await asyncio.sleep(5)

    return {"candidates": [{"url": url, "seed": 0}], "duration_seconds": 5.0}
```

**`tasks.py`、`main.py`、整个前端，一行都不用改。**

## 7.3 为什么这个设计在真实公司极其重要

AI 影视公司这几年换过一堆模型供应商：可灵、即梦、Vidu、Runway、自研……
但**产线的编排层是稳定的**：剧本 → 分镜 → 角色资产 → 生成 → 挑选 → 成片。

所以工程上一定是：
- **模型层可替换**（可能还同时接多家，做 A/B 或兜底）
- **编排层稳定**（业务逻辑在这层）

**这个设计正好也是你面试时能讲的"我理解这个行业的工程形态"的证据。**

## 7.4 成本函数

```python
def compute_cost(duration_seconds: float, candidates: int) -> float:
    return round(
        config.PRICE_PER_GENERATION * candidates
        + config.PRICE_PER_SECOND * duration_seconds * candidates,
        4,
    )
```

**注意**：成本乘了 `candidates`（候选数）。
因为一次"生成"其实是 N 个候选各生成一次，**每一次调用都花钱，但只有一个被采用**。

## 7.5 这里藏着你最值钱的一个判断（重要）

> **决定单分钟成片成本的，不是推理单价，是"抽卡率"。**

推导：
- 假设单次生成成本固定为 C，每个镜头要采 1 个、生成 K 个候选 → 成本 ≈ K × C
- K 就是抽卡率（也叫重试放大系数）
- 如果推理单价降一半（供应商降价 / 蒸馏加速），但为了质量多抽一倍 → **总成本不变甚至更高**
- 所以优化重点应该是**提高采纳率**（第一次就抽中），而不是一味压单价

**在真实产线里，"提高采纳率"的手段是**：
- 角色资产固定（seed / 参数模板固化）→ 同一个角色不用反复试
- 人工修改沉淀回模板 → 下次直接用对的参数
- 失败原因分类统计 → 知道是 prompt 问题还是模型问题

**这三件事都是前端 + 工具能做的**，这正好是你的落点。

**动手任务**
1. 在 `generator.py` 里加一个 `_replicate_generate`（可以先 mock，只是结构不同）
2. 改 `compute_cost`，让候选数不影响成本，观察成本面板变化，想想为什么现实里必须乘
3. 把 `CANDIDATES_PER_SHOT` 改成 10，看成本面板的放大倍数

**自测题**
1. 为什么 mock 层和真实层要分成两个函数，而不是写在一个函数里用 `if`？
2. 真实生成 API 是"提交任务 → 轮询 → 拿结果"三步，为什么不能写成一步？
3. 你说"抽卡率比单价更重要"，请给一个具体场景说明单价降了但总成本反而涨了。
4. 怎么提高采纳率？给三个前端/工具侧能做的具体手段。

<details><summary>答案</summary>

1. 分成两个函数后，`generate()` 是一个稳定的"门面"，切换实现只需要换一行调用；写在一个函数里用 `if` 分支，会让函数越来越长、测试要 mock 一堆东西。**这是依赖倒置**——高层（tasks）依赖抽象（generate），不依赖具体实现（_mock/_kling）。
2. 因为视频生成动辄几十秒到几分钟，同步 HTTP 连接撑不住。真实做法是提交后立刻拿 task_id 返回，客户端（这里是我们的 worker）再轮询或等 webhook 回调。
3. 例：原来一个镜头只生成 1 个候选（¥1.2），采纳率 100%；现在用了更便宜更快的模型，单价降到 ¥0.6，但因为模型质量不稳，每个镜头要抽 3 个才有一个可用 → 3 × ¥0.6 = ¥1.8，**比原来贵 50%**。
4. ① 角色资产固化（seed/参数模板/参考图集跨集复用）；② 人工修改回写模板（把选中的那次的参数存成该角色的标准资产）；③ 失败原因分类（prompt 问题 / 模型问题 / 素材问题），分别优化；④ 候选预生成策略（先用小尺寸低成本试构图，选中后再放大出片）。

</details>

---

# 第 8 章 · 生产版架构（Redis / Celery / PostgreSQL）

**学完你能回答：我的 demo 和真实生产差在哪？需要换什么？为什么？**

> ⚠️ 这一章**不需要会写代码**，只需要能画图、能说清每层职责和"为什么这么分"。

## 8.1 生产架构图

```
                        ┌──────────────────────────────┐
   浏览器  ───────────►  │  前端 (React/Vue)            │
                        │  创作工作台 / 播放端          │
                        └───────────┬──────────────────┘
                                    │ REST + SSE
                        ┌───────────▼──────────────────┐
                        │  FastAPI (Web 层)             │
                        │  鉴权 / 校验 / 编排 / 计费     │
                        └──┬────────────────────────┬──┘
                           │ 写状态                 │ 投递任务
              ┌────────────▼──────┐      ┌─────────▼────────────┐
              │  PostgreSQL       │      │  Redis                │
              │  项目/镜头/候选   │      │  ① Broker（任务队列）  │
              │  用户/成本账单    │      │  ② 缓存 / 计数器      │
              │  （demo 用 SQLite）│      │  ③ 进度 / 幂等键      │
              └────────────▲──────┘      └─────────┬────────────┘
                           │                       │
                           │              ┌────────▼─────────────┐
                           │              │  Celery Worker 池    │
                           │              │  （跑在 GPU 机器上）  │
                           │              │  调模型 / 渲染 / 转码 │
                           │              └────────┬─────────────┘
                           │                       │
              ┌────────────▼───────────────────────▼────────┐
              │  对象存储 (OSS/S3/MinIO) + CDN               │
              │  视频 / 图片 / 音频 / 字幕文件                │
              └──────────────────────────────────────────────┘
```

**记忆口诀**：
- 数据库存**状态**，对象存储存**文件**
- Redis 既**排队**又**加速**
- Celery 让"提交"和"执行"**分居两台机器**
- **GPU 机器只干重活，Web 层绝不碰推理**

## 8.2 Redis —— 三个用法

| 用法 | 例子 | 为什么需要 |
|---|---|---|
| **Broker（任务队列）** | Celery 把待生成任务扔进 Redis 队列 | 解耦提交与执行；GPU worker 跨机器取任务 |
| **缓存** | 模型参数、项目配置放内存 | 读数据库慢，这类数据读多写少 |
| **幂等键 / 限流** | `idem:{client_token}` 标记已提交过 | **生成任务重试极易重复扣费**，必须幂等 |

**一句话**：Redis 是用内存换速度的键值存储。

## 8.3 Celery —— 四个角色

| 概念 | 是什么 | 类比 |
|---|---|---|
| **Broker** | 任务队列（Redis/RabbitMQ） | 排队取号的地方 |
| **Worker** | 真正干活的进程 | 柜台后面的员工 |
| **Result Backend** | 结果存哪（Redis/DB） | 办事结果贴在窗口 |
| **路由** | 不同任务给不同队列 | 普通单和加急单分开叫号 |

**为什么 demo 不能用 BackgroundTasks 上生产**（4 条）：
1. 任务在 Web 进程里，**进程重启就丢**
2. Web 机器和 GPU 机器**不是同一台**，BackgroundTasks 跨不过去
3. **没有**重试策略、死信队列、限速、优先级
4. 长任务占住 Web 进程，**接口整体变慢**

## 8.4 PostgreSQL vs SQLite

| | SQLite | PostgreSQL |
|---|---|---|
| 形态 | 一个文件 | 独立服务 |
| 并发写 | 库级写锁，基本串行 | MVCC，真并发 |
| 权限 | 无 | 用户/角色/**行级安全(RLS)** |
| 备份 | 复制文件 | 逻辑备份/流复制 |
| 适合 | 本地工具、demo | 生产服务 |

**为什么这个分层有意义**：`store.py` 是唯一碰数据库的地方，换 PG 只改这一个文件。

## 8.5 对象存储（OSS / S3 / MinIO）

- 大文件（视频、图片、音频）**不进数据库**
- 数据库只存 **URL + 元数据**
- 配 **CDN** 做分发 → 播放端首帧速度就靠它

**AI 影视特别重要**：一部短剧几十个镜头，每个几 MB 到几十 MB。

## 8.6 GPU 调度

- 真正的瓶颈是**显存**，不是 CPU 核数
- 并发上限 = 显存能装下几个模型实例
- 所以需要：排队、优先级（付费客户优先）、配额、超时释放

## 8.7 demo → 生产的完整对照（**这段是面试重点，背下来**）

| demo 现状 | 生产要换什么 | 为什么 |
|---|---|---|
| SQLite | PostgreSQL | 并发写、备份、租户隔离 |
| BackgroundTasks | Celery + Redis | 跨机器、重启不丢、重试限流 |
| `time.sleep` 式等待 | 真实模型 API + 轮询/webhook | 生成是异步的 |
| mock 生成 SVG | 真实模型服务 | —— |
| 单机存储 | 对象存储 + CDN | 视频文件大、要分发 |
| 无鉴权 | 登录态 + 按租户/用户限流 | 成本失控的第一道闸 |
| 无幂等 | client_token 唯一索引 | 重试重复扣费 |
| 成本记在 shot 表 | 独立的成本账单表 | 要按用户/项目/模型维度归因 |
| 前端 `types.ts` 手写 | OpenAPI 自动生成 TS 类型 | 前后端契约不漂移 |
| 无监控 | 任务成功率/队列长度/成本告警 | 线上问题要能第一时间发现 |

## 8.8 动手任务
1. 把上面这张表抄进你自己的笔记，每一行**用一句话说明"为什么"**
2. 用 AI 问你最不懂的一行（比如"为什么幂等键要放 Redis 不放 PG"）
3. 读一遍 `store.py` 的 `_lock` 那段，想清楚它在 demo 里防的是什么、生产里为什么不需要（或者还是需要？）

**自测题**
1. 为什么 Celery 的 broker 常用 Redis 而不是数据库？
2. 幂等键放 Redis 还是放 PostgreSQL？各有什么问题？
3. 如果模型供应商从可灵换成自研模型，需要改哪几个文件？
4. 一个任务在 Postgres 里状态是 running，但 GPU worker 已经崩了，怎么发现和处理？

<details><summary>答案</summary>

1. 因为 broker 的负载是**高频读写**（每秒几百上千次入队出队），Redis 内存读写极快；而数据库的写要落盘、要事务，吞吐和延迟都不划算，而且会给业务库带来压力。代价是 Redis 挂了队列就丢，所以生产上要做持久化（RDB/AOF）。
2. 放 Redis：快，TTL 自动过期，天然适合短期幂等窗口；问题是**数据可能丢**（Redis 挂了/主从切换/过期了），所以要配合数据库的唯一索引兜底。放 PG：靠唯一索引最可靠，但每次都要查一次数据库，高并发下是瓶颈。**实践中通常两者都做**：Redis 挡大部分，PG 唯一索引保证最终正确。
3. 只改 `generator.py`（换实现）——这正是第 7 章那个抽象的价值。如果模型需要长任务 + 进度回调，还要在 `main.py` 加一个 webhook 端点，但 `tasks.py` 的状态机逻辑不用动。
4. 靠**心跳/超时看门狗**：worker 定期更新任务的 `updated_at`，一个定时任务扫描 `status='running' AND updated_at < N分钟前` 的任务，判定为僵死，改成 failed 并允许重试。同时 worker 用 Celery 的 `acks_late` + `reject_on_worker_lost` 保证任务重新入队。

</details>

---

# 第 9 章 · 成本模型与抽卡率（你的差异化观点）

**学完你能回答：你对 AI 影视的成本结构有什么判断？这是你最值钱的一个观点。**

## 9.1 一个短剧的钱花在哪

```
单集成本 ≈ 剧本/分镜(人力)
         + 生成调用次数 × 单次成本        ← AI 时代的增量
         + 人工挑选/返修工时
         + 投流成本                       ← 通常是大头
         + (失败的算力也要付钱)
```

**注意最后一条**：失败的调用**照样扣费**。所以失败率直接吃毛利。

## 9.2 抽卡率（重试放大系数）

```
抽卡率 K = 总生成调用次数 ÷ 成功镜头数
单镜头成本 = K × 单次生成成本
```

**K 的来源**：
- 质量不稳定，需要多抽几个
- 角色一致性失败，重抽
- 素材/参数错误，重抽
- 失败重试（25% 的失败率 → 平均 attempts 会明显大于 1）

## 9.3 关键推论

> **单价下降 ≠ 成本下降。**

单价降 50%，但为了保质量 K 从 1 涨到 1.5 → 成本 = 0.5C × 1.5 = 0.75C，降了 25%，没降一半。
如果 K 涨到 2 → 0.5C × 2 = 1C，**一点没降**。

所以成本优化的正确顺序是：
1. **先提高采纳率**（K 降下来）—— 这主要是工具和资产设计的事
2. **再压单价**（蒸馏、量化、缓存、更便宜的模型）
3. **最后做规模效应**（批量、并发、缓存命中）

## 9.4 提高采纳率的手段（前端/工具侧能做的）

| 手段 | 原理 | 属于谁 |
|---|---|---|
| **角色资产固化** | 同一个角色的 seed/参数模板/参考图集固定，跨集复用，不用反复试 | 后端+工具 |
| **人工修改回写模板** | 人工挑中的那次的参数，存成该角色的"标准资产"，下次直接用对 | **前端 + 工具** |
| **失败原因分类** | 区分 prompt 问题 / 模型问题 / 素材问题，分别优化 | 后端 + 数据 |
| **分层出片** | 先用低分辨率低成本出构图，选中后再放大出片 | 工具 + 后端 |
| **参数面板 + 批量重试** | 让人能微调一个参数就批量重试，而不是全靠抽 | **前端** |

**这五条里有一半是前端和工具的活** —— 这就是你的落点。

## 9.5 一致性问题（第二个值钱判断）

> **观众在第 10 集发现主角换了脸就弃剧。所以"角色一致性"是当前最大的工程瓶颈，而不是单镜头画质。**

推论：
- **角色资产（LoRA / 参考图集 / 固定参数）是公司真正的资产**
- **生成引擎随时可以换供应商，角色资产换不了**
- 所以资产库的投入产出比 > 模型调优的投入产出比

**动手任务**
1. 在 `store.py` 里加一张 `characters` 表：一个角色 → 固定的 seed / 参考图 URL / 参数模板
2. 提交镜头时选角色，自动带上该角色的固定参数
3. 加一个"一致性检查"：同角色的镜头 seed 不一致就告警

**这一步做完，你在面试里讲"一致性"就有实物支撑了，是第 10 章里最强的一张牌。**

**自测题**
1. 抽卡率 K 是什么？怎么在系统里算出来？
2. 为什么"角色资产"比"模型效果"更值得投资？
3. 如果供应商宣布模型降价 60%，你的成本模型会怎么变？为什么？
4. 举一个你的 demo 里能体现"抽卡率"的地方。

<details><summary>答案</summary>

1. K = 总生成调用次数 ÷ 成功镜头数。demo 里就是 `cost_summary()` 里的 `attempts_total / succeeded`，前端成本面板最后那行已经在算了。
2. 因为角色资产是**跨集、跨镜头、跨项目复用**的沉没资产，做一次能用几百次；而模型效果是持续投入且随时被下一代模型抹平的。而且换供应商时，模型可以换，资产带不走。
3. 单镜头成本 = K × C，C 降 60% 后成本变成 0.4C × K。如果 K 不变，成本降 60%；但**实际中降价往往伴随质量波动，K 会上升**，真实降幅会小于 60%。这就是为什么不能只看单价。
4. `run_shot` 里每次重试都会 `attempts + 1` 并再生成 3 个候选，所以失败镜头实际上消耗了多次调用的钱。而成本面板的"抽卡率"那行就是在算 `attempts_total / succeeded`。

</details>

---

# 第 10 章 · 面试怎么讲

**学完你能回答：这个项目怎么讲？老板会追问什么？我怎么不露怯？**

## 10.1 原则：讲"认知"，不讲"代码"

领导面（技术已过的情况下）不关心你的 `asyncio.gather` 写得好不好。
他关心的是：**你看没看懂这个行业的生产逻辑。**

所以你的讲法应该是：
- **60% 讲认知**（成本结构、一致性瓶颈、抽卡率、人在环）
- **30% 讲设计**（为什么抽象生成层、为什么每镜头独立状态、为什么 SSE）
- **10% 讲代码**（够证明你真做过就行）

## 10.2 三分钟版本（背下来）

:::writing{variant="standard" id="45602"}
"我为了理解 AI 影视的生产链路，自己做了一个小工具，叫 AI 短剧素材流水线。

它解决的是 AI 介入之后新出现的三个问题。第一，几十个镜头要并行跑，而且要实时看到进度——我用的是每镜头独立的任务状态机加 SSE 推送，前端能实时看到排队、生成、成功、失败，失败可以单独重试。第二，生成结果不是唯一答案——每次生成会产出多个候选，需要人工挑选，所以候选并存加人工确认是必须的。第三，钱花在哪了——我把成本精确到每一次生成调用，所以能算出抽卡率，也就是重试带来的成本放大系数。

技术上，后端是 FastAPI 加 SQLite，前端是 React 加 Vite。生成层我特意抽象成一个接口，mock 和真实模型可以随时换，接真实可灵或即梦只需要改一个文件，业务代码一行不动。

这个项目最有价值的部分其实不是代码，是我第一次真正理解了 AI 内容生产的三个结构性特征：单点操作会失败、结果不是唯一答案、真正的成本杠杆是采纳率而不是推理单价。这些是我在传统影视生产里学不到的东西。"
:::

## 10.3 老板会追问的 6 个问题 + 应答方向

### Q1「这跟真实生产差在哪？」

**不要答"差很多"。要答"我知道每一处的差距和原因"。**

方向：见第 8.7 节那张对照表，挑 4-5 条讲。
最强的一条：**"我 demo 用的是 FastAPI 的 BackgroundTasks，因为零依赖。但我知道生产必须换 Celery——任务要能跨机器、重启不能丢、要能区分可重试和不可重试的错误、要能限流。"**

### Q2「为什么不用现成的 ComfyUI？」

> "ComfyUI 是单节点的工作流编排，缺的是'项目 / 分镜 / 候选 / 成本'这一层业务编排。
> 而这一层恰恰是真实产线里最复杂的部分——几十个镜头要排队、失败的要重试、每个镜头的成本要能归因。
> ComfyUI 解决的是'怎么调一个模型'，我做的解决的是'怎么管一条产线'。"

### Q3「你觉得 AI 短剧现在最大的瓶颈是什么？」

**这题是加分题。给一个有观点、不绝对的回答。**

> "我觉得现在最大的瓶颈不是模型画质，是**一致性**。观众在第 10 集发现主角换了脸就弃剧了，
> 所以角色资产——LoRA、参考图集、固定参数模板——才是公司真正的资产。
> 生成引擎随时能换供应商，角色资产换不了。
> 所以工程投入产出比最高的，是把角色资产做成可复用、可跨集继承的东西，
> 而不是每次去调一版模型。"

### Q4「你怎么控制成本？」

> "我觉得关键是**别只盯推理单价，要盯抽卡率**。
> 单价降一半，但为了保质量每个镜头多抽一倍，总成本一点没降。
> 所以优化顺序是：先提高采纳率，再压单价。
> 而提高采纳率有一半是工具侧的事——把角色资产固化、把人工挑中的参数沉淀回模板、
> 让人能改一个参数就批量重试，而不是全靠抽。"

### Q5「这个项目你自己觉得哪里做得不好？」

**这题必问，答"没有缺点"等于没答。**

> "三个：
> 一是数据存 SQLite，而且是每次操作新建连接 + 线程锁——这是为了让 demo 零依赖能跑，
> 生产上那是吞吐瓶颈，得上连接池 + PostgreSQL。
> 二是没做幂等，重试会重复扣费——真实产线里这是会出事故的，得加 client_token 唯一索引。
> 三是没做角色一致性资产，只在 prompt 里带了个 character_ref 字符串，
> 实际上没有真正固化 seed 和参数。这是这个 demo 最该补的一块。"

### Q6「你 Python 不是只会语法吗？」

> "语法层面没问题，FastAPI 我是用着写的。
> 但生产级的 Python 工程经验我确实没有——比如 Celery 的幂等、asyncio 的并发陷阱、
> 连接池这些，我目前是知道概念、还没在真实负载下踩过坑。
> 所以我定位很清楚：不投后端岗，来投前端 + AI 应用落地。
> 这两周做这个 demo 最直接的价值，是我把后端从'完全不懂'变成'能设计、能 review、能跟后端对上话'。"

## 10.4 一分钟自检清单（面试前 5 分钟过一遍）

- [ ] 我能用 30 秒说清这个 demo 解决什么问题
- [ ] 我能说出 demo → 生产的至少 4 处差距和原因
- [ ] 我能讲清"抽卡率"和"一致性"两个判断
- [ ] 我能说出一个"我这个 demo 做得不好"的具体点
- [ ] 我能诚实说清 Python 水平，不夸大也不自卑
- [ ] 我知道被问"了解我们后端吗"时该画哪张图
- [ ] 我准备好了"这个 demo 是我边学边做的"这个说法

## 10.5 最后一件事：把它变成"作品"

做完第 9 章的动手任务（角色一致性资产）之后：

1. **录一段 2-3 分钟演示视频**：提交 → 进度 → 失败重试 → 选候选 → 成本面板
2. **重写 README**：把第 8.7 节那张对照表放进去，加上真实耗时数据
3. **推到 GitHub**，仓库名建议：`ai-short-drama-pipeline`
4. **README 顶部写清你的身份**：
   > "7 年前端开发经验，为理解 AI 影视生产链路而做的技术 demo。
   > 用人话讲：这个项目解决的是 AI 生成内容时'会失败、结果不唯一、成本要精确记账'三个新问题。"

---

# 附录 · 卡住时的提问模板

复制下面任一条去问 Codex / Claude Code。**原则：问"解释"和"出题"，不要问"帮我写完"。**

## 问 FastAPI

```
解释 backend/app/main.py 里 events() 这个生成器函数，每一行在做什么？
为什么 SSE 要加 X-Accel-Buffering: no？
BackgroundTasks 和 asyncio.create_task 有什么区别？什么场景必须用前者？
FastAPI 是在哪一层做请求体校验的？为什么校验失败返回 422？
response_model 除了生成文档，还做了什么安全上的事？
出 5 道题考我 FastAPI 装饰器和 Express 路由的对应关系
```

## 问 SQL / 存储

```
我 store.py 里的 SQL 有 N+1 查询问题吗？怎么改成 JOIN？
为什么 SQLite 需要 conn.commit()？不 commit 会怎样？
我的 _lock 在 demo 里防的是什么？生产上还需要吗？
PostgreSQL 的 MVCC 是什么意思？为什么它能支持高并发写？
什么情况下 SQLite 的写锁会成为瓶颈？
```

## 问 asyncio / 任务队列

```
asyncio 的 Semaphore 是怎么实现的？为什么 gather 是并发的？
如果我在 async 函数里用了 time.sleep 会发生什么？给我一个能复现的最小例子
Celery 的 prefork 和 gthread 两种 worker 模式分别适合什么场景？
如果 Redis 挂了，正在排队的 Celery 任务会怎样？
为什么很多公司用 RabbitMQ 而不是 Redis 当 Celery 的 broker？
```

## 问 Redis

```
缓存穿透、缓存击穿、缓存雪崩分别是什么？怎么防？
用 Redis 做限流有哪几种实现方式？各自的优缺点？
幂等键放 Redis 还是放 PostgreSQL？各有什么问题？
```

## 问代码 review（把你的代码贴给它）

```
看下我 backend/app/tasks.py 里的状态机，有没有竞态条件？
我的 SSE 端点在有 nginx 反代的情况下会有什么问题？
我 store.py 每次操作都新建连接，这样做在生产上会有什么后果？
我的 generator.py 的抽象层，接口设计有没有问题？
```

## 问"行业"（用来准备面试观点）

```
AI 短剧的制作成本结构是怎样的？主要花在哪？
为什么"角色一致性"被认为是当前最大的瓶颈之一？
为什么说 AI 视频生成的"抽卡率"比推理单价更影响成本？
AI 短剧出海相比国内，最大的不同点是什么？
```

---

# 附录 · 三份配套文档

| 文件 | 用途 |
|---|---|
| `README.md` | 架构图 + 7 个设计决策（面试直接背这个） |
| `KNOWLEDGE_MAP.md` | 后端概念速查（Redis/Celery/PG）+ 领导问"你了解我们后端吗"的答法 |
| `LEARN_STEP_BY_STEP.md` | 本文件，按章节学 |

**建议顺序**：`LEARN_STEP_BY_STEP.md`（学） → `README.md`（背） → `KNOWLEDGE_MAP.md`（查）
