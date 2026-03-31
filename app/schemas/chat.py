from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.schemas.product import Product


class ChatMessageCreate(BaseModel):
    sender: str
    message: str


class ChatMessage(BaseModel):
    id: int
    sender: str
    message: str
    timestamp: datetime
    is_product_offer: bool
    product_id: Optional[int] = None

    model_config = {"from_attributes": True}


class ChatResponse(BaseModel):
    response: str
    recommendations: list[Product]
    chat_history: list[ChatMessage]
