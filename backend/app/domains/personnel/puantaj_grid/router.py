"""Puantaj Grid domain router"""
from fastapi import APIRouter, Depends, Query, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from io import BytesIO

from app.core.database import get_db
from app.domains.personnel.puantaj_grid.service import PuantajGridService
from app.domains.auth.dependencies import get_current_user
from app.schemas.auth import UserInDB

router = APIRouter()


class GridSaveRequest(BaseModel):
    """Grid save request"""
    donem: str
    records: List[dict]


@router.get("/")
async def get_grid_data(
    donem: str = Query(..., description="Period (YYYY-MM)"),
    cost_center_id: Optional[int] = Query(None, description="Cost center filter"),
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get Excel-like grid data for personnel and daily status
    Only shows personnel active in the given period
    
    Args:
        donem: Period in YYYY-MM format
        cost_center_id: Optional cost center filter
    
    Returns:
        {
            success: true,
            donem: "2025-01",
            total: number of records,
            records: [
                {
                    row_type: "header" | "data",
                    id: personnel_id,
                    adi_soyadi: "Name Surname",
                    tc_kimlik_no: "12345678901",
                    cost_center_id: 123,
                    departman: "Department Name",
                    gun_1: "C" | "I" | "R" | "U" | "T" | null,
                    fm_gun_1: 1.0,
                    ... (gun_2 through gun_31)
                }
            ],
            holidays: [1, 15, 29]  # Day numbers that are holidays
        }
    """
    service = PuantajGridService(db)
    return service.get_grid_data(donem, cost_center_id)


@router.post("/save")
async def save_grid_data(
    request: GridSaveRequest,
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Save grid data from Excel-like interface
    INSERT/UPDATE 31-day data for each personnel
    
    Args:
        request: {
            donem: "2025-01",
            records: [
                {
                    id: personnel_id,
                    gun_1: "C",
                    fm_gun_1: 1.0,
                    ... (gun_2 through gun_31)
                }
            ]
        }
    
    Returns:
        {
            success: true,
            donem: "2025-01",
            saved: number of new records created,
            updated: number of existing records updated,
            total: saved + updated
        }
    """
    try:
        service = PuantajGridService(db)
        return service.save_grid_data(request.donem, request.records)
    except Exception as e:
        import traceback
        print(f"❌ SAVE ERROR: {str(e)}")
        print(traceback.format_exc())
        raise


@router.post("/upload")
async def upload_grid_excel(
    file: UploadFile = File(...),
    donem: Optional[str] = Query(None, description="Period (YYYY-MM), optional if in filename"),
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Parse Excel file and return data (does NOT save to database)
    Frontend will merge with existing data and user will click Save button
    
    Args:
        file: Excel file with puantaj data
        donem: Optional period in YYYY-MM format (can be extracted from filename)
    
    Returns:
        {
            success: true,
            donem: "2025-01",
            records: [...],  # Parsed records to be merged in frontend
            total: number of records parsed
        }
    """
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Sadece Excel dosyaları yüklenebilir (.xlsx, .xls)")
    
    try:
        contents = await file.read()
        service = PuantajGridService(db)
        # Parse only, don't save to database
        result = service.parse_excel_without_saving(contents, donem or file.filename)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Excel yükleme hatası: {str(e)}")


@router.get("/template/download")
async def download_template(
    donem: str = Query(..., description="Period (YYYY-MM)"),
    cost_center_id: Optional[int] = Query(None, description="Cost center ID to filter personnel"),
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Download Excel template for puantaj grid
    
    Args:
        donem: Period in YYYY-MM format
        cost_center_id: Optional cost center ID to include only personnel from that cost center
    
    Returns:
        Excel file with template structure
    """
    try:
        service = PuantajGridService(db)
        excel_bytes = service.create_template_excel(donem, cost_center_id)
        
        # Create response
        output = BytesIO(excel_bytes)
        output.seek(0)
        
        filename = f"puantaj_sablonu_{donem}.xlsx"
        
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Şablon oluşturma hatası: {str(e)}")
