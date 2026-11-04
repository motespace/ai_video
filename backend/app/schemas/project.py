
from pydantic import BaseModel, Field

class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="短剧项目名")


class ProjectOut(BaseModel):
    id: int
    name: str
    created_at: str
