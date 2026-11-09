"""
ORM 模型 = 表结构声明。

★ 本文件是第 2 课的核心 ★

对照旧的手写 SQL 表结构，最重要的变化是【shots 被拆成了两张表】：

  旧 shots 表（一表混装）              新：拆成两张
  ┌──────────────────────┐            ┌────────────────────────┐
  │ id, project_id, idx  │ 业务属性 →  │ storyboards            │
  │ prompt, character_ref│            │  （镜头【是什么】）    │
  ├──────────────────────┤            ├────────────────────────┤
  │ status, error        │ 运行时属性 → │ generate_tasks         │
  │ attempts, duration   │            │  （一次生成【发生了什么】）│
  │ cost, selected_cand… │            └────────────────────────┘
  └──────────────────────┘
  为什么拆？一个镜头要生成 3 版图 + 2 版视频时，
  混装表就只能"开多行"（镜头重复了）或"加字段"（列爆炸）。
"""

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


def now() -> str:
    """统一的时间戳格式，和老 store.py 保持一致。"""
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class Project(Base):
    """项目表。"""

    __tablename__ = "projects"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="draft")
    project_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("projects.id"), nullable=True
    )
