"""
Database Connection Module - Synchronous for Vercel Serverless
===============================================================
PyMongo (sync) with SSL/TLS fixes for Vercel.
"""

from pymongo import MongoClient
from pymongo.database import Database as PyMongoDatabase
import certifi  # Provides Mozilla's CA bundle
from app.config import settings
from app.core.logging_config import logger


class Database:
    """Singleton database manager using synchronous PyMongo."""
    
    def __init__(self):
        self.client: MongoClient | None = None
        self.database: PyMongoDatabase | None = None
    
    def connect(self) -> None:
        """Connect to MongoDB Atlas with SSL fix."""
        if self.client is not None:
            return
        
        try:
            logger.info("Connecting to MongoDB Atlas...")
            
            self.client = MongoClient(
                settings.mongodb_url,
                maxPoolSize=10,
                minPoolSize=1,
                serverSelectionTimeoutMS=10000,  # Increased timeout
                connectTimeoutMS=10000,
                socketTimeoutMS=10000,
                retryWrites=True,
                # SSL/TLS fixes for Vercel
                tls=True,
                tlsCAFile=certifi.where(),  # Use Mozilla CA bundle
            )
            
            self.database = self.client[settings.database_name]
            self.client.admin.command("ping")
            
            logger.info("Successfully connected to MongoDB Atlas!")
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            raise
    
    def disconnect(self) -> None:
        if self.client:
            self.client.close()
            self.client = None
            self.database = None
    
    def get_collection(self, collection_name: str):
        if self.database is None:
            self.connect()
        return self.database[collection_name]


db = Database()