from .. import store
from typing import Optional
from ..schemas.shot import CandidateOut
from sqlalchemy.orm import Session


def create_shots(
    project_id: int, prompts: list[str], character_ref: Optional[str], db: Session
) -> list[dict]:
    # 业务规则：项目必须存在
    project = store.get_project(project_id, db)
    if not project:
        raise ValueError("project not found")

    ids = store.add_shots(project_id, prompts, character_ref, db)
    return [store.get_shot(i) for i in ids]


def list_shots(project_id: Optional[int] = None, db: Session = None) -> list[dict]:
    return store.list_shots(project_id, db)


def get_shot_detail(shot_id: int, db: Session) -> Optional[dict]:
    shot = store.get_shot(shot_id, db)
    if not shot:
        return None
    cands = store.list_candidates(shot_id, db)
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


def retry_shot(shot_id: int, db: Session) -> Optional[dict]:
    shot = store.get_shot(shot_id, db)
    if not shot:
        return None
    store.update_shot(shot_id, status="pending", error=None, db=db)
    return store.get_shot(shot_id, db)


def select_candidate(shot_id: int, candidate_id: int, db: Session) -> Optional[dict]:
    shot = store.get_shot(shot_id, db)
    if not shot:
        return None
    cands = store.list_candidates(shot_id, db)
    # 业务规则：候选必须属于这个镜头
    if not any(c["id"] == candidate_id for c in cands):
        raise ValueError("candidate not belongs to this shot")
    store.select_candidate(shot_id, candidate_id, db)
    return store.get_shot(shot_id, db)
