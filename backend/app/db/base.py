"""
所有 ORM 模型的基类。

为什么要有基类？
- `Base.metadata` 是所有表的"登记表"。你每定义一个模型类，
  SQLAlchemy 就把它登记进去；`Base.metadata.create_all(engine)`
  一句话就能把【全部】表建出来。
- 有了共同的基类，SQLAlchemy 才能在类之间解析 relationship 的引用。

`DeclarativeBase` 是 SQLAlchemy 2.0 之后的写法（2.0 之前叫 `declarative_base()`）。
它让下面每个类自动获得 ORM 能力：能被 session.add()、能被 select() 查询。
"""
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
