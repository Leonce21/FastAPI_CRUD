"""
Pydantic Schemas Module
======================
Schemas define the shape of request/response data.
Pydantic automatically validates incoming data against these schemas,
ensuring type safety and providing clear error messages.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class ItemBase(BaseModel):
    """
    Base schema with common fields for all item operations.
    Used as parent class for create/update/read schemas.
    """
    
    # Field(...) means required, with description for Swagger docs
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Name of the item",
        examples=["Laptop Computer"]
    )
    
    description: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Detailed description of the item",
        examples=["High-performance laptop for development"]
    )
    
    price: float = Field(
        ...,
        gt=0,  # Greater than 0
        description="Price in USD",
        examples=[999.99]
    )
    
    quantity: int = Field(
        default=0,
        ge=0,  # Greater than or equal to 0
        description="Available quantity in stock",
        examples=[10]
    )
    
    category: Optional[str] = Field(
        default="general",
        description="Item category for grouping",
        examples=["electronics"]
    )


class ItemCreate(ItemBase):
    """
    Schema for creating a new item.
    Inherits all fields from ItemBase (all required except defaults).
    """
    pass  # No additional fields needed for creation


class ItemUpdate(BaseModel):
    """
    Schema for updating an existing item.
    All fields are optional since updates can be partial.
    """
    
    # Optional fields allow partial updates (PATCH semantic)
    name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=100,
        description="Updated name"
    )
    
    description: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Updated description"
    )
    
    price: Optional[float] = Field(
        default=None,
        gt=0,
        description="Updated price"
    )
    
    quantity: Optional[int] = Field(
        default=None,
        ge=0,
        description="Updated quantity"
    )
    
    category: Optional[str] = Field(
        default=None,
        description="Updated category"
    )


class ItemInDB(ItemBase):
    """
    Schema representing an item as stored in MongoDB.
    Includes database-generated fields like _id and timestamps.
    """
    
    # ConfigDict allows Pydantic to work with MongoDB's _id field
    model_config = ConfigDict(
        populate_by_name=True,  # Allow both _id and id
        json_schema_extra={
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "name": "Laptop Computer",
                "description": "High-performance laptop",
                "price": 999.99,
                "quantity": 10,
                "category": "electronics",
                "created_at": "2024-01-15T10:30:00",
                "updated_at": "2024-01-15T10:30:00"
            }
        }
    )
    
    # MongoDB's ObjectId stored as string for JSON serialization
    id: str = Field(
        ...,
        alias="_id",  # Maps MongoDB's _id to Python's id
        description="MongoDB ObjectId (auto-generated)"
    )
    
    created_at: datetime = Field(
        ...,
        description="Timestamp when item was created"
    )
    
    updated_at: datetime = Field(
        ...,
        description="Timestamp when item was last updated"
    )


class ItemResponse(BaseModel):
    """
    Wrapper schema for API responses.
    Provides consistent response structure with metadata.
    """
    
    success: bool = Field(default=True, description="Operation success status")
    message: str = Field(default="Operation completed", description="Status message")
    data: Optional[ItemInDB] = Field(default=None, description="Item data")
    
    # Allow arbitrary types for flexibility
    model_config = ConfigDict(arbitrary_types_allowed=True)


class ItemsListResponse(BaseModel):
    """
    Schema for listing multiple items with pagination info.
    """
    
    success: bool = True
    message: str = "Items retrieved successfully"
    data: list[ItemInDB] = []
    total: int = Field(..., description="Total number of items")
    page: int = Field(default=1, description="Current page number")
    per_page: int = Field(default=10, description="Items per page")
    total_pages: int = Field(default=1, description="Total number of pages")