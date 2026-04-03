from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Negotiation(Base):
    __tablename__ = "negotiations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    product_id: Mapped[int] = mapped_column(Integer, index=True)
    buyer: Mapped[str] = mapped_column(String)
    seller: Mapped[str] = mapped_column(String)
    # Price tracking
    original_price: Mapped[float] = mapped_column(Float)
    offered_price: Mapped[float] = mapped_column(Float)
    counter_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    final_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    # Status: open → countered → accepted → rejected → expired
    status: Mapped[str] = mapped_column(String, default="open")
    last_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
