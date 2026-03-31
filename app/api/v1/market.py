from fastapi import APIRouter, HTTPException

from app.schemas.market import CompareRequest, MarketPrice, PriceComparison
from app.services.product_engine import compare_price, get_all_market_prices, get_market_price, search_market_catalog

router = APIRouter()


@router.get("", response_model=list[MarketPrice])
async def list_market_prices():
    """Get all market prices / बजार भाउ हेर्नुहोस्"""
    return get_all_market_prices()


@router.get("/search", response_model=list[MarketPrice])
async def search_market(q: str):
    """Search market catalog (English or Nepali) / बजारमा खोज्नुहोस्"""
    results = search_market_catalog(q)
    if not results:
        raise HTTPException(status_code=404, detail=f"No products found for '{q}' / '{q}' को लागि कुनै उत्पादन भेटिएन")
    return results


@router.get("/{product}", response_model=MarketPrice)
async def get_price(product: str):
    """Get market price for a product / उत्पादनको बजार भाउ"""
    info = get_market_price(product)
    if not info:
        raise HTTPException(status_code=404, detail=f"Product '{product}' not found / '{product}' भेटिएन")
    return info


@router.post("/compare", response_model=PriceComparison)
async def compare(req: CompareRequest):
    """Compare offered price vs market rate / बजार भाउसँग तुलना गर्नुहोस्"""
    result = compare_price(req.product, req.price)
    if not result:
        raise HTTPException(status_code=404, detail=f"Product '{req.product}' not found / '{req.product}' भेटिएन")
    return result
