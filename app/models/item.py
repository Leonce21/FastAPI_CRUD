"""
MongoDB Document Models
========================
This module defines how data is structured in MongoDB.
While MongoDB is schemaless, defining models helps maintain
consistency and provides helper methods for document conversion.
"""

from datetime import datetime
from bson import ObjectId
from typing import Any


class ItemModel:
    """
    Represents an item document in MongoDB.
    Provides methods to convert between MongoDB format and Python dicts.
    """
    
    COLLECTION_NAME = "items"  # MongoDB collection name
    
    @staticmethod
    def to_document(data: dict) -> dict:
        """
        Convert Pydantic dict to MongoDB document format.
        Adds timestamps and prepares for insertion.
        
        Args:
            data: Dictionary from Pydantic schema
        
        Returns:
            MongoDB-ready document dict
        """
        document = {
            "name": data["name"],
            "description": data.get("description"),
            "price": data["price"],
            "quantity": data.get("quantity", 0),
            "category": data.get("category", "general"),
            "created_at": datetime.utcnow(),  # UTC timestamp
            "updated_at": datetime.utcnow()
        }
        return document
    
    @staticmethod
    def to_dict(document: dict) -> dict:
        """
        Convert MongoDB document to API-friendly dict.
        Converts ObjectId to string for JSON serialization.
        
        Args:
            document: Raw MongoDB document
        
        Returns:
            Dictionary with string id (JSON serializable)
        """
        if not document:
            return {}
        
        # Convert ObjectId to string
        document["_id"] = str(document["_id"])
        
        # Convert datetime objects to ISO format strings
        if "created_at" in document and isinstance(document["created_at"], datetime):
            document["created_at"] = document["created_at"].isoformat()
        if "updated_at" in document and isinstance(document["updated_at"], datetime):
            document["updated_at"] = document["updated_at"].isoformat()
        
        return document
    
    @staticmethod
    def prepare_update(data: dict) -> dict:
        """
        Prepare update data with $set operator and timestamp.
        MongoDB updates use $set to specify fields to change.
        
        Args:
            data: Dictionary of fields to update
        
        Returns:
            MongoDB update document with $set operator
        """
        # Remove None values (partial update)
        update_data = {k: v for k, v in data.items() if v is not None}
        
        # Always update the updated_at timestamp
        update_data["updated_at"] = datetime.utcnow()
        
        return {"$set": update_data}