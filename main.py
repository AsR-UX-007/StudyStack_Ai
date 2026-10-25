
import os
import time
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="StudyStack AI", version="1.2.0")

app.mount(
    "/assets",
    StaticFiles(directory=BASE_DIR / "assets"),
    name="assets"
)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    tasks: list[dict[str, Any]] = Field(
        default_factory=list,
        max_length=100
    )


@app.get("/")
def home():
    return FileResponse(BASE_DIR / "index.html")


@app.get("/api/health")
def health():
    configured = bool(os.getenv("GEMINI_API_KEY"))

    return {
        "status": "ok",
        "ai_configured": configured,
        "provider": "Google Gemini" if configured else "local-demo",
        "model": os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
    }


@app.get("/api/config")
def public_config():
    return {
        "supabase_url": os.getenv("SUPABASE_URL", ""),
        "supabase_anon_key": os.getenv("SUPABASE_ANON_KEY", "")
    }




import time
import random


def generate_with_retry(client, model, prompt):
    for attempt in range(2):
        try:
            return client.models.generate_content(
                model=model,
                contents=prompt,
            )

        except Exception as exc:
            error_text = str(exc).upper()

            temporary = any(
                code in error_text
                for code in (
                    "503",
                    "UNAVAILABLE",
                    "429",
                    "RESOURCE_EXHAUSTED",
                    "500",
                    "502",
                    "504",
                )
            )

            if not temporary or attempt == 1:
                raise

            delay = 1 + random.uniform(0, 0.5)
            print(f"Temporary Gemini error. Retrying once.")
            time.sleep(delay)


@app.post("/api/chat")
def chat(payload: ChatRequest):
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return {
            "mode": "demo",
            "reply": (
                "Real AI is not configured. "
                "Set GEMINI_API_KEY in Render."
            )
        }

    try:
        from google import genai

        model = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
        client = genai.Client(api_key=api_key)

        prompt = (
            "You are StudyStack AI, a friendly study coach "
            "for college students. Use simple English. "
            "Explain DSA concepts such as arrays, stacks, queues, "
            "priority queues, searching and sorting. "
            "For study plans, consider the student's task list. "
            "Do not claim to have changed tasks; the website "
            "handles task actions.\n\n"
            f"Student task list (JSON): {payload.tasks[:100]}\n\n"
            f"Student question: {payload.message}"
        )

        from google.genai import types

        response = generate_with_retry(
            client,
            model,
            prompt
        )


        answer = (getattr(response, "text", None) or "").strip()

        if not answer:
            raise RuntimeError(
                "Gemini returned an empty response."
            )

        return {
            "mode": "live",
            "reply": answer
        }

    except Exception as exc:
        print(
            f"Gemini request failed: "
            f"{type(exc).__name__}: {exc}"
        )

        error_text = str(exc).upper()

        if "429" in error_text or "RESOURCE_EXHAUSTED" in error_text:
            detail = (
                "Gemini rate limit or quota reached. "
                "Check your Gemini API quota and try again later."
            )
        elif "503" in error_text or "UNAVAILABLE" in error_text:
            detail = (
                "Gemini is temporarily unavailable. "
                "Please try again shortly."
            )
        elif "404" in error_text or "NOT_FOUND" in error_text:
            detail = (
                "The configured Gemini model was not found or "
                "is unavailable to this API key. Check GEMINI_MODEL."
            )
        elif "401" in error_text or "403" in error_text or "PERMISSION_DENIED" in error_text:
            detail = (
                "Gemini rejected the API key or access permission. "
                "Check GEMINI_API_KEY and model access in Google AI Studio."
            )
        else:
            detail = (
                "Gemini could not complete the request. "
                "Check the Render logs for details."
            )

        raise HTTPException(status_code=502, detail=detail)


@app.get("/api")
def api_root():
    return {
        "name": "StudyStack AI API",
        "docs": "/docs",
        "health": "/api/health"
    }
