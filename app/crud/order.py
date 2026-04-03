from datetime import datetime

from sqlalchemy.orm import Session

from app.models.order import Order
from app.models.product import Product


def create_order(
    db: Session,
    product_id: int,
    buyer: str,
    quantity: int,
    unit_price: float,
    delivery_address: str,
    delivery_phone: str,
    payment_method: str,
    negotiation_id: int | None = None,
    delivery_note: str | None = None,
) -> Order | None:
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product or not product.is_available or product.quantity < quantity:
        return None

    total = unit_price * quantity
    order = Order(
        product_id=product_id,
        negotiation_id=negotiation_id,
        buyer=buyer,
        seller=product.supplier,
        product_name=product.name,
        quantity=quantity,
        unit_price=unit_price,
        total_price=total,
        payment_method=payment_method,
        delivery_address=delivery_address,
        delivery_phone=delivery_phone,
        delivery_note=delivery_note,
        status="confirmed",
        payment_status="pending",
    )
    db.add(order)

    # Reduce stock
    product.quantity -= quantity
    if product.quantity <= 0:
        product.is_available = False

    db.commit()
    db.refresh(order)
    return order


def pay_order(db: Session, order_id: int, amount: float) -> Order | None:
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        return None

    order.amount_paid += amount
    half = order.total_price / 2

    if order.amount_paid >= order.total_price:
        order.payment_status = "full_paid"
        order.status = "completed"
    elif order.amount_paid >= half:
        order.payment_status = "half_paid"
        if order.status == "confirmed":
            order.status = "half_paid"

    order.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(order)
    return order


def update_order_status(db: Session, order_id: int, status: str) -> Order | None:
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        return None
    order.status = status
    order.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(order)
    return order


def get_order(db: Session, order_id: int) -> Order | None:
    return db.query(Order).filter(Order.id == order_id).first()


def get_orders_for_user(db: Session, username: str) -> list[Order]:
    return (
        db.query(Order)
        .filter((Order.buyer == username) | (Order.seller == username))
        .order_by(Order.created_at.desc())
        .all()
    )
