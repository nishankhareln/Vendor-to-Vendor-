from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.crud import product as product_crud
from app.schemas.product import Product, ProductCreate

router = APIRouter()


@router.get("", response_model=list[Product])
async def list_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return product_crud.get_products(db, skip=skip, limit=limit)


@router.get("/{category}", response_model=list[Product])
async def get_by_category(category: str, db: Session = Depends(get_db)):
    return product_crud.search_products(db, query="", category=category)


@router.post("", response_model=Product)
async def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    return product_crud.create_product(db, product)
