from fastapi import APIRouter
from .endpoints import scripts, versions, detections

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(scripts.router)
api_router.include_router(versions.router, prefix="/scripts", tags=["versions"])
api_router.include_router(detections.router, prefix="/scripts", tags=["detections"])
