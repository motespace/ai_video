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
def create_project(name: str) -> dict:
    pid = _execute("INSERT INTO projects(name, created_at) VALUES (?,?)", (name, now()))
    return get_project(pid)


def get_project(pid: int) -> Optional[dict]:
    return _query("SELECT * FROM projects WHERE id=?", (pid,), one=True)


def list_projects() -> list[dict]:
    return _query("SELECT * FROM projects ORDER BY id DESC")


# ---------------- shots ----------------
def add_shots(project_id: int, prompts: list[str], character_ref: Optional[str]) -> list[int]:
    ts = now()
    ids: list[int] = []
    with _lock:
        conn = _connect()
        try:
            for i, p in enumerate(prompts):
                cur = conn.execute(
                    "INSERT INTO shots(project_id, idx, prompt, character_ref, status, created_at, updated_at)"
                    " VALUES (?,?,?,?,?,?,?)",
                    (project_id, i, p, character_ref, "pending", ts, ts),
                )
                ids.append(cur.lastrowid)
            conn.commit()
        finally:
            conn.close()
    return ids


def get_shot(sid: int) -> Optional[dict]:
    return _query("SELECT * FROM shots WHERE id=?", (sid,), one=True)


def list_shots(project_id: Optional[int] = None) -> list[dict]:
    if project_id is None:
        return _query("SELECT * FROM shots ORDER BY id")
    return _query("SELECT * FROM shots WHERE project_id=? ORDER BY idx", (project_id,))


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
            conn.execute("UPDATE candidates SET is_selected=0 WHERE shot_id=?", (shot_id,))
            conn.execute("UPDATE candidates SET is_selected=1 WHERE id=? AND shot_id=?", (candidate_id, shot_id))
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
