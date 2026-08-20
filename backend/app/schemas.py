from pydantic import BaseModel, EmailStr
from datetime import datetime, date
from typing import Optional, List
from enum import Enum

class UserRole(str, Enum):
    FARMER = "farmer"
    TRADER = "trader"
    COOPERATIVE = "cooperative"
    ADMIN = "admin"

# User Schemas
class UserBase(BaseModel):
    phone_number: str
    name: Optional[str] = None
    email: Optional[EmailStr] = None

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    phone_number: str
    password: str

class UserResponse(UserBase):
    id: int
    role: UserRole
    is_premium: bool
    reputation_score: int
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

# Price Schemas
class PriceBase(BaseModel):
    crop_id: int
    market_id: int
    grade: str
    price_etb: float
    price_type: Optional[str] = "wholesale"
    effective_date: date

class PriceCreate(PriceBase):
    pass

class PriceResponse(PriceBase):
    id: int
    source: str
    verified: bool
    created_at: datetime
    crop_name: Optional[str] = None
    market_name: Optional[str] = None

    class Config:
        from_attributes = True

# Alert Schemas
class AlertBase(BaseModel):
    crop_id: int
    market_id: Optional[int] = None
    grade: str
    condition: str
    threshold: float
    delivery_method: dict

class AlertCreate(AlertBase):
    pass

class AlertResponse(AlertBase):
    id: int
    user_id: int
    active: bool
    last_triggered: Optional[datetime]
    created_at: datetime
    crop_name: Optional[str] = None
    market_name: Optional[str] = None

    class Config:
        from_attributes = True

# Report Schemas
class PriceReportBase(BaseModel):
    crop_id: int
    market_id: int
    grade: str
    price_etb: float
    price_type: Optional[str] = "wholesale"
    notes: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class PriceReportCreate(PriceReportBase):
    pass

class PriceReportResponse(PriceReportBase):
    id: int
    user_id: int
    status: str
    photo_url: Optional[str]
    created_at: datetime
    crop_name: Optional[str] = None
    market_name: Optional[str] = None

    class Config:
        from_attributes = True
