import os
from pathlib import Path
from typing import Any
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent
app = FastAPI(title="StudyStack AI", version="1.1.0")
app.mount("/assets", StaticFiles(directory=BASE_DIR / "assets"), name="assets")

class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    tasks: list[dict[str, Any]] = Field(default_factory=list, max_length=100)

@app.get("/")
def home():
    return FileResponse(BASE_DIR / "index.html")

@app.get("/api/health")
def health():
    configured = bool(os.getenv("GEMINI_API_KEY"))
    return {"status": "ok", "ai_configured": configured,
            "provider": "Google Gemini" if configured else "local-demo"}

@app.post("/api/chat")
def chat(payload: ChatRequest):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {"mode": "demo", "reply": "Real AI is not configured. Set GEMINI_API_KEY and restart the backend."}
    try:
        from google import genai
        model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        client = genai.Client(api_key=api_key)
        prompt = (
            "You are StudyStack AI, a friendly study coach for college students. "
            "Use simple English. Explain DSA concepts like arrays, stacks, queues, "
            "priority queues, searching and sorting. For study plans, use the task list. "
            "Do not claim to have changed tasks; the website handles task actions.\n\n"
            f"Student task list (JSON): {payload.tasks[:100]}\n\n"
            f"Student question: {payload.message}"
        )
        response = client.models.generate_content(model=model, contents=prompt)
        answer = (getattr(response, "text", None) or "").strip()
        return {"mode": "live", "reply": answer or "I couldn't generate a response. Please try again."}
    except Exception as exc:
        print(f"Gemini request failed: {type(exc).__name__}: {exc}")
        raise HTTPException(status_code=502, detail="Gemini API request failed. Check the server log, API key, model access and free-tier quota.")

@app.get("/api")
def api_root():
    return {"name": "StudyStack AI API", "docs": "/docs", "health": "/api/health"}
