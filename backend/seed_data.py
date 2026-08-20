"""
Database seeding script for Hidar.
Run this once to populate initial crops, markets, and price data.
"""

import asyncio
import json
from datetime import date, datetime, timedelta
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select

from app.database import Base, engine, AsyncSessionLocal
from app.models import Crop, Market, Price, User, UserRole
from app.auth import get_password_hash
from app.config import settings

# --- CROP DATA ---
CROPS = [
    {"name": "Teff", "unit": "quintal"},
    {"name": "Wheat", "unit": "quintal"},
    {"name": "Maize", "unit": "quintal"},
    {"name": "Coffee", "unit": "quintal"},
    {"name": "Sesame", "unit": "quintal"},
]

# --- MARKET DATA ---
# 20 major Ethiopian markets with regions and approximate coordinates
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
    {"name": "Hossana", "region": "Central Ethiopia", "latitude": 7.5500, "longitude": 37.8500},
    {"name": "Wolaita Sodo", "region": "South Ethiopia", "latitude": 6.8500, "longitude": 37.7667},
    {"name": "Jijiga", "region": "Somali", "latitude": 9.3500, "longitude": 42.8000},
    {"name": "Metema", "region": "Amhara", "latitude": 12.9667, "longitude": 36.2000},
    {"name": "Debre Berhan", "region": "Amhara", "latitude": 9.6833, "longitude": 39.5333},
    {"name": "Awasa", "region": "Sidama", "latitude": 7.0500, "longitude": 38.4667},
    {"name": "Addis Mercato", "region": "Addis Ababa", "latitude": 9.0270, "longitude": 38.7450},
    {"name": "Chiromedia", "region": "Addis Ababa", "latitude": 9.0200, "longitude": 38.7600},
    {"name": "Sholla", "region": "Addis Ababa", "latitude": 9.0100, "longitude": 38.7500},
    {"name": "Bure", "region": "Amhara", "latitude": 10.7000, "longitude": 37.0667},
]

# --- INITIAL PRICE DATA (Sample for seeding) ---
# Based on real market data from 2025-2026 [reference:0]
SAMPLE_PRICES = [
    # Teff - Adama - Grade 1
    {"crop": "Teff", "market": "Adama", "grade": "Grade 1", "price_etb": 11750, "price_type": "wholesale"},
    # Teff - Addis Ababa - Grade 1
    {"crop": "Teff", "market": "Addis Ababa", "grade": "Grade 1", "price_etb": 12000, "price_type": "wholesale"},
    # Wheat - Bahir Dar - Grade 1
    {"crop": "Wheat", "market": "Bahir Dar", "grade": "Grade 1", "price_etb": 8250, "price_type": "wholesale"},
    # Wheat - Adama - Grade 1
    {"crop": "Wheat", "market": "Adama", "grade": "Grade 1", "price_etb": 8000, "price_type": "wholesale"},
    # Maize - Shashemene - Grade 1
    {"crop": "Maize", "market": "Shashemene", "grade": "Grade 1", "price_etb": 5000, "price_type": "wholesale"},
    # Maize - Adama - Grade 1
    {"crop": "Maize", "market": "Adama", "grade": "Grade 1", "price_etb": 4900, "price_type": "wholesale"},
    # Coffee - Jimma - Grade 1
    {"crop": "Coffee", "market": "Jimma", "grade": "Grade 1", "price_etb": 10706, "price_type": "wholesale"},  # ECX data [reference:1]
    # Sesame - Humera - Grade 1
    {"crop": "Sesame", "market": "Mekele", "grade": "Grade 1", "price_etb": 18265, "price_type": "wholesale"},  # ECX data [reference:2]
]


# --- SEEDING FUNCTIONS ---

async def seed_crops(db: AsyncSession):
    """Insert crops if they don't exist."""
    for crop_data in CROPS:
        result = await db.execute(select(Crop).where(Crop.name == crop_data["name"]))
        existing = result.scalar_one_or_none()
        if not existing:
            crop = Crop(**crop_data)
            db.add(crop)
            print(f"✅ Added crop: {crop_data['name']}")
    await db.commit()


async def seed_markets(db: AsyncSession):
    """Insert markets if they don't exist."""
    for market_data in MARKETS:
        result = await db.execute(select(Market).where(Market.name == market_data["name"]))
        existing = result.scalar_one_or_none()
        if not existing:
            market = Market(**market_data)
            db.add(market)
            print(f"✅ Added market: {market_data['name']}")
    await db.commit()


async def seed_sample_prices(db: AsyncSession):
    """Insert sample price data."""
    # Get crop and market mappings
    crops = {}
    result = await db.execute(select(Crop))
    for crop in result.scalars():
        crops[crop.name] = crop.id

    markets = {}
    result = await db.execute(select(Market))
    for market in result.scalars():
        markets[market.name] = market.id

    for price_data in SAMPLE_PRICES:
        crop_id = crops.get(price_data["crop"])
        market_id = markets.get(price_data["market"])
        if crop_id and market_id:
            # Check if price already exists for today
            today = date.today()
            result = await db.execute(
                select(Price).where(
                    Price.crop_id == crop_id,
                    Price.market_id == market_id,
                    Price.grade == price_data["grade"],
                    Price.effective_date == today
                )
            )
            existing = result.scalar_one_or_none()
            if not existing:
                price = Price(
                    crop_id=crop_id,
                    market_id=market_id,
                    grade=price_data["grade"],
                    price_etb=price_data["price_etb"],
                    price_type=price_data["price_type"],
                    source="admin",
                    verified=True,
                    effective_date=today
                )
                db.add(price)
                print(f"✅ Added price: {price_data['crop']} @ {price_data['market']} = {price_data['price_etb']} ETB")
    await db.commit()


async def seed_test_user(db: AsyncSession):
    """Create a test user for development."""
    phone = "0912345678"
    result = await db.execute(select(User).where(User.phone_number == phone))
    existing = result.scalar_one_or_none()
    if not existing:
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
    else:
        print(f"ℹ️ Test user already exists: {phone}")


# --- MAIN SEED FUNCTION ---

async def main():
    print("🌾 Starting Hidar data seeding...")
    print("=" * 40)

    async with AsyncSessionLocal() as db:
        await seed_crops(db)
        await seed_markets(db)
        await seed_sample_prices(db)
        await seed_test_user(db)

    print("=" * 40)
    print("✅ Seeding complete!")


if __name__ == "__main__":
    asyncio.run(main())
