from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app import crud, schemas, auth
from app.database import get_db
from app.models import User

router = APIRouter(prefix="/reports", tags=["reports"])

@router.get("/", response_model=List[schemas.PriceReportResponse])
async def get_my_reports(
    current_user: User = Depends(auth.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all price reports submitted by the authenticated user.
    """
    reports = await crud.get_user_reports(db, current_user.id)
    return reports

@router.post("/", response_model=schemas.PriceReportResponse)
async def create_report(
    report: schemas.PriceReportCreate,
    current_user: User = Depends(auth.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Submit a new price report.
    """
    return await crud.create_report(db, report, current_user.id)
