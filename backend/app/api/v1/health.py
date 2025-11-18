"""Health check and monitoring endpoints."""

import logging
import os
import shutil
import time
from typing import Any, Dict

import psutil
import redis
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse, PlainTextResponse
from sqlalchemy import text

from app.config import settings
from app.core.database import engine

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/liveness", response_class=PlainTextResponse)
async def liveness_probe() -> str:
    """
    Liveness probe for Kubernetes/Docker health checks.

    This endpoint simply checks if the application is running.
    It should return 200 OK if the application is alive.

    Returns:
        Plain text "OK"

    Example:
        curl http://localhost:8000/health/liveness
        OK
    """
    return "OK"


@router.get("/readiness")
async def readiness_probe() -> JSONResponse:
    """
    Readiness probe for Kubernetes/Docker health checks.

    Checks if the application is ready to serve traffic by verifying:
    - PostgreSQL database connection
    - Redis connection
    - Disk space availability
    - Memory availability

    Returns:
        JSONResponse with status and details of each check

    Status Codes:
        200: All checks passed, ready to serve traffic
        503: One or more checks failed, not ready

    Example:
        {
            "status": "healthy",
            "checks": {
                "database": {"status": "healthy", "latency_ms": 5.2},
                "redis": {"status": "healthy", "latency_ms": 1.1},
                "disk": {"status": "healthy", "free_gb": 50.5, "usage_percent": 45.2},
                "memory": {"status": "healthy", "available_gb": 4.2, "usage_percent": 62.1}
            },
            "timestamp": "2025-11-18T10:30:00Z"
        }
    """
    checks = {}
    all_healthy = True

    # Check PostgreSQL
    db_check = await check_database()
    checks["database"] = db_check
    if db_check["status"] != "healthy":
        all_healthy = False

    # Check Redis
    redis_check = await check_redis()
    checks["redis"] = redis_check
    if redis_check["status"] != "healthy":
        all_healthy = False

    # Check Disk Space
    disk_check = check_disk_space()
    checks["disk"] = disk_check
    if disk_check["status"] != "healthy":
        all_healthy = False

    # Check Memory
    memory_check = check_memory()
    checks["memory"] = memory_check
    if memory_check["status"] != "healthy":
        all_healthy = False

    # Build response
    response_data = {
        "status": "healthy" if all_healthy else "unhealthy",
        "checks": checks,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    status_code = status.HTTP_200_OK if all_healthy else status.HTTP_503_SERVICE_UNAVAILABLE

    if not all_healthy:
        logger.warning("Readiness check failed", extra={"checks": checks})

    return JSONResponse(content=response_data, status_code=status_code)


@router.get("/metrics", response_class=PlainTextResponse)
async def metrics() -> str:
    """
    Prometheus-compatible metrics endpoint.

    Provides basic application metrics in Prometheus exposition format:
    - Database connection pool metrics
    - Redis connection status
    - System resource usage (CPU, memory, disk)
    - HTTP request metrics (if available)

    Returns:
        Plain text metrics in Prometheus format

    Example:
        # HELP fitcoach_database_pool_size Database connection pool size
        # TYPE fitcoach_database_pool_size gauge
        fitcoach_database_pool_size 5

        # HELP fitcoach_memory_usage_bytes Memory usage in bytes
        # TYPE fitcoach_memory_usage_bytes gauge
        fitcoach_memory_usage_bytes 134217728
    """
    metrics_lines = []

    # Database pool metrics
    try:
        pool = engine.pool
        metrics_lines.extend([
            "# HELP fitcoach_database_pool_size Database connection pool size",
            "# TYPE fitcoach_database_pool_size gauge",
            f"fitcoach_database_pool_size {pool.size()}",
            "",
            "# HELP fitcoach_database_pool_checked_out Database connections checked out",
            "# TYPE fitcoach_database_pool_checked_out gauge",
            f"fitcoach_database_pool_checked_out {pool.checkedout()}",
            "",
        ])
    except Exception as e:
        logger.error(f"Failed to get database pool metrics: {e}")

    # Memory metrics
    try:
        memory = psutil.virtual_memory()
        process = psutil.Process()
        process_memory = process.memory_info()

        metrics_lines.extend([
            "# HELP fitcoach_memory_usage_bytes Application memory usage in bytes",
            "# TYPE fitcoach_memory_usage_bytes gauge",
            f"fitcoach_memory_usage_bytes {process_memory.rss}",
            "",
            "# HELP fitcoach_system_memory_total_bytes Total system memory in bytes",
            "# TYPE fitcoach_system_memory_total_bytes gauge",
            f"fitcoach_system_memory_total_bytes {memory.total}",
            "",
            "# HELP fitcoach_system_memory_available_bytes Available system memory in bytes",
            "# TYPE fitcoach_system_memory_available_bytes gauge",
            f"fitcoach_system_memory_available_bytes {memory.available}",
            "",
        ])
    except Exception as e:
        logger.error(f"Failed to get memory metrics: {e}")

    # CPU metrics
    try:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        metrics_lines.extend([
            "# HELP fitcoach_cpu_usage_percent CPU usage percentage",
            "# TYPE fitcoach_cpu_usage_percent gauge",
            f"fitcoach_cpu_usage_percent {cpu_percent}",
            "",
        ])
    except Exception as e:
        logger.error(f"Failed to get CPU metrics: {e}")

    # Disk metrics
    try:
        disk = shutil.disk_usage("/")
        metrics_lines.extend([
            "# HELP fitcoach_disk_total_bytes Total disk space in bytes",
            "# TYPE fitcoach_disk_total_bytes gauge",
            f"fitcoach_disk_total_bytes {disk.total}",
            "",
            "# HELP fitcoach_disk_used_bytes Used disk space in bytes",
            "# TYPE fitcoach_disk_used_bytes gauge",
            f"fitcoach_disk_used_bytes {disk.used}",
            "",
            "# HELP fitcoach_disk_free_bytes Free disk space in bytes",
            "# TYPE fitcoach_disk_free_bytes gauge",
            f"fitcoach_disk_free_bytes {disk.free}",
            "",
        ])
    except Exception as e:
        logger.error(f"Failed to get disk metrics: {e}")

    return "\n".join(metrics_lines)


async def check_database() -> Dict[str, Any]:
    """
    Check PostgreSQL database connection and latency.

    Returns:
        Dictionary with status and latency information
    """
    try:
        start_time = time.time()

        # Simple query to check connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))

        latency_ms = (time.time() - start_time) * 1000

        return {
            "status": "healthy",
            "latency_ms": round(latency_ms, 2),
        }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
        }


async def check_redis() -> Dict[str, Any]:
    """
    Check Redis connection and latency.

    Returns:
        Dictionary with status and latency information
    """
    try:
        start_time = time.time()

        # Create Redis connection
        redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            socket_connect_timeout=5,
            socket_timeout=5,
        )

        # Ping Redis
        redis_client.ping()

        latency_ms = (time.time() - start_time) * 1000

        redis_client.close()

        return {
            "status": "healthy",
            "latency_ms": round(latency_ms, 2),
        }
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
        }


def check_disk_space(warning_threshold_percent: float = 90.0) -> Dict[str, Any]:
    """
    Check available disk space.

    Args:
        warning_threshold_percent: Threshold for warning (default 90%)

    Returns:
        Dictionary with status and disk usage information
    """
    try:
        disk = shutil.disk_usage("/")
        total_gb = disk.total / (1024**3)
        used_gb = disk.used / (1024**3)
        free_gb = disk.free / (1024**3)
        usage_percent = (disk.used / disk.total) * 100

        status_result = (
            "healthy" if usage_percent < warning_threshold_percent else "unhealthy"
        )

        return {
            "status": status_result,
            "total_gb": round(total_gb, 2),
            "used_gb": round(used_gb, 2),
            "free_gb": round(free_gb, 2),
            "usage_percent": round(usage_percent, 2),
        }
    except Exception as e:
        logger.error(f"Disk space check failed: {e}")
        return {
            "status": "unknown",
            "error": str(e),
        }


def check_memory(warning_threshold_percent: float = 90.0) -> Dict[str, Any]:
    """
    Check available memory.

    Args:
        warning_threshold_percent: Threshold for warning (default 90%)

    Returns:
        Dictionary with status and memory usage information
    """
    try:
        memory = psutil.virtual_memory()
        total_gb = memory.total / (1024**3)
        available_gb = memory.available / (1024**3)
        used_gb = memory.used / (1024**3)
        usage_percent = memory.percent

        status_result = (
            "healthy" if usage_percent < warning_threshold_percent else "unhealthy"
        )

        return {
            "status": status_result,
            "total_gb": round(total_gb, 2),
            "used_gb": round(used_gb, 2),
            "available_gb": round(available_gb, 2),
            "usage_percent": round(usage_percent, 2),
        }
    except Exception as e:
        logger.error(f"Memory check failed: {e}")
        return {
            "status": "unknown",
            "error": str(e),
        }
