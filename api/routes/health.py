"""
Health check endpoints
"""
from fastapi import APIRouter
from datetime import datetime
import time

from api.models.responses import HealthResponse
from api.config import settings

router = APIRouter()

# Track startup time
startup_time = time.time()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint
    
    Returns API status and uptime information
    """
    return HealthResponse(
        status="healthy",
        version=settings.api_version,
        uptime_seconds=time.time() - startup_time,
        timestamp=datetime.now()
    )


@router.get("/health/ready")
async def readiness_check():
    """
    Readiness check for Kubernetes/Docker
    
    Returns 200 if API is ready to accept requests
    """
    # Add checks for dependencies here (DB, Redis, etc.)
    # For now, just return healthy
    return {"ready": True}


@router.get("/health/live")
async def liveness_check():
    """
    Liveness check for Kubernetes/Docker
    
    Returns 200 if API is alive
    """
    return {"alive": True}