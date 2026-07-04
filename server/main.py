"""FastAPI 服务端，通过 WebSocket 推送实时仿真。"""

from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from server.simulation import SimulationEngine

app = FastAPI(title="III 数字智能体演示")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = SimulationEngine()
FRONTEND_DIST = Path(__file__).resolve().parent.parent / "frontend" / "dist"


@app.get("/api/state")
def get_state():
    return engine.get_snapshot()


@app.post("/api/reset")
def reset():
    engine.stop()
    engine.env = engine.env.__class__()
    engine.reset_episode()
    return engine.get_snapshot()


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()

    async def send_snapshot(_: dict | None = None):
        await ws.send_json(engine.get_snapshot())

    engine.subscribe(send_snapshot)
    await send_snapshot()

    try:
        while True:
            raw = await ws.receive_text()
            msg = json.loads(raw)
            cmd = msg.get("cmd")

            if cmd == "start":
                engine.start()
            elif cmd == "stop":
                engine.stop()
            elif cmd == "reset":
                engine.stop()
                engine.env = engine.env.__class__()
                engine.reset_episode()
            elif cmd == "hint":
                engine.set_human_hint(msg.get("direction"))
            elif cmd == "clear_hint":
                engine.set_human_hint(None)
            elif cmd == "swap_agent":
                engine.swap_agent(msg.get("name", "q_learning"))
            elif cmd == "speed":
                engine.set_speed(int(msg.get("tick_ms", 300)))
            elif cmd == "step":
                if not engine.state.running:
                    await engine._tick()
                else:
                    await send_snapshot()

            await send_snapshot()
    except WebSocketDisconnect:
        pass
    finally:
        if send_snapshot in engine._listeners:
            engine._listeners.remove(send_snapshot)


# 构建后的前端可用时挂载静态资源
if FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="assets")

    @app.get("/{full_path:path}")
    async def spa(full_path: str):
        index = FRONTEND_DIST / "index.html"
        if full_path.startswith("api") or full_path.startswith("ws"):
            return {"error": "not found"}
        return FileResponse(index)
