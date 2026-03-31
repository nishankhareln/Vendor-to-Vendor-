from sqlalchemy.orm import Session

from app.crud.product import get_product
from app.models.transaction import Transaction
from app.schemas.transaction import TransactionCreate


def create_transaction(db: Session, transaction: TransactionCreate) -> Transaction | None:
    product = get_product(db, transaction.product_id)
    if not product or product.quantity < transaction.quantity:
        return None

    total_price = product.price * transaction.quantity
    db_transaction = Transaction(**transaction.model_dump(), total_price=total_price)
    db.add(db_transaction)

    product.quantity -= transaction.quantity
    if product.quantity == 0:
        product.is_available = False

    db.commit()
    db.refresh(db_transaction)
    return db_transaction
