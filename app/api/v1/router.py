from fastapi import APIRouter

from app.api.v1 import chat, market, products, transactions

router = APIRouter()
router.include_router(chat.router, prefix="/chat", tags=["chat"])
router.include_router(products.router, prefix="/products", tags=["products"])
router.include_router(transactions.router, prefix="/transactions", tags=["transactions"])
router.include_router(market.router, prefix="/market", tags=["market"])
