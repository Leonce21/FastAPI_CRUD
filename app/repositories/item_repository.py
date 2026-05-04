"""
Item Repository Module
======================
Repository pattern abstracts database operations.
This layer handles all direct MongoDB interactions, making it easy to:
- Test business logic without database
- Switch databases (e.g., to PostgreSQL) without touching services
- Centralize query logic
"""

from bson import ObjectId
from motor.core import AgnosticCollection
from app.models.item import ItemModel
from app.core.logging_config import logger


class ItemRepository:
    """
    Handles all database operations for items.
    Uses Motor's async methods for non-blocking I/O.
    """
    
    def __init__(self, collection: AgnosticCollection):
        """
        Initialize repository with MongoDB collection.
        
        Args:
            collection: Motor collection instance
        """
        self.collection = collection
        logger.info("ItemRepository initialized")
    
    async def create(self, item_data: dict) -> dict:
        """
        Insert a new item into MongoDB.
        
        Args:
            item_data: Validated item dictionary
        
        Returns:
            Created document with generated _id
        
        Logic:
            1. Convert Pydantic data to MongoDB document format
            2. Insert into collection
            3. Fetch and return the created document
        """
        logger.info(f"Creating item: {item_data.get('name', 'Unknown')}")
        
        # Prepare document with timestamps
        document = ItemModel.to_document(item_data)
        
        # Insert into MongoDB
        # insert_one returns InsertOneResult with inserted_id
        result = await self.collection.insert_one(document)
        
        logger.info(f"Item created with ID: {result.inserted_id}")
        
        # Fetch the created document to return complete data
        created = await self.collection.find_one({"_id": result.inserted_id})
        return ItemModel.to_dict(created)
    
    async def get_by_id(self, item_id: str) -> dict | None:
        """
        Retrieve a single item by its MongoDB ObjectId.
        
        Args:
            item_id: String representation of MongoDB ObjectId
        
        Returns:
            Item dictionary or None if not found
        
        Logic:
            1. Convert string ID to ObjectId
            2. Query MongoDB
            3. Return formatted dict or None
        """
        logger.debug(f"Fetching item by ID: {item_id}")
        
        try:
            # Convert string to ObjectId (MongoDB's ID type)
            object_id = ObjectId(item_id)
        except Exception:
            logger.warning(f"Invalid ObjectId format: {item_id}")
            return None
        
        # find_one returns dict or None
        document = await self.collection.find_one({"_id": object_id})
        
        if document:
            logger.debug(f"Item found: {document.get('name')}")
            return ItemModel.to_dict(document)
        
        logger.info(f"Item not found: {item_id}")
        return None
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> list[dict]:
        """
        Retrieve multiple items with pagination.
        
        Args:
            skip: Number of documents to skip (for pagination)
            limit: Maximum documents to return (page size)
        
        Returns:
            List of item dictionaries
        
        Logic:
            1. Create cursor with skip/limit
            2. Sort by created_at descending (newest first)
            3. Convert all documents to dicts
        """
        logger.info(f"Fetching items - skip: {skip}, limit: {limit}")
        
        # Create cursor with pagination and sorting
        cursor = (
            self.collection
            .find()  # Find all documents
            .skip(skip)  # Skip N documents
            .limit(limit)  # Limit results
            .sort("created_at", -1)  # -1 = descending (newest first)
        )
        
        # Convert cursor to list (async operation)
        documents = await cursor.to_list(length=limit)
        
        # Transform each document
        items = [ItemModel.to_dict(doc) for doc in documents]
        
        logger.info(f"Retrieved {len(items)} items")
        return items
    
    async def count_all(self) -> int:
        """
        Count total number of items in collection.
        Used for pagination metadata.
        """
        count = await self.collection.count_documents({})
        logger.debug(f"Total items count: {count}")
        return count
    
    async def update(self, item_id: str, update_data: dict) -> dict | None:
        """
        Update an existing item.
        
        Args:
            item_id: ID of item to update
            update_data: Dictionary of fields to change
        
        Returns:
            Updated document or None if not found
        
        Logic:
            1. Validate ObjectId
            2. Prepare $set update with timestamp
            3. Use find_one_and_update to get updated doc atomically
        """
        logger.info(f"Updating item: {item_id}")
        
        try:
            object_id = ObjectId(item_id)
        except Exception:
            logger.warning(f"Invalid ObjectId for update: {item_id}")
            return None
        
        # Prepare update with $set operator and timestamp
        update_doc = ItemModel.prepare_update(update_data)
        
        # find_one_and_update returns the document AFTER update
        # return_document=True ensures we get updated version
        updated = await self.collection.find_one_and_update(
            {"_id": object_id},  # Filter
            update_doc,  # Update operations
            return_document=True  # Return updated document
        )
        
        if updated:
            logger.info(f"Item updated successfully: {item_id}")
            return ItemModel.to_dict(updated)
        
        logger.warning(f"Item not found for update: {item_id}")
        return None
    
    async def delete(self, item_id: str) -> bool:
        """
        Delete an item by ID.
        
        Args:
            item_id: ID of item to delete
        
        Returns:
            True if deleted, False if not found
        
        Logic:
            1. Validate ObjectId
            2. delete_one returns DeleteResult with deleted_count
            3. Return True if deleted_count > 0
        """
        logger.info(f"Deleting item: {item_id}")
        
        try:
            object_id = ObjectId(item_id)
        except Exception:
            logger.warning(f"Invalid ObjectId for delete: {item_id}")
            return False
        
        # delete_one removes single document
        result = await self.collection.delete_one({"_id": object_id})
        
        # deleted_count is 1 if document existed, 0 if not found
        if result.deleted_count > 0:
            logger.info(f"Item deleted successfully: {item_id}")
            return True
        
        logger.warning(f"Item not found for delete: {item_id}")
        return False
    
    async def search_by_name(self, name_query: str, limit: int = 10) -> list[dict]:
        """
        Search items by name using regex (case-insensitive).
        
        Args:
            name_query: Search string
            limit: Max results
        
        Returns:
            List of matching items
        """
        logger.info(f"Searching items by name: {name_query}")
        
        # MongoDB regex for case-insensitive partial match
        # 'i' flag = case insensitive
        cursor = self.collection.find(
            {"name": {"$regex": name_query, "$options": "i"}}
        ).limit(limit)
        
        documents = await cursor.to_list(length=limit)
        items = [ItemModel.to_dict(doc) for doc in documents]
        
        logger.info(f"Search found {len(items)} items")
        return items