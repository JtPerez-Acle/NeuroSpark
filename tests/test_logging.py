"""Tests for logging configuration."""
import os
import tempfile
from pathlib import Path
import pytest
from fastapi import FastAPI, Request
import httpx
import asyncio
from starlette.datastructures import Headers
from loguru import logger

from app.monitoring.logging_config import setup_logging, log_request_middleware
from app.main import app

@pytest.fixture(autouse=True)
def test_log_dir():
    """Create a temporary directory for test logs."""
    with tempfile.TemporaryDirectory() as tmpdir:
        os.environ["TEST_LOG_DIR"] = tmpdir
        os.environ["TESTING"] = "1"
        setup_logging()  # Setup logging with the test directory
        yield Path(tmpdir)
        os.environ.pop("TEST_LOG_DIR", None)
        os.environ.pop("TESTING", None)

@pytest.fixture
def test_app():
    """Create test app."""
    test_app = FastAPI()
    test_app.middleware("http")(log_request_middleware)
    
    @test_app.get("/test")
    async def test_endpoint():
        return {"message": "test"}
    
    @test_app.get("/error")
    async def error_endpoint():
        logger.error("Test error", exc_info=True)
        raise ValueError("Test error")
    
    return test_app

@pytest.fixture
async def async_client(test_app):
    """Create async client."""
    async with httpx.AsyncClient(
        base_url="http://test",
        transport=httpx.ASGITransport(app=test_app)
    ) as client:
        yield client

@pytest.mark.asyncio
async def test_log_format_with_request(test_log_dir, test_app, async_client):
    """Test log format with request context."""
    response = await async_client.get("/test")
    assert response.status_code == 200
    
    # Wait for log to be written
    await asyncio.sleep(0.1)
    
    # Check log files
    log_file = test_log_dir / "app.log"
    assert log_file.exists()
    
    # Verify log content
    with open(log_file) as f:
        log_content = f.read()
        assert "Request started" in log_content
        assert "method=GET" in log_content
        assert "path=/test" in log_content

@pytest.mark.asyncio
async def test_log_format_without_request_context(test_log_dir):
    """Test log format without request context."""
    logger.info("Test message")
    
    # Wait for log to be written
    await asyncio.sleep(0.1)
    
    # Check log files
    log_file = test_log_dir / "app.log"
    assert log_file.exists()
    
    # Verify log content
    with open(log_file) as f:
        log_content = f.read()
        assert "Test message" in log_content

@pytest.mark.asyncio
async def test_error_logging_context(test_log_dir, test_app, async_client):
    """Test error logging."""
    try:
        await async_client.get("/error")
    except ValueError:
        pass  # Expected error
    
    # Wait for log to be written
    await asyncio.sleep(0.1)
    
    # Check log files
    error_log = test_log_dir / "error.log"
    assert error_log.exists()
    
    # Verify log content
    with open(error_log) as f:
        log_content = f.read()
        assert "Test error" in log_content
