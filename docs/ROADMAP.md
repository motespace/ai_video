# ROADMAP · 融合调整版学习与开发路线

> **本文档 = `plan.md`（技术阶梯）× `planB.md`（业务蓝图）× 现有代码（真实起点）的融合结果**
>
> - `plan.md` → 决定**学什么、按什么顺序**（技术阶梯，不可乱序）
> - `planB.md` → 决定**建什么、为什么建**（业务模型）
> - 现有 `backend/` → 决定**从哪儿起步**（不推倒重来）
>
> 原始文档保留不动：`plan.md`（根目录）、`backend/planB.md`

---

## 0. 一句话路线

> **用 14 课的技术阶梯，把现有的"镜头流水线 demo"长成 planB 描述的"漫剧创作工作台"后端骨架。**
>
> 技术栈 100% 重合，所以融合几乎零额外成本——**planB 不是新工作，是 plan.md 的目标形态**。

---

## 1. 范围裁剪（先砍清楚，后面不纠结）

### ✅ 本路线要做（一条纵切，85% 的后端学习价值）

```
项目 → 剧集 → 剧本 → AI 拆解 → 角色/场景 → 分镜 → 图片生成 → 视频生成 → 任务追踪 → 素材
```

### ⏭️ 明确延后（连同理由一起记下来，避免反复纠结）

| 模块 | 决定 | 理由 |
|---|---|---|
| 视频合成 / 时间轴 / 多轨道 / 转场 | 延后 | 主要是 FFmpeg + 前端编排，对后端能力增益低；`plan.md` 自己也标 P2 |
| 配音 TTS / 字幕 / 音频模型 | 延后 | 同上，音频模型接入复杂度高，且需要额外账号/费用 |
| `workflows` / `workflow_nodes`（工作流编排画布） | 延后 | planB 最有特色但复杂度最高，等主体链路跑通再谈 |
| `users` / 权限 / 鉴权 | 延后 | 单用户即可；鉴权属于 `plan.md` 第 31～45 天「工程化能力」阶段 |
| 前端 React Flow / Konva 创作画布 | 延后 | 前端时间占比硬性压在 **30% 以内** |
| 前端框架升级（AntD / Zustand / TanStack Query） | 延后 | 你已熟练 React+TS；现有单页先撑住，最后统一接 |

### 📌 前端时间硬约束

> 每课 2 小时里，**前端最多 30 分钟**。后端是主线，前端是"证明后端能用"的配角。
> 违反这条，6～8 周会变成 3 个月。

---

## 2. 数据模型迁移映射（最重要的一张表）

### 2.1 现状 → 目标

| 现有表 | → | 目标表 | 迁移难度 |
|---|---|---|---|
| `projects` | ➡️ | `projects` | ⭐ 扩字段 |
| `shots` | ➡️✂️ | `storyboards`（业务属性）<br>`generate_tasks`（生成属性） | ⭐⭐⭐ **要拆** |
| `candidates` | ➡️ | `asset_versions` | ⭐⭐ 换概念 |
| — | ➕ | `episodes` 剧集 | ⭐ 新增 |
| — | ➕ | `scripts` 剧本 | ⭐ 新增 |
| — | ➕ | `characters` 角色 | ⭐ 新增 |
| — | ➕ | `scenes` 场景 | ⭐ 新增 |
| — | ➕ | `storyboard_characters` 关联表 | ⭐ 新增 |
| — | ➕ | `assets` 素材 | ⭐ 新增 |
| — | ➕ | `asset_versions` 素材版本 | ⭐⭐ |
| — | ➕ | `generate_tasks` 生成任务 | ⭐⭐ |

### 2.2 `shots` 表拆分对照（**这是整个路线最关键的一次重构**）

现在的 `shots` **把两件事混在一张表里**：

| 现在的列 | 它其实属于 | 去哪 |
|---|---|---|
| `id`, `project_id`, `idx` | **镜头业务属性** | → `storyboards` |
| `prompt` | 镜头业务属性（图片提示词） | → `storyboards.image_prompt` |
| `character_ref` | 镜头业务属性 | → `storyboards` + `storyboard_characters` 关联表 |
| `status` | ❗**生成任务属性** | → `generate_tasks.status` |
| `error` | ❗生成任务属性 | → `generate_tasks.error` |
| `attempts` | ❗生成任务属性 | → `generate_tasks.retry_count` |
| `duration_seconds` | ❗生成任务属性 | → `generate_tasks.duration_seconds` |
| `cost` | ❗生成任务属性 | → `generate_tasks.cost` |
| `selected_candidate_id` | ❗生成产物引用 | → `asset_versions.is_default` |
| `created_at`/`updated_at` | 都有 | 两张表都要 |

> 🎯 **为什么必须拆？**
>
> 现在"一个镜头 = 一条记录"，意味着：
> - 一个镜头想同时生成 3 版图片 + 2 版视频 → **要么开 3 条记录，要么加字段**，两者都乱
> - `status` 到底是"镜头的状态"还是"这次生成的状态"？**现在两者混在一起**
> - 重试次数属于"生成行为"，不属于"镜头本身"——**镜头不该因为重试而变**
>
> 拆开后：
> ```
> storyboards      ← 镜头是什么（景别、运镜、时长、画面描述、对白）
> generate_tasks  ← 一次生成发生了什么（状态、进度、重试、耗时、成本、错误）
> assets          ← 产出了什么（图片/视频）
> asset_versions  ← 这个素材的第几版，哪版是默认
> ```
> **这就是真实 AI 影视系统的建模方式**，也大概率是你公司现在的做法。
> 你能讲清楚"为什么要拆"和"拆之前错在哪"，本身就是很强的面试素材。

### 2.3 目标核心表（9 张，延后的表不在此列）

| 表 | 关键字段 |
|---|---|
| `projects` | id, name, description, cover_asset_id, status, created_at, updated_at |
| `episodes` | id, project_id, episode_no, title, synopsis, status, created_at, updated_at |
| `scripts` | id, episode_id, version, content, created_at |
| `characters` | id, project_id, name, description, appearance, age, personality, costume, status |
| `scenes` | id, project_id, name, description, time_of_day, mood |
| `storyboards` | id, episode_id, scene_id, seq, shot_size, camera_movement, duration, description, dialogue, image_prompt, video_prompt |
| `storyboard_characters` | storyboard_id, character_id |
| `assets` | id, project_id, type, owner_type, owner_id, path, mime, size |
| `asset_versions` | id, asset_id, version, url, is_default, seed, created_at |
| `generate_tasks` | id, project_id, task_type, provider, provider_task_id, status, progress, input_json, output_asset_id, error, retry_count, cost, duration_seconds, created_at, updated_at |

---

## 3. API 演进映射（现有接口怎么长成目标接口）

| 现有 | → | 目标 | 说明 |
|---|---|---|---|
| `POST /api/projects` | ➡️ | `POST /api/projects` | 保留，加 description/status |
| `GET /api/projects` | ➡️ | `GET /api/projects` | 保留 |
| `POST /api/shots` | ➡️ | `POST /api/episodes/{id}/storyboards/generate` | 语义升级：从"塞 prompt"到"生成分镜" |
| `GET /api/shots` | ➡️ | `GET /api/episodes/{id}/storyboards` | |
| `GET /api/shots/{id}` | ➡️ | `GET /api/storyboards/{id}` | |
| `POST /api/shots/{id}/retry` | ➡️ | `POST /api/generations/{task_id}/retry` | **重试对象从"镜头"变成"任务"** |
| `POST /api/shots/{id}/select` | ➡️ | `PUT /api/assets/{id}/default-version` | |
| `GET /api/cost` | ➡️ | `GET /api/projects/{id}/cost-summary` | 加项目维度 |
| `GET /api/events` | ➡️ | `GET /api/events`（带 project_id 过滤） | SSE 保留，planB 也用 SSE |
| — | ➕ | `POST /api/scripts/parse` | **第 8 课核心**：LLM 结构化拆解 |
| — | ➕ | `GET /api/projects/{id}/characters` | |
| — | ➕ | `GET /api/projects/{id}/scenes` | |
| — | ➕ | `POST /api/generations/image` | |
| — | ➕ | `POST /api/generations/video` | |
| — | ➕ | `GET /api/generations/{task_id}` | |
| — | ➕ | `GET /api/assets` | |

> 📌 **注意 `retry` 的语义变化**：从"重试这个镜头"变成"重试这次生成任务"。
> 这是 `shots` 拆表带来的连锁反应——**拆对了，很多 API 会自然长对**。

---

## 4. 14 课 → 5 个里程碑

| 课 | 技术主题 | 产出 | 对应 planB 里程碑 |
|---|---|---|---|
| **1** | 分层拆分（Schema/Router/Service/Store） | `main.py` 从 174 行降到 ~40 行 | 一、基础建设 |
| **2** | SQLAlchemy ORM + 9 张目标表 + 数据迁移 | `store.py` 从手写 SQL 变 ORM | 一、基础建设 |
| **3** | 异常体系 + 分层收尾（service 抛业务异常） | 干净的层次边界 | 一、基础建设 |
| **4** | PostgreSQL 落地（SQLite → PG 只需改一处） | 验证分层的价值 | 一、基础建设 |
| **5** | Redis + Celery：asyncio 状态机搬进 Celery | worker 独立跑任务 | 三、异步任务管理 |
| **6** | SSE 补强 + 断线重连 + 任务状态恢复 | 进度实时推送 | 三、异步任务管理 |
| **7** | **LLM 接入**：`POST /api/scripts/parse` | 剧本 → 结构化 JSON → 落 episodes/characters/scenes | 二、剧本与资产 |
| **8** | 模型适配器抽象（`generate_text/image/video`） | `generator.py` 进化成统一适配层 | 二、剧本与资产 |
| **9** | 真实图片/视频 API + 任务状态机 + 失败重试 | 真模型跑通 | 二、剧本与资产 |
| **10** | 资产版本管理 + 素材中心 | assets/asset_versions | 四、素材管理 |
| **11** | 前端接上完整链路（剧集→拆解→分镜→生成） | 端到端可演示 | 全链路打通 |
| **12** | Docker + 环境变量 + 部署 | 一键起全套 | 工程化 |
| **13** | 文档：架构图 / 数据库设计 / API 文档 | 三份交付物 | 验收清单 |
| **14** | 复盘 + 录制演示 + 面试话术整理 | 能讲清楚全流程 | 验收清单 |

> 🎯 **每课结束都能演示一个"比昨天多跑通一点"的东西**——这是坚持下来的关键。

---

## 5. 每课验收命令（贴在手边）

```bash
# 起后端（端口 8011）
cd backend && .venv/bin/python -m uvicorn app.main:app --port 8011 --reload

# 接口文档（人看的）
open http://localhost:8011/docs

# 接口契约（机器读的，喂给前端生成 TS 类型）
open http://localhost:8011/openapi.json

# 起前端（端口 5173）
cd frontend && pnpm dev
```

---

## 6. 关键设计决策记录（面试素材）

| # | 决策 | 一句话理由 |
|---|---|---|
| 1 | 生成层抽象成接口，mock 与真实 API 可替换 | 没有 GPU / 没有 Key 也能跑通全链路；换供应商不改业务代码 |
| 2 | `shots` 拆成 `storyboards` + `generate_tasks` | 镜头是业务实体，生成是行为；一个镜头可以有多个生成任务和多版素材 |
| 3 | 候选图存 `asset_versions` 而不是独立表 | 角色参考图、分镜关键帧、视频片段都是"素材的多个版本"，同一套机制 |
| 4 | 业务规则放 Service，不放 Router | HTTP 接口、Celery Worker、脚本都要复用同一套判断 |
| 5 | Service 抛业务异常，Router 翻译成 HTTP | Worker 里没有 HTTP 概念，异常体系必须与传输层解耦 |
| 6 | 成本精确到"每次生成调用" | 真正决定单分钟成本的不是推理单价，而是抽卡率 |
| 7 | SSE 而非 WebSocket | 只需服务端→前端单向推，SSE 自带断线重连 |
| 8 | 前端类型从 OpenAPI 自动生成 | 前后端类型同源，杜绝"字段改名"引发的联调扯皮 |

---

## 7. 风险清单（提前想好对策）

| 风险 | 对策 |
|---|---|
| 前端吞噬学习时间 | 硬性 30% 上限；每课前端只做"能证明接口能用"的最小量 |
| 范围失控 | 严格按纵切走，不按 planB 里程碑顺序走 |
| 真实模型 API 要花钱 / 要 Key | 第 9 课之前全部用 mock；接真 API 时只跑最短链路验证 |
| 本地装 Redis/PG/Celery 折腾半天 | 第 4/5 课一次性解决，配 docker-compose，别每天纠结 |
| ORM 阶段觉得"手写 SQL 更直观" | 记住：**ORM 的价值不是省代码，是让"改存储层只改一个文件"成为可能** |
| 长时间没有可见产出而放弃 | 每课结束必须有一个能演示的增量（见第 4 节「产出」列） |

---

## 8. 立即行动（本周）

- [ ] 第 1 课：分层拆分（**当前任务**）
- [ ] 写完 `LEARNING_LOG.md` 第 1 课的 4 节
- [ ] 提交 `docs/ROADMAP.md` + `plan.md` + `planB.md` 三件套
- [ ] 决定第 7 课用哪家 LLM（国内可直连 / OpenAI 兼容 / 公司内部网关）——**这会影响第 8 课的 API 形态**

> 📌 **第 7 课的模型选择不用现在定**，但第 4 课之前最好心里有个数：所有主流 LLM 都提供 OpenAI 兼容接口，所以接入代码基本一样。
