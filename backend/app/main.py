"""
FastAPI 主应用：路由层。

FastAPI 的心智模型（你已经会 Express，一分钟就能懂）：
  @app.get("/api/xxx")  ≈  app.get('/api/xxx', handler)
  Pydantic 模型        ≈  TS interface + 自动校验
  BackgroundTasks      ≈  接口返回后丢后台继续跑
  StreamingResponse    ≈  服务端持续推数据（SSE）

跑起来：
    uvicorn app.main:app --reload --port 8000
    然后打开 http://localhost:8000/docs
（/docs 是 FastAPI 自动生成的 Swagger 文档，前端直接能点接口，很适合演示）
"""
import asyncio
import json
from typing import Optional

from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles

from . import config, store, tasks
from .models import (
    CandidateOut,
    CostSummary,
    ProjectCreate,
    ProjectOut,
    SelectCandidateIn,
    ShotCreate,
    ShotDetail,
    ShotOut,
)

app = FastAPI(title="AI 短剧素材流水线", version="0.1.0")

# 前端跑在 5173 (Vite)，后端 8000，跨域要放开。
# 面试可讲：生产环境这里会换成自己的网关鉴权 + 域名同源，不用 CORS。
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/media", StaticFiles(directory=str(config.MEDIA_DIR)), name="media")


@app.on_event("startup")
def _startup() -> None:
    store.init_db()


# ---------------- 项目 ----------------
@app.post("/api/projects", response_model=ProjectOut)
def create_project(payload: ProjectCreate):
    return store.create_project(payload.name)


@app.get("/api/projects", response_model=list[ProjectOut])
def list_projects():
    return store.list_projects()


# ---------------- 镜头 ----------------
@app.post("/api/shots", response_model=list[ShotOut])
def create_shots(payload: ShotCreate, background: BackgroundTasks):
    """批量提交镜头并立刻返回，后台生成。

    面试可讲：这里体现了 AI 内容生产的核心交互——
    运营提交一整集分镜（几十个镜头），系统异步跑，
    前端通过 SSE 拿进度，而不是让用户卡在一个请求上等 10 分钟。
    """
    project = store.get_project(payload.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="project not found")

    ids = store.add_shots(payload.project_id, payload.prompts, payload.character_ref)
    background.add_task(tasks.run_shots, ids)
    return [store.get_shot(i) for i in ids]


@app.get("/api/shots", response_model=list[ShotOut])
def list_shots(project_id: Optional[int] = None):
    return store.list_shots(project_id)


@app.get("/api/shots/{shot_id}", response_model=ShotDetail)
def get_shot(shot_id: int):
    shot = store.get_shot(shot_id)
    if not shot:
        raise HTTPException(status_code=404, detail="shot not found")
    cands = store.list_candidates(shot_id)
    shot["candidates"] = [
        CandidateOut(
            id=c["id"],
            shot_id=c["shot_id"],
            url=c["url"],
            seed=c["seed"],
            is_selected=bool(c["is_selected"]),
        )
        for c in cands
    ]
    return shot


@app.post("/api/shots/{shot_id}/retry", response_model=ShotOut)
def retry_shot(shot_id: int, background: BackgroundTasks):
    shot = store.get_shot(shot_id)
    if not shot:
        raise HTTPException(status_code=404, detail="shot not found")
    store.update_shot(shot_id, status="pending", error=None)
    background.add_task(tasks.run_shot, shot_id)
    return store.get_shot(shot_id)


@app.post("/api/shots/{shot_id}/select", response_model=ShotOut)
def select_candidate(shot_id: int, payload: SelectCandidateIn):
    """人工从多个候选里挑一个。

    面试可讲：这一步是"人在环"的落点。
    没有这一步，AI 产线就只能是"全自动但质量不可控"。
    """
    shot = store.get_shot(shot_id)
    if not shot:
        raise HTTPException(status_code=404, detail="shot not found")
    cands = store.list_candidates(shot_id)
    if not any(c["id"] == payload.candidate_id for c in cands):
        raise HTTPException(status_code=400, detail="candidate not belongs to this shot")
    store.select_candidate(shot_id, payload.candidate_id)
    return store.get_shot(shot_id)


# ---------------- 成本 ----------------
@app.get("/api/cost", response_model=CostSummary)
def cost():
    return store.cost_summary()


# ---------------- SSE 进度推送 ----------------
@app.get("/api/events")
async def events():
    """服务端推送进度。

    为什么用 SSE 而不是 WebSocket？
    面试可讲：SSE 是单向的、走 HTTP、自带断线重连，
    而我们只需要服务端→前端单向推，WebSocket 是杀鸡用牛刀。
    真实项目里如果要做"用户实时编辑同一个剧本"才需要 WebSocket。

    用法（前端）：
        const es = new EventSource('/api/events')
        es.onmessage = e => { const shots = JSON.parse(e.data); ... }
    """

    async def stream():
        while True:
            payload = {
                "shots": store.list_shots(),
                "cost": store.cost_summary(),
            }
            # SSE 协议格式：data:<json>\n\n
            yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"
            await asyncio.sleep(1.0)

    return StreamingResponse(
        stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # 关掉 nginx 缓冲，否则 SSE 会被攒着不发
        },
    )
