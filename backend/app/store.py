"""
存储层：SQLite（Python 标准库自带，不用装任何东西）。

为什么用 SQLite 而不是 MySQL/Postgres？
面试可讲：这是 demo，要的是"零依赖跑起来"。真实生产里这一层会换成
Postgres + 对象存储，但接口不变——这是分层的意义。

注意：生产环境绝不会用 sqlite3 直接在多线程里写，
这里的 check_same_thread=False + Lock 是为了 demo 能跑，
面试时要主动说明这一点（显得你知道差距在哪，而不是误以为生产就这么写）。
"""

import sqlite3
import threading
from datetime import datetime, timezone
from typing import Any, Optional

from . import config
from sqlalchemy import select
from sqlalchemy.orm import Session
from .db.models import Project, Storyboard, GenerateTask

_lock = threading.Lock()

SCHEMA = """
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS shots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    idx INTEGER NOT NULL,
    prompt TEXT NOT NULL,
    character_ref TEXT,
    status TEXT NOT NULL DEFAULT 'pending',
    error TEXT,
    attempts INTEGER NOT NULL DEFAULT 0,
    duration_seconds REAL,
    cost REAL NOT NULL DEFAULT 0,
    selected_candidate_id INTEGER,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS candidates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    shot_id INTEGER NOT NULL,
    url TEXT NOT NULL,
    seed INTEGER NOT NULL,
    is_selected INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_shots_project ON shots(project_id);
CREATE INDEX IF NOT EXISTS idx_candidates_shot ON candidates(shot_id);
"""


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(config.DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with _lock:
        conn = _connect()
        try:
            conn.executescript(SCHEMA)
            conn.commit()
        finally:
            conn.close()


def _query(sql: str, args: tuple = (), one: bool = False) -> Any:
    with _lock:
        conn = _connect()
        try:
            cur = conn.execute(sql, args)
            rows = cur.fetchall()
            if one:
                return dict(rows[0]) if rows else None
            return [dict(r) for r in rows]
        finally:
            conn.close()


def _execute(sql: str, args: tuple = ()) -> int:
    with _lock:
        conn = _connect()
        try:
            cur = conn.execute(sql, args)
            conn.commit()
            return cur.lastrowid
        finally:
            conn.close()


# ---------------- projects ----------------
def create_project(name: str, db: Session) -> dict:
    p = Project(name=name, created_at=now(), updated_at=now())
    db.add(p)
    db.flush()  # 刷新到数据库，拿到自增 id
    return {
        "id": p.id,
        "name": p.name,
        "created_at": p.created_at,
        "updated_at": p.updated_at,
    }


def get_project(pid: int, db: Session) -> Optional[dict]:
    p = db.get(Project, pid)
    if not p:
        return None
    return {
        "id": p.id,
        "name": p.name,
        "created_at": p.created_at,
        "updated_at": p.updated_at,
    }


def list_projects(db: Session) -> list[dict]:
    rows = db.execute(select(Project).order_by(Project.id.desc())).scalars().all()
    return [
        {
            "id": p.id,
            "name": p.name,
            "created_at": p.created_at,
            "updated_at": p.updated_at,
        }
        for p in rows
    ]


# ---------------- shots ----------------
def add_shots(
    project_id: int, prompts: list[str], character_ref: Optional[str], db: Session
) -> list[int]:
    """批量提交镜头：每个镜头建1 条 Storyboard + 1 条 GenerateTask(pending)。"""
    ids: list[int] = []
    # with _lock:
    #     conn = _connect()
    #     try:
    #         for i, p in enumerate(prompts):
    #             cur = conn.execute(
    #                 "INSERT INTO shots(project_id, idx, prompt, character_ref, status, created_at, updated_at)"
    #                 " VALUES (?,?,?,?,?,?,?)",
    #                 (project_id, i, p, character_ref, "pending", ts, ts),
    #             )
    #             ids.append(cur.lastrowid)
    #         conn.commit()
    #     finally:
    #         conn.close()

    for i, p in enumerate(prompts):
        sb = Storyboard(
            project_id=project_id,
            idx=i,
            prompt=p,
            character_ref=character_ref,
            created_at=now(),          # ★ Storyboard 没有 updated_at 这一列
        )
        db.add(sb)
        db.flush()  # 拿到自增 id
        task = GenerateTask(
            project_id=project_id,
            storyboard_id=sb.id,
            task_type="video",          # ★ 必填列，不给会报错
            status="pending",
            created_at=now(),
            updated_at=now(),
        )
        db.add(task)
        db.flush()
        ids.append(sb.id)
    return ids


def get_shot(sid: int, db: Session) -> Optional[dict]:
    """按 id 查镜头。"""
    sb = db.get(Storyboard, sid)
    if not sb:
        return None
    return _shot_to_dict(sb, db)


def _shot_to_dict(sb: Storyboard, db: Session) -> dict:
    """把 Storyboard + 它的 GenerateTask 拼成老 API 的字段形状。
    前端不能改，所以返回的字段必须和老 shots 表一模一样。
    """
    task = (
        db.execute(
            select(GenerateTask)
            .where(GenerateTask.storyboard_id == sb.id)
            .order_by(GenerateTask.id.desc())
        )
        .scalars()
        .first()
    )
    return {
        "id": sb.id,
        "project_id": sb.project_id,
        "idx": sb.idx,
        "prompt": sb.prompt,
        "character_ref": sb.character_ref,
        "status": task.status if task else "pending",
        "error": task.error if task else None,
        "attempts": task.retry_count if task else 0,
        "duration_seconds": task.duration_seconds if task else None,
        "cost": task.cost if task else 0.0,
        "selected_candidate_id": None,   # ★ 这轮先写 None，下轮接 asset_versions
        "created_at": sb.created_at,
        "updated_at": task.updated_at if task else sb.created_at,
    }


def list_shots(project_id: Optional[int] = None, db: Session = None) -> list[dict]:
    """列镜头。可按 project_id 过滤。"""
    stmt = select(Storyboard).order_by(Storyboard.id)
    if project_id is not None:
        stmt = stmt.where(Storyboard.project_id == project_id)
    rows = db.execute(stmt).scalars().all()
    return [_shot_to_dict(r, db) for r in rows]


def update_shot(sid: int, **fields: Any) -> None:
    if not fields:
        return
    fields["updated_at"] = now()
    sets = ", ".join(f"{k}=?" for k in fields)
    args = tuple(fields.values()) + (sid,)
    _execute(f"UPDATE shots SET {sets} WHERE id=?", args)


# ---------------- candidates ----------------
def add_candidates(shot_id: int, cands: list[dict]) -> list[int]:
    ts = now()
    ids = []
    with _lock:
        conn = _connect()
        try:
            for c in cands:
                cur = conn.execute(
                    "INSERT INTO candidates(shot_id, url, seed, created_at) VALUES (?,?,?,?)",
                    (shot_id, c["url"], c["seed"], ts),
                )
                ids.append(cur.lastrowid)
            conn.commit()
        finally:
            conn.close()
    return ids


def list_candidates(shot_id: int) -> list[dict]:
    return _query("SELECT * FROM candidates WHERE shot_id=? ORDER BY id", (shot_id,))


def select_candidate(shot_id: int, candidate_id: int) -> None:
    """选中一个候选。

    面试可讲：AI 内容工具的核心不是"生成"，是"生成 + 人工挑选"。
    所以必须支持多个候选并存 + 人工确认 + 把确认结果沉淀回去。
    """
    with _lock:
        conn = _connect()
        try:
            conn.execute(
                "UPDATE candidates SET is_selected=0 WHERE shot_id=?", (shot_id,)
            )
            conn.execute(
                "UPDATE candidates SET is_selected=1 WHERE id=? AND shot_id=?",
                (candidate_id, shot_id),
            )
            conn.commit()
        finally:
            conn.close()
    update_shot(shot_id, selected_candidate_id=candidate_id)


# ---------------- 成本汇总 ----------------
def cost_summary() -> dict:
    shots = list_shots()
    total = sum(s["cost"] for s in shots)
    ok = [s for s in shots if s["status"] == "succeeded"]
    failed = [s for s in shots if s["status"] == "failed"]
    pending = [s for s in shots if s["status"] in ("pending", "running")]
    avg = (total / len(ok)) if ok else 0.0
    return {
        "total_cost": round(total, 4),
        "total_shots": len(shots),
        "succeeded": len(ok),
        "failed": len(failed),
        "pending_or_running": len(pending),
        "avg_cost_per_succeeded_shot": round(avg, 4),
        "attempts_total": sum(s["attempts"] for s in shots),
    }
