from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class TransactionCreate(BaseModel):
    buyer: str
    seller: str
    product_id: int
    quantity: int


class Transaction(BaseModel):
    id: int
    buyer: str
    seller: str
    product_id: int
    quantity: int
    total_price: float
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
