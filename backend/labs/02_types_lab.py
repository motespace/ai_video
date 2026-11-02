"""
类型实验室 —— 第 1 课配套
运行：cd backend && .venv/bin/python labs/02_types_lab.py
"""
from typing import Optional, Literal, Any
from datetime import datetime
from pydantic import BaseModel, Field, ValidationError

def t(title):
    print("\n" + "=" * 66)
    print(title)
    print("=" * 66)

def show(model_cls, payload, label):
    try:
        obj = model_cls(**payload)
        print(f"  {label:34} -> ✅ {obj.model_dump()}")
    except ValidationError as e:
        err = e.errors()[0]
        print(f"  {label:34} -> ❌ {err['type']} | {err['msg']}")

# ---------------- 布尔 ----------------
t("【1】bool —— 经典坑：字符串 'false' 会变成 True")
class B(BaseModel):
    flag: bool
    opt: Optional[bool] = None
    default_false: bool = False

show(B, {"flag": True}, "flag=True")
show(B, {"flag": False}, "flag=False")
show(B, {"flag": "false"}, "flag='false'  ⚠️ 字符串")
show(B, {"flag": "true"}, "flag='true'")
show(B, {"flag": 0}, "flag=0")
show(B, {"flag": 1}, "flag=1")
show(B, {}, "不传 flag（必填）")
show(B, {"flag": True}, "不传 opt（Optional+默认值）")

# ---------------- 数值 ----------------
t("【2】int / float —— 互相转换的规则")
class N(BaseModel):
    i: int
    f: float
    d: float = 0.0

show(N, {"i": 3, "f": 3}, "i=3, f=3  (int->float)")
show(N, {"i": "3", "f": "1.5"}, "i='3', f='1.5' (字符串数字)")
show(N, {"i": 3.0, "f": 1.5}, "i=3.0 (整数值的float)")
show(N, {"i": 3.5, "f": 1.5}, "i=3.5 ⚠️ 小数给int")
show(N, {"i": True, "f": 1.5}, "i=True ⚠️ bool给int")

# ---------------- 列表 ----------------
t("【3】list —— 默认值必须用 default_factory")
class L(BaseModel):
    items: list[str] = Field(default_factory=list)
    tags: Optional[list[str]] = None
    nums: list[int] = Field(default_factory=list, min_length=1, max_length=3)

show(L, {}, "什么都不传")
show(L, {"items": ["a"], "nums": [1, 2]}, "正常传")
show(L, {"items": "abc"}, "items='abc' ⚠️ 字符串不是列表")
show(L, {"nums": []}, "nums=[] (违反 min_length=1)")
show(L, {"nums": [1, 2, 3, 4]}, "nums 有4个 (违反 max_length=3)")

print("\n  ⚠️ 陷阱示范：直接写 = [] 会共享同一个列表对象")
class BadList(BaseModel):
    items: list[str] = []
b1, b2 = BadList(), BadList()
b1.items.append("x")
print(f"     b1={b1.items}  b2={b2.items}  -> b1 改了 b2 也变了: {b1.items is b2.items}")

# ---------------- 字典 ----------------
t("【4】dict —— key/value 都能定类型")
class D(BaseModel):
    meta: dict[str, Any] = Field(default_factory=dict)
    scores: dict[str, int] = Field(default_factory=dict)

show(D, {}, "不传")
show(D, {"meta": {"a": 1, "b": "x"}}, "meta 任意值")
show(D, {"scores": {"数学": 100}}, "scores 键值都合法")
show(D, {"scores": {"数学": "A"}}, "scores 值是字符串 ⚠️")
show(D, {"scores": {1: 100}}, "scores key 是数字 ⚠️")

# ---------------- 枚举 / Literal ----------------
t("【5】Literal 与 Enum")
class S(BaseModel):
    status: Literal["draft", "running", "done"]
    level: int = Literal[1, 2, 3]

show(S, {"status": "draft", "level": 1}, "合法")
show(S, {"status": "unknown", "level": 1}, "status 不在枚举里")
show(S, {"status": "draft", "level": 9}, "level 不在枚举里")

# ---------------- 嵌套模型 ----------------
t("【6】嵌套模型 —— list[Model] / Model 里套 Model")
class Character(BaseModel):
    name: str
    age: Optional[int] = None

class Project(BaseModel):
    title: str
    characters: list[Character] = Field(default_factory=list)
    lead: Optional[Character] = None

show(Project, {"title": "x"}, "不传嵌套字段")
show(Project, {"title": "x", "characters": [{"name": "小明"}]}, "嵌套列表(省略 age)")
show(Project, {"title": "x", "characters": [{"name": "小明", "age": "20"}]}, "age='20' 自动转 int")
show(Project, {"title": "x", "characters": [{"age": 20}]}, "嵌套对象缺 name")
show(Project, {"title": "x", "lead": {"name": "小红", "age": 22}}, "单个嵌套对象")

# ---------------- 数值约束 ----------------
t("【7】数值约束 gt / ge / lt / le / multiple_of")
class P(BaseModel):
    score: int = Field(..., ge=0, le=100)
    count: int = Field(..., gt=0)
    step: int = Field(..., multiple_of=5)

show(P, {"score": 100, "count": 1, "step": 10}, "合法")
show(P, {"score": 101, "count": 1, "step": 10}, "score=101 (le=100)")
show(P, {"score": -1, "count": 1, "step": 10}, "score=-1 (ge=0)")
show(P, {"score": 50, "count": 0, "step": 10}, "count=0 (gt=0)")
show(P, {"score": 50, "count": 1, "step": 7}, "step=7 (multiple_of=5)")

# ---------------- 字符串约束 ----------------
t("【8】字符串约束 pattern / strip_whitespace / to_lower")
class Str(BaseModel):
    phone: str = Field(..., pattern=r"^1[3-9]\d{9}$")
    title: str = Field(..., min_length=1, max_length=20, strip_whitespace=True)

show(Str, {"phone": "13800138000", "title": "  标题  "}, "合法(自动去空格)")
show(Str, {"phone": "13800138000", "title": "   "}, "title 纯空格 ⚠️")
show(Str, {"phone": "12345", "title": "x"}, "phone 格式错")
show(Str, {"phone": "13800138000", "title": "x" * 21}, "title 超长")

# ---------------- 时间 ----------------
t("【9】datetime —— ISO 字符串自动解析")
class Dt(BaseModel):
    created_at: datetime

show(Dt, {"created_at": "2026-11-02T10:30:00"}, "ISO 字符串")
show(Dt, {"created_at": "2026-11-02 10:30:00"}, "空格分隔")
show(Dt, {"created_at": "not a date"}, "乱传")
