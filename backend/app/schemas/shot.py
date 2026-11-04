
from typing import Literal, Optional
from pydantic import BaseModel, Field


# 镜头状态机：这就是整个 demo 的核心
ShotStatus = Literal["pending", "running", "succeeded", "failed"]

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

