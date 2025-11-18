"""Pytest configuration and shared fixtures for all tests."""

import pytest
import asyncio
from typing import Generator


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Marker for tests that require OpenAI API key
def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "requires_openai: mark test as requiring OpenAI API key"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test requiring running server"
    )
