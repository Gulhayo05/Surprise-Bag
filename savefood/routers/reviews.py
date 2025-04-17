# routers/reviews.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import uuid

from database import get_db
from models import Order, User, SurpriseBag  # Added SurpriseBag import
from schemas import OrderOut, OrderUpdate  # No need for SurpriseBag here since we use model directly
from routers.auth import get_current_customer
from schemas import OrderOut, OrderCreate

router = APIRouter(tags=["Reviews"])

@router.post("/{order_id}/review", response_model=OrderOut)
async def create_review(
    order_id: uuid.UUID,
    review_data: OrderUpdate,
    current_user: User = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """Add a review to a completed order"""
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.customer_id == current_user.id,
        Order.status == "completed"
    ).first()
    
    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found or not completed"
        )
    
    if review_data.rating is not None:
        order.rating = review_data.rating
    if review_data.feedback is not None:
        order.feedback = review_data.feedback
    
    db.commit()
    db.refresh(order)
    return order

@router.get("/business/{business_id}", response_model=List[OrderOut])
async def get_business_reviews(
    business_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """Get all reviews for a business"""
    reviews = db.query(Order).join(SurpriseBag).filter(
        SurpriseBag.business_id == business_id,
        Order.rating != None
    ).order_by(Order.updated_at.desc()).all()
    return reviews