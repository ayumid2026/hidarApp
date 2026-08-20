from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from datetime import date
from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix="/prices", tags=["prices"])

@router.get("/", response_model=List[schemas.PriceResponse])
async def get_prices(
    crop_id: Optional[int] = Query(None),
    market_id: Optional[int] = Query(None),
    grade: Optional[str] = Query(None),
    effective_date: Optional[date] = Query(None),
    limit: int = Query(10, ge=1, le=100),
    skip: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    return await crud.get_prices(
        db, crop_id=crop_id, market_id=market_id, grade=grade,
        effective_date=effective_date, limit=limit, skip=skip
    )

@router.post("/", response_model=schemas.PriceResponse)
async def create_price(
    price: schemas.PriceCreate,
    db: AsyncSession = Depends(get_db)
):
    return await crud.create_price(db, price)
