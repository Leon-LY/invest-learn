"""
FastAPI application entry point.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: init DB pool, Redis, scheduler
    from app.core.database import engine, Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Start scheduler (skipped if no scheduler configured)
    try:
        from app.tasks.scheduler import start_scheduler
        start_scheduler()
    except Exception:
        pass

    yield

    # Shutdown: dispose engine, close Redis
    from app.tasks.scheduler import shutdown_scheduler
    try:
        shutdown_scheduler()
    except Exception:
        pass
    await engine.dispose()


app = FastAPI(
    title="基智学 API",
    description="基金投资学习平台 — by Leon",
    version="0.2.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/health")
async def health_check():
    return {"status": "ok", "version": "0.1.0"}
