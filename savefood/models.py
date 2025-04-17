# models.py
import enum
import uuid
from datetime import datetime
from typing import List
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy import Column, Integer, String, Float, ForeignKey

from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, 
    Numeric, JSON, ForeignKey, Enum as SQLEnum, Index
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base

# Enums
class UserRole(str, enum.Enum):
    customer = "customer"
    business_owner = "business_owner"
    admin = "admin"

class OrderStatus(str, enum.Enum):
    pending = "pending"
    confirmed = "confirmed"
    cancelled = "cancelled"
    completed = "completed"

class NotificationType(str, enum.Enum):
    order_confirmation = "order_confirmation"
    pickup_reminder = "pickup_reminder"
    new_bag = "new_bag"
    order_update = "order_update"

# Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    role = Column(SQLEnum(UserRole), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    is_active = Column(Boolean, default=True)
    device_token = Column(String(255), nullable=True)
    
    # Relationships
    business = relationship("Business", back_populates="user", uselist=False, cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="customer")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")

class Business(Base):
    __tablename__ = "businesses"
    __table_args__ = (
        Index('ix_business_name', 'name'),
    )
    is_approved = Column(Boolean, default=False)
    
    id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    address = Column(String(255))
    logo_url = Column(String(255))
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="business")
    bags = relationship("SurpriseBag", back_populates="business", cascade="all, delete-orphan")

class SurpriseBag(Base):
    __tablename__ = "surprise_bags"
    __table_args__ = (
        Index('ix_surprise_bag_business', 'business_id'),
        Index('ix_surprise_bag_active', 'is_active'),
    )
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    business_id = Column(UUID(as_uuid=True), ForeignKey('businesses.id', ondelete='CASCADE'), nullable=False)
    title = Column(String(100), nullable=False)
    description = Column(Text)
    original_price = Column(Numeric(10, 2), nullable=False)
    discount_price = Column(Numeric(10, 2), nullable=False)
    quantity_available = Column(Integer, nullable=False)
    quantity_sold = Column(Integer, default=0)
    pickup_start = Column(DateTime, nullable=False)
    pickup_end = Column(DateTime, nullable=False)
    image_urls = Column(JSON)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    business = relationship("Business", back_populates="bags")
    orders = relationship("Order", back_populates="bag", cascade="all, delete-orphan")

class Order(Base):
    __tablename__ = "orders"
    __table_args__ = (
        Index('ix_order_customer', 'customer_id','bag_id', 'created_at', unique=True),
        Index('ix_order_status', 'status'),
    )
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='SET NULL'))
    bag_id = Column(UUID(as_uuid=True), ForeignKey('surprise_bags.id', ondelete='RESTRICT'), nullable=False)
    quantity = Column(Integer, nullable=False)
    total_price = Column(Numeric(10, 2), nullable=False)
    status = Column(SQLEnum(OrderStatus), default=OrderStatus.pending)
    pickup_code = Column(String(20), unique=True)
    rating = Column(Integer)
    feedback = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    customer = relationship("User", back_populates="orders")
    bag = relationship("SurpriseBag", back_populates="orders")
    notifications = relationship("Notification", back_populates="order", cascade="all, delete-orphan")

class Notification(Base):
    __tablename__ = "notifications"
    __table_args__ = (
        Index('ix_notification_user', 'user_id'),
        Index('ix_notification_read', 'is_read'),
    )
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    order_id = Column(UUID(as_uuid=True), ForeignKey('orders.id', ondelete='CASCADE'))
    type = Column(SQLEnum(NotificationType), nullable=False)
    title = Column(String(100), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="notifications")
    order = relationship("Order", back_populates="notifications")

