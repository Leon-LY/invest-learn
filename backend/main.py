"""
FastAPI application entry point.
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1.router import api_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: init DB pool
    from app.core.database import engine, Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created")

    # Start scheduler
    try:
        from app.tasks.scheduler import start_scheduler
        start_scheduler()
        logger.info("Scheduler started successfully")
    except Exception as e:
        logger.error(f"Scheduler failed to start: {e}")

    yield

    # Shutdown
    from app.tasks.scheduler import shutdown_scheduler
    try:
        shutdown_scheduler()
    except Exception as e:
        logger.error(f"Scheduler shutdown error: {e}")
    from app.services.llm_service import llm_service
    try:
        await llm_service.close()
        logger.info("LLM service closed")
    except Exception as e:
        logger.error(f"LLM close error: {e}")
    await engine.dispose()


app = FastAPI(
    title="远见 API",
    description="洞察趋势，智选未来 — 基金投资智能分析平台 · by Leon",
    version="0.3.0",
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
