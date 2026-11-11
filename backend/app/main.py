from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db import create_pool, get_db
from app.routers import audit, questions, reports, reviews


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not settings.database_url:
        raise RuntimeError("DATABASE_URL is missing. Copy backend/.env.example to backend/.env.")
    if not settings.supabase_url:
        raise RuntimeError("SUPABASE_URL is missing. Configure backend/.env.")
    app.state.pool = await create_pool(settings.database_url)
    try:
        yield
    finally:
        await app.state.pool.close()


app = FastAPI(
    title="Acadza Report → Fix API",
    version="1.0.0",
    description="Authenticated API for question reports, faculty review and audited corrections.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Idempotency-Key"],
)

app.include_router(reports.router)
app.include_router(questions.router)
app.include_router(reviews.router)
app.include_router(audit.router)


@app.get("/api/health", tags=["Health"])
async def health(db=Depends(get_db)):
    await db.fetchval("select 1")
    return {"ok": True, "service": "acadza-api", "database": "connected"}


@app.get("/", include_in_schema=False)
async def root():
    return {"service": "Acadza API", "docs": "/docs"}
