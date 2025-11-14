from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import sys
from uuid import uuid4
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from prometheus_fastapi_instrumentator import Instrumentator
import redis.asyncio as redis

from .core.config import settings
from .api.router import api_router
from .db.base import get_db

logger.remove()
logger.add(sys.stderr, level=settings.log_level)

app = FastAPI(
    title=settings.app_name, version=settings.app_version, debug=settings.debug
)


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid4())
    with logger.contextualize(request_id=request_id):
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

app.include_router(api_router)

Instrumentator().instrument(app).expose(app)


@app.get("/health")
async def health(db: AsyncSession = Depends(get_db)):
    checks = {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "database": "unknown",
        "redis": "unknown",
    }

    try:
        await db.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        checks["database"] = "error"
        checks["status"] = "unhealthy"

    try:
        redis_settings = settings.get_arq_settings()
        redis_client = redis.Redis(
            host=redis_settings.host,
            port=redis_settings.port,
            db=redis_settings.database,
        )
        await redis_client.ping()
        await redis_client.close()
        checks["redis"] = "ok"
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        checks["redis"] = "error"
        checks["status"] = "unhealthy"

    if checks["status"] == "unhealthy":
        raise HTTPException(status_code=503, detail=checks)

    return checks


@app.get("/")
async def root():
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
    }
