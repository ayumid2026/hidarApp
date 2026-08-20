from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app import crud, schemas, auth
from app.database import get_db
from app.models import User

router = APIRouter(prefix="/alerts", tags=["alerts"])

@router.get("/", response_model=List[schemas.AlertResponse])
async def get_my_alerts(
    current_user: User = Depends(auth.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all alerts for the currently authenticated user.
    """
    alerts = await crud.get_user_alerts(db, current_user.id)
    return alerts

@router.post("/", response_model=schemas.AlertResponse)
async def create_alert(
    alert: schemas.AlertCreate,
    current_user: User = Depends(auth.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new price alert for the authenticated user.
    """
    return await crud.create_alert(db, alert, current_user.id)

@router.delete("/{alert_id}")
async def delete_alert(
    alert_id: int,
    current_user: User = Depends(auth.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete an alert by ID.
    """
    deleted = await crud.delete_alert(db, alert_id, current_user.id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")
    return {"message": "Alert deleted successfully"}
