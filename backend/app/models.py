from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text, Enum, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum

class UserRole(str, enum.Enum):
    FARMER = "farmer"
    TRADER = "trader"
    COOPERATIVE = "cooperative"
    ADMIN = "admin"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String(20), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=True)
    email = Column(String(100), unique=True, nullable=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.FARMER)
    is_premium = Column(Boolean, default=False)
    premium_expiry = Column(DateTime, nullable=True)
    reputation_score = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    alerts = relationship("Alert", back_populates="user")
    reports = relationship("PriceReport", back_populates="reporter")

class Crop(Base):
    __tablename__ = "crops"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    unit = Column(String(20), default="quintal")

class Market(Base):
    __tablename__ = "markets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    region = Column(String(50), nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

class Price(Base):
    __tablename__ = "prices"

    id = Column(Integer, primary_key=True, index=True)
    crop_id = Column(Integer, ForeignKey("crops.id"), nullable=False)
    market_id = Column(Integer, ForeignKey("markets.id"), nullable=False)
    grade = Column(String(20), nullable=False)  # Grade 1, Grade 2, Mixed
    price_etb = Column(Float, nullable=False)
    price_type = Column(String(20), default="wholesale")  # farmgate, wholesale, retail
    source = Column(String(50), default="crowdsourced")  # crowdsourced, exchange, govt
    reported_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    verified = Column(Boolean, default=False)
    effective_date = Column(Date, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    crop = relationship("Crop")
    market = relationship("Market")
    reporter = relationship("User", foreign_keys=[reported_by])

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    crop_id = Column(Integer, ForeignKey("crops.id"), nullable=False)
    market_id = Column(Integer, ForeignKey("markets.id"), nullable=True)  # NULL = all markets
    grade = Column(String(20), nullable=False)
    condition = Column(String(10), nullable=False)  # 'above' or 'below'
    threshold = Column(Float, nullable=False)
    delivery_method = Column(Text, nullable=False)  # JSON: {"sms": true, "push": true}
    active = Column(Boolean, default=True)
    last_triggered = Column(DateTime, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="alerts")
    crop = relationship("Crop")
    market = relationship("Market")

class PriceReport(Base):
    __tablename__ = "price_reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    crop_id = Column(Integer, ForeignKey("crops.id"), nullable=False)
    market_id = Column(Integer, ForeignKey("markets.id"), nullable=False)
    grade = Column(String(20), nullable=False)
    price_etb = Column(Float, nullable=False)
    price_type = Column(String(20), default="wholesale")
    photo_url = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    status = Column(String(20), default="pending")  # pending, verified, rejected
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    reporter = relationship("User", back_populates="reports")
    crop = relationship("Crop")
    market = relationship("Market")
