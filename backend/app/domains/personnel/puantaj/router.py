"""Puantaj domain router (V2)"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.domains.auth.dependencies import get_current_user
from app.schemas.auth import UserInDB

router = APIRouter(prefix="/puantaj", tags=["Personnel - Puantaj (V2)"])


@router.get("/template/{donem}")
async def download_puantaj_template(
    donem: str,
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Download Puantaj Excel template (with personnel list for the period)
    
    Args:
        donem: Period in YYYY-MM format
    
    Returns:
        Excel file as StreamingResponse
    """
    # TODO: Implement V2 puantaj template generation
    raise HTTPException(
        status_code=501,
        detail="Puantaj template download not yet implemented in V2. Please use V2 API or implement this feature."
    )


@router.post("/test-upload")
async def test_upload_puantaj(
    file: UploadFile = File(...),
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    TEST MODE: Parse Excel, show calculations but DO NOT WRITE TO DATABASE
    Test contracts, payroll, and cost calculations
    
    Args:
        file: Excel file (.xlsx or .xls)
    
    Returns:
        Test results with calculations and validations
    """
    # TODO: Implement V2 puantaj test upload
    raise HTTPException(
        status_code=501,
        detail="Puantaj test upload not yet implemented in V2. Please use V2 API or implement this feature."
    )


@router.post("/upload")
async def upload_puantaj(
    file: UploadFile = File(...),
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload and process Puantaj Excel file
    Creates/updates monthly_puantaj records
    
    Args:
        file: Excel file (.xlsx or .xls)
    
    Returns:
        Processing results with counts and errors
    """
    # TODO: Implement V2 puantaj upload
    raise HTTPException(
        status_code=501,
        detail="Puantaj upload not yet implemented in V2. Please use V2 API or implement this feature."
    )


@router.get("/list")
async def list_puantaj(
    yil: Optional[int] = None,
    ay: Optional[int] = None,
    personnel_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    List monthly puantaj records with filters
    
    Args:
        yil: Filter by year
        ay: Filter by month
        personnel_id: Filter by personnel ID
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return
    
    Returns:
        {
            items: List of puantaj records
            total: Total count matching filters
        }
    """
    from app.models import MonthlyPuantaj
    
    query = db.query(MonthlyPuantaj)
    
    if yil:
        query = query.filter(MonthlyPuantaj.yil == yil)
    if ay:
        query = query.filter(MonthlyPuantaj.ay == ay)
    if personnel_id:
        query = query.filter(MonthlyPuantaj.personnel_id == personnel_id)
    
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    
    return {
        "items": items,
        "total": total
    }
