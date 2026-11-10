from fastapi import APIRouter, HTTPException, Depends

from sqlalchemy.orm import Session
from .. import services
from ..schemas.project import ProjectCreate, ProjectOut
from ..db.session import get_db

router = APIRouter(prefix="/api/projects", tags=["项目"])


@router.post("", response_model=ProjectOut)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)):
    try:
        return services.create_project(payload.name, db)
    except ValueError as e:
        # service 抛业务异常，router 负责翻译成 HTTP 语义
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=list[ProjectOut])
def list_projects(db: Session = Depends(get_db)):
    return services.list_projects(db)
