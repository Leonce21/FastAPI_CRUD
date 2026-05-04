"""
Item Service Module - Synchronous Version
==========================================
Business logic layer - all async/await removed.
"""

from app.repositories.item_repository import ItemRepository
from app.schemas.item import ItemCreate, ItemUpdate
from app.core.logging_config import logger


class ItemService:
    """Business logic for item operations."""
    
    def __init__(self, repository: ItemRepository):
        self.repository = repository
        logger.info("ItemService initialized")
    
    def create_item(self, item_data: ItemCreate) -> dict:
        """Create a new item."""
        logger.info("Processing item creation request")
        data = item_data.model_dump()
        created = self.repository.create(data)
        
        return {
            "success": True,
            "message": "Item created successfully",
            "data": created
        }
    
    def get_item(self, item_id: str) -> dict:
        """Retrieve single item by ID."""
        logger.info(f"Processing get item request: {item_id}")
        item = self.repository.get_by_id(item_id)
        
        if not item:
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
    
    def list_items(self, page: int = 1, per_page: int = 10) -> dict:
        """List items with pagination."""
        logger.info(f"Processing list items request: page={page}, per_page={per_page}")
        
        safe_per_page = min(per_page, 100)
        skip = (page - 1) * safe_per_page
        
        items = self.repository.get_all(skip=skip, limit=safe_per_page)
        total = self.repository.count_all()
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
    
    def update_item(self, item_id: str, update_data: ItemUpdate) -> dict:
        """Update existing item."""
        logger.info(f"Processing update request: {item_id}")
        data = update_data.model_dump(exclude_unset=True)
        
        if not data:
            return {
                "success": False,
                "message": "No fields provided for update",
                "data": None
            }
        
        updated = self.repository.update(item_id, data)
        
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
    
    def delete_item(self, item_id: str) -> dict:
        """Delete item by ID."""
        logger.info(f"Processing delete request: {item_id}")
        deleted = self.repository.delete(item_id)
        
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
    
    def search_items(self, query: str, limit: int = 10) -> dict:
        """Search items by name."""
        logger.info(f"Processing search request: {query}")
        items = self.repository.search_by_name(query, limit)
        
        return {
            "success": True,
            "message": f"Found {len(items)} items matching '{query}'",
            "data": items
        }