from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from models import Notification, User
from schemas import NotificationCreate, NotificationUpdate, NotificationOut
from database import get_db
from routers.auth import get_current_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
logger.info("Notifications router initialized")

@router.post("/", response_model=NotificationOut, status_code=status.HTTP_201_CREATED)
async def create_notification(
    notification_data: NotificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new notification for a user"""
    logger.info(f"Creating notification for user: {current_user.email}")
    new_notification = Notification(
        user_id=current_user.id,
        order_id=notification_data.order_id,
        type=notification_data.type,
        title=notification_data.title,
        message=notification_data.message,
        is_read=False
    )
    db.add(new_notification)
    db.commit()
    db.refresh(new_notification)
    logger.info(f"Notification created: {new_notification.id}")
    return new_notification

@router.get("/", response_model=List[NotificationOut])
async def list_notifications(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all notifications for the current user"""
    logger.info(f"Fetching notifications for user: {current_user.email}, skip={skip}, limit={limit}")
    notifications = (
        db.query(Notification)
        .filter(Notification.user_id == current_user.id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return notifications

@router.get("/{notification_id}", response_model=NotificationOut)
async def get_notification(
    notification_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific notification by ID"""
    logger.info(f"Fetching notification {notification_id} for user: {current_user.email}")
    notification = (
        db.query(Notification)
        .filter(Notification.id == notification_id, Notification.user_id == current_user.id)
        .first()
    )
    if not notification:
        logger.error(f"Notification not found: {notification_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    return notification

@router.put("/{notification_id}", response_model=NotificationOut)
async def update_notification(
    notification_id: str,
    notification_data: NotificationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a notification (e.g., mark as read)"""
    logger.info(f"Updating notification {notification_id} for user: {current_user.email}")
    notification = (
        db.query(Notification)
        .filter(Notification.id == notification_id, Notification.user_id == current_user.id)
        .first()
    )
    if not notification:
        logger.error(f"Notification not found: {notification_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    for key, value in notification_data.dict(exclude_unset=True).items():
        setattr(notification, key, value)
    db.commit()
    db.refresh(notification)
    logger.info(f"Notification updated: {notification_id}")
    return notification

@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(
    notification_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a notification"""
    logger.info(f"Deleting notification {notification_id} for user: {current_user.email}")
    notification = (
        db.query(Notification)
        .filter(Notification.id == notification_id, Notification.user_id == current_user.id)
        .first()
    )
    if not notification:
        logger.error(f"Notification not found: {notification_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    db.delete(notification)
    db.commit()
    logger.info(f"Notification deleted: {notification_id}")