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

from . import config, store
from .routers.project import router as project_router
from .routers.shot import router as shot_router
from .routers.event import router as event_router
from .routers.cost import router as cost_router


from fastapi import  FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles



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

app.include_router(project_router)
app.include_router(shot_router)
app.include_router(event_router)
app.include_router(cost_router)