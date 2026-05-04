"""
Item Service Module
===================
Service layer contains business logic.
This layer is independent of HTTP and database details.
It orchestrates repositories and handles business rules.
"""

from app.repositories.item_repository import ItemRepository
from app.schemas.item import ItemCreate, ItemUpdate, ItemInDB
from app.core.logging_config import logger


class ItemService:
    """
    Business logic for item operations.
    Acts as intermediary between API routes and repository.
    """
    
    def __init__(self, repository: ItemRepository):
        """
        Initialize service with repository dependency.
        Dependency injection allows easy testing with mock repositories.
        """
        self.repository = repository
        logger.info("ItemService initialized")
    
    async def create_item(self, item_data: ItemCreate) -> dict:
        """
        Business logic for creating an item.
        
        Args:
            item_data: Validated Pydantic schema
        
        Returns:
            Response dict with created item
        
        Logic:
            1. Convert Pydantic model to dict
            2. Call repository to persist
            3. Return formatted response
        """
        logger.info("Processing item creation request")
        
        # Convert Pydantic model to plain dict for repository
        data = item_data.model_dump()
        
        # Additional business logic could go here:
        # - Check for duplicates
        # - Validate business rules
        # - Send notifications
        
        created = await self.repository.create(data)
        
        return {
            "success": True,
            "message": "Item created successfully",
            "data": created
        }
    
    async def get_item(self, item_id: str) -> dict:
        """
        Retrieve single item by ID.
        
        Args:
            item_id: MongoDB ObjectId string
        
        Returns:
            Response dict or error if not found
        """
        logger.info(f"Processing get item request: {item_id}")
        
        item = await self.repository.get_by_id(item_id)
        
        if not item:
            logger.warning(f"Item not found in service: {item_id}")
            return {
                "success": False,
                "message": f"Item with ID '{item_id}' not found",
                "data": None
            }
        
        return {
            "success": True,
            "message": "Item retrieved successfully",
            "data": item
        }
    
    async def list_items(self, page: int = 1, per_page: int = 10) -> dict:
        """
        List items with pagination.
        
        Args:
            page: Page number (starts at 1)
            per_page: Items per page (max 100)
        
        Returns:
            Response with items list and pagination metadata
        """
        logger.info(f"Processing list items request: page={page}, per_page={per_page}")
        
        # Enforce maximum limit to prevent abuse
        safe_per_page = min(per_page, 100)
        
        # Calculate skip from page
        skip = (page - 1) * safe_per_page
        
        items = await self.repository.get_all(skip=skip, limit=safe_per_page)
        total = await self.repository.count_all()
        
        # Calculate total pages
        total_pages = (total + safe_per_page - 1) // safe_per_page if total > 0 else 1
        
        return {
            "success": True,
            "message": "Items retrieved successfully",
            "data": items,
            "total": total,
            "page": page,
            "per_page": safe_per_page,
            "total_pages": total_pages
        }
    
    async def update_item(self, item_id: str, update_data: ItemUpdate) -> dict:
        """
        Update existing item.
        
        Args:
            item_id: ID of item to update
            update_data: Partial update data
        
        Returns:
            Response with updated item or error
        """
        logger.info(f"Processing update request: {item_id}")
        
        # Convert Pydantic model to dict, excluding unset fields
        # exclude_unset=True means only include fields user actually sent
        data = update_data.model_dump(exclude_unset=True)
        
        if not data:
            return {
                "success": False,
                "message": "No fields provided for update",
                "data": None
            }
        
        updated = await self.repository.update(item_id, data)
        
        if not updated:
            return {
                "success": False,
                "message": f"Item with ID '{item_id}' not found",
                "data": None
            }
        
        return {
            "success": True,
            "message": "Item updated successfully",
            "data": updated
        }
    
    async def delete_item(self, item_id: str) -> dict:
        """
        Delete item by ID.
        
        Args:
            item_id: ID of item to delete
        
        Returns:
            Success/failure response
        """
        logger.info(f"Processing delete request: {item_id}")
        
        deleted = await self.repository.delete(item_id)
        
        if not deleted:
            return {
                "success": False,
                "message": f"Item with ID '{item_id}' not found",
                "data": None
            }
        
        return {
            "success": True,
            "message": "Item deleted successfully",
            "data": None
        }
    
    async def search_items(self, query: str, limit: int = 10) -> dict:
        """
        Search items by name.
        
        Args:
            query: Search string
            limit: Max results
        
        Returns:
            Search results
        """
        logger.info(f"Processing search request: {query}")
        
        items = await self.repository.search_by_name(query, limit)
        
        return {
            "success": True,
            "message": f"Found {len(items)} items matching '{query}'",
            "data": items
        }