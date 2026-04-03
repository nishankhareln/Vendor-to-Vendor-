from datetime import datetime

from sqlalchemy.orm import Session

from app.models.negotiation import Negotiation
from app.models.product import Product


def create_negotiation(
    db: Session,
    product_id: int,
    buyer: str,
    offered_price: float,
    message: str | None = None,
) -> Negotiation | None:
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product or not product.is_available:
        return None

    nego = Negotiation(
        product_id=product_id,
        buyer=buyer,
        seller=product.supplier,
        original_price=product.price,
        offered_price=offered_price,
        status="open",
        last_message=message,
    )
    db.add(nego)
    db.commit()
    db.refresh(nego)
    return nego


def counter_negotiation(
    db: Session,
    negotiation_id: int,
    counter_price: float,
    message: str | None = None,
) -> Negotiation | None:
    nego = db.query(Negotiation).filter(Negotiation.id == negotiation_id).first()
    if not nego or nego.status not in ("open", "countered"):
        return None

    nego.counter_price = counter_price
    nego.status = "countered"
    nego.last_message = message
    nego.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(nego)
    return nego


def accept_negotiation(db: Session, negotiation_id: int) -> Negotiation | None:
    nego = db.query(Negotiation).filter(Negotiation.id == negotiation_id).first()
    if not nego or nego.status not in ("open", "countered"):
        return None

    # Final price = counter_price (if seller countered) or offered_price (if seller accepts buyer's offer)
    nego.final_price = nego.counter_price or nego.offered_price
    nego.status = "accepted"
    nego.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(nego)
    return nego


def reject_negotiation(db: Session, negotiation_id: int) -> Negotiation | None:
    nego = db.query(Negotiation).filter(Negotiation.id == negotiation_id).first()
    if not nego or nego.status not in ("open", "countered"):
        return None

    nego.status = "rejected"
    nego.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(nego)
    return nego


def get_negotiation(db: Session, negotiation_id: int) -> Negotiation | None:
    return db.query(Negotiation).filter(Negotiation.id == negotiation_id).first()


def get_negotiations_for_product(db: Session, product_id: int) -> list[Negotiation]:
    return (
        db.query(Negotiation)
        .filter(Negotiation.product_id == product_id)
        .order_by(Negotiation.created_at.desc())
        .all()
    )


def get_negotiations_for_user(db: Session, username: str) -> list[Negotiation]:
    return (
        db.query(Negotiation)
        .filter((Negotiation.buyer == username) | (Negotiation.seller == username))
        .filter(Negotiation.status.in_(["open", "countered", "accepted"]))
        .order_by(Negotiation.updated_at.desc())
        .all()
    )
