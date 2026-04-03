from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class NegotiationCreate(BaseModel):
    product_id: int
    buyer: str
    offered_price: float
    message: Optional[str] = None


class NegotiationCounter(BaseModel):
    counter_price: float
    message: Optional[str] = None


class NegotiationResponse(BaseModel):
    id: int
    product_id: int
    buyer: str
    seller: str
    original_price: float
    offered_price: float
    counter_price: Optional[float] = None
    final_price: Optional[float] = None
    status: str
    last_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
