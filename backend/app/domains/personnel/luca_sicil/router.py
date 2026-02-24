"""Luca Sicil domain router (V2)"""
from fastapi import APIRouter, Depends, UploadFile, File, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.domains.auth.dependencies import get_current_user
from app.schemas.auth import UserInDB

router = APIRouter(prefix="/luca-sicil", tags=["Personnel - Luca Sicil (V2)"])


@router.post("/upload")
async def upload_luca_sicil(
    file: UploadFile = File(...),
    donem: Optional[str] = Query(None, description="Period in yyyy-mm format"),
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload Luca Sicil Excel file and process personnel records
    
    Args:
        file: Luca Sicil Excel file
        donem: Optional period override (yyyy-mm)
    
    Returns:
        Upload results with processing summary and errors
    """
    # TODO: Implement V2 Luca Sicil upload
    raise HTTPException(
        status_code=501,
        detail="Luca Sicil upload not yet implemented in V2. Please implement this feature."
    )


@router.get("/records")
async def get_luca_sicil_records(
    donem: Optional[str] = Query(None, description="Filter by period (yyyy-mm)"),
    skip: int = 0,
    limit: int = 100,
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get Luca Sicil records (monthly personnel records)
    
    Args:
        donem: Filter by period
        skip: Pagination skip
        limit: Pagination limit
    
    Returns:
        List of monthly personnel records
    """
    # TODO: Implement V2 Luca Sicil records listing
    raise HTTPException(
        status_code=501,
        detail="Luca Sicil records listing not yet implemented in V2. Please implement this feature."
    )


@router.get("/periods")
async def get_luca_sicil_periods(
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all available Luca Sicil periods
    
    Returns:
        List of periods (yyyy-mm)
    """
    # TODO: Implement V2 Luca Sicil periods listing
    raise HTTPException(
        status_code=501,
        detail="Luca Sicil periods listing not yet implemented in V2. Please implement this feature."
    )
