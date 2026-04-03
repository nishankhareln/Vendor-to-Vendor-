from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.crud import negotiation as nego_crud
from app.schemas.negotiation import NegotiationCreate, NegotiationCounter, NegotiationResponse

router = APIRouter()


@router.post("", response_model=NegotiationResponse)
async def start_negotiation(data: NegotiationCreate, db: Session = Depends(get_db)):
    """Buyer makes an offer on a product / खरिदकर्ताले मोलमोलाई सुरु गर्छ"""
    nego = nego_crud.create_negotiation(
        db, data.product_id, data.buyer, data.offered_price, data.message
    )
    if not nego:
        raise HTTPException(status_code=400, detail="Product not available / उत्पादन उपलब्ध छैन")
    return nego


@router.post("/{negotiation_id}/counter", response_model=NegotiationResponse)
async def counter_offer(negotiation_id: int, data: NegotiationCounter, db: Session = Depends(get_db)):
    """Seller counters with a different price / विक्रेताले फरक मूल्य प्रस्ताव गर्छ"""
    nego = nego_crud.counter_negotiation(db, negotiation_id, data.counter_price, data.message)
    if not nego:
        raise HTTPException(status_code=400, detail="Cannot counter this negotiation")
    return nego


@router.post("/{negotiation_id}/accept", response_model=NegotiationResponse)
async def accept_offer(negotiation_id: int, db: Session = Depends(get_db)):
    """Accept the current offer / प्रस्ताव स्वीकार"""
    nego = nego_crud.accept_negotiation(db, negotiation_id)
    if not nego:
        raise HTTPException(status_code=400, detail="Cannot accept this negotiation")
    return nego


@router.post("/{negotiation_id}/reject", response_model=NegotiationResponse)
async def reject_offer(negotiation_id: int, db: Session = Depends(get_db)):
    """Reject the offer / प्रस्ताव अस्वीकार"""
    nego = nego_crud.reject_negotiation(db, negotiation_id)
    if not nego:
        raise HTTPException(status_code=400, detail="Cannot reject this negotiation")
    return nego


@router.get("/{negotiation_id}", response_model=NegotiationResponse)
async def get_negotiation(negotiation_id: int, db: Session = Depends(get_db)):
    nego = nego_crud.get_negotiation(db, negotiation_id)
    if not nego:
        raise HTTPException(status_code=404, detail="Negotiation not found")
    return nego


@router.get("/user/{username}", response_model=list[NegotiationResponse])
async def get_user_negotiations(username: str, db: Session = Depends(get_db)):
    """Get active negotiations for a user"""
    return nego_crud.get_negotiations_for_user(db, username)


@router.get("/product/{product_id}", response_model=list[NegotiationResponse])
async def get_product_negotiations(product_id: int, db: Session = Depends(get_db)):
    return nego_crud.get_negotiations_for_product(db, product_id)
