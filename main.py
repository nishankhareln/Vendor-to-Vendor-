from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import crud
import models
import schemas
from database import SessionLocal, engine, get_db
from llm_integration import extract_product_info, generate_vendor_response
import uvicorn

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Vendor-to-Vendor Chat API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/chat", response_model=schemas.ChatResponse)
async def chat_endpoint(message: schemas.ChatMessageCreate, db: Session = Depends(get_db)):
    # Extract product information from message
    product_info = extract_product_info(message.message)
    
    # If this is a product offer, create a product record
    product_id = None
    if product_info["is_product_offer"]:
        product_data = {
            "name": product_info["product_name"],
            "category": product_info["product_category"],
            "price": product_info["price"],
            "supplier": message.sender,
            "description": product_info["description"],
            "quantity": product_info["quantity"]
        }
        product = crud.create_product(db, schemas.ProductCreate(**product_data))
        product_id = product.id
    
    # Create chat message (ONLY the user's message, no auto-response)
    db_message = crud.create_chat_message(db, message)
    
    # Get product recommendations
    recommendations = crud.get_products(db)
    
    # Get updated chat history
    updated_chat_history = crud.get_chat_messages(db)
    
    return schemas.ChatResponse(
        response="",  # Empty response since we're not auto-generating
        recommendations=recommendations[-5:],
        chat_history=updated_chat_history[-10:]
    )
    
@app.get("/chat/history", response_model=List[schemas.ChatMessage])
async def get_chat_history(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_chat_messages(db, skip=skip, limit=limit)

@app.delete("/chat/clear")
async def clear_chat(db: Session = Depends(get_db)):
    # In a real application, you might want to archive instead of delete
    db.query(models.ChatMessage).delete()
    db.commit()
    return {"message": "Chat history cleared"}

@app.get("/products", response_model=List[schemas.Product])
async def get_all_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_products(db, skip=skip, limit=limit)

@app.get("/products/{category}", response_model=List[schemas.Product])
async def get_products_by_category(category: str, db: Session = Depends(get_db)):
    return crud.search_products(db, query="", category=category)

@app.post("/products", response_model=schemas.Product)
async def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    return crud.create_product(db, product)

@app.post("/transactions", response_model=schemas.Transaction)
async def create_transaction(transaction: schemas.TransactionCreate, db: Session = Depends(get_db)):
    db_transaction = crud.create_transaction(db, transaction)
    if not db_transaction:
        raise HTTPException(status_code=400, detail="Product not available or insufficient quantity")
    return db_transaction

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)