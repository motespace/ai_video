"""
生成服务抽象层。

这是整个 demo 最重要的一个设计决策，也是你面试时要重点讲的地方：

    把"生成"抽象成一个接口，mock 和真实 API 都能替换。

为什么重要（面试话术）：
1. 本地没有 GPU / 没有 API key 也能把整条链路跑通、能演示
2. 真实供应商（可灵、即梦、Replicate…）随时可以切换，业务代码一行不改
3. 这正是他们公司现在一定在做的事——模型供应商换了好几轮，
   但剧本→分镜→生成→挑选→成片的编排层是稳定的。
"""
import asyncio
import random
from typing import Optional

from . import config

# 真实 API 接入时，在这里读 key
# os.environ.get("KLING_API_KEY")
API_KEY: Optional[str] = None


async def _mock_generate(prompt: str, shot_id: int, attempt: int) -> dict:
    """模拟一次生成调用。

    关键点：这里用 asyncio.sleep 而不是 time.sleep。
    因为 sleep 期间要把 CPU 让给别的请求，
    这就是 async 的意义（面试可以主动讲这个对比）。
    """
    delay = random.uniform(config.MOCK_MIN_SECONDS, config.MOCK_MAX_SECONDS)
    await asyncio.sleep(delay)

    # 生成一个占位"视频"（实际这里会返回真实文件的 URL）
    # 生成一个占位"分镜图"（真实场景这里返回生成视频的 URL）
    cands = []
    for i in range(config.CANDIDATES_PER_SHOT):
        seed = random.randint(1, 10_000_000)
        filename = f"shot{shot_id}_a{attempt}_c{i}.svg"
        (config.MEDIA_DIR / filename).write_text(
            _placeholder_svg(prompt, seed, attempt), encoding="utf-8"
        )
        cands.append({"url": f"/media/{filename}", "seed": seed})

    return {
        "candidates": cands,
        "duration_seconds": round(delay, 2),
    }


def _placeholder_svg(prompt: str, seed: int, attempt: int) -> str:
    """生成一张占位分镜图，让前端能真实渲染出候选对比。

    面试可讲：这是"mock 层"的一部分。真实实现里这里换成
    生成服务的产物 URL，前端代码完全不用动——
    这就是为什么要把生成抽象成接口。
    """
    from html import escape

    text = escape(prompt[:16])
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="640" height="360" viewBox="0 0 640 360">
  <defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0%" stop-color="#312e81"/><stop offset="100%" stop-color="#1f2937"/>
  </linearGradient></defs>
  <rect width="640" height="360" fill="url(#g)"/>
  <circle cx="320" cy="150" r="56" fill="#818cf8" opacity="0.85"/>
  <text x="320" y="248" fill="#f3f4f6" font-size="26" text-anchor="middle"
        font-family="-apple-system, 'PingFang SC', sans-serif">{text}</text>
  <text x="320" y="286" fill="#9ca3af" font-size="16" text-anchor="middle"
        font-family="-apple-system, 'PingFang SC', sans-serif">seed {seed} / attempt {attempt}</text>
</svg>"""


async def generate(prompt: str, shot_id: int, attempt: int) -> dict:
    """统一入口。返回 {"candidates": [...], "duration_seconds": float}

    接入真实模型的步骤（写在 README 里）：
    1. 在这里写一个 _kling_generate / _jimeng_generate
    2. 提交任务 → 拿到 task_id → 轮询或等 webhook
    3. 拿到视频 URL 后塞进 candidates 列表返回
    业务代码（tasks.py / main.py）完全不用改。
    """
    return await _mock_generate(prompt, shot_id, attempt)


def compute_cost(duration_seconds: float, candidates: int) -> float:
    """成本核算。

    面试可讲（这条是我的核心判断之一）：
    真正决定单分钟成本的不是推理单价，而是"抽卡率"——
    生成 10 次采纳 1 次，单价降一半而抽卡率翻倍，总成本反而上升。
    所以成本要精确到"每一次生成调用"，而不是只算"每分钟成片"。
    """
    return round(
        config.PRICE_PER_GENERATION * candidates
        + config.PRICE_PER_SECOND * duration_seconds * candidates,
        4,
    )
