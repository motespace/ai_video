from .. import store
from sqlalchemy.orm import Session


def create_project(name: str, db: Session) -> dict:
    """创建项目。

    这里放【业务规则】，不放 SQL。
    """
    name = name.strip()
    if not name:
        raise ValueError("项目名不能为空")

    # 业务规则：项目名不允许重复
    for p in store.list_projects(db):
        if p["name"] == name:
            raise ValueError(f"项目名已存在：{name}")

    return store.create_project(name, db)


def list_projects(db: Session) -> list[dict]:
    return store.list_projects(db)
