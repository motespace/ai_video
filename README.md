# AI 短剧素材流水线（AI Short Drama Production Pipeline）

一个可运行的 AI 短剧内容生产工作台 demo：**批量提交分镜 → 异步生成 → 多候选人工挑选 → 逐镜头成本核算**。

> 这个项目的目的不是"做个玩具"，而是把 AI 影视生产线上"前端 + 服务编排"这一段的
> 真实形态跑通，用来支撑面试时的技术论证。

---

## 一、它解决什么问题

传统短剧生产是**串行人工**：编剧 → 分镜 → 拍摄 → 剪辑。AI 介入后，单镜头生成变成了
一个**会失败、会耗时、会产生多个候选**的异步过程。这带来三个新问题：

1. **怎么让几十个镜头并行跑、还能实时看到进度？** → 任务队列 + SSE 推送
2. **生成结果不是唯一答案，谁来挑？** → 多候选并存 + 人工确认（人在环）
3. **钱花在哪了？** → 成本精确到每一次生成调用，暴露"抽卡率"这个真实成本因子

这三条正好对应 AI 影视公司前端/后端每天在处理的事。

---

## 二、架构

```
┌──────────────── 前端工作台 (React + Vite) ────────────────┐
│  分镜批量提交 │  实时进度 (SSE)  │  候选对比挑选  │  成本面板  │
└───────────┬───────────────────────────────┬──────────────┘
            │ REST                          │ SSE /api/events
┌───────────▼───────────────────────────────▼──────────────┐
│                  FastAPI 服务 (Python)                    │
│  main.py    路由层：项目 / 镜头 / 重试 / 选候选 / 成本      │
│  models.py  Pydantic 契约（= 前后端接口契约的唯一来源）      │
│  tasks.py   任务层：状态机 + 重试 + 并发闸门 + 成本核算      │
│  generator.py 生成抽象层：mock / 真实模型可插拔             │
│  store.py   存储层：SQLite（生产替换为 Postgres + OSS）     │
└───────────────────────────────────────────────────────────┘
```

### 核心状态机

```
pending ──► running ──► succeeded
   ▲            │
   │            ▼
   └── retry ── failed
```

每个镜头**独立**持有状态与重试次数，互不影响。

### 目录结构

```
ai-short-drama-pipeline/
├── backend/
│   ├── app/
│   │   ├── config.py      # 成本单价等业务参数（与代码分离）
│   │   ├── models.py      # Pydantic 数据模型 = 接口契约
│   │   ├── store.py       # SQLite 存储层
│   │   ├── generator.py   # 生成服务抽象（mock / 真实 API）
│   │   ├── tasks.py       # 任务状态机 + 重试 + 成本
│   │   └── main.py        # FastAPI 路由 + SSE
│   ├── requirements.txt
│   └── data/              # SQLite + mock 产物
├── frontend/
│   └── src/
│       ├── api.ts         # 统一请求层
│       ├── types.ts       # 与后端 schema 对齐的 TS 类型
│       ├── App.tsx        # 工作台
│       └── styles.css
└── README.md
```

---

## 三、跑起来

### 后端

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8011
```

打开 http://localhost:8011/docs —— FastAPI 自动生成的 Swagger 文档，可以直接点接口调试。

### 前端

```bash
cd frontend
pnpm install      # 或 npm install
pnpm dev          # http://localhost:5173
```

Vite 已配好 proxy：`/api` 和 `/media` 自动转发到 `127.0.0.1:8011`，所以前端代码里全用相对路径。

### 操作流程

1. 新建/选择一个项目
2. 编辑分镜列表（可增删），填写角色资产引用
3. 点「批量生成」→ 后端立刻返回，镜头在后台跑
4. 表格里实时看到状态流转（排队中 → 生成中 → 已完成 / 失败）
5. 失败的可点「重试」；成功的点「候选」查看 3 个候选图，点「选用」切换
6. 底部成本面板实时更新总成本、单镜头均价、**抽卡率放大系数**

---

## 四、关键设计决策（面试可讲的点）

| 决策 | 为什么 | 真实生产里会怎么变 |
|---|---|---|
| 生成层抽象成接口 | 没有 GPU / API key 也能跑通全链路；换供应商不改业务代码 | 接可灵/即梦：提交任务 → 拿 task_id → 轮询或 webhook → 塞进 candidates 返回 |
| SQLite 而非 MySQL | demo 零依赖；分层是为了将来无痛替换 | Postgres + 对象存储（MinIO/S3/OSS）+ CDN |
| asyncio 而非 Celery | 轻量、易懂；`asyncio.sleep` 不阻塞事件循环 | Celery/RQ + GPU worker 池，并发上限受**显存**而非 CPU 限制 |
| SSE 而非 WebSocket | 单向推送，SSE 走 HTTP 且自带断线重连 | 需要双向协同编辑时才换 WebSocket |
| 成本记在"每次生成调用" | 真正的成本杀手是**抽卡率**——生成 10 次采纳 1 次 | 加模型版本/参数维度，做成本归因 |
| `BackgroundTasks` 跑任务 | 接口不能被 10 分钟的生成阻塞 | 独立队列 + 幂等键 + 死信队列 |
| 多个候选并存 + 人工选 | 没有这一步，AI 产线只能是"全自动但质量不可控" | 把人工修改沉淀回参数模板，形成资产复用 |

### 抽卡率：这一条最重要

`总生成次数 ÷ 成功镜头数` 就是**成本放大系数**。

推理单价降一半，如果抽卡率同时翻倍，总成本反而上升。所以内容生产的成本优化
不应该盯着"每分钟推理成本"，而应该盯着**采纳率 / 返修率 / 人工介入率**。

---

## 五、接入真实模型（可选，做了加分）

在 `backend/app/generator.py` 里加一个真实实现：

```python
async def _kling_generate(prompt: str, shot_id: int, attempt: int) -> dict:
    # 1. 提交任务
    r = await httpx.AsyncClient().post(
        "https://api.klingai.com/v1/videos/image2video",
        headers={"Authorization": f"Bearer {API_KEY}"},
        json={"prompt": prompt, "model_name": "kling-v2"},
    )
    task_id = r.json()["data"]["task_id"]

    # 2. 轮询直到完成
    while True:
        s = await httpx.AsyncClient().get(f".../v1/videos/image2video/{task_id}")
        status = s.json()["data"]["task_status"]
        if status == "succeed":
            url = s.json()["data"]["task_result"]["videos"][0]["url"]
            break
        await asyncio.sleep(5)   # 注意：必须 await，不能用 time.sleep

    # 3. 塞进统一结构返回，业务代码一行不改
    return {"candidates": [{"url": url, "seed": 0}], "duration_seconds": 5.0}
```

然后把 `generate()` 里的分支接上即可。**前端和任务层完全不用动**——这正是抽象的价值。

---

## 六、下一步可以加什么（每个都是面试加分项）

- [ ] **幂等键**：提交镜头带 client_token，重复提交不重复扣费
- [ ] **角色一致性回归**：同 `character_ref` 的镜头共享 seed/参数模板，跨集校验
- [ ] **参数模板沉淀**：人工选中的候选 → 把它的 seed/参数存为该角色的"标准资产"
- [ ] **成本归因**：按模型版本 / 参数 / 时长分组，看钱花在哪
- [ ] **鉴权与配额**：按用户/团队限流，这是真实成本失控的第一道闸
- [ ] **接入真实模型**：见上
- [ ] **Playwright 测试**：覆盖"提交 → 失败 → 重试 → 选候选"主流程
