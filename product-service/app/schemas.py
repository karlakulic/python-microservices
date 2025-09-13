from pydantic import BaseModel, Field
from typing import Optional, Annotated
from decimal import Decimal
from datetime import datetime

Money = Annotated[Decimal, Field(max_digits=10, decimal_places=2, ge=0)]

class ProductBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    sku: str = Field(min_length=1, max_length=64)
    description: Optional[str] = None
    price: float
    currency: str = Field(default="EUR", min_length=3, max_length=3)
    stock: int = Field(default=0, ge=0)
    is_active: bool = True

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    sku: Optional[str] = Field(default=None, min_length=1, max_length=64)
    description: Optional[str] = None
    price: Optional[float] = None
    currency: Optional[str] = Field(default=None, min_length=3, max_length=3)
    stock: Optional[int] = Field(default=None, ge=0)
    is_active: Optional[bool] = None

class ProductRead(ProductBase):
    id: str
    user_id: str
    price: float
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}

class StockAdjust(BaseModel):
    delta: int = Field(..., description="Promjena zalihe, može biti negativna")
    reason: Optional[str] = None
