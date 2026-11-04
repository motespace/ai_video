from typing import Optional
from fastapi import APIRouter, BackgroundTasks, HTTPException
from .. import services, tasks
from ..schemas.shot import ShotCreate, ShotOut, ShotDetail, SelectCandidateIn

router = APIRouter(prefix="/api/shots", tags=["镜头"])

@router.post("", response_model=list[ShotOut])
def create_shots(payload: ShotCreate, background: BackgroundTasks):
    try:
        shot_list = services.create_shots(payload.project_id, payload.prompts, payload.character_ref)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    ids = [s["id"] for s in shot_list]
    background.add_task(tasks.run_shots, ids)
    return shot_list

@router.get("", response_model=list[ShotOut])
def list_shots(project_id: Optional[int] = None):
    return services.list_shots(project_id)

@router.get("/{shot_id}", response_model=ShotDetail)
def get_shot(shot_id: int):
    shot = services.get_shot_detail(shot_id)
    if not shot:
        raise HTTPException(status_code=404, detail="shot not found")
    return shot

@router.post("/{shot_id}/retry", response_model=ShotOut)
def retry_shot(shot_id: int, background: BackgroundTasks):
    shot = services.retry_shot(shot_id)
    if not shot:
        raise HTTPException(status_code=404, detail="shot not found")
    background.add_task(tasks.run_shot, shot_id)
    return shot

@router.post("/{shot_id}/select", response_model=ShotOut)
def select_candidate(shot_id: int, payload: SelectCandidateIn):
    try:
        shot = services.select_candidate(shot_id, payload.candidate_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not shot:
        raise HTTPException(status_code=404, detail="shot not found")
    return shot