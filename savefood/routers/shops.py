from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from models import Business, User
from schemas import ShopCreate, ShopOut, ShopUpdate
from database import get_db
from routers.auth import get_current_business_owner
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
logger.info("Shops router initialized")

@router.post("/", response_model=ShopOut, status_code=status.HTTP_201_CREATED)
async def create_shop(
    shop_data: ShopCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_business_owner)
):
    """Create a new shop for a business owner"""
    logger.info(f"Creating shop for user: {current_user.email}")
    existing_shop = db.query(Business).filter(Business.owner_id == current_user.id).first()
    if existing_shop:
        logger.error(f"User already has a shop: {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already has a shop"
        )
    new_shop = Business(
        owner_id=current_user.id,
        name=shop_data.name,
        description=shop_data.description,
        address=shop_data.address,
        logo_url=shop_data.logo_url,
        is_approved=False
    )
    db.add(new_shop)
    db.commit()
    db.refresh(new_shop)
    logger.info(f"Shop created: {new_shop.id}")
    return new_shop

@router.get("/", response_model=List[ShopOut])
async def list_shops(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all shops with pagination"""
    logger.info(f"Fetching shops: skip={skip}, limit={limit}")
    shops = db.query(Business).offset(skip).limit(limit).all()
    return shops

@router.get("/{shop_id}", response_model=ShopOut)
async def get_shop(
    shop_id: str,
    db: Session = Depends(get_db)
):
    """Get a specific shop by ID"""
    logger.info(f"Fetching shop: {shop_id}")
    shop = db.query(Business).filter(Business.id == shop_id).first()
    if not shop:
        logger.error(f"Shop not found: {shop_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shop not found"
        )
    return shop

@router.put("/{shop_id}", response_model=ShopOut)
async def update_shop(
    shop_id: str,
    shop_data: ShopUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_business_owner)
):
    """Update a shop's details"""
    logger.info(f"Updating shop {shop_id} for user: {current_user.email}")
    shop = db.query(Business).filter(Business.id == shop_id).first()
    if not shop:
        logger.error(f"Shop not found: {shop_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shop not found"
        )
    if shop.owner_id != current_user.id:
        logger.error(f"Unauthorized update attempt by user: {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this shop"
        )
    for key, value in shop_data.dict(exclude_unset=True).items():
        setattr(shop, key, value)
    db.commit()
    db.refresh(shop)
    logger.info(f"Shop updated: {shop_id}")
    return shop

@router.delete("/{shop_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_shop(
    shop_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_business_owner)
):
    """Delete a shop"""
    logger.info(f"Deleting shop {shop_id} for user: {current_user.email}")
    shop = db.query(Business).filter(Business.id == shop_id).first()
    if not shop:
        logger.error(f"Shop not found: {shop_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shop not found"
        )
    if shop.owner_id != current_user.id:
        logger.error(f"Unauthorized delete attempt by user: {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this shop"
        )
    db.delete(shop)
    db.commit()
    logger.info(f"Shop deleted: {shop_id}")