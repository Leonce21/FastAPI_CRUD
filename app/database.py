"""
Database Connection Module
=========================
This module manages the MongoDB connection using Motor (async driver).
Motor is the official async Python driver for MongoDB, required for
FastAPI's async/await pattern. It provides non-blocking database operations.
"""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config import settings
from app.core.logging_config import logger


class Database:
    """
    Singleton database manager.
    Handles MongoDB client lifecycle (connect/disconnect).
    Using singleton pattern ensures only one connection pool exists.
    """
    
    def __init__(self):
        """Initialize database manager (does not connect yet)."""
        self.client: AsyncIOMotorClient | None = None
        self.database: AsyncIOMotorDatabase | None = None
    
    async def connect(self) -> None:
        """
        Establish connection to MongoDB Atlas.
        Called during FastAPI startup event.
        """
        try:
            logger.info("Connecting to MongoDB Atlas...")
            
            # Create Motor client with connection pooling
            # maxPoolSize: Maximum connections in pool (default 100)
            # serverSelectionTimeoutMS: Fail fast if can't connect (5 seconds)
            self.client = AsyncIOMotorClient(
                settings.mongodb_url,
                maxPoolSize=50,  # Limit concurrent connections
                minPoolSize=10,  # Maintain minimum connections
                serverSelectionTimeoutMS=5000,  # 5 second timeout
                retryWrites=True  # Auto-retry failed writes
            )
            
            # Get database reference
            self.database = self.client[settings.database_name]
            
            # Verify connection with ping command
            # This raises exception if connection fails
            await self.client.admin.command("ping")
            
            logger.info("✅ Successfully connected to MongoDB Atlas!")
            logger.info(f"Database: {settings.database_name}")
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to MongoDB: {str(e)}")
            raise
    
    async def disconnect(self) -> None:
        """
        Close MongoDB connection.
        Called during FastAPI shutdown event.
        """
        if self.client:
            logger.info("Disconnecting from MongoDB Atlas...")
            self.client.close()
            logger.info("✅ MongoDB connection closed")
            self.client = None
            self.database = None
    
    def get_collection(self, collection_name: str):
        """
        Get a MongoDB collection for CRUD operations.
        
        Args:
            collection_name: Name of the collection (e.g., "items")
        
        Returns:
            AsyncIOMotorCollection instance
        """
        if self.database is None:
            raise RuntimeError("Database not connected. Call connect() first.")
        
        return self.database[collection_name]


# Global database instance (singleton)
db = Database()