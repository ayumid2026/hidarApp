"""
Unit tests for CRUD operations.
Run with: pytest backend/tests/
"""

import pytest
import asyncio
from datetime import date, timedelta
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.database import Base
from app import models, crud, schemas
from app.auth import get_password_hash

# Test database (in-memory SQLite for speed)
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

@pytest.fixture
async def db_session():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session
    
    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest.mark.asyncio
async def test_create_user(db_session):
    """Test user creation."""
    user_data = schemas.UserCreate(
        phone_number="0912345678",
        name="Test User",
        email="test@example.com",
        password="testpassword123"
    )
    user = await crud.create_user(db_session, user_data)
    assert user.id is not None
    assert user.phone_number == "0912345678"
    assert user.name == "Test User"
    assert user.hashed_password != "testpassword123"  # Should be hashed

@pytest.mark.asyncio
async def test_get_user_by_phone(db_session):
    """Test retrieving user by phone number."""
    # Create user first
    user_data = schemas.UserCreate(
        phone_number="0998765432",
        name="Another User",
        password="password123"
    )
    created = await crud.create_user(db_session, user_data)
    
    # Retrieve
    retrieved = await crud.get_user_by_phone(db_session, "0998765432")
    assert retrieved is not None
    assert retrieved.id == created.id
    assert retrieved.phone_number == "0998765432"

@pytest.mark.asyncio
async def test_create_price(db_session):
    """Test price creation."""
    # First create a crop and market
    crop = models.Crop(name="Teff", unit="quintal")
    market = models.Market(name="Adama", region="Oromia")
    db_session.add(crop)
    db_session.add(market)
    await db_session.commit()
    await db_session.refresh(crop)
    await db_session.refresh(market)
    
    price_data = schemas.PriceCreate(
        crop_id=crop.id,
        market_id=market.id,
        grade="Grade 1",
        price_etb=11750.0,
        price_type="wholesale",
        effective_date=date.today()
    )
    price = await crud.create_price(db_session, price_data)
    assert price.id is not None
    assert price.price_etb == 11750.0
    assert price.source == "admin"

@pytest.mark.asyncio
async def test_get_prices(db_session):
    """Test price retrieval with filters."""
    # Setup: create crop, market, and prices
    crop = models.Crop(name="Wheat", unit="quintal")
    market = models.Market(name="Bahir Dar", region="Amhara")
    db_session.add(crop)
    db_session.add(market)
    await db_session.commit()
    await db_session.refresh(crop)
    await db_session.refresh(market)
    
    # Create multiple prices
    for i in range(5):
        price = models.Price(
            crop_id=crop.id,
            market_id=market.id,
            grade="Grade 1",
            price_etb=8000 + i * 100,
            effective_date=date.today() - timedelta(days=i),
            verified=True
        )
        db_session.add(price)
    await db_session.commit()
    
    # Test retrieval
    prices = await crud.get_prices(
        db_session,
        crop_id=crop.id,
        market_id=market.id,
        grade="Grade 1",
        limit=3
    )
    assert len(prices) == 3
    # Should be sorted by effective_date descending (most recent first)
    assert prices[0].price_etb == 8000  # Today's price

@pytest.mark.asyncio
async def test_create_alert(db_session):
    """Test alert creation."""
    # Create user, crop, market first
    user = models.User(
        phone_number="0911111111",
        hashed_password=get_password_hash("pass")
    )
    crop = models.Crop(name="Maize", unit="quintal")
    market = models.Market(name="Shashemene", region="Oromia")
    db_session.add_all([user, crop, market])
    await db_session.commit()
    await db_session.refresh(user)
    await db_session.refresh(crop)
    await db_session.refresh(market)
    
    alert_data = schemas.AlertCreate(
        crop_id=crop.id,
        market_id=market.id,
        grade="Grade 1",
        condition="below",
        threshold=4500.0,
        delivery_method={"sms": True, "push": False}
    )
    alert = await crud.create_alert(db_session, alert_data, user.id)
    assert alert.id is not None
    assert alert.user_id == user.id
    assert alert.threshold == 4500.0
    assert alert.active is True
