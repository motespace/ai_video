"""
Pydantic 数据模型 = 相当于 TS 的 interface + 运行时校验。

FastAPI 会自动做两件事：
1. 用它校验请求体（字段缺失/类型不对 → 直接返回 422，根本进不到你的函数）
2. 用它生成 OpenAPI 文档（前端同学能直接看到接口定义）

面试可讲：接口契约先用 schema 定义清楚，前后端不用口头对齐。
"""
from typing import Literal, Optional
from pydantic import BaseModel, Field

# 镜头状态机：这就是整个 demo 的核心
ShotStatus = Literal["pending", "running", "succeeded", "failed"]


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="短剧项目名")


class ProjectOut(BaseModel):
    id: int
    name: str
    created_at: str


class ShotCreate(BaseModel):
    """批量提交镜头。

    对应前端：一次性提交整集的分镜，而不是一个一个点。
    这是 AI 内容生产工具的典型交互——运营要的是"批量"。
    """
    project_id: int
    prompts: list[str] = Field(..., min_length=1, description="每个元素是一个镜头的画面描述")
    character_ref: Optional[str] = Field(None, description="角色资产引用，对应同一角色的 LoRA/参考图集 ID")


class ShotOut(BaseModel):
    id: int
    project_id: int
    idx: int
    prompt: str
    character_ref: Optional[str]
    status: ShotStatus
    error: Optional[str] = None
    attempts: int = 0
    duration_seconds: Optional[float] = None
    cost: float = 0.0
    selected_candidate_id: Optional[int] = None
    created_at: str
    updated_at: str


class CandidateOut(BaseModel):
    id: int
    shot_id: int
    url: str
    seed: int
    is_selected: bool = False


class ShotDetail(ShotOut):
    candidates: list[CandidateOut] = []


class SelectCandidateIn(BaseModel):
    candidate_id: int


class CostSummary(BaseModel):
    """成本面板。

    面试可讲：这是 demo 里最有"业务感"的部分——
    老板不关心你生成了多少个镜头，关心的是这一集花了多少钱。
    """
    total_cost: float
    total_shots: int
    succeeded: int
    failed: int
    pending_or_running: int
    avg_cost_per_succeeded_shot: float
    attempts_total: int
