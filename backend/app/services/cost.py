from .. import store


def get_cost_summary() -> dict:
    """成本汇总。

    统计口径（只对 succeeded 的镜头算均价）属于【业务规则】，
    应该在这一层；store 只负责提供原始数据。
    第 2 课会把这个函数从 store 里彻底搬出来。
    """
    return store.cost_summary()
