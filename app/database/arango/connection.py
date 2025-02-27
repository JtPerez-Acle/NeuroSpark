"""ArangoDB connection module."""
import logging
import time
from typing import Optional, Any, Union

from arango import ArangoClient
from arango.database import StandardDatabase
from arango.exceptions import ServerConnectionError, DatabaseCreateError
from urllib3.exceptions import NewConnectionError, MaxRetryError

logger = logging.getLogger(__name__)

class ArangoConnection:
    """ArangoDB connection class."""

    def __init__(self, host: str, port: int, username: str, password: str, db_name: str):
        """Initialize ArangoDB connection.
        
        Args:
            host: ArangoDB host
            port: ArangoDB port
            username: ArangoDB username
            password: ArangoDB password
            db_name: Database name
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.db_name = db_name
        self.client = None
        self.db = None
    
    async def connect(self) -> None:
        """Connect to ArangoDB database."""
        retries = 5  # Increased number of retries
        retry_delay = 2  # seconds
        connection_errors = (
            ServerConnectionError, 
            DatabaseCreateError, 
            NewConnectionError, 
            MaxRetryError,
            ConnectionError,
            ConnectionRefusedError
        )
        
        for attempt in range(retries):
            try:
                # Create ArangoDB client with a reasonable timeout
                self.client = ArangoClient(
                    hosts=f"http://{self.host}:{self.port}",
                    request_timeout=10  # 10 second timeout
                )
                
                # Connect to system database first (to create our database if needed)
                sys_db = self.client.db("_system", username=self.username, password=self.password)
                
                # Create database if it doesn't exist
                if not sys_db.has_database(self.db_name):
                    logger.info(f"Creating database '{self.db_name}'")
                    sys_db.create_database(self.db_name)
                
                # Connect to our database
                self.db = self.client.db(self.db_name, username=self.username, password=self.password)
                
                # Ensure required collections exist
                self._ensure_collections()
                
                logger.info("Successfully connected to ArangoDB database")
                return
            except connection_errors as e:
                logger.warning(f"Failed to connect to ArangoDB database (attempt {attempt + 1}/{retries}): {str(e)}")
                if attempt < retries - 1:
                    import asyncio
                    # Increase the delay with each retry (exponential backoff)
                    current_delay = retry_delay * (attempt + 1)
                    logger.info(f"Waiting {current_delay}s before next connection attempt...")
                    await asyncio.sleep(current_delay)
                    continue
                logger.error(f"All connection attempts failed after {retries} tries: {str(e)}")
                raise
    
    def _ensure_collections(self) -> None:
        """Ensure required collections exist with proper error handling."""
        try:
            # Collections for nodes
            if not self.db.has_collection("agents"):
                logger.info("Creating 'agents' collection")
                self.db.create_collection("agents")
            
            if not self.db.has_collection("runs"):
                logger.info("Creating 'runs' collection")
                self.db.create_collection("runs")
                
            # Edge collections
            if not self.db.has_collection("interactions"):
                logger.info("Creating 'interactions' edge collection")
                self.db.create_collection("interactions", edge=True)
            
            if not self.db.has_collection("participations"):
                logger.info("Creating 'participations' edge collection")
                self.db.create_collection("participations", edge=True)
                
            logger.info("All required collections created or verified")
        except Exception as e:
            logger.error(f"Error ensuring collections exist: {str(e)}")
            raise
    
    async def disconnect(self) -> None:
        """Disconnect from ArangoDB database."""
        try:
            if self.client:
                # ArangoDB Python driver doesn't have an explicit disconnect method,
                # but we can close any open connections by dereferencing
                self.db = None
                self.client = None
                logger.info("Disconnected from ArangoDB database")
        except Exception as e:
            logger.warning(f"Error during database disconnect: {str(e)}")
    
    def get_database(self) -> StandardDatabase:
        """Get database instance.
        
        Returns:
            ArangoDB database instance
            
        Raises:
            ValueError: If the database is not connected
        """
        if not self.db:
            logger.error("Attempted to access database before connection was established")
            raise ValueError("Database not connected. Call connect() first.")
        return self.db