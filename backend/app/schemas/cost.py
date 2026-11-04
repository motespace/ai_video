from pydantic import BaseModel


class CostSummary(BaseModel):
    """成本面板。

    面试可讲：这是 demo 里最有"业务感"的部分——
    老板不关心你生成了多少个镜头，关心的是这一集花了多少钱。
    """
    total_cost: float
    total_shots: int
    succeeded: int
    failed: int
    pending_or_running: int
    avg_cost_per_succeeded_shot: float
    attempts_total: int