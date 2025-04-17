# routers/users.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import User
from schemas import UserOut
from routers.auth import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me", response_model=UserOut)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user's profile information"""
    return current_user

@router.put("/me", response_model=UserOut)
async def update_user_profile(
    name: str = None,
    phone: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user's profile"""
    if name:
        current_user.name = name
    if phone:
        current_user.phone = phone
    
    db.commit()
    db.refresh(current_user)
    return current_user

@router.delete("/me")
async def delete_user(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete current user's account"""
    db.delete(current_user)
    db.commit()
    return {"message": "User account deleted successfully"}