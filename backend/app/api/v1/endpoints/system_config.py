"""
System Config API endpoints - SSK oranları, vergi dilimleri vb.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.core.database import get_db
from app.models.system_config import SystemConfig, TaxBracket

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


# System Config Endpoints
@router.get("/configs")
def list_configs(
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Tüm sistem konfigürasyonlarını listele
    """
    query = db.query(SystemConfig)
    
    if category:
        query = query.filter(SystemConfig.category == category)
    
    configs = query.order_by(SystemConfig.category, SystemConfig.config_key).all()
    
    # Kategorilere göre grupla
    result = {}
    for config in configs:
        cat = config.category or 'GENEL'
        if cat not in result:
            result[cat] = []
        result[cat].append({
            "id": config.id,
            "key": config.config_key,
            "value": config.config_value,
            "type": config.config_type,
            "description": config.description
        })
    
    return result


@router.get("/configs/{config_key}")
def get_config(
    config_key: str,
    db: Session = Depends(get_db)
):
    """
    Belirli bir config değerini getir
    """
    config = db.query(SystemConfig).filter(SystemConfig.config_key == config_key).first()
    
    if not config:
        raise HTTPException(status_code=404, detail="Config bulunamadı")
    
    return config


@router.post("/configs")
def create_config(
    data: SystemConfigCreate,
    db: Session = Depends(get_db)
):
    """
    Yeni config ekle
    """
    # Aynı key var mı kontrol et
    existing = db.query(SystemConfig).filter(SystemConfig.config_key == data.config_key).first()
    if existing:
        raise HTTPException(status_code=400, detail="Bu config key zaten mevcut")
    
    config = SystemConfig(**data.dict())
    db.add(config)
    db.commit()
    db.refresh(config)
    
    return config


@router.put("/configs/{config_key}")
def update_config(
    config_key: str,
    data: SystemConfigUpdate,
    db: Session = Depends(get_db)
):
    """
    Config güncelle
    """
    config = db.query(SystemConfig).filter(SystemConfig.config_key == config_key).first()
    
    if not config:
        raise HTTPException(status_code=404, detail="Config bulunamadı")
    
    config.config_value = data.config_value
    if data.description:
        config.description = data.description
    
    db.commit()
    db.refresh(config)
    
    return config


@router.delete("/configs/{config_id}")
def delete_config(
    config_id: int,
    db: Session = Depends(get_db)
):
    """
    Config sil
    """
    config = db.query(SystemConfig).filter(SystemConfig.id == config_id).first()
    
    if not config:
        raise HTTPException(status_code=404, detail="Config bulunamadı")
    
    db.delete(config)
    db.commit()
    
    return {"success": True, "message": "Config silindi"}


# Tax Bracket Endpoints
@router.get("/tax-brackets")
def list_tax_brackets(
    year: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Gelir vergisi dilimlerini listele
    """
    query = db.query(TaxBracket).filter(TaxBracket.is_active == True)
    
    if year:
        query = query.filter(TaxBracket.year == year)
    
    brackets = query.order_by(TaxBracket.year.desc(), TaxBracket.min_amount).all()
    
    # Yıllara göre grupla
    result = {}
    for bracket in brackets:
        y = str(bracket.year)
        if y not in result:
            result[y] = []
        result[y].append({
            "id": bracket.id,
            "min_amount": float(bracket.min_amount),
            "max_amount": float(bracket.max_amount) if bracket.max_amount else None,
            "tax_rate": float(bracket.tax_rate),
            "tax_rate_percent": float(bracket.tax_rate) * 100
        })
    
    return result


@router.post("/tax-brackets")
def create_tax_bracket(
    data: TaxBracketCreate,
    db: Session = Depends(get_db)
):
    """
    Yeni vergi dilimi ekle
    """
    bracket = TaxBracket(**data.dict())
    db.add(bracket)
    db.commit()
    db.refresh(bracket)
    
    return bracket


@router.put("/tax-brackets/{bracket_id}")
def update_tax_bracket(
    bracket_id: int,
    data: TaxBracketCreate,
    db: Session = Depends(get_db)
):
    """
    Vergi dilimi güncelle
    """
    bracket = db.query(TaxBracket).filter(TaxBracket.id == bracket_id).first()
    
    if not bracket:
        raise HTTPException(status_code=404, detail="Vergi dilimi bulunamadı")
    
    for key, value in data.dict().items():
        setattr(bracket, key, value)
    
    db.commit()
    db.refresh(bracket)
    
    return bracket


@router.delete("/tax-brackets/{bracket_id}")
def delete_tax_bracket(
    bracket_id: int,
    db: Session = Depends(get_db)
):
    """
    Vergi dilimi sil
    """
    bracket = db.query(TaxBracket).filter(TaxBracket.id == bracket_id).first()
    
    if not bracket:
        raise HTTPException(status_code=404, detail="Vergi dilimi bulunamadı")
    
    db.delete(bracket)
    db.commit()
    
    return {"success": True, "message": "Vergi dilimi silindi"}


@router.get("/oranlar/{kanun_tipi}")
def get_oranlar(
    kanun_tipi: str,  # 05510, 00000, EMEKLI
    db: Session = Depends(get_db)
):
    """
    Belirli kanun tipine göre tüm oranları getir
    """
    suffix = kanun_tipi.upper()
    
    keys = [
        f"SSK_ISCI_{suffix}",
        f"ISSIZLIK_ISCI_{suffix}",
        f"SSK_ISVEREN_{suffix}",
        f"ISSIZLIK_ISVEREN_{suffix}",
    ]
    
    # 05510 için teşvik oranları da ekle
    if kanun_tipi == "05510":
        keys.extend([f"SSK_TESVIKI_4_{suffix}", f"SSK_TESVIKI_5_{suffix}"])
    
    configs = db.query(SystemConfig).filter(SystemConfig.config_key.in_(keys)).all()
    
    result = {}
    for config in configs:
        # Key'den suffix'i çıkar
        clean_key = config.config_key.replace(f"_{suffix}", "")
        result[clean_key] = {
            "value": float(config.config_value),
            "description": config.description
        }
    
    # Genel oranlar
    genel_keys = ["DAMGA_VERGISI_ORAN", "BES_ORAN", "ELDEN_YUVARLAMA_TUTAR"]
    genel_configs = db.query(SystemConfig).filter(SystemConfig.config_key.in_(genel_keys)).all()
    
    for config in genel_configs:
        result[config.config_key] = {
            "value": float(config.config_value),
            "description": config.description
        }
    
    return result
