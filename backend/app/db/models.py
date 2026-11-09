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
    """项目：一个 AI 影视 / 漫剧创作项目。"""

    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft")
    created_at: Mapped[str] = mapped_column(String(32), nullable=False, default=now)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False, default=now)

    # 关系：反向的那一侧在对应类里（back_populates 必须双向都写）
    storyboards: Mapped[list["Storyboard"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",  # 删项目 → 级联删分镜
    )
    generate_tasks: Mapped[list["GenerateTask"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
    )

    episodes: Mapped[list["Episode"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )

    characters: Mapped[list["Character"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    scenes: Mapped[list["Scene"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )


class Storyboard(Base):
    """分镜（镜头）：它【是什么】——业务属性。

    ★ 注意这里【没有】status / error / attempts / cost。
    那些是"一次生成"的属性，住在 GenerateTask 里。
    """

    __tablename__ = "storyboards"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    idx: Mapped[int] = mapped_column(Integer, nullable=False)  # 第几个镜头
    prompt: Mapped[str] = mapped_column(Text, nullable=False)  # 画面描述
    image_prompt: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )  # 图片提示词
    video_prompt: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )  # 视频提示词
    shot_size: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # 景别
    camera_movement: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True
    )  # 运镜

    duration: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True
    )  # 时长（秒）
    dialogue: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # 对白
    character_ref: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    created_at: Mapped[str] = mapped_column(String(32), nullable=False, default=now)

    project: Mapped["Project"] = relationship(back_populates="storyboards")
    generate_tasks: Mapped[list["GenerateTask"]] = relationship(
        back_populates="storyboard",
        cascade="all, delete-orphan",
    )


class GenerateTask(Base):
    """生成任务：一次生成【发生了什么】——运行时属性。

    这是从老 shots 表拆出来的另一半。
    一个分镜可以对应多条 GenerateTask（重试、多版本、多类型）。
    """

    __tablename__ = "generate_tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    storyboard_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("storyboards.id"), nullable=True
    )

    task_type: Mapped[str] = mapped_column(String(20), nullable=False)  # image / video
    provider: Mapped[Optional[str]] = mapped_column(
        String(32), nullable=True
    )  # 模型供应商
    provider_task_id: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True
    )  # 供应商那边的 id

    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    duration_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    cost: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    output_asset_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False, default=now)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False, default=now)

    project: Mapped["Project"] = relationship(back_populates="generate_tasks")
    storyboard: Mapped[Optional["Storyboard"]] = relationship(
        back_populates="generate_tasks"
    )


# 加到 backend/app/db/models.py
class Episode(Base):  # 剧集
    __tablename__ = "episodes"
    id, project_id(FK), episode_no, title, synopsis, status, created_at, updated_at


class Character(Base):  # 角色
    __tablename__ = "characters"
    id, project_id(
        FK
    ), name, description, appearance, personality, costume, status, created_at, updated_at


class Scene(Base):  # 场景
    __tablename__ = "scenes"
    id, project_id(FK), name, description, time_of_day, mood, created_at, updated_at
