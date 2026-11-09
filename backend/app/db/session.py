"""
数据库连接与会话管理。

三个概念：
1. engine  —— 数据库连接池。整个应用【共用一个】，不要每次请求新建。
2. Session —— 一个"工作单元"：改动先记在这里，commit() 才真正写库。
3. get_db  —— FastAPI 依赖：每个请求一个 Session，请求结束自动收尾。
"""
from collections.abc import Iterator
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from ..config import DATA_DIR
from .base import Base

# 第 2 课用【新库】，和老的 pipeline.db 并存。
# 原因：老的 pipeline.db 里的 projects 表只有 3 列，
# 而 ORM 的 projects 表有 5 列 —— create_all 遇到同名表【不会改结构】，
# 直接用同一个库会导致"缺列"报错。改了库名，问题自然消失。
# （真实项目里这种情况要写迁移脚本 Alembic，第 4 课之后会讲。）
DB_PATH = DATA_DIR / "pipeline_v2.db"

# 第 4 课切 PostgreSQL 时，【只改这一行】
engine = create_engine(
    f"sqlite:///{DB_PATH}",
    connect_args={"check_same_thread": False},   # FastAPI 用线程池跑同步函数，必须关这个检查
    echo=False,                                   # 想看 ORM 生成的 SQL 就改 True
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db() -> Iterator[Session]:
    """FastAPI 依赖注入：每个请求一个 Session，结束自动关。"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def init_db() -> None:
    """建表（已存在则跳过）。"""
    Base.metadata.create_all(engine)
