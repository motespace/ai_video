# Pydantic 类型速查表（v2 实测版）

> 所有结论都在本机 `backend/.venv`（Pydantic v2.14 / FastAPI 0.162）跑过一遍。
> 配套实验：`backend/labs/01_pydantic_lab.py`、`backend/labs/02_types_lab.py`
> 跑法：`cd backend && .venv/bin/python labs/02_types_lab.py`

---

## 0. 总原则：可选 / 必填 的四象限

**两个独立开关**：

- 开关 A「值能不能是 null」→ 由类型里的 `Optional` / `X | None` 决定
- 开关 B「字段能不能不出现」→ 由**有没有默认值**决定

| 类型写法 | 不传 | 传 `null` | 传合法值 |
|---|---|---|---|
| `x: str` | ❌ missing | ❌ string_type | ✅ |
| `x: Optional[str]`（无默认值） | ❌ missing | ✅ | ✅ |
| `x: Optional[str] = None` | ✅ | ✅ | ✅ |
| `x: str = Field(None, ...)` | ✅ | ❌ string_type | ✅ |

⚠️ v2 变化：`Optional[str]` **不再**意味着可以不传。必须显式 `= None`。
⚠️ 反例：`str = Field(None, ...)` 会让"不传"能过、"传 null"报错，契约自相矛盾，别用。

---

## 1. 基础类型

### str
```python
name: str                                              # 必填
name: str = Field(..., min_length=1, max_length=100)   # 必填 + 长度
name: str = Field("未命名", max_length=100)             # 可选 + 默认值
name: Optional[str] = Field(None, max_length=100)      # 可选 + 可为 null
name: str = Field(..., pattern=r"^1[3-9]\d{9}$")        # 正则
```
约束：`min_length` / `max_length` / `pattern`
错误 type：`missing` / `string_type` / `string_too_short` / `string_too_long` / `string_pattern_mismatch`

### int / float
```python
i: int
f: float
i: int = Field(..., ge=0, le=100)      # 0 <= i <= 100
i: int = Field(..., gt=0, lt=10)       # 0 < i < 10
i: int = Field(..., multiple_of=5)     # 必须是 5 的倍数
```
| 输入 | `int` 字段 | `float` 字段 |
|---|---|---|
| `3` | 3 | 3.0 |
| `"3"` | 3（自动转） | 3.0 |
| `3.0` | 3（整数值的 float 可以） | 3.0 |
| `3.5` | ❌ `int_from_float` | 3.5 |
| `True` | 1（bool 是 int 的子类） | 1.0 |
| `"abc"` | ❌ `int_parsing` | ❌ `float_parsing` |

### bool —— 实际行为（实测，别信"字符串 false 变 true"的谣传）
| 输入 | 结果 |
|---|---|
| `True` / `False` | 原样 |
| `"true"` `"false"` `"True"` `"False"` | 正确转 ✅（v2 处理得很好） |
| `"yes"` `"no"` `"on"` `"off"` `"1"` `"0"` | ✅ 也能转 |
| `1` / `0` | ✅ |
| `2` / `""` / `None` / `"abc"` | ❌ `bool_parsing` / `bool_type` |

```python
flag: bool = False                    # 可选，默认 False
flag: Optional[bool] = None           # 可选 + 可为 null
```

---

## 2. 容器类型

### list
```python
items: list[str]                                   # 必填
items: list[str] = Field(default_factory=list)    # 可选，默认空列表
items: list[str] = Field(default_factory=list, min_length=1, max_length=100)
tags: Optional[list[str]] = None
```
约束：`min_length` / `max_length`（作用在**元素个数**上，不是字符串长度）
错误 type：`list_type` / `too_short` / `too_long`

💡 `default_factory=list` 的意义：告诉 Pydantic「每次创建实例都调用一次 `list()`」。
（实测：Pydantic 对 `= []` 也会做深拷贝，不会串数据；但 `default_factory` 是官方推荐写法，表达意图更清晰。）

### dict
```python
meta: dict[str, Any] = Field(default_factory=dict)
scores: dict[str, int] = Field(default_factory=dict)
```
- key 和 value 都能定类型：`dict[str, int]` 表示 key 必须是 str、value 必须是 int
- `dict[str, Any]` = 任意键值的 JSON 对象
- **多余的 key 不会被拦截**（dict 本身就是"任意键"），要严格控制得用 `TypedDict`（本次不展开）

### tuple / set
```python
pair: tuple[str, int]      # 长度固定，位置对应类型
nums: set[int]             # 自动去重
```

---

## 3. 枚举

```python
status: Literal["draft", "running", "done"]   # ✅ 类型就是 Literal
level: Literal[1, 2, 3] = 3                   # ✅ 带默认值
level: Literal[1, 2, 3]                       # ✅ 必填枚举

level: int = Literal[1, 2, 3]                 # ❌❌❌ 大坑！
```
☝️ 上面这行 **Literal 写在了【值】的位置，而不是【类型】的位置**：
`Literal[1,2,3]` 变成了「默认值」，类型仍然是 `int` → **校验完全失效，传 5 也能过**（实测确认）。
错误 type（写对时）：`literal_error`

---

## 4. 嵌套模型

```python
class Character(BaseModel):
    name: str
    age: Optional[int] = None

class Project(BaseModel):
    title: str
    characters: list[Character] = Field(default_factory=list)  # 列表套模型
    lead: Optional[Character] = None                            # 单个嵌套
```
- 嵌套对象内部也走完整校验（缺 `name` → `missing`）
- 嵌套里的 `age="20"` 依然会自动转成 `20`

---

## 5. 时间

```python
created_at: datetime
```
- `"2026-11-02T10:30:00"` ✅
- `"2026-11-02 10:30:00"` ✅（空格分隔也能解析）
- `"not a date"` ❌ `datetime_from_date_parsing`

---

## 6. ⚠️ 四个实测出来的坑

### 坑 1：`Field(strip_whitespace=True)` 在 v2 里**静默失效**
```python
title: str = Field(..., min_length=1, max_length=20, strip_whitespace=True)
# '  x  ' -> '  x  '   ❌ 根本没去空格（而且会打 deprecation 警告）
```
✅ 正确写法（二选一）：
```python
from typing import Annotated
from pydantic import StringConstraints

title: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=20)]
# '  x  ' -> 'x' ✅   '   ' -> ❌ string_too_short ✅
```
或用 `field_validator` 手动 strip（业务清洗首选，见坑 4）。

### 坑 2：`Literal` 写错位置 → 校验静默失效（见第 3 节）

### 坑 3：`bool` 来自 int 家族
Python 里 `True` 是 `int` 的子类，所以 `bool` 字段会接受 `1`/`0`。
如果你要严格只接受真正的布尔，用 `StrictBool` 或 `model_config = ConfigDict(strict=True)`。

### 坑 4：`min_length` 挡不住纯空格
`"   "` 有 3 个字符 → 通过。真正的"非空"要用 `field_validator` 手动 strip + 判空。

---

## 7. 写业务代码时的选择清单

| 场景 | 写法 |
|---|---|
| 必填字符串 | `x: str = Field(..., min_length=1, max_length=N)` |
| 可选字符串（补充说明） | `x: Optional[str] = Field(None, max_length=N)` |
| 可选字符串（有默认值） | `x: str = Field("未命名")` |
| 可选列表 | `x: list[str] = Field(default_factory=list)` |
| 可选字典 | `x: dict[str, Any] = Field(default_factory=dict)` |
| 枚举 | `x: Literal["a", "b"]` |
| 数值范围 | `x: int = Field(..., ge=0, le=100)` |
| 正则 | `x: str = Field(..., pattern=r"...")` |
| 需要清洗/自定义规则 | `@field_validator` + `raise ValueError("中文提示")` |
| 时间 | `x: datetime` |
