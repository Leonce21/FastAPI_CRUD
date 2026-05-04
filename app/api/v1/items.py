"""
Item API Routes Module
======================
This module defines HTTP endpoints for item CRUD operations.
Routes are thin - they only handle HTTP concerns (status codes, request/response)
and delegate all business logic to the service layer.
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from app.schemas.item import ItemCreate, ItemUpdate, ItemResponse, ItemsListResponse
from app.services.item_service import ItemService
from app.repositories.item_repository import ItemRepository
from app.database import db
from app.core.logging_config import logger

# Create router with prefix and tags for Swagger organization
router = APIRouter(
    prefix="/items",  # All routes will be /api/v1/items/...
    tags=["Items"],   # Group name in Swagger UI
    responses={
        404: {"description": "Item not found"},
        500: {"description": "Internal server error"}
    }
)


async def get_item_service():
    """
    Dependency injection for ItemService.
    Creates service with repository injected with MongoDB collection.
    
    This function is called automatically by FastAPI for each request.
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
async def create_item(
    item: ItemCreate,
    service: ItemService = Depends(get_item_service)
):
    """
    POST /api/v1/items/
    
    Create a new item.
    
    - **name**: Item name (required, 1-100 chars)
    - **description**: Item description (optional, max 500 chars)
    - **price**: Price in USD (required, must be > 0)
    - **quantity**: Stock quantity (optional, default 0)
    - **category**: Category name (optional, default "general")
    """
    logger.info(f"POST /items - Creating item: {item.name}")
    result = await service.create_item(item)
    
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
    description="Retrieve paginated list of all items, sorted by newest first. Use page and per_page for pagination."
)
async def list_items(
    page: int = Query(1, ge=1, description="Page number (starts at 1)"),
    per_page: int = Query(10, ge=1, le=100, description="Number of items per page"),
    service: ItemService = Depends(get_item_service)
):
    """
    GET /api/v1/items/
    
    List all items with pagination.
    
    - **page**: Page number to retrieve (default 1)
    - **per_page**: Items per page (default 10, max 100)
    """
    # Calculate skip from page and per_page
    skip = (page - 1) * per_page
    
    logger.info(f"GET /items - Listing items (page={page}, per_page={per_page})")
    return await service.list_items(page=page, per_page=per_page)


@router.get(
    "/search",
    response_model=ItemsListResponse,
    summary="Search items by name",
    description="Case-insensitive partial search on item names."
)
async def search_items(
    search: str = Query(..., min_length=1, description="Search query string"),
    limit: int = Query(10, ge=1, le=50, description="Max results"),
    service: ItemService = Depends(get_item_service)
):
    """
    GET /api/v1/items/search?search=macbook&limit=10
    
    Search items by name (case-insensitive).
    """
    logger.info(f"GET /items/search - Query: {search}")
    result = await service.search_items(search, limit)
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
async def get_item(
    item_id: str,
    service: ItemService = Depends(get_item_service)
):
    """
    GET /api/v1/items/{item_id}
    
    Get a specific item by ID.
    
    - **item_id**: MongoDB ObjectId (24 character hex string)
    """
    logger.info(f"GET /items/{item_id} - Fetching single item")
    result = await service.get_item(item_id)
    
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
async def update_item(
    item_id: str,
    item_update: ItemUpdate,
    service: ItemService = Depends(get_item_service)
):
    """
    PATCH /api/v1/items/{item_id}
    
    Update an existing item (partial update allowed).
    
    - **item_id**: ID of item to update
    - **name**, **description**, **price**, **quantity**, **category**: Optional fields
    """
    logger.info(f"PATCH /items/{item_id} - Updating item")
    result = await service.update_item(item_id, item_update)
    
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
async def delete_item(
    item_id: str,
    service: ItemService = Depends(get_item_service)
):
    """
    DELETE /api/v1/items/{item_id}
    
    Delete an item.
    
    - **item_id**: ID of item to delete
    """
    logger.info(f"DELETE /items/{item_id} - Deleting item")
    result = await service.delete_item(item_id)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result["message"]
        )
    
    return result