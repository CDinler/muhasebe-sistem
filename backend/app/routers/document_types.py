"""
Document Types API Router
Evrak tipi dropdown'ları için GET endpoints
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.core.database import get_db
from app.models.document_type import DocumentType, DocumentSubtype
from pydantic import BaseModel

router = APIRouter(tags=["document-types"])


# Schemas
class DocumentTypeResponse(BaseModel):
    id: int
    code: str
    name: str
    category: str
    is_active: bool
    sort_order: int
    
    class Config:
        from_attributes = True


class DocumentSubtypeResponse(BaseModel):
    id: int
    code: str
    name: str
    category: str
    is_active: bool
    sort_order: int
    
    class Config:
        from_attributes = True


@router.get("/types", response_model=List[DocumentTypeResponse])
def get_document_types(
    category: str = None,
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """
    Ana evrak tiplerini listele
    
    Args:
        category: Kategori filtresi (FATURA, KASA, BANKA, PERSONEL, VERGI, DIGER)
        active_only: Sadece aktif kayıtlar (default: True)
    
    Returns:
        List[DocumentTypeResponse]: Evrak tipleri listesi
    """
    query = db.query(DocumentType)
    
    if active_only:
        query = query.filter(DocumentType.is_active == True)
    
    if category:
        query = query.filter(DocumentType.category == category.upper())
    
    types = query.order_by(DocumentType.sort_order, DocumentType.name).all()
    return types


@router.get("/subtypes", response_model=List[DocumentSubtypeResponse])
def get_document_subtypes(
    category: str = None,
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """
    Alt evrak tiplerini listele
    
    Args:
        category: Kategori filtresi (E_BELGE, KASA, BANKA, CEK_SENET, PERSONEL, DIGER)
        active_only: Sadece aktif kayıtlar (default: True)
    
    Returns:
        List[DocumentSubtypeResponse]: Alt evrak tipleri listesi
    """
    query = db.query(DocumentSubtype)
    
    if active_only:
        query = query.filter(DocumentSubtype.is_active == True)
    
    if category:
        query = query.filter(DocumentSubtype.category == category.upper())
    
    subtypes = query.order_by(DocumentSubtype.sort_order, DocumentSubtype.name).all()
    return subtypes


@router.get("/categories")
def get_categories(db: Session = Depends(get_db)):
    """
    Kullanılabilir kategorileri listele
    
    Returns:
        dict: Ana tip ve alt tip kategorileri
    """
    type_categories = db.query(DocumentType.category)\
        .filter(DocumentType.is_active == True)\
        .distinct()\
        .order_by(DocumentType.category)\
        .all()
    
    subtype_categories = db.query(DocumentSubtype.category)\
        .filter(DocumentSubtype.is_active == True)\
        .distinct()\
        .order_by(DocumentSubtype.category)\
        .all()
    
    return {
        "document_types": [cat[0] for cat in type_categories],
        "document_subtypes": [cat[0] for cat in subtype_categories]
    }
