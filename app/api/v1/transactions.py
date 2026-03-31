from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.crud import transaction as transaction_crud
from app.schemas.transaction import Transaction, TransactionCreate

router = APIRouter()


@router.post("", response_model=Transaction)
async def create_transaction(transaction: TransactionCreate, db: Session = Depends(get_db)):
    db_transaction = transaction_crud.create_transaction(db, transaction)
    if not db_transaction:
        raise HTTPException(status_code=400, detail="Product not available or insufficient quantity")
    return db_transaction
