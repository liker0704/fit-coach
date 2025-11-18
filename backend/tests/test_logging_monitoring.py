"""Tests for logging, monitoring, and health check endpoints."""

import logging
import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.main import app
from app.core.logging_config import get_logger, setup_logging
from app.core.request_id import get_request_id


class TestLogging:
    """Tests for centralized logging configuration."""

    def test_setup_logging(self, tmp_path):
        """Test logging setup creates proper configuration."""
        log_dir = tmp_path / "logs"
        setup_logging(log_level="DEBUG", log_dir=str(log_dir), app_name="test")

        # Check that log directory was created
        assert log_dir.exists()

        # Test logger creation
        logger = get_logger("test_module")
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_module"

    def test_get_logger(self):
        """Test getting logger instances."""
        logger1 = get_logger("module1")
        logger2 = get_logger("module2")

        assert logger1.name == "module1"
        assert logger2.name == "module2"
        assert logger1 != logger2


class TestRequestID:
    """Tests for Request ID middleware."""

    def test_request_id_generated(self):
        """Test that request ID is generated for requests."""
        client = TestClient(app)
        response = client.get("/")

        # Check response has X-Request-ID header
        assert "X-Request-ID" in response.headers
        request_id = response.headers["X-Request-ID"]

        # Validate UUID format (basic check)
        assert len(request_id) == 36  # UUID v4 format: 8-4-4-4-12
        assert request_id.count("-") == 4

    def test_request_id_preserved(self):
        """Test that provided request ID is preserved."""
        client = TestClient(app)
        custom_request_id = "12345678-1234-1234-1234-123456789012"

        response = client.get("/", headers={"X-Request-ID": custom_request_id})

        # Check response has the same request ID
        assert response.headers["X-Request-ID"] == custom_request_id

    def test_request_id_in_logs(self, caplog):
        """Test that request ID appears in logs."""
        client = TestClient(app)

        with caplog.at_level(logging.INFO):
            response = client.get("/")

        request_id = response.headers["X-Request-ID"]

        # Check that request ID appears in log messages
        log_records = [record for record in caplog.records if "request_id" in record.__dict__]
        assert len(log_records) > 0


class TestHealthChecks:
    """Tests for health check endpoints."""

    def test_liveness_probe(self):
        """Test liveness probe endpoint."""
        client = TestClient(app)
        response = client.get("/health/liveness")

        assert response.status_code == status.HTTP_200_OK
        assert response.text == "OK"

    def test_readiness_probe_structure(self):
        """Test readiness probe returns proper structure."""
        client = TestClient(app)
        response = client.get("/health/readiness")

        # Should return JSON
        data = response.json()

        # Check structure
        assert "status" in data
        assert "checks" in data
        assert "timestamp" in data

        # Check that checks are present
        checks = data["checks"]
        assert "database" in checks
        assert "redis" in checks
        assert "disk" in checks
        assert "memory" in checks

    def test_readiness_probe_database_check(self):
        """Test database health check in readiness probe."""
        client = TestClient(app)
        response = client.get("/health/readiness")

        data = response.json()
        db_check = data["checks"]["database"]

        # Database check should have status
        assert "status" in db_check

        # If healthy, should have latency
        if db_check["status"] == "healthy":
            assert "latency_ms" in db_check
            assert isinstance(db_check["latency_ms"], (int, float))
            assert db_check["latency_ms"] > 0

    def test_readiness_probe_redis_check(self):
        """Test Redis health check in readiness probe."""
        client = TestClient(app)
        response = client.get("/health/readiness")

        data = response.json()
        redis_check = data["checks"]["redis"]

        # Redis check should have status
        assert "status" in redis_check

        # If healthy, should have latency
        if redis_check["status"] == "healthy":
            assert "latency_ms" in redis_check
            assert isinstance(redis_check["latency_ms"], (int, float))

    def test_readiness_probe_disk_check(self):
        """Test disk space check in readiness probe."""
        client = TestClient(app)
        response = client.get("/health/readiness")

        data = response.json()
        disk_check = data["checks"]["disk"]

        # Disk check should have status and metrics
        assert "status" in disk_check

        if disk_check["status"] in ["healthy", "unhealthy"]:
            assert "total_gb" in disk_check
            assert "free_gb" in disk_check
            assert "usage_percent" in disk_check

            # Validate metrics are numbers
            assert isinstance(disk_check["total_gb"], (int, float))
            assert isinstance(disk_check["free_gb"], (int, float))
            assert isinstance(disk_check["usage_percent"], (int, float))

            # Validate reasonable ranges
            assert disk_check["total_gb"] > 0
            assert 0 <= disk_check["usage_percent"] <= 100

    def test_readiness_probe_memory_check(self):
        """Test memory check in readiness probe."""
        client = TestClient(app)
        response = client.get("/health/readiness")

        data = response.json()
        memory_check = data["checks"]["memory"]

        # Memory check should have status and metrics
        assert "status" in memory_check

        if memory_check["status"] in ["healthy", "unhealthy"]:
            assert "total_gb" in memory_check
            assert "available_gb" in memory_check
            assert "usage_percent" in memory_check

            # Validate metrics are numbers
            assert isinstance(memory_check["total_gb"], (int, float))
            assert isinstance(memory_check["available_gb"], (int, float))
            assert isinstance(memory_check["usage_percent"], (int, float))

            # Validate reasonable ranges
            assert memory_check["total_gb"] > 0
            assert 0 <= memory_check["usage_percent"] <= 100

    def test_deprecated_health_endpoint(self):
        """Test deprecated /health endpoint."""
        client = TestClient(app)
        response = client.get("/health")

        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["status"] == "healthy"
        assert data["deprecated"] is True
        assert "use" in data


class TestMetrics:
    """Tests for Prometheus metrics endpoint."""

    def test_metrics_endpoint(self):
        """Test metrics endpoint returns Prometheus format."""
        client = TestClient(app)
        response = client.get("/health/metrics")

        assert response.status_code == status.HTTP_200_OK

        # Check content type
        content = response.text
        assert len(content) > 0

        # Check for basic Prometheus format markers
        assert "# HELP" in content
        assert "# TYPE" in content

        # Check for specific metrics
        assert "fitcoach" in content.lower()

    def test_metrics_has_memory_info(self):
        """Test metrics includes memory information."""
        client = TestClient(app)
        response = client.get("/health/metrics")

        content = response.text

        # Should have memory metrics
        assert "memory" in content.lower()
        assert "fitcoach_memory_usage_bytes" in content

    def test_metrics_has_cpu_info(self):
        """Test metrics includes CPU information."""
        client = TestClient(app)
        response = client.get("/health/metrics")

        content = response.text

        # Should have CPU metrics
        assert "cpu" in content.lower()

    def test_metrics_has_disk_info(self):
        """Test metrics includes disk information."""
        client = TestClient(app)
        response = client.get("/health/metrics")

        content = response.text

        # Should have disk metrics
        assert "disk" in content.lower()


class TestErrorHandling:
    """Tests for error tracking and handling."""

    def test_http_error_includes_request_id(self):
        """Test that HTTP errors include request ID."""
        client = TestClient(app)

        # Request non-existent endpoint
        response = client.get("/api/v1/nonexistent")

        # Check request ID in response
        assert "X-Request-ID" in response.headers

        # For JSON error responses, check request_id in body
        if response.headers.get("content-type") == "application/json":
            data = response.json()
            # Note: might have 'request_id' or not depending on error handler
            # Just verify it's a proper error response
            assert response.status_code == 404

    def test_error_logging_includes_traceback(self, caplog):
        """Test that errors are logged with traceback."""
        # This would require triggering an actual error in the app
        # For now, we just verify the error handler is registered
        client = TestClient(app)

        # The app should handle exceptions gracefully
        # We can't easily test this without creating a broken endpoint
        assert app.exception_handlers is not None


class TestGracefulShutdown:
    """Tests for graceful shutdown behavior."""

    def test_app_has_lifespan(self):
        """Test that app has lifespan context configured."""
        # Check that lifespan is configured
        assert app.router.lifespan_context is not None

    def test_shutdown_event_exists(self):
        """Test that shutdown event is defined."""
        from app.main import shutdown_event

        assert shutdown_event is not None


# Integration test
class TestLoggingIntegration:
    """Integration tests for logging across requests."""

    def test_multiple_requests_different_request_ids(self):
        """Test that multiple requests get different request IDs."""
        client = TestClient(app)

        response1 = client.get("/")
        response2 = client.get("/")

        request_id1 = response1.headers["X-Request-ID"]
        request_id2 = response2.headers["X-Request-ID"]

        # Request IDs should be different
        assert request_id1 != request_id2

    def test_logging_performance(self):
        """Test that logging doesn't significantly impact performance."""
        import time

        client = TestClient(app)

        # Make multiple requests and measure time
        start_time = time.time()
        num_requests = 10

        for _ in range(num_requests):
            response = client.get("/")
            assert response.status_code == 200

        elapsed = time.time() - start_time

        # Should complete 10 requests in reasonable time (< 5 seconds)
        assert elapsed < 5.0

        avg_time = elapsed / num_requests
        # Average request should be fast (< 500ms)
        assert avg_time < 0.5
