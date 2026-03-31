from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.product import Product
from app.schemas.product import ProductCreate


def get_products(db: Session, skip: int = 0, limit: int = 100) -> list[Product]:
    return (
        db.query(Product)
        .filter(Product.is_available == True)  # noqa: E712
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_product(db: Session, product_id: int) -> Product | None:
    return db.query(Product).filter(Product.id == product_id).first()


def create_product(db: Session, product: ProductCreate) -> Product:
    db_product = Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def update_product_availability(db: Session, product_id: int, is_available: bool) -> Product | None:
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if db_product:
        db_product.is_available = is_available
        db.commit()
        db.refresh(db_product)
    return db_product


def search_products(
    db: Session,
    query: str = "",
    category: str | None = None,
    max_price: float | None = None,
) -> list[Product]:
    search = db.query(Product).filter(Product.is_available == True)  # noqa: E712

    if query:
        search = search.filter(
            or_(
                Product.name.ilike(f"%{query}%"),
                Product.description.ilike(f"%{query}%"),
                Product.category.ilike(f"%{query}%"),
            )
        )
    if category:
        search = search.filter(Product.category.ilike(f"%{category}%"))
    if max_price:
        search = search.filter(Product.price <= max_price)

    return search.all()
