"""
Service 层统一出口。

为什么这里要显式写出函数名？
- 空 __init__.py 时，`from .. import services` 只能拿到【包】，
  拿不到包里的函数 —— 会报 "module has no attribute 'create_project'"。
- 写 `from .project import ...` 之后，`services.create_project` 才存在。

注意：这里必须列出【具体函数名】，不要写 `from .project import *`（星号导入不可读，
且会把内部函数也暴露出去）。
"""
from .project import create_project, list_projects
from .shot import (
    create_shots,
    list_shots,
    get_shot_detail,
    retry_shot,
    select_candidate,
)
from .cost import get_cost_summary
