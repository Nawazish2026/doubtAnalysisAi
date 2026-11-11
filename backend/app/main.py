from contextlib import asynccontextmanager

import asyncpg
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db import create_pool
from app.routers import audit, questions, reports, reviews


@asynccontextmanager
async def lifespan(app: FastAPI):
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
async def health():
    return {"ok": True, "service": "ac adza-api"}


@app.get("/", include_in_schema=False)
async def root():
    return {"service": "Acadza API", "docs": "/docs"}
