# routers/bags.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import uuid

from database import get_db
from models import SurpriseBag, User, Business
from schemas import SurpriseBagCreate, SurpriseBagOut, SurpriseBagUpdate
from routers.auth import get_current_business_owner

router = APIRouter(tags=["Bags"])

def recommend_tags(title: str, description: str) -> List[str]:
    """Generate tag recommendations based on title and description."""
    common_words = {"the", "and", "of", "to", "a", "in", "for", "with"}
    title_words = set(title.lower().split()) - common_words
    desc_words = set(description.lower().split()) - common_words
    return list(title_words.union(desc_words))[:5]

@router.post("/tags/recommend", response_model=List[str])
async def recommend_bag_tags(bag: SurpriseBagCreate):
    """Recommend tags based on bag title and description."""
    tags = recommend_tags(bag.title, bag.description)
    return tags

@router.post("/", response_model=SurpriseBagOut, status_code=201)
async def create_bag(
    bag: SurpriseBagCreate,
    current_user: User = Depends(get_current_business_owner),
    db: Session = Depends(get_db)
):
    """Create a new surprise bag"""
    business = db.query(Business).filter(Business.id == current_user.id).first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found for this user")
    if not business.is_approved:
        raise HTTPException(status_code=403, detail="Business must be approved to create bags")

    db_bag = SurpriseBag(
        business_id=business.id,
        title=bag.title,
        description=bag.description,
        original_price=bag.original_price,
        discount_price=bag.discount_price,
        quantity_available=bag.quantity_available,
        pickup_start=bag.pickup_start,
        pickup_end=bag.pickup_end,
        image_urls=bag.image_urls
    )

    db.add(db_bag)
    db.commit()
    db.refresh(db_bag)
    return db_bag

@router.put("/{bag_id}", response_model=SurpriseBagOut)
async def update_bag(
    bag_id: uuid.UUID,
    bag_update: SurpriseBagUpdate,
    current_user: User = Depends(get_current_business_owner),
    db: Session = Depends(get_db)
):
    """Update an existing surprise bag"""
    db_bag = db.query(SurpriseBag).filter(
        SurpriseBag.id == bag_id,
        SurpriseBag.business_id == current_user.id
    ).first()
    
    if not db_bag:
        raise HTTPException(status_code=404, detail="Bag not found or not owned by user")
    
    for field, value in bag_update.dict(exclude_unset=True).items():
        setattr(db_bag, field, value)
    
    db.commit()
    db.refresh(db_bag)
    return db_bag

@router.get("/{bag_id}", response_model=SurpriseBagOut)
async def get_bag(
    bag_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """Get details of a specific surprise bag"""
    db_bag = db.query(SurpriseBag).filter(SurpriseBag.id == bag_id).first()
    if not db_bag:
        raise HTTPException(status_code=404, detail="Bag not found")
    return db_bag

@router.delete("/{bag_id}", status_code=204)
async def delete_bag(
    bag_id: uuid.UUID,
    current_user: User = Depends(get_current_business_owner),
    db: Session = Depends(get_db)
):
    """Delete a specific surprise bag"""
    db_bag = db.query(SurpriseBag).filter(
        SurpriseBag.id == bag_id,
        SurpriseBag.business_id == current_user.id
    ).first()
    
    if not db_bag:
        raise HTTPException(status_code=404, detail="Bag not found or not owned by user")
    
    db.delete(db_bag)
    db.commit()
    return None

@router.get("/", response_model=List[SurpriseBagOut])
async def list_bags(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all surprise bags with pagination"""
    bags = db.query(SurpriseBag).offset(skip).limit(limit).all()
    return bags