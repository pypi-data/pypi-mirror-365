"""
FastAPI Server for ISA Model Serving

Main FastAPI application that serves model inference endpoints
"""

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
import time
import logging
import os
from typing import Dict, Any, Optional

from .routes import health, unified, deployments, logs, analytics, settings, evaluations
from .middleware.request_logger import RequestLoggerMiddleware
from .middleware.security import setup_security_middleware, check_redis_health
from .startup import run_startup_initialization

logger = logging.getLogger(__name__)

def configure_logging():
    """Configure logging based on environment variables"""
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    verbose_logging = os.getenv('VERBOSE_LOGGING', 'false').lower() == 'true'
    
    # Set log level
    level = getattr(logging, log_level, logging.INFO)
    
    # Configure format
    if verbose_logging:
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    else:
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Configure root logger
    logging.basicConfig(
        level=level,
        format=log_format,
        datefmt='%Y-%m-%d %H:%M:%S',
        force=True  # Override existing configuration
    )
    
    # Set uvicorn logger level to match
    uvicorn_logger = logging.getLogger("uvicorn")
    uvicorn_logger.setLevel(level)
    
    # Set app logger level
    app_logger = logging.getLogger("isa_model")
    app_logger.setLevel(level)
    
    logger.info(f"Logging configured - Level: {log_level}, Verbose: {verbose_logging}")

def create_app(config: Dict[str, Any] = None) -> FastAPI:
    """
    Create and configure FastAPI application
    
    Args:
        config: Optional configuration dictionary
        
    Returns:
        Configured FastAPI application
    """
    # Configure logging first
    configure_logging()
    
    app = FastAPI(
        title="ISA Model Serving API",
        description="High-performance model inference API",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # Setup comprehensive security middleware
    # This includes CORS, rate limiting, security headers, request validation
    setup_security_middleware(app)
    
    # Add custom middleware
    app.add_middleware(RequestLoggerMiddleware)
    
    # Exception handlers
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Global exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "detail": str(exc) if config and config.get("debug") else "An error occurred"
            }
        )
    
    # Include routers
    app.include_router(health.router, prefix="/health", tags=["health"])
    
    # MAIN UNIFIED API - Single endpoint for all AI services
    app.include_router(unified.router, prefix="/api/v1", tags=["unified-api"])
    
    # DEPLOYMENTS API - Model deployment management
    app.include_router(deployments.router, prefix="/api/v1/deployments", tags=["deployments"])
    
    # LOGS API - Log management and streaming
    app.include_router(logs.router, prefix="/api/v1/logs", tags=["logs"])
    
    # ANALYTICS API - Usage analytics and reporting
    app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"])
    
    # SETTINGS API - Configuration and API key management
    app.include_router(settings.router, prefix="/api/v1/settings", tags=["settings"])
    
    # EVALUATIONS API - Model evaluation and benchmarking
    app.include_router(evaluations.router, prefix="/api/v1/evaluations", tags=["evaluations"])
    
    # Mount static files
    static_path = os.path.join(os.path.dirname(__file__), "../static")
    if os.path.exists(static_path):
        app.mount("/static", StaticFiles(directory=static_path), name="static")
        
        # Serve management dashboard at /admin
        @app.get("/admin")
        async def admin_dashboard():
            from fastapi.responses import FileResponse
            index_path = os.path.join(static_path, "index.html")
            if os.path.exists(index_path):
                return FileResponse(index_path)
            return {"error": "Management dashboard not found"}
    
    # Root endpoint
    @app.get("/")
    async def root():
        return {
            "service": "isa-model-serving",
            "version": "1.0.0",
            "status": "running",
            "timestamp": time.time(),
            "admin_url": "/admin"
        }
    
    # Add startup event handler
    @app.on_event("startup")
    async def startup_event():
        logger.info("🚀 Starting application startup initialization...")
        try:
            await run_startup_initialization()
            logger.info("✅ Application startup completed successfully")
        except Exception as e:
            logger.error(f"❌ Application startup failed: {e}")
            # Don't raise - let the app start anyway
    
    return app

# Create default app instance
app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)