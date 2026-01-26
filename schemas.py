from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ChatMessageBase(BaseModel):
    sender: str
    message: str

class ChatMessageCreate(ChatMessageBase):
    pass

class ChatMessage(ChatMessageBase):
    id: int
    timestamp: datetime
    is_product_offer: bool
    product_id: Optional[int] = None
    
    class Config:
        from_attributes = True

class ProductBase(BaseModel):
    name: str
    category: str
    price: float
    supplier: str
    description: Optional[str] = None
    quantity: int = 1

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int
    is_available: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class TransactionBase(BaseModel):
    buyer: str
    seller: str
    product_id: int
    quantity: int

class TransactionCreate(TransactionBase):
    pass

class Transaction(TransactionBase):
    id: int
    total_price: float
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class ChatResponse(BaseModel):
    response: str
    recommendations: List[Product]
    chat_history: List[ChatMessage]