"""
Database Connection Module - Synchronous for Vercel Serverless
===============================================================
PyMongo (sync) works reliably on Vercel/AWS Lambda.
Connection is established lazily on first request and reused.
"""

from pymongo import MongoClient
from pymongo.database import Database as PyMongoDatabase
from app.config import settings
from app.core.logging_config import logger


class Database:
    """
    Singleton database manager using synchronous PyMongo.
    Works reliably on Vercel serverless functions.
    """
    
    def __init__(self):
        self.client: MongoClient | None = None
        self.database: PyMongoDatabase | None = None
    
    def connect(self) -> None:
        """
        Establish connection to MongoDB Atlas.
        Called automatically on first request.
        """
        if self.client is not None:
            return  # Already connected
        
        try:
            logger.info("Connecting to MongoDB Atlas...")
            
            # Create PyMongo client (synchronous)
            self.client = MongoClient(
                settings.mongodb_url,
                maxPoolSize=10,
                minPoolSize=1,
                serverSelectionTimeoutMS=5000,
                retryWrites=True
            )
            
            # Get database reference
            self.database = self.client[settings.database_name]
            
            # Verify connection with ping
            self.client.admin.command("ping")
            
            logger.info("Successfully connected to MongoDB Atlas!")
            logger.info(f"Database: {settings.database_name}")
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            raise
    
    def disconnect(self) -> None:
        """Close MongoDB connection."""
        if self.client:
            logger.info("Disconnecting from MongoDB Atlas...")
            self.client.close()
            logger.info("MongoDB connection closed")
            self.client = None
            self.database = None
    
    def get_collection(self, collection_name: str):
        """
        Get a MongoDB collection.
        Auto-connects if not already connected.
        """
        if self.database is None:
            self.connect()
        
        return self.database[collection_name]


# Global database instance (singleton)
db = Database()