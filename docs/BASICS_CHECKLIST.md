# 后端基础补完清单（按"什么时候会用到"排序）

> **用法**：每条都能打勾。✅=懂了 / ❓=半懂 / ❌=不懂。
> **不要一次学完**——用到哪条补哪条（Just-in-Time）。
> 每条后面都有「最小实验」，跑一遍就懂 80%。

---

## A · Python 语言（写代码立刻要用的）

| # | 知识点 | 什么时候会用到 | 自测题 |
|---|---|---|---|
| A1 | **装饰器 `@`** | 读懂 `@app.get` / `@router.post` / `@field_validator` | `@app.get("/x")` 到底做了什么？返回值去哪了？ |
| A2 | **异常** `try/except/raise` | service 抛 `ValueError` → router 翻译成 HTTP | `raise` 和 `assert` 有什么区别？ |
| A3 | **类型标注** `x: int -> str` | `def f(a: int) -> dict:` | 标注是给谁看的？不写会怎样？ |
| A4 | **可空类型** `Optional[X]` / `X \| None` | ORM 和 Pydantic 都用 | `Optional[str]` 一定可以不给吗？（v2 不行） |
| A5 | **上下文管理器** `with` | `with Session() as db:` / `with open() as f:` | `with` 退出时一定会提交事务吗？**（不会！）** |
| A6 | **推导式 / 字典推导** | 批量转换数据 | `[x*2 for x in items]` 等价于什么？ |
| A7 | **`*args` / `**kwargs`** | `update_shot(sid, **fields)` | `**fields` 传进来是什么类型？ |
| A8 | **装饰器 + 生成器组合**（`yield`） | SSE 的 `async def stream()` | `yield` 和 `return` 的区别？ |

---

## B · SQL 与数据库（**最大的缺口**）

| # | 知识点 | 什么时候会用到 | 自测题 |
|---|---|---|---|
| B1 | 表 / 行 / 列 / 主键 | 所有表设计 | 什么是主键？为什么不能没有？ |
| B2 | **外键 FK** | `project_id` | 外键是干什么的？删了主表记录会怎样？ |
| B3 | **NULL 的含义** | `nullable=True` | `NULL` 和空字符串 `''` 一样吗？ |
| B4 | **JOIN**（INNER/LEFT） | "查项目下所有镜头" | INNER 和 LEFT 的区别？什么时候用 LEFT？ |
| B5 | **聚合** `COUNT/SUM/AVG` | 成本汇总 | `avg_cost_per_succeeded_shot` 怎么算？为什么只对成功的算？ |
| B6 | **索引 Index** | 数据量大后 | 索引是干什么的？为什么会拖慢写入？ |
| B7 | **事务 Transaction** | `commit` / `rollback` | 什么是"原子性"？转账的例子 |
| B8 | **唯一约束 UNIQUE** | `provider_task_id` | 唯一约束和"业务上不能重复"是一回事吗？ |

---

## C · ORM 概念（第 2 课要用）

| # | 知识点 | 什么时候会用到 | 自测题 |
|---|---|---|---|
| C1 | **ORM vs 手写 SQL** | 理解为什么要换 | ORM 帮你省的是"写 SQL"还是"想清楚数据模型"？ |
| C2 | **模型类 = 表** | `class Project(Base)` | `__tablename__` 不写会怎样？ |
| C3 | **`Mapped[...]` / `mapped_column(...)`** | 写模型 | `Mapped[str]` 和 `mapped_column(String(100))` 各自管什么？ |
| C4 | **Session / Unit of Work** | 事务边界 | `db.add` 之后数据在哪？`commit` 之后在哪？ |
| C5 | **`flush()` vs `commit()`** | 拿自增 id | 什么时候用 flush？ |
| C6 | **`db.get()` / `select()`** | 查询 | `db.get(Project, 1)` 和 `select(Project)` 有什么区别？ |
| C7 | **relationship 懒加载** | 关联对象 | `p.storyboards` 什么时候才发 SQL？ |
| C8 | **N+1 查询** | 性能坑 | 查 10 个项目，每个访问 `.storyboards`，一共几条 SQL？ |

---

## D · FastAPI / 后端工程（补充）

| # | 知识点 | 什么时候会用到 | 自测题 |
|---|---|---|---|
| D1 | **依赖注入 Depends** | 把 Session 传进 store | `Depends` 的函数什么时候执行？ |
| D2 | **中间件 Middleware** | CORS、鉴权 | CORS 是在前端还是后端解决的？ |
| D3 | **异常处理器** | 统一错误格式 | 业务异常怎么变成 HTTP 响应？ |
| D4 | **后台任务 vs 任务队列** | 第 6 课 Celery | 进程重启后任务会怎样？ |
| D5 | **SSE vs 轮询 vs WebSocket** | 进度推送 | 三者分别适合什么场景？ |

---

## 📌 每次课前必做的 3 分钟自检

```
1. 这次要用的概念，我在上面清单里对应哪几号？
2. 这几条我 ✅/❓/❌ 哪些？
3. ❓ 和 ❌ 的，先跑一遍「最小实验」，再动手写业务代码。
```

> **不要系统学习，按需补课。** 清单是"地图"，不是"任务列表"。
