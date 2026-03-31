from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ProductCreate(BaseModel):
    name: str
    category: str
    price: float
    supplier: str
    description: Optional[str] = None
    quantity: int = 1


class Product(BaseModel):
    id: int
    name: str
    category: str
    price: float
    supplier: str
    description: Optional[str] = None
    quantity: int
    is_available: bool
    created_at: datetime

    model_config = {"from_attributes": True}
