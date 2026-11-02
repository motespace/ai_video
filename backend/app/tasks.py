"""
任务层：状态机 + 重试 + 成本核算。

这就是整条生产线的"工位"。对应现实里的一条短剧产线：
镜头排队 → 生成 → 失败重试 → 人工挑选 → 进入下一环节。

面试可讲：AI 内容生产和传统影视生产的最大结构差异是
"单点操作会失败"，所以系统必须内建"失败"这个状态，
并且让失败可观测、可重试、可核算成本，而不是崩在那里。
"""
import asyncio
import random
from typing import Optional

from . import config, generator, store


async def run_shot(shot_id: int) -> None:
    """执行一个镜头的生成任务。

    对应前端概念：这是一个 async job。
    """
    shot = store.get_shot(shot_id)
    if not shot:
        return

    attempt = shot["attempts"] + 1
    store.update_shot(shot_id, status="running", attempts=attempt, error=None)

    try:
        result = await generator.generate(shot["prompt"], shot_id, attempt)

        # 模拟真实世界：有一定概率生成失败，用来演示重试与失败态
        if attempt < config.MAX_ATTEMPTS and random.random() < 0.25:
            raise RuntimeError("生成超时：模型推理队列拥堵（模拟）")

        cand_ids = store.add_candidates(shot_id, result["candidates"])
        cost = generator.compute_cost(result["duration_seconds"], len(cand_ids))

        store.update_shot(
            shot_id,
            status="succeeded",
            duration_seconds=result["duration_seconds"],
            cost=cost,
            error=None,
            selected_candidate_id=cand_ids[0] if cand_ids else None,
        )
        # 默认选中第一个候选，并落库
        if cand_ids:
            store.select_candidate(shot_id, cand_ids[0])

    except Exception as e:  # noqa: BLE001
        store.update_shot(shot_id, status="failed", error=str(e))


async def run_shots(shot_ids: list[int], concurrency: int = 3) -> None:
    """批量跑。

    面试可讲：真实系统里这里不是 asyncio，而是 Celery/RQ + GPU worker 池，
    因为真正的瓶颈是 GPU 而不是 CPU；并发度受限于显存，不是受限于核数。
    """
    sem = asyncio.Semaphore(concurrency)

    async def guarded(sid: int) -> None:
        async with sem:
            await run_shot(sid)

    await asyncio.gather(*(guarded(s) for s in shot_ids))
