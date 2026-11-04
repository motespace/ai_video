from .. import store
from typing import Optional
from ..schemas.shot import CandidateOut

def create_shots(project_id: int, prompts: list[str], character_ref: Optional[str]) -> list[dict]:
    # 业务规则：项目必须存在
    project = store.get_project(project_id)
    if not project:
        raise ValueError("project not found")

    ids = store.add_shots(project_id, prompts, character_ref)
    return [store.get_shot(i) for i in ids]

def list_shots(project_id: Optional[int] = None) -> list[dict]:
    return store.list_shots(project_id)

def get_shot_detail(shot_id: int) -> Optional[dict]:
    shot = store.get_shot(shot_id)
    if not shot:
        return None
    cands = store.list_candidates(shot_id)
    shot["candidates"] = [
        CandidateOut(
            id=c["id"], shot_id=c["shot_id"], url=c["url"],
            seed=c["seed"], is_selected=bool(c["is_selected"]),
        )
        for c in cands
    ]
    return shot

def retry_shot(shot_id: int) -> Optional[dict]:
    shot = store.get_shot(shot_id)
    if not shot:
        return None
    store.update_shot(shot_id, status="pending", error=None)
    return store.get_shot(shot_id)

def select_candidate(shot_id: int, candidate_id: int) -> Optional[dict]:
    shot = store.get_shot(shot_id)
    if not shot:
        return None
    cands = store.list_candidates(shot_id)
    # 业务规则：候选必须属于这个镜头
    if not any(c["id"] == candidate_id for c in cands):
        raise ValueError("candidate not belongs to this shot")
    store.select_candidate(shot_id, candidate_id)
    return store.get_shot(shot_id)