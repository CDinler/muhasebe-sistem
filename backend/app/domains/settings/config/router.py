"""
Config Router
FastAPI endpoints for system configuration
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

from app.core.database import get_db
from .service import ConfigService

router = APIRouter()


# Schemas
class SystemConfigCreate(BaseModel):
    config_key: str
    config_value: str
    config_type: str = 'NUMBER'
    category: Optional[str] = None
    description: Optional[str] = None


class SystemConfigUpdate(BaseModel):
    config_value: str
    description: Optional[str] = None


class TaxBracketCreate(BaseModel):
    year: int
    min_amount: float
    max_amount: Optional[float] = None
    tax_rate: float


class TaxBracketUpdate(BaseModel):
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None
    tax_rate: Optional[float] = None


# Config Endpoints
@router.get("/configs")
def list_configs(
    category: Optional[str] = None,
    db: Session = Depends(get_db)
) -> Dict[str, List[Dict]]:
    """Tüm sistem konfigürasyonlarını kategorilere göre grupla"""
    service = ConfigService(db)
    return service.get_all_configs_grouped(category)


@router.get("/configs/{config_key}")
def get_config(config_key: str, db: Session = Depends(get_db)):
    """Belirli bir config değerini getir"""
    service = ConfigService(db)
    config = service.get_config(config_key)
    if not config:
        raise HTTPException(status_code=404, detail="Config bulunamadı")
    
    return {
        "id": config.id,
        "key": config.config_key,
        "value": config.config_value,
        "type": config.config_type,
        "description": config.description
    }


@router.post("/configs", status_code=201)
def create_config(config: SystemConfigCreate, db: Session = Depends(get_db)):
    """Yeni config oluştur"""
    service = ConfigService(db)
    try:
        new_config = service.create_config(config.model_dump())
        return {
            "id": new_config.id,
            "key": new_config.config_key,
            "value": new_config.config_value,
            "type": new_config.config_type,
            "description": new_config.description
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/configs/{config_key}")
def update_config(
    config_key: str,
    config: SystemConfigUpdate,
    db: Session = Depends(get_db)
):
    """Config güncelle"""
    service = ConfigService(db)
    updated = service.update_config(config_key, config.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Config bulunamadı")
    
    return {
        "id": updated.id,
        "key": updated.config_key,
        "value": updated.config_value,
        "type": updated.config_type,
        "description": updated.description
    }


@router.delete("/configs/{config_id}", status_code=204)
def delete_config(config_id: int, db: Session = Depends(get_db)):
    """Config sil"""
    service = ConfigService(db)
    deleted = service.delete_config(config_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Config bulunamadı")
    return None


# Tax Brackets Endpoints
@router.get("/tax-brackets")
def list_tax_brackets(
    year: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Vergi dilimlerini listele"""
    service = ConfigService(db)
    brackets = service.get_tax_brackets(year)
    
    return [{
        "id": b.id,
        "year": b.year,
        "min_amount": b.min_amount,
        "max_amount": b.max_amount,
        "tax_rate": b.tax_rate
    } for b in brackets]


@router.post("/tax-brackets", status_code=201)
def create_tax_bracket(bracket: TaxBracketCreate, db: Session = Depends(get_db)):
    """Yeni vergi dilimi oluştur"""
    service = ConfigService(db)
    new_bracket = service.create_tax_bracket(bracket.model_dump())
    
    return {
        "id": new_bracket.id,
        "year": new_bracket.year,
        "min_amount": new_bracket.min_amount,
        "max_amount": new_bracket.max_amount,
        "tax_rate": new_bracket.tax_rate
    }


@router.put("/tax-brackets/{bracket_id}")
def update_tax_bracket(
    bracket_id: int,
    bracket: TaxBracketUpdate,
    db: Session = Depends(get_db)
):
    """Vergi dilimi güncelle"""
    service = ConfigService(db)
    updated = service.update_tax_bracket(bracket_id, bracket.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Vergi dilimi bulunamadı")
    
    return {
        "id": updated.id,
        "year": updated.year,
        "min_amount": updated.min_amount,
        "max_amount": updated.max_amount,
        "tax_rate": updated.tax_rate
    }


@router.delete("/tax-brackets/{bracket_id}", status_code=204)
def delete_tax_bracket(bracket_id: int, db: Session = Depends(get_db)):
    """Vergi dilimi sil"""
    service = ConfigService(db)
    deleted = service.delete_tax_bracket(bracket_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Vergi dilimi bulunamadı")
    return None
