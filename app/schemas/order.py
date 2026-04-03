from datetime import datetime
from typing import Optional

from pydantic import BaseModel


PAYMENT_METHODS = {
    "esewa": {"name": "eSewa", "icon": "📱", "desc": "eSewa Mobile Wallet"},
    "khalti": {"name": "Khalti", "icon": "💜", "desc": "Khalti Digital Wallet"},
    "ime_pay": {"name": "IME Pay", "icon": "💚", "desc": "IME Pay"},
    "bank": {"name": "Bank Transfer", "icon": "🏦", "desc": "Bank Transfer / बैंक ट्रान्सफर"},
    "cash": {"name": "Cash on Delivery", "icon": "💵", "desc": "Cash on Delivery / क्यास अन डेलिभरी"},
}


class OrderCreate(BaseModel):
    product_id: int
    negotiation_id: Optional[int] = None
    quantity: int
    delivery_address: str
    delivery_phone: str
    delivery_note: Optional[str] = None
    payment_method: str = "esewa"


class OrderResponse(BaseModel):
    id: int
    product_id: int
    negotiation_id: Optional[int] = None
    buyer: str
    seller: str
    product_name: str
    quantity: int
    unit_price: float
    total_price: float
    payment_method: str
    payment_status: str
    amount_paid: float
    delivery_address: Optional[str] = None
    delivery_phone: Optional[str] = None
    delivery_note: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PaymentUpdate(BaseModel):
    amount: float


class PaymentMethodInfo(BaseModel):
    key: str
    name: str
    icon: str
    desc: str
