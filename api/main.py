"""
FastAPI REST API pentru Shopping Bot.

Pornire:
    uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

Documentație interactivă:
    http://localhost:8000/docs   (Swagger UI)
    http://localhost:8000/redoc  (ReDoc)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import groups, personal, users
from database.db import init_db

app = FastAPI(
    title="Shopping Bot API",
    description="REST API pentru botul de liste de cumpărături Telegram",
    version="1.0.0",
)

# ---------------------------------------------------------------------------
# CORS — permite orice origine în dev; restricționează în producție
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # schimbă cu domeniul tău în producție
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Inițializare DB la pornire
# ---------------------------------------------------------------------------

@app.on_event("startup")
async def startup():
    await init_db()


# ---------------------------------------------------------------------------
# Routere
# ---------------------------------------------------------------------------

app.include_router(users.router,    prefix="/api/users",    tags=["Utilizatori"])
app.include_router(personal.router, prefix="/api/personal", tags=["Lista personală"])
app.include_router(groups.router,   prefix="/api/groups",   tags=["Grupuri"])


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

@app.get("/health", tags=["System"])
async def health():
    return {"status": "ok"}
