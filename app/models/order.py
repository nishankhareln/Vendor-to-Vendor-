from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    product_id: Mapped[int] = mapped_column(Integer, index=True)
    negotiation_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    buyer: Mapped[str] = mapped_column(String)
    seller: Mapped[str] = mapped_column(String)
    product_name: Mapped[str] = mapped_column(String)
    quantity: Mapped[int] = mapped_column(Integer)
    unit_price: Mapped[float] = mapped_column(Float)
    total_price: Mapped[float] = mapped_column(Float)
    # Payment
    payment_method: Mapped[str] = mapped_column(String, default="esewa")  # esewa, khalti, ime_pay, bank, cash
    payment_status: Mapped[str] = mapped_column(String, default="pending")  # pending → half_paid → full_paid
    amount_paid: Mapped[float] = mapped_column(Float, default=0.0)
    # Delivery
    delivery_address: Mapped[str | None] = mapped_column(Text, nullable=True)
    delivery_phone: Mapped[str | None] = mapped_column(String, nullable=True)
    delivery_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Status: confirmed → half_paid → shipped → delivered → completed
    status: Mapped[str] = mapped_column(String, default="confirmed")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
