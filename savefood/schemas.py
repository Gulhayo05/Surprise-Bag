from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import List, Optional
from enum import Enum
from uuid import UUID

class UserRole(str, Enum):
    customer = "customer"
    business_owner = "business_owner"
    admin = "admin"

class OrderStatus(str, Enum):
    pending = "pending"
    confirmed = "confirmed"
    cancelled = "cancelled"
    completed = "completed"

class NotificationType(str, Enum):
    order_confirmation = "order_confirmation"
    pickup_reminder = "pickup_reminder"
    new_bag = "new_bag"
    order_update = "order_update"

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    name: str
    phone: Optional[str] = None
    role: UserRole = UserRole.customer

class UserOut(BaseModel):
    id: UUID
    email: EmailStr
    name: str
    phone: Optional[str]
    role: UserRole
    created_at: datetime
    is_active: bool

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8)
    name: Optional[str] = None
    phone: Optional[str] = None

class ShopCreate(BaseModel):
    name: str
    description: Optional[str] = None
    address: Optional[str] = None
    logo_url: Optional[str] = None

class ShopUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    logo_url: Optional[str] = None

class ShopOut(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    address: Optional[str]
    logo_url: Optional[str]
    is_approved: bool
    created_at: datetime

    class Config:
        from_attributes = True

class SurpriseBagCreate(BaseModel):
    title: str
    description: Optional[str] = None
    original_price: float = Field(..., gt=0)
    discount_price: float = Field(..., gt=0)
    quantity_available: int = Field(..., ge=1)
    pickup_start: datetime
    pickup_end: datetime
    image_urls: Optional[List[str]] = None


class SurpriseBagUpdate(BaseModel):  # Added to fix the ImportError
    title: Optional[str] = None
    description: Optional[str] = None
    original_price: Optional[float] = None
    discount_price: Optional[float] = None
    quantity_available: Optional[int] = None
    pickup_start: Optional[str] = None
    pickup_end: Optional[str] = None
    image_urls: Optional[List[str]] = None
    
class SurpriseBagOut(BaseModel):
    id: UUID
    business_id: UUID
    title: str
    description: Optional[str]
    original_price: float
    discount_price: float
    quantity_available: int
    quantity_sold: int
    pickup_start: datetime
    pickup_end: datetime
    image_urls: Optional[List[str]]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class OrderCreate(BaseModel):
    bag_id: UUID
    quantity: int = Field(..., ge=1)

class OrderOut(BaseModel):
    id: UUID
    customer_id: Optional[UUID]
    bag_id: UUID
    quantity: int
    total_price: float
    status: OrderStatus
    pickup_code: Optional[str]
    rating: Optional[int]
    feedback: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class OrderStatusUpdate(BaseModel):
    status: OrderStatus

class NotificationCreate(BaseModel):
    order_id: Optional[UUID] = None
    type: NotificationType
    title: str
    message: str

class NotificationUpdate(BaseModel):
    is_read: Optional[bool] = None

class NotificationOut(BaseModel):
    id: UUID
    user_id: UUID
    order_id: Optional[UUID]
    type: NotificationType
    title: str
    message: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True

class ReviewCreate(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    feedback: Optional[str] = None

class ReviewOut(BaseModel):
    order_id: UUID
    rating: int
    feedback: Optional[str]

class TagRecommendation(BaseModel):
    title: str
    description: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None


class OrderUpdate(BaseModel):  # Added to fix the import error
    status: Optional[str] = None
    quantity: Optional[int] = None