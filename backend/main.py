from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

app = FastAPI(title="Inter Mock API", openapi_url="/api/v1/openapi.json")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DEMO_TOKEN = "demo-token"

class MagicLinkIn(BaseModel):
    email: str

@app.get("/api/v1/health")
def health():
    return {"status": "ok"}

@app.post("/api/v1/auth/magic-link")
def send_magic_link(body: MagicLinkIn):
    return {"sent": True, "message": f"Magic link sent to {body.email}"}

@app.post("/api/v1/auth/verify")
def verify(token: Optional[str] = None):
    tok = token or DEMO_TOKEN
    return {"access_token": tok, "token_type": "bearer"}

@app.get("/api/v1/auth/me")
def me(request: Request):
    auth = request.headers.get("authorization", "")
    if not auth.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    return {
        "id": 1,
        "email": "demo@example.com",
        "auth_provider": "magic",
        "is_verified": True,
        "auto_delete_enabled": False,
        "retention_hours": 24,
        "created_at": "2025-01-01T00:00:00Z",
    }

@app.post("/api/v1/auth/logout")
def logout():
    return {"ok": True}

# In-memory stubs
_resumes: List[Dict[str, Any]] = []
_resume_id = 0

@app.post("/api/v1/resumes/")
async def upload_resume(file: UploadFile = File(...)):
    global _resume_id
    _resume_id += 1
    _resumes.append({"id": _resume_id, "filename": file.filename})
    return {"id": _resume_id, "filename": file.filename}

@app.get("/api/v1/resumes/")
def list_resumes():
    return _resumes

@app.get("/api/v1/resumes/{rid}")
def get_resume(rid: int):
    for r in _resumes:
        if r["id"] == rid:
            return r
    raise HTTPException(status_code=404, detail="Not found")

@app.delete("/api/v1/resumes/{rid}")
def delete_resume(rid: int):
    global _resumes
    _resumes = [r for r in _resumes if r["id"] != rid]
    return {"deleted": True}

_sessions: Dict[int, Dict[str, Any]] = {}
_session_id = 0

@app.post("/api/v1/sessions/")
def create_session(payload: Dict[str, Any]):
    global _session_id
    _session_id += 1
    _sessions[_session_id] = {"id": _session_id, "status": "active", **payload}
    return _sessions[_session_id]

@app.get("/api/v1/sessions/")
def list_sessions(limit: int = 50, offset: int = 0):
    items = list(_sessions.values())[offset : offset + limit]
    return {"items": items, "total": len(_sessions)}

@app.get("/api/v1/sessions/{sid}")
def get_session(sid: int):
    s = _sessions.get(sid)
    if not s:
        raise HTTPException(status_code=404, detail="Not found")
    return s

@app.patch("/api/v1/sessions/{sid}/end")
def end_session(sid: int):
    s = _sessions.get(sid)
    if not s:
        raise HTTPException(status_code=404, detail="Not found")
    s["status"] = "ended"
    return s

@app.delete("/api/v1/sessions/{sid}")
def delete_session(sid: int):
    _sessions.pop(sid, None)
    return {"deleted": True}

@app.get("/api/v1/asr/health")
def asr_health():
    return {"status": "ok"}

@app.post("/api/v1/asr/transcribe/{session_id}")
async def transcribe(session_id: int, request: Request):
    _ = await request.body()
    return {"session_id": session_id, "text": "This is a fake transcript."}

@app.post("/api/v1/llm/suggestions")
def generate_suggestion(payload: Dict[str, Any]):
    return {"suggestion": "Try highlighting your recent project impact more clearly."}

@app.get("/api/v1/llm/suggestions/{session_id}")
def get_suggestions(session_id: int, limit: int = 20, offset: int = 0):
    items = [
        {"id": 1, "text": "Keep answers concise."},
        {"id": 2, "text": "Use concrete metrics where possible."},
    ]
    return {"items": items[offset: offset + limit], "total": len(items)}

@app.patch("/api/v1/llm/suggestions/{suggestion_id}/feedback")
def update_feedback(suggestion_id: int, payload: Dict[str, Any]):
    return {"id": suggestion_id, "updated": True, "feedback": payload}

@app.post("/api/v1/llm/chat")
def chat(payload: Dict[str, Any]):
    msg = payload.get("message", "")
    sid = payload.get("session_id")
    return {"reply": f"(mock) You said: {msg}", "session_id": sid}
