"""
Item Repository Module - Synchronous Version
============================================
Uses PyMongo instead of Motor for Vercel compatibility.
All async/await keywords removed.
"""

from bson import ObjectId
from pymongo.collection import Collection
from app.models.item import ItemModel
from app.core.logging_config import logger


class ItemRepository:
    """
    Handles all database operations for items.
    Synchronous version for Vercel serverless.
    """
    
    def __init__(self, collection: Collection):
        self.collection = collection
        logger.info("ItemRepository initialized")
    
    def create(self, item_data: dict) -> dict:
        """Insert a new item into MongoDB."""
        logger.info(f"Creating item: {item_data.get('name', 'Unknown')}")
        
        document = ItemModel.to_document(item_data)
        result = self.collection.insert_one(document)
        
        logger.info(f"Item created with ID: {result.inserted_id}")
        
        created = self.collection.find_one({"_id": result.inserted_id})
        return ItemModel.to_dict(created)
    
    def get_by_id(self, item_id: str) -> dict | None:
        """Retrieve a single item by its MongoDB ObjectId."""
        logger.debug(f"Fetching item by ID: {item_id}")
        
        try:
            object_id = ObjectId(item_id)
        except Exception:
            logger.warning(f"Invalid ObjectId format: {item_id}")
            return None
        
        document = self.collection.find_one({"_id": object_id})
        
        if document:
            logger.debug(f"Item found: {document.get('name')}")
            return ItemModel.to_dict(document)
        
        logger.info(f"Item not found: {item_id}")
        return None
    
    def get_all(self, skip: int = 0, limit: int = 100) -> list[dict]:
        """Retrieve multiple items with pagination."""
        logger.info(f"Fetching items - skip: {skip}, limit: {limit}")
        
        cursor = (
            self.collection
            .find()
            .skip(skip)
            .limit(limit)
            .sort("created_at", -1)
        )
        
        documents = list(cursor)
        items = [ItemModel.to_dict(doc) for doc in documents]
        
        logger.info(f"Retrieved {len(items)} items")
        return items
    
    def count_all(self) -> int:
        """Count total number of items."""
        count = self.collection.count_documents({})
        logger.debug(f"Total items count: {count}")
        return count
    
    def update(self, item_id: str, update_data: dict) -> dict | None:
        """Update an existing item."""
        logger.info(f"Updating item: {item_id}")
        
        try:
            object_id = ObjectId(item_id)
        except Exception:
            logger.warning(f"Invalid ObjectId for update: {item_id}")
            return None
        
        update_doc = ItemModel.prepare_update(update_data)
        
        updated = self.collection.find_one_and_update(
            {"_id": object_id},
            update_doc,
            return_document=True
        )
        
        if updated:
            logger.info(f"Item updated successfully: {item_id}")
            return ItemModel.to_dict(updated)
        
        logger.warning(f"Item not found for update: {item_id}")
        return None
    
    def delete(self, item_id: str) -> bool:
        """Delete an item by ID."""
        logger.info(f"Deleting item: {item_id}")
        
        try:
            object_id = ObjectId(item_id)
        except Exception:
            logger.warning(f"Invalid ObjectId for delete: {item_id}")
            return False
        
        result = self.collection.delete_one({"_id": object_id})
        
        if result.deleted_count > 0:
            logger.info(f"Item deleted successfully: {item_id}")
            return True
        
        logger.warning(f"Item not found for delete: {item_id}")
        return False
    
    def search_by_name(self, name_query: str, limit: int = 10) -> list[dict]:
        """Search items by name using regex (case-insensitive)."""
        logger.info(f"Searching items by name: {name_query}")
        
        cursor = self.collection.find(
            {"name": {"$regex": name_query, "$options": "i"}}
        ).limit(limit)
        
        documents = list(cursor)
        items = [ItemModel.to_dict(doc) for doc in documents]
        
        logger.info(f"Search found {len(items)} items")
        return items