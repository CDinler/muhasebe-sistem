"""Monthly Personnel Records domain router"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.domains.auth.dependencies import get_current_user
from app.schemas.auth import UserInDB
from app.domains.personnel.monthly_records.service import MonthlyPersonnelRecordService
from app.domains.personnel.monthly_records.schemas import MonthlyPersonnelRecord

router = APIRouter(tags=["Personnel - Monthly Records"])


@router.get("/")
async def list_monthly_records(
    donem: Optional[str] = None,
    personnel_id: Optional[int] = None,
    page: int = 1,
    page_size: int = 100,
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List monthly personnel records with filters
    
    Args:
        donem: Filter by period (yyyy-mm format)
        personnel_id: Filter by personnel ID
        page: Page number (1-based)
        page_size: Number of records per page
    
    Returns:
        {
            items: List of monthly personnel records
            total: Total count matching filters
            page: Current page number
            page_size: Records per page
        }
    """
    service = MonthlyPersonnelRecordService(db)
    skip = (page - 1) * page_size
    result = service.list_records(
        donem=donem,
        personnel_id=personnel_id,
        skip=skip,
        limit=page_size
    )
    
    return {
        **result,
        "page": page,
        "page_size": page_size
    }


@router.get("/periods")
async def get_periods(
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all available periods from monthly_personnel_records
    
    Returns:
        List of periods (yyyy-mm format) sorted descending
    """
    service = MonthlyPersonnelRecordService(db)
    periods = service.get_periods()
    return {"periods": periods}


@router.get("/{record_id}", response_model=MonthlyPersonnelRecord)
async def get_monthly_record(
    record_id: int,
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific monthly personnel record
    
    Args:
        record_id: The ID of the monthly personnel record
    
    Returns:
        The monthly personnel record object
    """
    service = MonthlyPersonnelRecordService(db)
    record = service.get_record(record_id)
    
    if not record:
        raise HTTPException(status_code=404, detail="Monthly personnel record not found")
    
    return record


@router.post("/upload-sicil")
async def upload_personnel_sicil(
    donem: str = Form(..., description="Period in yyyy-mm format"),
    file: UploadFile = File(...),
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload personnel sicil Excel file
    
    Process:
    1. Read Excel file
    2. For each row:
       - Create personnel if doesn't exist
       - Create/update monthly_personnel_record
       - Create/update personnel_contract
    
    Args:
        donem: Period in yyyy-mm format
        file: Excel file (.xlsx or .xls)
    
    Returns:
        {
            message: Success message
            donem: Period processed
            total_records: Number of records processed
            created_personnel: Number of personnel created
            updated_personnel: Number of personnel updated
            created_contracts: Number of contracts created
            updated_contracts: Number of contracts updated
            created_records: Number of monthly records created
            updated_records: Number of monthly records updated
            errors: List of errors encountered
        }
    """
    service = MonthlyPersonnelRecordService(db)
    
    try:
        result = await service.upload_sicil(donem, file)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
