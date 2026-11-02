"""
Pydantic 校验实验室 —— 第 1 课配套
运行：cd backend && .venv/bin/python labs/01_pydantic_lab.py

每段都是「一个可观察的现象」，看完现象再读下面的结论。
"""
from typing import Optional, Literal
from pydantic import BaseModel, Field, ValidationError

print("=" * 70)
print("【实验 1】模型是什么？实例化 = 一次校验")
print("=" * 70)

class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="短剧项目名")

# 正常
p = ProjectCreate(name="雨夜的小猫")
print("✓ 合法:", p)
print("  类型:", type(p), "| 取值方式:", p.name)
print("  转 dict:", p.model_dump())

# 非法：类型错
try:
    ProjectCreate(name=123)
except ValidationError as e:
    print("\n✗ name=123 ->")
    print("  错误数:", e.error_count())
    for err in e.errors():
        print("   ", err["type"], "|", err["loc"], "|", err["msg"])

print("\n" + "=" * 70)
print("【实验 2】Field(...) 里的三个东西分别管什么")
print("=" * 70)

print("a) 省略号 ... = 必填")
try:
    ProjectCreate()
except ValidationError as e:
    print("   错误:", e.errors()[0]["type"], "|", e.errors()[0]["msg"])

print("\nb) min_length=1 -> 空字符串不行")
try:
    ProjectCreate(name="")
except ValidationError as e:
    print("   错误:", e.errors()[0]["type"], "|", e.errors()[0]["msg"])

print("\nc) max_length=100 -> 太长不行")
try:
    ProjectCreate(name="x" * 101)
except ValidationError as e:
    print("   错误:", e.errors()[0]["type"], "|", e.errors()[0]["msg"])
print("   正好 100 长度 ->", "通过" if ProjectCreate(name="x" * 100) else "")

print("\nd) description=... -> 只影响文档，不参与校验")
print("   项目名可以是中文空格吗? ->", ProjectCreate(name="  雨 夜  "))

print("\n" + "=" * 70)
print("【实验 3】v2 的大坑：Optional 不等于「可以不传」")
print("=" * 70)

class Demo(BaseModel):
    a: Optional[str]                 # 有 Optional，但没给默认值
    b: Optional[str] = None          # 有 Optional，且给了默认值

print("给 Demo(b='x') 试试（a 没传）：")
try:
    print("   ", Demo(b="x"))
except ValidationError as e:
    print("   ✗ 报错:", e.errors()[0]["type"], "|", e.errors()[0]["msg"])
    print("   → Pydantic v2 里 Optional[str] 仍然是【必填】！")
    print("   → 必须写 = None 才变成可省略。")

print("\n" + "=" * 70)
print("【实验 4】前端多传 / 乱传字段会怎样")
print("=" * 70)

class Strict(BaseModel):
    name: str

print("多传 id=999 ->", Strict(name="x", id=999))
print("  ↑ 多余字段被【静默丢弃】，默认不报错")
print("  原因：默认 model_config extra='ignore'")

print("\n" + "=" * 70)
print("【实验 5】类型转换：哪些能转，哪些不能")
print("=" * 70)

class Typed(BaseModel):
    i: int
    f: float
    b: bool

print("i='123' ->", Typed(i="123", f="1.5", b="true").i, "（字符串数字 -> 自动转 int）")
try:
    Typed(i="abc", f=1, b=True)
except ValidationError as e:
    print("i='abc' -> ✗", e.errors()[0]["msg"])

print("\n" + "=" * 70)
print("【实验 6】自定义校验：min_length 挡不住纯空格")
print("=" * 70)

class Trimmed(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)

print('name="   " ->', Trimmed(name="   "), "  ← min_length 拦不住空格！")
print("  因为 min_length 数的是【字符个数】，'   ' 有 3 个字符")
print("  解法：加 field_validator 自己做 strip（下面演示）")


print("\n" + "=" * 70)
print("【实验 7】自定义校验：field_validator（真正的业务规则）")
print("=" * 70)

from pydantic import field_validator

class ProjectCreateV2(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)

    @field_validator("name")
    @classmethod
    def _normalize(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("项目名不能为空或纯空格")
        return v

print('"  雨夜  " ->', repr(ProjectCreateV2(name="  雨夜  ").name), "← 自动去空格")
try:
    ProjectCreateV2(name="   ")
except ValidationError as e:
    print('"   " -> ✗', e.errors()[0]["msg"])

print("\n" + "=" * 70)
print("【实验 8】Annotated 写法（Pydantic v2 推荐）")
print("=" * 70)
from typing import Annotated

class ProjectCreateV3(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=100, description="短剧项目名")]

print("与写法 A 完全等价，但默认值的表达更清晰:", ProjectCreateV3(name="x").model_dump())

print("\n" + "=" * 70)
print("【实验 9】禁止多余字段 extra='forbid'")
print("=" * 70)
from pydantic import ConfigDict

class StrictProject(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str

try:
    StrictProject(name="x", id=999)
except ValidationError as e:
    print("多传 id -> ✗", e.errors()[0]["type"], "|", e.errors()[0]["msg"])
