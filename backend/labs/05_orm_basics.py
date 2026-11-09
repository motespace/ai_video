"""
ORM 基础实验 —— 第 2 课的基础补丁
运行：cd backend && .venv/bin/python labs/05_orm_basics.py

读法：先跑一遍看输出，再回头看每段上面的注释。
每个实验对应 BASICS_CHECKLIST.md 里的编号。
"""
import os
from typing import Optional
import tempfile

from sqlalchemy import create_engine, event, ForeignKey, Integer, String, Text, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship

# 临时库，不碰你的数据
DB = os.path.join(tempfile.mkdtemp(), "lab.db")
engine = create_engine(f"sqlite:///{DB}", echo=False)   # echo=True 可以看它生成的 SQL


class Base(DeclarativeBase):
    pass


# ============================================================
# 【实验 1】表 = 形状，行 = 一个个具体的数据
# 对应 B1 / C2
# ============================================================
print("\n" + "=" * 60)
print("【实验 1】表是【形状】，行是【具体数据】")
print("=" * 60)

class Project(Base):
    __tablename__ = "projects"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="draft")

Base.metadata.create_all(engine)
print("建表完成。表结构（DDL）长这样：")
import sqlite3
conn = sqlite3.connect(DB)
for row in conn.execute("SELECT sql FROM sqlite_master WHERE type='table'"):
    print("  ", row[0].replace("\n", " "))
conn.close()
print("\n★ 看到没：CREATE TABLE 里的每一列，都对应上面 Python 的一行。")
print("★ 表只是【形状】，里面还没有数据。")


# ============================================================
# 【实验 2】外键：project_id 指向 projects.id
# 对应 B2
# ============================================================
print("\n" + "=" * 60)
print("【实验 2】外键：这一列的值必须是另一张表里已存在的 id")
print("=" * 60)

class Storyboard(Base):
    __tablename__ = "storyboards"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)

Base.metadata.create_all(engine)

with Session(engine) as db:
    p = Project(name="雨夜的小猫")
    db.add(p)
    db.flush()
    print(f"已插入项目，id = {p.id}")

    # 故意插一个不存在的 project_id
    db.add(Storyboard(project_id=999, prompt="不存在的项目"))
    try:
        db.commit()
        print("  ❌ 竟然插进去了？（默认情况下 SQLite 不检查外键！）")
    except Exception as e:
        db.rollback()
        print(f"  ✅ 被数据库拦住了：{type(e).__name__}")
        print("     ", str(e).split("\n")[0][:90])
print("★ 外键的作用：保证【引用的东西真的存在】，不会出现指向幽灵的记录。")

print("\n  ⚠️ 上面为什么没拦住？因为【SQLite 默认不开启外键检查】！")
print("     打开这个开关后，外键才真的会生效：")

from sqlalchemy import event as sa_event

@sa_event.listens_for(engine, "connect")
def _fk_on(dbapi_conn, conn_record):
    dbapi_conn.execute("PRAGMA foreign_keys=ON")

engine.dispose()   # 让新连接带上新设置

with Session(engine) as db:
    p = Project(name="雨夜的小猫")
    db.add(p); db.flush()
    db.add(Storyboard(project_id=999, prompt="不存在的项目"))
    try:
        db.commit()
        print("     ❌ 还是插进去了")
    except Exception as e:
        db.rollback()
        print(f"     ✅ 现在被拦住了：{type(e).__name__}")
        print("       ", str(e).split("\n")[0][:80])

print("\n★ 【重要差别】SQLite 默认【不】检查外键，PostgreSQL 默认【检查】。")
print("  所以第 4 课换成 PostgreSQL 之后，同一份代码行为会变 —— 这不是 bug，是数据库的默认策略不同。")
print("  排查这类『本地好好的、上线就报错』的问题时，第一个要怀疑的就是它。")


# ============================================================
# 【实验 3】NULL：可空 和 空字符串 不一样
# 对应 B3
# ============================================================
print("\n" + "=" * 60)
print("【实验 3】NULL（没值） ≠ 空字符串（有值但是空的）")
print("=" * 60)

with Session(engine) as db:
    db.add(Project(name="有描述的", description="这是简介"))
    db.add(Project(name="没描述的"))          # 不给 description
    db.add(Project(name="空串的", description=""))  # 给了空字符串
    db.commit()

    rows = db.execute(select(Project)).scalars().all()
    for r in rows:
        print(f"  name={r.name!r:14} description={r.description!r}")
print("★ None（Python）= 数据库的 NULL = '这一列没有值'")
print("★ ''（空串）    = '这一列有值，只是内容是空的'")
print("★ 查询时区别很大：WHERE description IS NULL 和 WHERE description = '' 结果不同")


# ============================================================
# 【实验 4】Session：数据在哪？add / flush / commit 三步
# 对应 C4 / C5
# ============================================================
print("\n" + "=" * 60)
print("【实验 4】Session：add → flush → commit，数据到底在哪一步进去的")
print("=" * 60)

db = Session(engine)
p = Project(name="还没提交的")
db.add(p)
print(f"  add 之后    : p.id = {p.id}   ← 还是 None，因为数据库还不知道")

db.flush()
print(f"  flush 之后 : p.id = {p.id}   ← 有了！数据库执行了 INSERT，但事务没提交")

# 用另一个连接看一眼：数据在不在？
other = Session(engine)
found = other.execute(select(Project).where(Project.name == "还没提交的")).scalars().all()
print(f"  另一个连接看到: {len(found)} 条  ← flush 的数据对别的连接【还看不见】")
other.close()

db.rollback()
print("  rollback 之后 → 这次 add + flush 全部作废")

db = Session(engine)
p = Project(name="真的提交了")
db.add(p)
db.commit()
other = Session(engine)
found = other.execute(select(Project).where(Project.name == "真的提交了")).scalars().all()
print(f"  commit 之后 : 另一个连接看到 {len(found)} 条  ← 现在才真正写进库")
other.close()
db.close()

print("\n★ 记住这张表：")
print("  add     → 放进 Session 的【暂存区】，数据库完全不知道")
print("  flush   → 发给数据库执行（拿到自增 id），但【事务没提交】，别人看不见")
print("  commit  → 【真正写入】，别人才看得见")
print("  rollback→ 全部撤销")


# ============================================================
# 【实验 5】查询：db.get 和 select 的区别
# 对应 C6
# ============================================================
print("\n" + "=" * 60)
print("【实验 5】两种查询方式")
print("=" * 60)

with Session(engine) as db:
    print("  db.get(Project, 1)        →", db.get(Project, 1))
    print("  db.get(Project, 99999)     →", db.get(Project, 99999), "← 找不到就是 None，不用 try/except")
    print()
    all_rows = db.execute(select(Project)).scalars().all()
    print(f"  select(Project)            → {len(all_rows)} 条")
    print("     .execute(...)  返回【结果集】")
    print("     .scalars()    把每行拆成【单个对象】")
    print("     .all()        全部取出（是个 list）")
    print()
    named = db.execute(select(Project).where(Project.name == "真的提交了")).scalars().all()
    print(f"  where(name == ...)         → {len(named)} 条")
    print()
    print("  ★ .scalars() 忘了写会怎样？")
    try:
        wrong = db.execute(select(Project)).all()
        print(f"     {wrong}  ← 这是【一行一行的元组】，不是对象列表")
        print(f"     wrong[0].name 会报错：", end=" ")
        wrong[0].name
    except Exception as e:
        print(f"{type(e).__name__}: {e}")


# ============================================================
# 【实验 6】relationship 懒加载 + N+1 查询
# 对应 C7 / C8
# ============================================================
print("\n" + "=" * 60)
print("【实验 6】relationship 是【懒加载】，小心 N+1")
print("=" * 60)

class Task(Base):
    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    project: Mapped["Project"] = relationship(back_populates="tasks")

Project.tasks = relationship("Task", back_populates="project")
Base.metadata.create_all(engine)

with Session(engine) as db:
    for i in range(3):
        db.add(Task(project_id=1, status="pending"))
    db.commit()

# 数一数发了多少条 SQL
counter = {"n": 0}

@event.listens_for(engine, "before_cursor_execute")
def count_sql(conn, cursor, statement, parameters, context, executemany):
    counter["n"] += 1

print("\n  写法 A：循环里访问 .tasks（懒加载）")
counter["n"] = 0
with Session(engine) as db:
    projects = db.execute(select(Project)).scalars().all()
    for pr in projects:
        _ = pr.tasks          # ← 这一行会触发一条 SQL
print(f"    → 共发出 {counter['n']} 条 SQL  ← 这就是 N+1")

print("\n  写法 B：一次性把关联全查出来（selectinload）")
from sqlalchemy.orm import selectinload
counter["n"] = 0
with Session(engine) as db:
    projects = db.execute(select(Project).options(selectinload(Project.tasks))).scalars().all()
    for pr in projects:
        _ = pr.tasks          # ← 这次不发 SQL 了，数据早就一起查出来了
print(f"    → 共发出 {counter['n']} 条 SQL  ← 2 条搞定（1 查项目 + 1 查任务）")

print("\n★ 懒加载 = 用到才查。方便，但循环里用就是性能杀手。")
