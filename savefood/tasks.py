# tasks.py
from celery_config import celery_app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import SurpriseBag, Notification, User, NotificationType, Order  # Added Order import
from database import DATABASE_URL
import logging

# Database setup for Celery
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

logger = logging.getLogger(__name__)

@celery_app.task
def send_notification(user_id: str, title: str, message: str, type: str, order_id: str = None):
    """Send a notification to a user"""
    db = SessionLocal()
    try:
        notification = Notification(
            user_id=user_id,
            order_id=order_id,
            type=NotificationType(type),
            title=title,
            message=message
        )
        db.add(notification)
        db.commit()
        logger.info(f"Notification sent to user {user_id}: {title}")
    except Exception as e:
        db.rollback()
        logger.error(f"Error sending notification: {str(e)}")
    finally:
        db.close()

@celery_app.task
def check_expiring_bags():
    """Check for bags nearing pickup end time and notify customers"""
    db = SessionLocal()
    try:
        from datetime import datetime, timedelta
        now = datetime.utcnow()
        threshold = now + timedelta(hours=1)
        
        expiring_bags = db.query(SurpriseBag).filter(
            SurpriseBag.pickup_end.between(now, threshold),
            SurpriseBag.is_active == True
        ).all()
        
        for bag in expiring_bags:
            orders = db.query(Order).filter(
                Order.bag_id == bag.id,
                Order.status.in_(["pending", "confirmed"])
            ).all()
            
            for order in orders:
                send_notification.delay(
                    str(order.customer_id),
                    "Pickup Reminder",
                    f"Your surprise bag pickup ends at {bag.pickup_end}",
                    "pickup_reminder",
                    str(order.id)
                )
    except Exception as e:
        db.rollback()
        logger.error(f"Error checking expiring bags: {str(e)}")
    finally:
        db.close()