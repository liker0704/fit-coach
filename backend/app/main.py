"""Main FastAPI application."""

import asyncio
import logging
import signal
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.security_middleware import SecurityHeadersMiddleware
from app.core.rate_limit import limiter, rate_limit_exceeded_handler
from app.core.logging_config import setup_logging, get_logger
from app.core.request_id import RequestIDMiddleware
from app.core.error_tracking import (
    http_exception_handler,
    general_exception_handler,
)
from app.api.v1.agents import router as agents_router
from app.api.v1.ai import router as ai_router
from app.api.v1.auth import router as auth_router
from app.api.v1.days import router as days_router
from app.api.v1.exercises import router as exercises_router
from app.api.v1.goals import router as goals_router
from app.api.v1.meals import router as meals_router
from app.api.v1.meal_plans import router as meal_plans_router
from app.api.v1.moods import router as moods_router
from app.api.v1.notes import router as notes_router
from app.api.v1.training_programs import router as training_programs_router
from app.api.v1.notifications import router as notifications_router
from app.api.v1.sleep import router as sleep_router
from app.api.v1.users import router as users_router
from app.api.v1.voice import router as voice_router
from app.api.v1.water import router as water_router
from app.api.v1.health import router as health_router
from app.config import settings

# Setup centralized logging
setup_logging(
    log_level=settings.__dict__.get("LOG_LEVEL", "INFO"),
    log_dir="logs",
    app_name="fitcoach",
)

logger = get_logger(__name__)

# Global flag for graceful shutdown
shutdown_event = asyncio.Event()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager.

    Handles startup and shutdown events:
    - Startup: Log application start, setup signal handlers
    - Shutdown: Graceful shutdown with connection cleanup
    """
    # Startup
    logger.info(
        "Application starting",
        extra={
            "project": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "environment": settings.__dict__.get("ENVIRONMENT", "development"),
        },
    )

    # Setup signal handlers for graceful shutdown
    def handle_shutdown_signal(signum, frame):
        """Handle shutdown signals."""
        logger.info(
            "Shutdown signal received",
            extra={"signal": signal.Signals(signum).name},
        )
        shutdown_event.set()

    signal.signal(signal.SIGTERM, handle_shutdown_signal)
    signal.signal(signal.SIGINT, handle_shutdown_signal)

    yield

    # Shutdown
    logger.info("Application shutting down")

    # Wait for in-flight requests (max 5 seconds)
    try:
        await asyncio.wait_for(shutdown_event.wait(), timeout=5.0)
    except asyncio.TimeoutError:
        logger.warning("Shutdown timeout reached, forcing shutdown")

    # Cleanup connections
    try:
        from app.core.database import engine

        engine.dispose()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error closing database connections: {e}")

    logger.info("Application shutdown complete")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Personal Health Tracker with AI Coach",
    version=settings.VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    lifespan=lifespan,
)

# Exception handlers
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Rate limiting configuration
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# Request ID Middleware (apply early to track all requests)
app.add_middleware(RequestIDMiddleware)

# Security Headers Middleware
app.add_middleware(SecurityHeadersMiddleware)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=[
        "Content-Type",
        "Authorization",
        "Accept",
        "Origin",
        "User-Agent",
        "DNT",
        "Cache-Control",
        "X-Requested-With",
    ],
    expose_headers=["Content-Length", "Content-Type"],
    max_age=600,  # 10 minutes
)

# Include routers
app.include_router(
    auth_router,
    prefix=f"{settings.API_V1_PREFIX}/auth",
    tags=["authentication"],
)

app.include_router(
    days_router,
    prefix=settings.API_V1_PREFIX,
    tags=["days"],
)

app.include_router(
    exercises_router,
    prefix=settings.API_V1_PREFIX,
    tags=["exercises"],
)

app.include_router(
    goals_router,
    prefix=settings.API_V1_PREFIX,
    tags=["goals"],
)

app.include_router(
    meals_router,
    prefix=settings.API_V1_PREFIX,
    tags=["meals"],
)

app.include_router(
    water_router,
    prefix=settings.API_V1_PREFIX,
    tags=["water"],
)

app.include_router(
    sleep_router,
    prefix=settings.API_V1_PREFIX,
    tags=["sleep"],
)

app.include_router(
    moods_router,
    prefix=settings.API_V1_PREFIX,
    tags=["moods"],
)

app.include_router(
    notes_router,
    prefix=settings.API_V1_PREFIX,
    tags=["notes"],
)

app.include_router(
    notifications_router,
    prefix=settings.API_V1_PREFIX,
    tags=["notifications"],
)

app.include_router(
    users_router,
    prefix=f"{settings.API_V1_PREFIX}/users",
    tags=["users"],
)

app.include_router(
    ai_router,
    prefix=f"{settings.API_V1_PREFIX}/ai",
    tags=["ai"],
)

app.include_router(
    agents_router,
    prefix=f"{settings.API_V1_PREFIX}/agents",
    tags=["agents"],
)

app.include_router(
    meal_plans_router,
    prefix=f"{settings.API_V1_PREFIX}/meal-plans",
    tags=["meal-plans"],
)

app.include_router(
    training_programs_router,
    prefix=f"{settings.API_V1_PREFIX}/training-programs",
    tags=["training-programs"],
)

app.include_router(
    voice_router,
    prefix=f"{settings.API_V1_PREFIX}/voice",
    tags=["voice"],
)

app.include_router(
    health_router,
    prefix="/health",
    tags=["health"],
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to FitCoach API",
        "version": "0.1.0",
        "docs": "/api/docs",
    }


@app.get("/health")
async def health_check():
    """
    Deprecated: Use /health/liveness or /health/readiness instead.

    Simple health check endpoint for backwards compatibility.
    """
    logger.warning("Deprecated /health endpoint called, use /health/liveness or /health/readiness")
    return {"status": "healthy", "deprecated": True, "use": "/health/liveness or /health/readiness"}
