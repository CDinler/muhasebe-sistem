"""Bordro Yevmiye domain router (V2)"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.domains.auth.dependencies import get_current_user
from app.schemas.auth import UserInDB

router = APIRouter(prefix="/bordro-yevmiye", tags=["Personnel - Bordro Yevmiye (V2)"])


@router.post("/generate-yevmiye")
async def generate_bordro_yevmiye(
    yil: int = Query(...),
    ay: int = Query(...),
    cost_center_id: Optional[int] = Query(None),
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate bordro yevmiye (journal entries) for a period
    
    Args:
        yil: Year
        ay: Month
        cost_center_id: Optional cost center filter
    
    Returns:
        Generated yevmiye entries
    """
    # TODO: Implement V2 bordro yevmiye generation
    raise HTTPException(
        status_code=501,
        detail="Bordro yevmiye generation not yet implemented in V2. Please implement this feature."
    )


@router.get("/yevmiye-list")
async def list_bordro_yevmiye(
    yil: Optional[int] = Query(None),
    ay: Optional[int] = Query(None),
    cost_center_id: Optional[int] = Query(None),
    skip: int = 0,
    limit: int = 100,
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List bordro yevmiye entries
    
    Args:
        yil: Filter by year
        ay: Filter by month
        cost_center_id: Filter by cost center
        skip: Pagination skip
        limit: Pagination limit
    
    Returns:
        {
            items: List of yevmiye entries
            total: Total count
        }
    """
    # TODO: Implement V2 bordro yevmiye listing
    raise HTTPException(
        status_code=501,
        detail="Bordro yevmiye listing not yet implemented in V2. Please implement this feature."
    )
