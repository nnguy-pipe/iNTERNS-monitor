"""Main FastAPI application for AHMS Backend."""

import logging
import os
from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text

from src.store.sqlite import get_db, init_db
from src.api.routes import router as api_router

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AHMS Backend",
    description="Agentic Health Monitoring System Backend",
    version="0.1.0",
    openapi_url="/api/openapi.json",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router)


@app.on_event("startup")
def startup_event():
    """Initialize database on startup."""
    logger.info("Starting AHMS Backend...")
    logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    logger.info("Initializing database...")
    init_db()
    logger.info("Database initialized")
    logger.info("AHMS Backend ready")


@app.get("/health", tags=["health"])
def health_check(db: Session = Depends(get_db)) -> JSONResponse:
    """
    Health check endpoint.
    
    Returns:
        - status: "ok" if healthy, "degraded" if issues detected
        - database: "ok" if database connection is available
        - version: backend version
    """
    db_status = "ok"
    try:
        # Quick database connectivity check
        db.execute(text("SELECT 1"))
    except Exception as e:
        logger.warning(f"Database health check failed: {e}")
        db_status = "degraded"

    return JSONResponse(
        status_code=200 if db_status == "ok" else 503,
        content={
            "status": "ok" if db_status == "ok" else "degraded",
            "database": db_status,
            "version": "0.1.0",
            "environment": os.getenv("ENVIRONMENT", "development"),
        },
    )


@app.get("/", tags=["root"])
def root() -> dict:
    """Root endpoint."""
    return {
        "message": "Welcome to AHMS Backend",
        "docs": "/api/docs",
        "health": "/health",
        "version": "0.1.0",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
