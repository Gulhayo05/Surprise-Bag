from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from datetime import datetime, UTC
from fastapi import status
import logging

from database import get_db
from models import Order, SurpriseBag, User
from schemas import OrderCreate, OrderOut, OrderStatus
from routers.auth import get_current_customer, get_current_business_owner, get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_customer)
):
    """Create a new order (status: pending)"""
    logger.info(f"Attempting to create order for user: {current_user.email}")
    
    # Verify bag exists and has sufficient quantity
    bag = db.query(SurpriseBag).filter(
        SurpriseBag.id == order_data.bag_id,
        SurpriseBag.is_active == True,
        SurpriseBag.quantity_available >= order_data.quantity
    ).first()
    
    if not bag:
        logger.error(f"Bag not available: {order_data.bag_id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bag not available or insufficient quantity"
        )

    # Create new order
    new_order = Order(
        customer_id=current_user.id,
        bag_id=order_data.bag_id,
        quantity=order_data.quantity,
        total_price=bag.discount_price * order_data.quantity,
        status=OrderStatus.pending,
        pickup_code=str(uuid.uuid4())[:8].upper(),
        created_at=datetime.now(UTC)
    )

    # Update bag quantity
    bag.quantity_available -= order_data.quantity

    # Save to database
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    
    return new_order

@router.put("/{order_id}/confirm", response_model=OrderOut)
async def confirm_order(
    order_id: uuid.UUID,
    current_user: User = Depends(get_current_business_owner),
    db: Session = Depends(get_db)
):
    """Confirm an order (status: pending → confirmed)"""
    db_order = db.query(Order).join(SurpriseBag).filter(
        Order.id == order_id,
        SurpriseBag.business_id == current_user.id,
        Order.status == OrderStatus.pending
    ).first()
    
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found or already processed")
    
    db_order.status = OrderStatus.confirmed
    db_order.updated_at = datetime.now(UTC)
    db.commit()
    db.refresh(db_order)
    return db_order

@router.put("/{order_id}/complete", response_model=OrderOut)
async def complete_order(
    order_id: uuid.UUID,
    current_user: User = Depends(get_current_business_owner),
    db: Session = Depends(get_db)
):
    """Complete an order (status: confirmed → completed)"""
    db_order = db.query(Order).join(SurpriseBag).filter(
        Order.id == order_id,
        SurpriseBag.business_id == current_user.id,
        Order.status == OrderStatus.confirmed
    ).first()
    
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found or not confirmed")
    
    db_order.status = OrderStatus.completed
    db_order.updated_at = datetime.now(UTC)
    db.commit()
    db.refresh(db_order)
    return db_order

@router.put("/{order_id}/cancel", response_model=OrderOut)
async def cancel_order(
    order_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel an order (returns quantity if not completed)"""
    db_order = db.query(Order).filter(Order.id == order_id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if current_user.role == "customer" and db_order.customer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your order")
    elif current_user.role == "business_owner":
        db_bag = db.query(SurpriseBag).filter(
            SurpriseBag.id == db_order.bag_id,
            SurpriseBag.business_id == current_user.id
        ).first()
        if not db_bag:
            raise HTTPException(status_code=403, detail="Not your business order")
    
    if db_order.status in [OrderStatus.pending, OrderStatus.confirmed]:
        db_bag = db.query(SurpriseBag).filter(SurpriseBag.id == db_order.bag_id).first()
        db_bag.quantity_available += db_order.quantity
    
    db_order.status = OrderStatus.cancelled
    db_order.updated_at = datetime.now(UTC)
    db.commit()
    db.refresh(db_order)
    return db_order

@router.get("/", response_model=List[OrderOut])
async def list_orders(
    status: Optional[OrderStatus] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List orders with optional status filter"""
    query = db.query(Order)
    
    if current_user.role == "customer":
        query = query.filter(Order.customer_id == current_user.id)
    elif current_user.role == "business_owner":
        query = query.join(SurpriseBag).filter(SurpriseBag.business_id == current_user.id)
    
    if status:
        query = query.filter(Order.status == status)
    
    return query.order_by(Order.created_at.desc()).all()