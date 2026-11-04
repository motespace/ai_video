from fastapi import APIRouter, HTTPException

from .. import services
from ..schemas.project import ProjectCreate, ProjectOut

router = APIRouter(prefix="/api/projects", tags=["项目"])


@router.post("", response_model=ProjectOut)
def create_project(payload: ProjectCreate):
    try:
        return services.create_project(payload.name)
    except ValueError as e:
        # service 抛业务异常，router 负责翻译成 HTTP 语义
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=list[ProjectOut])
def list_projects():
    return services.list_projects()
