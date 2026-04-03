from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.crud import order as order_crud
from app.crud import negotiation as nego_crud
from app.schemas.order import OrderCreate, OrderResponse, PaymentUpdate, PaymentMethodInfo, PAYMENT_METHODS

router = APIRouter()


@router.get("/payment-methods", response_model=list[PaymentMethodInfo])
async def list_payment_methods():
    """List available payment methods / उपलब्ध भुक्तानी विधिहरू"""
    return [
        PaymentMethodInfo(key=k, name=v["name"], icon=v["icon"], desc=v["desc"])
        for k, v in PAYMENT_METHODS.items()
    ]


@router.post("", response_model=OrderResponse)
async def create_order(data: OrderCreate, buyer: str = "Vendor B / व्यापारी ख", db: Session = Depends(get_db)):
    """Place an order after negotiation / अर्डर दिनुहोस्"""
    # Determine price: from negotiation or product listing
    unit_price = None
    if data.negotiation_id:
        nego = nego_crud.get_negotiation(db, data.negotiation_id)
        if nego and nego.status == "accepted" and nego.final_price:
            unit_price = nego.final_price

    if unit_price is None:
        from app.crud.product import get_product
        product = get_product(db, data.product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        unit_price = product.price

    order = order_crud.create_order(
        db=db,
        product_id=data.product_id,
        buyer=buyer,
        quantity=data.quantity,
        unit_price=unit_price,
        delivery_address=data.delivery_address,
        delivery_phone=data.delivery_phone,
        payment_method=data.payment_method,
        negotiation_id=data.negotiation_id,
        delivery_note=data.delivery_note,
    )
    if not order:
        raise HTTPException(status_code=400, detail="Product not available or insufficient stock / स्टक अपर्याप्त")
    return order


@router.post("/{order_id}/pay", response_model=OrderResponse)
async def make_payment(order_id: int, data: PaymentUpdate, db: Session = Depends(get_db)):
    """Make a payment (half or full) / भुक्तानी गर्नुहोस्"""
    order = order_crud.pay_order(db, order_id, data.amount)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.post("/{order_id}/ship", response_model=OrderResponse)
async def mark_shipped(order_id: int, db: Session = Depends(get_db)):
    """Seller marks order as shipped / पठाइयो"""
    order = order_crud.update_order_status(db, order_id, "shipped")
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.post("/{order_id}/deliver", response_model=OrderResponse)
async def mark_delivered(order_id: int, db: Session = Depends(get_db)):
    """Mark order as delivered / डेलिभर भयो"""
    order = order_crud.update_order_status(db, order_id, "delivered")
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(order_id: int, db: Session = Depends(get_db)):
    order = order_crud.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.get("/user/{username}", response_model=list[OrderResponse])
async def get_user_orders(username: str, db: Session = Depends(get_db)):
    return order_crud.get_orders_for_user(db, username)
