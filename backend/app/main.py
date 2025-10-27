"""
Main FastAPI application
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import structlog

from app.core.config import settings
from app.core.database import create_tables
from app.core.exceptions import setup_exception_handlers
from app.core.redis import close_redis
from app.api.v1.api import api_router
from app.services.privacy_service import PrivacyService
from app.core.database import AsyncSessionLocal


# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting up Interview AI Assistant")
    
    # Create database tables
    await create_tables()
    logger.info("Database tables created")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Interview AI Assistant")
    await close_redis()
    logger.info("Redis connection closed")


# Create FastAPI app
app = FastAPI(
    title="Interview AI Assistant",
    description="Real-time interview assistance with AI-powered suggestions",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"] if settings.DEBUG else ["localhost", "127.0.0.1"]
)

# Setup exception handlers
setup_exception_handlers(app)

# Include API router
app.include_router(api_router, prefix="/api/v1")


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests"""
    start_time = time.time()
    
    # Process request
    response = await call_next(request)
    
    # Calculate processing time
    process_time = time.time() - start_time
    
    # Log request
    logger.info(
        "HTTP request",
        method=request.method,
        url=str(request.url),
        status_code=response.status_code,
        process_time=process_time,
        client_ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )
    
    return response


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": settings.APP_ENV
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Interview AI Assistant API",
        "version": "1.0.0",
        "docs": "/docs" if settings.DEBUG else "Documentation not available in production"
    }


# Privacy and GDPR endpoints
@app.post("/privacy/data-export/{user_id}")
async def export_user_data(user_id: int):
    """Export all user data for GDPR compliance"""
    async with AsyncSessionLocal() as db:
        privacy_service = PrivacyService(db)
        return await privacy_service.export_user_data(user_id)


@app.post("/privacy/data-deletion/{user_id}")
async def delete_user_data(user_id: int):
    """Delete all user data for GDPR compliance"""
    async with AsyncSessionLocal() as db:
        privacy_service = PrivacyService(db)
        return await privacy_service.delete_user_data(user_id)


@app.get("/privacy/data-summary/{user_id}")
async def get_user_data_summary(user_id: int):
    """Get summary of user data for privacy dashboard"""
    async with AsyncSessionLocal() as db:
        privacy_service = PrivacyService(db)
        return await privacy_service.get_user_data_summary(user_id)


@app.post("/privacy/cleanup")
async def cleanup_expired_data():
    """Manually trigger cleanup of expired data"""
    async with AsyncSessionLocal() as db:
        privacy_service = PrivacyService(db)
        return await privacy_service.auto_delete_expired_data()


if __name__ == "__main__":
    import time
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )
