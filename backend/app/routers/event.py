import asyncio
import json

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from .. import services

router = APIRouter(prefix="/api", tags=["实时"])


@router.get("/events")
async def events():
    """服务端推送进度。

    为什么用 SSE 而不是 WebSocket？
    SSE 是单向的、走 HTTP、自带断线重连，
    而我们只需要服务端→前端单向推，WebSocket 是杀鸡用牛刀。
    真实项目里如果要做"用户实时编辑同一个剧本"才需要 WebSocket。

    用法（前端）：
        const es = new EventSource('/api/events')
        es.onmessage = e => { const shots = JSON.parse(e.data); ... }
    """

    async def stream():
        while True:
            payload = {
                # 注意：这里走 service，不直接碰 store（分层禁令）
                "shots": services.list_shots(),
                "cost": services.get_cost_summary(),
            }
            # SSE 协议格式：data:<json>\n\n
            yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"
            await asyncio.sleep(1.0)

    return StreamingResponse(
        stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # 关掉 nginx 缓冲，否则 SSE 会被攒着不发
        },
    )
