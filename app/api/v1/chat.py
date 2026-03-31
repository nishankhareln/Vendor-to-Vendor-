from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.crud import chat as chat_crud
from app.crud import product as product_crud
from app.models.chat import ChatMessage
from app.schemas.chat import ChatMessageCreate, ChatResponse, ChatMessage as ChatMessageSchema
from app.schemas.product import ProductCreate
from app.services.product_engine import extract_product_info, compare_price

router = APIRouter()


@router.post("", response_model=ChatResponse)
async def send_message(message: ChatMessageCreate, db: Session = Depends(get_db)):
    product_info = extract_product_info(message.message)

    # Auto-create product listing if vendor is offering something
    if product_info["is_product_offer"]:
        product_data = ProductCreate(
            name=product_info["product_name"] or "Unknown Product",
            category=product_info["product_category"] or "general",
            price=product_info["price"] or 0.0,
            supplier=message.sender,
            description=product_info["description"],
            quantity=product_info["quantity"] or 1,
        )
        product_crud.create_product(db, product_data)

    # Build system response with market comparison
    response = ""
    if product_info["matched_key"] and product_info["price"]:
        comparison = compare_price(product_info["matched_key"], product_info["price"])
        if comparison:
            response = (
                f"Market Info ({comparison['name_np']}): "
                f"बजार भाउ Rs.{comparison['market_price']}/{comparison['unit']} | "
                f"Offered: Rs.{comparison['offered_price']} | "
                f"{comparison['verdict_np']} ({comparison['difference_pct']:+.1f}%)"
            )
    elif product_info["matched_key"]:
        from app.services.product_engine import get_market_price
        mp = get_market_price(product_info["matched_key"])
        if mp:
            response = (
                f"Market Info ({mp['name_np']}): "
                f"बजार भाउ Rs.{mp['market_price']}/{mp['unit']} | "
                f"Range: Rs.{mp['price_min']} - Rs.{mp['price_max']}"
            )

    chat_crud.create_chat_message(db, message)

    recommendations = product_crud.get_products(db)
    history = chat_crud.get_chat_messages(db)

    return ChatResponse(
        response=response,
        recommendations=recommendations[-5:],
        chat_history=history[-10:],
    )


@router.get("/history", response_model=list[ChatMessageSchema])
async def get_history(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return chat_crud.get_chat_messages(db, skip=skip, limit=limit)


@router.delete("/clear")
async def clear_history(db: Session = Depends(get_db)):
    db.query(ChatMessage).delete()
    db.commit()
    return {"message": "Chat history cleared / च्याट इतिहास मेटाइयो"}
