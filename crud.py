from sqlalchemy.orm import Session
from sqlalchemy import or_
from models import ChatMessage, Product, Transaction
import schemas

def get_chat_messages(db: Session, skip: int = 0, limit: int = 100):
    return db.query(ChatMessage).order_by(ChatMessage.timestamp.desc()).offset(skip).limit(limit).all()

def create_chat_message(db: Session, message: schemas.ChatMessageCreate):
    db_message = ChatMessage(**message.dict())
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def get_products(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Product).filter(Product.is_available == True).offset(skip).limit(limit).all()

def get_product(db: Session, product_id: int):
    return db.query(Product).filter(Product.id == product_id).first()

def create_product(db: Session, product: schemas.ProductCreate):
    db_product = Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def update_product_availability(db: Session, product_id: int, is_available: bool):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if db_product:
        db_product.is_available = is_available
        db.commit()
        db.refresh(db_product)
    return db_product

def create_transaction(db: Session, transaction: schemas.TransactionCreate):
    product = get_product(db, transaction.product_id)
    if not product or product.quantity < transaction.quantity:
        return None
    
    total_price = product.price * transaction.quantity
    db_transaction = Transaction(
        **transaction.dict(),
        total_price=total_price
    )
    db.add(db_transaction)
    
    # Update product quantity
    product.quantity -= transaction.quantity
    if product.quantity == 0:
        product.is_available = False
    
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

def search_products(db: Session, query: str, category: str = None, max_price: float = None):
    search_query = db.query(Product).filter(Product.is_available == True)
    
    if query:
        search_query = search_query.filter(
            or_(
                Product.name.ilike(f"%{query}%"),
                Product.description.ilike(f"%{query}%"),
                Product.category.ilike(f"%{query}%")
            )
        )
    
    if category:
        search_query = search_query.filter(Product.category.ilike(f"%{category}%"))
    
    if max_price:
        search_query = search_query.filter(Product.price <= max_price)
    
    return search_query.all()