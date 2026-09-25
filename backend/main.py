"""
HireScope Backend — main.py
Run from HireScope root: python -m uvicorn backend.main:app --reload --port 8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes import auth, interview, resume

app = FastAPI(
    title="HireScope API",
    description="AI-powered interview simulation platform",
    version="1.0.0",
)

# ── CORS must be before routers ───────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────
app.include_router(auth.router,      prefix="/api/auth",      tags=["Auth"])
app.include_router(interview.router, prefix="/api/interview", tags=["Interview"])
app.include_router(resume.router,    prefix="/api/resume",    tags=["Resume"])

@app.get("/")
def root():
    return {"message": "HireScope Backend Running"}