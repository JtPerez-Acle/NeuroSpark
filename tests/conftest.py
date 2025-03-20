"""Test configuration."""
import os
import sys
import tempfile
import uuid
import pytest
import pytest_asyncio
import httpx
from typing import Dict, Any, List
from fastapi import FastAPI
from httpx import AsyncClient
from unittest.mock import patch, MagicMock

# Add the project root directory to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Mock logging setup to avoid file access issues
patch('app.monitoring.logging_config.setup_logging', MagicMock()).start()

from app.database.arango.database import ArangoDatabase

# Set test environment variables if not already set
os.environ.setdefault("ARANGO_HOST", "localhost")
os.environ.setdefault("ARANGO_PORT", "8529")
os.environ.setdefault("ARANGO_USER", "root")
os.environ.setdefault("ARANGO_PASSWORD", "password")
# Use a unique database name for each test run to avoid collisions
os.environ.setdefault("ARANGO_DB", f"test_db_{uuid.uuid4().hex[:8]}")

# Configure logging to reduce noise during tests
import logging
logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)
logging.getLogger("arango").setLevel(logging.WARNING)

@pytest.fixture(scope="session")
def test_log_dir():
    """Create a temporary directory for test logs."""
    with tempfile.TemporaryDirectory() as temp_dir:
        os.environ["TEST_LOG_DIR"] = temp_dir
        os.environ["TESTING"] = "1"
        yield temp_dir

# Import app after setting up test log directory
from app.main import app

@pytest_asyncio.fixture
async def test_db_arango():
    """Create test ArangoDB database with improved retry logic."""
    import time
    import asyncio
    import logging
    from urllib3.exceptions import NewConnectionError
    from arango.exceptions import ServerConnectionError, DatabaseCreateError
    
    # Configure urllib3 logging to reduce verbosity of connection retry warnings
    logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)
    
    db = ArangoDatabase(
        host=os.environ["ARANGO_HOST"],
        port=int(os.environ["ARANGO_PORT"]),
        username=os.environ["ARANGO_USER"],
        password=os.environ["ARANGO_PASSWORD"],
        db_name=os.environ["ARANGO_DB"]
    )
    
    # Try to connect with improved retry logic
    max_retries = 5
    retry_count = 0
    connected = False
    
    while retry_count < max_retries and not connected:
        try:
            await db.connect()
            connected = True
            print(f"Successfully connected to ArangoDB on attempt {retry_count + 1}")
        except (ServerConnectionError, ConnectionError, NewConnectionError) as e:
            retry_count += 1
            wait_time = 2 * retry_count  # Exponential backoff
            print(f"Connection attempt {retry_count} failed: {str(e)}. Waiting {wait_time}s...")
            await asyncio.sleep(wait_time)  # Use asyncio.sleep instead of time.sleep
    
    if not connected:
        raise ConnectionError(f"Failed to connect to ArangoDB after {max_retries} attempts")
    
    try:
        # Clean up any existing data
        await db.clear_database()
        yield db
    finally:
        try:
            await db.disconnect()
            
            # Delete test database
            if db._db:
                try:
                    sys_db = db._connection.client.db("_system", 
                                                   username=os.environ["ARANGO_USER"], 
                                                   password=os.environ["ARANGO_PASSWORD"])
                    if sys_db.has_database(os.environ["ARANGO_DB"]):
                        try:
                            sys_db.delete_database(os.environ["ARANGO_DB"])
                            print(f"Successfully deleted test database: {os.environ['ARANGO_DB']}")
                        except Exception as e:
                            print(f"Error deleting test database: {str(e)}")
                except Exception as e:
                    print(f"Error accessing system database during cleanup: {str(e)}")
        except Exception as e:
            print(f"Error during test database cleanup: {str(e)}")

@pytest_asyncio.fixture
async def test_app(test_db_arango) -> FastAPI:
    """Create test FastAPI application."""
    app.state.db = test_db_arango
    return app

@pytest_asyncio.fixture
async def async_client(test_app):
    """Create async test client."""
    base_url = "http://test"
    transport = httpx.ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url=base_url) as client:
        yield client

@pytest.fixture
def test_wallets() -> List[Dict[str, Any]]:
    """Get test blockchain wallets data."""
    return [
        {
            "address": "0x1234567890123456789012345678901234567890",
            "chain": "ethereum",
            "type": "EOA",
            "balance": 1.5,
            "first_seen": "2025-01-01T00:00:00Z",
            "last_active": "2025-03-01T00:00:00Z",
            "risk_score": 25.0,
            "tags": ["trader"]
        }
    ]

@pytest.fixture
def test_contracts() -> List[Dict[str, Any]]:
    """Get test blockchain contracts data."""
    return [
        {
            "address": "0xabcdef0123456789abcdef0123456789abcdef01",
            "chain": "ethereum",
            "type": "contract",
            "creator": "0x1234567890123456789012345678901234567890",
            "creation_tx": "0xaaaaaaaabbbbbbbbccccccccddddddddeeeeeeeeffffffffaaaaaaaabbbbbbbb",
            "creation_timestamp": "2025-01-15T00:00:00Z",
            "verified": True,
            "name": "TestToken",
            "risk_score": 15.0,
            "tags": ["token", "erc20"]
        }
    ]

@pytest.fixture
def test_transactions() -> List[Dict[str, Any]]:
    """Get test blockchain transactions data."""
    return [
        {
            "hash": "0xaaaaaaaabbbbbbbbccccccccddddddddeeeeeeeeffffffffaaaaaaaabbbbbbbb",
            "chain": "ethereum",
            "block_number": 12345678,
            "timestamp": "2025-02-15T12:00:00Z",
            "from_address": "0x1234567890123456789012345678901234567890",
            "to_address": "0xabcdef0123456789abcdef0123456789abcdef01",
            "value": 1000000000000000000,  # 1 ETH in wei
            "gas_used": 21000,
            "gas_price": 50000000000,
            "status": "success",
            "input_data": "0x",
            "risk_score": 10.0
        }
    ]
