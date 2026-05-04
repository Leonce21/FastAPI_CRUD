"""
Item API Routes Module - Synchronous Version
=============================================
All async/await removed. FastAPI works great with sync code too.
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from app.schemas.item import ItemCreate, ItemUpdate, ItemResponse, ItemsListResponse
from app.services.item_service import ItemService
from app.repositories.item_repository import ItemRepository
from app.database import db
from app.core.logging_config import logger

router = APIRouter(
    prefix="/items",
    tags=["Items"],
    responses={
        404: {"description": "Item not found"},
        500: {"description": "Internal server error"}
    }
)


def get_item_service():
    """
    Synchronous dependency injection.
    Creates service with repository injected with MongoDB collection.
    """
    collection = db.get_collection("items")
    repository = ItemRepository(collection)
    return ItemService(repository)


@router.post(
    "/",
    response_model=ItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new item",
    description="Creates a new item in the database with auto-generated ID and timestamps."
)
def create_item(
    item: ItemCreate,
    service: ItemService = Depends(get_item_service)
):
    """POST /api/v1/items/ - Create a new item."""
    logger.info(f"POST /items - Creating item: {item.name}")
    result = service.create_item(item)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )
    
    return result


@router.get(
    "/",
    response_model=ItemsListResponse,
    summary="List all items",
    description="Retrieve paginated list of all items, sorted by newest first."
)
def list_items(
    page: int = Query(1, ge=1, description="Page number (starts at 1)"),
    per_page: int = Query(10, ge=1, le=100, description="Number of items per page"),
    service: ItemService = Depends(get_item_service)
):
    """GET /api/v1/items/ - List all items with pagination."""
    logger.info(f"GET /items - Listing items (page={page}, per_page={per_page})")
    return service.list_items(page=page, per_page=per_page)


@router.get(
    "/search",
    response_model=ItemsListResponse,
    summary="Search items by name",
    description="Case-insensitive partial search on item names."
)
def search_items(
    search: str = Query(..., min_length=1, description="Search query string"),
    limit: int = Query(10, ge=1, le=50, description="Max results"),
    service: ItemService = Depends(get_item_service)
):
    """GET /api/v1/items/search?search=macbook&limit=10 - Search items."""
    logger.info(f"GET /items/search - Query: {search}")
    result = service.search_items(search, limit)
    return {
        "success": True,
        "message": result["message"],
        "data": result["data"],
        "total": len(result["data"]),
        "page": 1,
        "per_page": limit,
        "total_pages": 1
    }


@router.get(
    "/{item_id}",
    response_model=ItemResponse,
    summary="Get item by ID",
    description="Retrieve a single item by its MongoDB ObjectId."
)
def get_item(
    item_id: str,
    service: ItemService = Depends(get_item_service)
):
    """GET /api/v1/items/{item_id} - Get a specific item."""
    logger.info(f"GET /items/{item_id} - Fetching single item")
    result = service.get_item(item_id)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result["message"]
        )
    
    return result


@router.patch(
    "/{item_id}",
    response_model=ItemResponse,
    summary="Update item",
    description="Partially update an item. Only provided fields are updated."
)
def update_item(
    item_id: str,
    item_update: ItemUpdate,
    service: ItemService = Depends(get_item_service)
):
    """PATCH /api/v1/items/{item_id} - Update an existing item."""
    logger.info(f"PATCH /items/{item_id} - Updating item")
    result = service.update_item(item_id, item_update)
    
    if not result["success"]:
        if "not found" in result["message"].lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result["message"]
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )
    
    return result


@router.delete(
    "/{item_id}",
    response_model=ItemResponse,
    summary="Delete item",
    description="Permanently delete an item by ID."
)
def delete_item(
    item_id: str,
    service: ItemService = Depends(get_item_service)
):
    """DELETE /api/v1/items/{item_id} - Delete an item."""
    logger.info(f"DELETE /items/{item_id} - Deleting item")
    result = service.delete_item(item_id)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result["message"]
        )
    
    return result