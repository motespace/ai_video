# 14 天学习路线：从「Python 只会语法」到「能讲清楚这个 demo」

目标不是变成 Python 专家，而是——**能独立跑通、能改、能被问到时讲清楚 5 分钟**。

每天建议 2-3 小时。**关键：每天都要真的动手改一行代码**，不要只读。

---

## Day 1（1.5h）跑通 + 搞懂骨架

**目标**：能在浏览器里看到东西动起来。

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8011
```

打开 http://localhost:8011/docs，用 Swagger 直接创建项目、提交镜头，看状态变化。

**必须搞懂的 3 件事**（问 AI，别读长文档）：
1. `@app.post("/api/shots")` 这个装饰器做了什么
2. `BackgroundTasks` 为什么能让接口先返回、任务后跑
3. `async def` 里的 `await` 到底让出了什么

**动手改**：把 `config.py` 里的 `MOCK_MIN_SECONDS` 从 3 改成 8，重启，看看进度条变化。

---

## Day 2（2h）FastAPI 路由 + Pydantic

**目标**：能自己加一个接口。

看 `main.py` 的 `create_shots`，然后自己加：
- `GET /api/projects/{id}/shots`（按项目查镜头，带路径参数）
- `DELETE /api/shots/{id}`（删镜头）
- 一个 `GET /api/stats`（返回每个项目的镜头数/成本）

**必须搞懂**：`ShotCreate` 这个 Pydantic 模型如果前端传了 `prompts: "abc"`（字符串不是数组），会发生什么？为什么 FastAPI 能在进函数之前就拦下来？

这对应你熟悉的 zod + TS interface，但更强：**校验是运行时强制的，不是靠类型系统静态保证**。

**动手改**：给 `ShotCreate` 加一个字段 `negative_prompt: Optional[str]`，前端也传一下。

---

## Day 3（2h）任务状态机 + asyncio

**目标**：能解释清楚"为什么一个镜头失败不影响其他镜头"。

读 `tasks.py` 的 `run_shot` 和 `run_shots`。

**必须搞懂**：
1. `asyncio.Semaphore(3)` 是什么，为什么限制并发
2. `await asyncio.gather(...)` 和 `asyncio.sleep` 的关系
3. **为什么不能用 `time.sleep`**（写个 demo 感受一下：改成 time.sleep 后 3 个镜头串行执行）

**动手改**：把失败概率从 0.25 改成 0.6，多提交几个镜头，观察"失败 + 重试"的分布。

---

## Day 4（2h）SQLite + 分层

**目标**：理解为什么要分层，以及"零依赖"是怎么做到的。

读 `store.py`。

**必须搞懂**：
1. 为什么 `sqlite3.connect` 每次操作都新建连接（因为 demo 简单，真实项目用连接池）
2. `with _lock` 是干什么的（多线程安全）
3. 这个锁在真实生产里会带来什么问题（吞吐瓶颈 → 需要连接池 + 真正的数据库）

**动手改**：给 `shots` 表加一个 `tags` 字段，提交时支持带上标签。

---

## Day 5（2h）SSE 实时推送

**目标**：理解"服务端推"和"前端轮询"的取舍。

读 `main.py` 的 `events` 端点。

**必须搞懂**：
1. SSE 的报文格式 `data: xxx\n\n` 是什么约定
2. `X-Accel-Buffering: no` 是干什么的（nginx 缓冲会把 SSE 攒住不发——这是个真实踩坑点）
3. 为什么不用 WebSocket

**动手改**：把推送间隔从 1.0s 改成 0.3s，感受区别；再试试改成 WebSocket（用 FastAPI 的 `WebSocket`）。

---

## Day 6（2h）前端接上

**目标**：前后端串起来。

读 `frontend/src/api.ts` 和 `App.tsx`。

**必须搞懂**：
1. Vite proxy 的作用（避免开发期跨域）
2. `EventSource` 的生命周期管理（组件卸载要 `close()`，否则内存泄漏）
3. 前端 `types.ts` 和后端 `models.py` 怎么保持一致（现在是手写的，真实项目用 OpenAPI 自动生成）

**动手改**：给候选对比加一个"全部选用第一个"的操作。

---

## Day 7（2h）成本模型

**目标**：能讲"抽卡率"这个概念——这是你面试里最有杀伤力的判断。

读 `generator.py` 的 `compute_cost` 和 `main.py` 的 `/api/cost`。

**必须搞懂**：为什么成本要记在"每次生成调用"上，而不是"每分钟成片"上。

**动手改**：在成本面板里加一个"每集成本"和"预算超支警告"（比如预算 100 元，超了标红）。

---

## Day 8（2h）接真实模型（可选但强烈建议）

在 `generator.py` 加 `_kling_generate`，流程见 README 第五节。

没有 API key 就先读代码理解流程也行。**重点是理解"提交任务 → 轮询 → 拿 URL → 塞进统一结构"这个模式**，因为这就是他们公司现在的日常。

---

## Day 9（2h）幂等 + 重试的正确姿势

**目标**：理解为什么生成任务必须幂等。

**动手改**：
- 提交镜头时带 `client_token`
- 服务端用 token 建唯一索引，重复提交直接返回已有 task_id，不重复扣费
- 重试时区分"网络超时（该重试）"和"参数错误（不该重试）"

---

## Day 10（2h）角色一致性资产

**目标**：把"一致性是最大瓶颈"这个判断变成代码。

**动手改**：
- 建 `characters` 表：一个角色 → 固定的 seed / 参数模板 / 参考图 URL
- 提交镜头时选角色，自动带上该角色的固定参数
- 加一个"一致性检查"：同角色的镜头 seed 不一致就告警

**这个功能做完，你在面试里讲"一致性"就有了实物支撑。**

---

## Day 11（1.5h）测试

**动手改**：用 pytest 写 3 个测试：
1. 提交镜头 → 状态最终变成 succeeded
2. 失败重试 → attempts 累加
3. 选候选 → 只有 1 个 is_selected=1

---

## Day 12（2h）部署与工程化

**动手改**：写一个 `Dockerfile`（多阶段）+ `docker-compose.yml`（前端 nginx + 后端 uvicorn），跑通。

面试可讲：我知道怎么把它变成一个能部署的服务，而不只是本地能跑。

---

## Day 13（2h）README 与话术

- 重写 README：架构图、每个决策的"为什么"、真实耗时数据、**如果上生产要改什么**
- 把"如果上生产要改什么"写成一段话：幂等、真实队列（Celery）、Postgres+OSS、鉴权配额、监控告警、GPU 调度

---

## Day 14（2h）录屏 + 演练

- 录一段 2-3 分钟的演示视频：提交 → 进度 → 失败重试 → 选候选 → 成本面板
- 准备 3 分钟口述版（对着 README 讲，不用背）
- 准备"这个 demo 哪里做得不够好"的自我批判（老板一定会问这个，答得诚实反而加分）

---

## 每天的 AI 使用方式（这点本身就是面试素材）

用 Codex 当 tutor，不要让它替你写完：

好的问法：
- "解释 `main.py` 里 `events()` 这个函数，每一行在做什么？"
- "`BackgroundTasks` 和 `asyncio.create_task` 有什么区别？"
- "如果我的 SSE 在 nginx 后面不推送，可能是哪些原因？"

坏的问法：
- "帮我写完整个后端"

**面试时你可以讲**：这个项目里我用 AI 的方式是"让它解释、让它出题、让它 review，我自己实现"。
这句话本身就是"我会用 AI 提效"的最强证据——因为它证明你不是被 AI 替代的人。
