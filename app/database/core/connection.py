"""Neo4j connection module."""
import logging
from neo4j import AsyncGraphDatabase, AsyncSession

logger = logging.getLogger(__name__)

class Neo4jConnection:
    """Neo4j connection class."""

    def __init__(self, uri: str, user: str, password: str):
        """Initialize Neo4j connection.
        
        Args:
            uri: Neo4j URI
            user: Neo4j username
            password: Neo4j password
        """
        self.uri = uri
        self.user = user
        self.password = password
        self.driver = None

    async def connect(self):
        """Connect to Neo4j database."""
        retries = 3
        retry_delay = 2  # seconds
        
        for attempt in range(retries):
            try:
                self.driver = AsyncGraphDatabase.driver(
                    self.uri,
                    auth=(self.user, self.password)
                )
                # Test connection
                async with self.driver.session() as session:
                    await session.run("RETURN 1")
                logger.info("Successfully connected to Neo4j database")
                return
            except Exception as e:
                logger.error(f"Failed to connect to Neo4j database (attempt {attempt + 1}/{retries}): {e}")
                if attempt < retries - 1:
                    import asyncio
                    await asyncio.sleep(retry_delay)
                    continue
                raise

    async def disconnect(self):
        """Disconnect from Neo4j database."""
        if self.driver:
            await self.driver.close()
            logger.info("Disconnected from Neo4j database")

    async def session(self) -> AsyncSession:
        """Get database session."""
        if not self.driver:
            await self.connect()
        return self.driver.session()
