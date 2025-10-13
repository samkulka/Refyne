"""
Refyne Data Cleanser API
FastAPI application entry point
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time
import logging

from api.config import settings
from api.routes import upload, clean, profile, health, customers

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Track API startup time
startup_time = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events for the API"""
    # Startup
    logger.info("🚀 Refyne API starting up...")
    logger.info(f"📁 Upload directory: {settings.upload_dir}")
    logger.info(f"📁 Output directory: {settings.output_dir}")
    
    yield
    
    # Shutdown
    logger.info("👋 Refyne API shutting down...")


# Create FastAPI app
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description=settings.api_description,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Custom middleware to track request time
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "Internal server error",
            "details": str(exc) if settings.api_reload else None
        }
    )


# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(upload.router, prefix="/api/v1", tags=["Upload"])
app.include_router(clean.router, prefix="/api/v1", tags=["Clean"])
app.include_router(profile.router, prefix="/api/v1", tags=["Profile"])
app.include_router(customers.router, prefix="/api/v1", tags=["Customers"])


# Root endpoint
@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "name": settings.api_title,
        "version": settings.api_version,
        "status": "running",
        "docs": "/docs",
        "health": "/api/v1/health"
    }


# For running with uvicorn
if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting Refyne API on {settings.api_host}:{settings.api_port}")
    
    uvicorn.run(
        "api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload,
        log_level="info"
    )