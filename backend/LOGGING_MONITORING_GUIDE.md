# Logging, Monitoring & Health Checks Guide

## Overview

This guide covers the newly implemented logging, monitoring, and health check infrastructure for FitCoach backend.

## Features Implemented

### 1. Centralized Logging ✅
- **Structured JSON logging** with `python-json-logger`
- **Request/Response middleware** logging
- **Multiple log levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Log rotation** by size and time
- **Separate error log files**

### 2. Request ID & Correlation ✅
- **UUID v4 request IDs** for each request
- **Request ID propagation** in all logs
- **X-Request-ID header** in responses
- **Request tracking** across the application

### 3. Health Checks ✅
- **Liveness probe**: `/health/liveness`
- **Readiness probe**: `/health/readiness`
- **Prometheus metrics**: `/health/metrics`
- **Dependency checks**: PostgreSQL, Redis, Disk, Memory

### 4. Error Tracking ✅
- **Sentry integration** (optional)
- **Custom error handlers** with context
- **Sensitive data filtering**
- **Request ID in error responses**

### 5. Graceful Shutdown ✅
- **Signal handlers** for SIGTERM, SIGINT
- **5-second wait** for in-flight requests
- **Connection cleanup**
- **Shutdown event logging**

---

## Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

New dependencies:
- `python-json-logger>=2.0.7` - Structured JSON logging
- `psutil>=5.9.0` - System monitoring (CPU, memory, disk)
- `sentry-sdk[fastapi]>=1.40.0` - Error tracking (optional)

### 2. Configure Environment Variables

Add to `.env`:

```bash
# Logging Configuration
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
ENVIRONMENT=development  # development, staging, production

# Error Tracking (Optional - Sentry)
# SENTRY_DSN=https://your-sentry-dsn@sentry.io/your-project-id
# SENTRY_ENVIRONMENT=production
```

### 3. Start Application

```bash
uvicorn app.main:app --reload
```

Logs will be created in `backend/logs/`:
- `fitcoach.log` - All logs with rotation (10MB, 5 backups)
- `fitcoach_error.log` - Only ERROR and CRITICAL logs
- `fitcoach_daily.log` - Daily rotation (30 days retention)

---

## Using Logging in Your Code

### Basic Usage

```python
from app.core.logging_config import get_logger

logger = get_logger(__name__)

# Simple logging
logger.info("User created successfully")
logger.warning("Rate limit approaching")
logger.error("Database connection failed")

# Structured logging with extra fields
logger.info(
    "User login successful",
    extra={
        "user_id": 123,
        "email": "user@example.com",
        "ip_address": "192.168.1.1",
    }
)
```

### Logging with Request ID

The request ID is automatically added to logs when using the middleware:

```python
from app.core.request_id import get_request_id

request_id = get_request_id()
logger.info(
    "Processing payment",
    extra={
        "request_id": request_id,  # Automatically included
        "user_id": user.id,
        "amount": 99.99,
    }
)
```

### Logging Errors with Traceback

```python
try:
    # Some operation
    result = risky_operation()
except Exception as e:
    logger.error(
        "Operation failed",
        extra={
            "operation": "risky_operation",
            "input_data": data,
        },
        exc_info=True  # Includes full traceback
    )
```

---

## Health Check Endpoints

### Liveness Probe

**Endpoint**: `GET /health/liveness`

Simple check if application is alive.

```bash
curl http://localhost:8000/health/liveness
# Response: OK
```

**Use case**: Kubernetes liveness probe

```yaml
livenessProbe:
  httpGet:
    path: /health/liveness
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10
```

### Readiness Probe

**Endpoint**: `GET /health/readiness`

Checks if application is ready to serve traffic.

```bash
curl http://localhost:8000/health/readiness
```

**Response** (200 OK if all healthy):
```json
{
  "status": "healthy",
  "checks": {
    "database": {
      "status": "healthy",
      "latency_ms": 5.2
    },
    "redis": {
      "status": "healthy",
      "latency_ms": 1.1
    },
    "disk": {
      "status": "healthy",
      "total_gb": 100.0,
      "free_gb": 50.5,
      "usage_percent": 49.5
    },
    "memory": {
      "status": "healthy",
      "total_gb": 8.0,
      "available_gb": 4.2,
      "usage_percent": 47.5
    }
  },
  "timestamp": "2025-11-18T10:30:00Z"
}
```

**Use case**: Kubernetes readiness probe

```yaml
readinessProbe:
  httpGet:
    path: /health/readiness
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 5
```

### Metrics (Prometheus)

**Endpoint**: `GET /health/metrics`

Prometheus-compatible metrics.

```bash
curl http://localhost:8000/health/metrics
```

**Response** (Prometheus format):
```
# HELP fitcoach_database_pool_size Database connection pool size
# TYPE fitcoach_database_pool_size gauge
fitcoach_database_pool_size 5

# HELP fitcoach_memory_usage_bytes Application memory usage in bytes
# TYPE fitcoach_memory_usage_bytes gauge
fitcoach_memory_usage_bytes 134217728

# HELP fitcoach_cpu_usage_percent CPU usage percentage
# TYPE fitcoach_cpu_usage_percent gauge
fitcoach_cpu_usage_percent 25.5
```

---

## Error Tracking with Sentry

### Setup

1. **Sign up** for Sentry at https://sentry.io
2. **Create a project** for your application
3. **Get DSN** from project settings
4. **Add to `.env`**:

```bash
SENTRY_DSN=https://xxxxx@xxxxx.ingest.sentry.io/xxxxx
SENTRY_ENVIRONMENT=production
```

### Automatic Error Capture

Errors are automatically captured by the error handler:

```python
# This error will be automatically sent to Sentry
@router.get("/users/{user_id}")
async def get_user(user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

### Manual Error Capture

```python
from app.core.error_tracking import capture_exception

try:
    # Some operation
    result = process_payment(user_id, amount)
except PaymentError as e:
    capture_exception(
        exception=e,
        user_id=user_id,
        extra_context={
            "amount": amount,
            "payment_method": "credit_card",
        }
    )
    raise
```

---

## Request ID Usage

### In Endpoints

```python
from fastapi import Request

@router.get("/users")
async def get_users(request: Request):
    # Get request ID from request state
    request_id = request.state.request_id

    logger.info(
        "Fetching users",
        extra={"request_id": request_id}
    )

    return users
```

### In Response Headers

All responses automatically include `X-Request-ID` header:

```bash
curl -v http://localhost:8000/api/v1/users
# Response headers:
# X-Request-ID: 12345678-1234-1234-1234-123456789012
```

### Custom Request ID

You can provide your own request ID:

```bash
curl -H "X-Request-ID: my-custom-id" http://localhost:8000/api/v1/users
# Response will use the same request ID
```

---

## Log File Structure

### Log Files

```
backend/logs/
├── fitcoach.log           # All logs (rotated at 10MB, 5 backups)
├── fitcoach_error.log     # Only ERROR and CRITICAL (rotated at 10MB)
└── fitcoach_daily.log     # Daily rotation (30 days retention)
```

### Log Format (JSON)

Each log entry is a JSON object:

```json
{
  "timestamp": "2025-11-18T10:30:00.123Z",
  "level": "INFO",
  "logger": "app.api.v1.users",
  "module": "users",
  "function": "create_user",
  "line": 45,
  "message": "User created successfully",
  "request_id": "12345678-1234-1234-1234-123456789012",
  "user_id": 123,
  "email": "user@example.com"
}
```

---

## Graceful Shutdown

The application handles shutdown signals gracefully:

1. **Receives SIGTERM/SIGINT** signal
2. **Logs shutdown event**
3. **Waits up to 5 seconds** for in-flight requests
4. **Closes database connections**
5. **Logs completion** and exits

### Testing Shutdown

```bash
# Start app
uvicorn app.main:app

# Send shutdown signal
# Press Ctrl+C or:
kill -TERM <pid>
```

**Log output**:
```
INFO: Shutdown signal received, signal=SIGTERM
INFO: Application shutting down
INFO: Database connections closed
INFO: Application shutdown complete
```

---

## Monitoring Best Practices

### 1. Set Appropriate Log Levels

- **Development**: `LOG_LEVEL=DEBUG`
- **Staging**: `LOG_LEVEL=INFO`
- **Production**: `LOG_LEVEL=WARNING` or `INFO`

### 2. Monitor Health Endpoints

Set up automated monitoring:
- **Liveness**: Every 10 seconds
- **Readiness**: Every 5 seconds
- **Alert** if readiness fails for > 30 seconds

### 3. Use Structured Logging

Always add context:

```python
# Good
logger.info("Payment processed", extra={
    "user_id": user.id,
    "amount": amount,
    "currency": "USD",
    "payment_method": "stripe",
})

# Bad
logger.info(f"Payment of ${amount} processed for user {user.id}")
```

### 4. Configure Sentry in Production

Essential for tracking production errors:
- Set up **error alerts**
- Configure **release tracking**
- Enable **performance monitoring**
- Set up **user feedback**

### 5. Monitor Metrics

Use Prometheus + Grafana:

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'fitcoach'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/health/metrics'
    scrape_interval: 15s
```

---

## Troubleshooting

### Logs Not Appearing

1. Check `LOG_LEVEL` in `.env`
2. Verify `logs/` directory exists
3. Check file permissions
4. Look for errors in console output

### Health Check Failing

Check individual components:

```python
# Database
curl http://localhost:8000/health/readiness | jq '.checks.database'

# Redis
curl http://localhost:8000/health/readiness | jq '.checks.redis'

# Disk
curl http://localhost:8000/health/readiness | jq '.checks.disk'

# Memory
curl http://localhost:8000/health/readiness | jq '.checks.memory'
```

### Sentry Not Receiving Errors

1. Verify `SENTRY_DSN` is set
2. Check network connectivity
3. Look for Sentry initialization errors in logs
4. Test with manual capture:

```python
from app.core.error_tracking import capture_exception

try:
    raise Exception("Test error")
except Exception as e:
    capture_exception(e)
```

### Request IDs Not Appearing

1. Ensure `RequestIDMiddleware` is registered in `main.py`
2. Check middleware order (should be early in chain)
3. Verify `X-Request-ID` header in response

---

## Testing

Run tests:

```bash
cd backend
pytest tests/test_logging_monitoring.py -v
```

Test coverage includes:
- Logging configuration
- Request ID generation and propagation
- Health check endpoints
- Metrics endpoint
- Error handling
- Graceful shutdown

---

## Production Deployment Checklist

- [ ] Set `LOG_LEVEL=WARNING` or `INFO`
- [ ] Set `ENVIRONMENT=production`
- [ ] Configure `SENTRY_DSN` for error tracking
- [ ] Set up log rotation and retention policies
- [ ] Configure Prometheus scraping
- [ ] Set up Grafana dashboards
- [ ] Configure health check monitoring
- [ ] Test graceful shutdown
- [ ] Verify all logs are structured JSON
- [ ] Set up log aggregation (ELK, CloudWatch, etc.)
- [ ] Configure alerts for critical errors
- [ ] Test request ID propagation

---

## Support

For issues or questions:
1. Check logs in `backend/logs/`
2. Review error messages in Sentry
3. Check health endpoints for system status
4. Review this guide for configuration options
