"""
Database seeding script for Hidar (SQLite embedded).
Run this once to populate initial data.
"""

import asyncio
from datetime import date, datetime, timedelta
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select

from app.database import Base, engine, AsyncSessionLocal
from app.models import Crop, Market, Price, User, UserRole
from app.auth import get_password_hash
from app.config import settings

# --- DATA ---
CROPS = [
    {"name": "Teff", "unit": "quintal"},
    {"name": "Wheat", "unit": "quintal"},
    {"name": "Maize", "unit": "quintal"},
    {"name": "Coffee", "unit": "quintal"},
    {"name": "Sesame", "unit": "quintal"},
]

MARKETS = [
    {"name": "Adama", "region": "Oromia", "latitude": 8.5486, "longitude": 39.2698},
    {"name": "Addis Ababa", "region": "Addis Ababa", "latitude": 9.0320, "longitude": 38.7420},
    {"name": "Bahir Dar", "region": "Amhara", "latitude": 11.5742, "longitude": 37.3613},
    {"name": "Mekele", "region": "Tigray", "latitude": 13.4967, "longitude": 39.4753},
    {"name": "Dire Dawa", "region": "Dire Dawa", "latitude": 9.6000, "longitude": 41.8500},
    {"name": "Jimma", "region": "Oromia", "latitude": 7.6667, "longitude": 36.8333},
    {"name": "Shashemene", "region": "Oromia", "latitude": 7.2000, "longitude": 38.6000},
    {"name": "Hawassa", "region": "Sidama", "latitude": 7.0500, "longitude": 38.4667},
    {"name": "Gondar", "region": "Amhara", "latitude": 12.6000, "longitude": 37.4667},
    {"name": "Dessie", "region": "Amhara", "latitude": 11.1333, "longitude": 39.6333},
]

SAMPLE_PRICES = [
    {"crop": "Teff", "market": "Adama", "grade": "Grade 1", "price_etb": 11750},
    {"crop": "Teff", "market": "Addis Ababa", "grade": "Grade 1", "price_etb": 12000},
    {"crop": "Wheat", "market": "Bahir Dar", "grade": "Grade 1", "price_etb": 8250},
    {"crop": "Wheat", "market": "Adama", "grade": "Grade 1", "price_etb": 8000},
    {"crop": "Maize", "market": "Shashemene", "grade": "Grade 1", "price_etb": 5000},
    {"crop": "Maize", "market": "Adama", "grade": "Grade 1", "price_etb": 4900},
    {"crop": "Coffee", "market": "Jimma", "grade": "Grade 1", "price_etb": 10706},
    {"crop": "Sesame", "market": "Mekele", "grade": "Grade 1", "price_etb": 18265},
]

async def seed_crops(db: AsyncSession):
    for data in CROPS:
        result = await db.execute(select(Crop).where(Crop.name == data["name"]))
        if not result.scalar_one_or_none():
            db.add(Crop(**data))
            print(f"✅ Added crop: {data['name']}")
    await db.commit()

async def seed_markets(db: AsyncSession):
    for data in MARKETS:
        result = await db.execute(select(Market).where(Market.name == data["name"]))
        if not result.scalar_one_or_none():
            db.add(Market(**data))
            print(f"✅ Added market: {data['name']}")
    await db.commit()

async def seed_prices(db: AsyncSession):
    crops = {c.name: c.id for c in (await db.execute(select(Crop))).scalars()}
    markets = {m.name: m.id for m in (await db.execute(select(Market))).scalars()}
    today = date.today()

    for data in SAMPLE_PRICES:
        crop_id = crops.get(data["crop"])
        market_id = markets.get(data["market"])
        if crop_id and market_id:
            existing = await db.execute(
                select(Price).where(
                    Price.crop_id == crop_id,
                    Price.market_id == market_id,
                    Price.effective_date == today
                )
            )
            if not existing.scalar_one_or_none():
                price = Price(
                    crop_id=crop_id,
                    market_id=market_id,
                    grade=data["grade"],
                    price_etb=data["price_etb"],
                    effective_date=today,
                    verified=True,
                    source="admin"
                )
                db.add(price)
                print(f"✅ Added price: {data['crop']} @ {data['market']} = {data['price_etb']} ETB")
    await db.commit()

async def seed_test_user(db: AsyncSession):
    phone = "0912345678"
    result = await db.execute(select(User).where(User.phone_number == phone))
    if not result.scalar_one_or_none():
        user = User(
            phone_number=phone,
            name="Test Farmer",
            email="test@hidar.com",
            hashed_password=get_password_hash("password123"),
            role=UserRole.FARMER,
            is_premium=True
        )
        db.add(user)
        await db.commit()
        print(f"✅ Created test user: {phone} / password123")

async def main():
    print("🌾 Seeding Hidar database (SQLite)...")
    async with AsyncSessionLocal() as db:
        await seed_crops(db)
        await seed_markets(db)
        await seed_prices(db)
        await seed_test_user(db)
    print("✅ Seeding complete!")

if __name__ == "__main__":
    asyncio.run(main())
