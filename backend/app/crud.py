from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload
from datetime import date, datetime
from typing import Optional, List
from app import models, schemas
from app.auth import get_password_hash

# --- User CRUD ---
async def get_user_by_id(db: AsyncSession, user_id: int):
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    return result.scalar_one_or_none()

async def get_user_by_phone(db: AsyncSession, phone_number: str):
    result = await db.execute(select(models.User).where(models.User.phone_number == phone_number))
    return result.scalar_one_or_none()

async def create_user(db: AsyncSession, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        phone_number=user.phone_number,
        name=user.name,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

# --- Price CRUD ---
async def get_prices(
    db: AsyncSession,
    crop_id: Optional[int] = None,
    market_id: Optional[int] = None,
    grade: Optional[str] = None,
    effective_date: Optional[date] = None,
    limit: int = 10,
    skip: int = 0
):
    query = select(models.Price).options(
        selectinload(models.Price.crop),
        selectinload(models.Price.market)
    )
    if crop_id:
        query = query.where(models.Price.crop_id == crop_id)
    if market_id:
        query = query.where(models.Price.market_id == market_id)
    if grade:
        query = query.where(models.Price.grade == grade)
    if effective_date:
        query = query.where(models.Price.effective_date == effective_date)
    query = query.order_by(models.Price.effective_date.desc()).limit(limit).offset(skip)
    result = await db.execute(query)
    return result.scalars().all()

async def create_price(db: AsyncSession, price: schemas.PriceCreate, reported_by: Optional[int] = None):
    db_price = models.Price(
        **price.model_dump(),
        reported_by=reported_by,
        source="crowdsourced" if reported_by else "admin"
    )
    db.add(db_price)
    await db.commit()
    await db.refresh(db_price)
    return db_price

# --- Alert CRUD ---
async def get_user_alerts(db: AsyncSession, user_id: int):
    result = await db.execute(
        select(models.Alert)
        .options(selectinload(models.Alert.crop), selectinload(models.Alert.market))
        .where(models.Alert.user_id == user_id)
    )
    return result.scalars().all()

async def create_alert(db: AsyncSession, alert: schemas.AlertCreate, user_id: int):
    db_alert = models.Alert(
        **alert.model_dump(),
        user_id=user_id
    )
    db.add(db_alert)
    await db.commit()
    await db.refresh(db_alert)
    return db_alert

async def delete_alert(db: AsyncSession, alert_id: int, user_id: int):
    result = await db.execute(
        select(models.Alert).where(
            and_(models.Alert.id == alert_id, models.Alert.user_id == user_id)
        )
    )
    alert = result.scalar_one_or_none()
    if alert:
        await db.delete(alert)
        await db.commit()
        return True
    return False

# --- Report CRUD ---
async def create_report(db: AsyncSession, report: schemas.PriceReportCreate, user_id: int):
    db_report = models.PriceReport(
        **report.model_dump(),
        user_id=user_id
    )
    db.add(db_report)
    await db.commit()
    await db.refresh(db_report)
    return db_report

async def get_user_reports(db: AsyncSession, user_id: int):
    result = await db.execute(
        select(models.PriceReport)
        .options(selectinload(models.PriceReport.crop), selectinload(models.PriceReport.market))
        .where(models.PriceReport.user_id == user_id)
        .order_by(models.PriceReport.created_at.desc())
    )
    return result.scalars().all()
