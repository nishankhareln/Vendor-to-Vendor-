from typing import Optional

from pydantic import BaseModel


class MarketPrice(BaseModel):
    product: str
    name_np: str
    category: str
    unit: str
    market_price: float
    price_min: float
    price_max: float


class PriceComparison(BaseModel):
    product: str
    name_np: str
    category: str
    unit: str
    market_price: float
    price_min: float
    price_max: float
    offered_price: float
    difference: float
    difference_pct: float
    verdict: str
    verdict_np: str


class CompareRequest(BaseModel):
    product: str
    price: float
