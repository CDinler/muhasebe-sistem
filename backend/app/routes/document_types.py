"""
Document Type ve Subtype API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.document_type import DocumentType, DocumentSubtype
from pydantic import BaseModel

router = APIRouter(prefix="/document-types", tags=["document-types"])
subtype_router = APIRouter(prefix="/document-subtypes", tags=["document-subtypes"])


# Schemas
class DocumentTypeResponse(BaseModel):
    id: int
    code: str
    name: str
    category: str
    requires_subtype: bool = False  # Alt tür zorunlu mu?
    is_active: bool
    sort_order: int
    
    class Config:
        from_attributes = True


class DocumentSubtypeResponse(BaseModel):
    id: int
    document_type_id: int  # Foreign key - direkt modelden geliyor
    code: str
    name: str
    category: Optional[str] = None
    parent_code: Optional[str] = None  # DEPRECATED - Geriye dönük uyumluluk
    is_active: bool
    sort_order: int
    
    class Config:
        from_attributes = True


# Document Types endpoints
@router.get("", response_model=List[DocumentTypeResponse])
def get_document_types(
    is_active: Optional[bool] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Tüm document types listesi"""
    query = db.query(DocumentType)
    
    if is_active is not None:
        query = query.filter(DocumentType.is_active == is_active)
    
    if category:
        query = query.filter(DocumentType.category == category)
    
    return query.order_by(DocumentType.category, DocumentType.sort_order).all()


@router.get("/{doc_type_id}", response_model=DocumentTypeResponse)
def get_document_type(doc_type_id: int, db: Session = Depends(get_db)):
    """Tek bir document type"""
    doc_type = db.query(DocumentType).filter(DocumentType.id == doc_type_id).first()
    if not doc_type:
        raise HTTPException(status_code=404, detail="Document type not found")
    return doc_type


# Document Subtypes endpoints
@subtype_router.get("", response_model=List[DocumentSubtypeResponse])
def get_document_subtypes(
    is_active: Optional[bool] = None,
    parent_code: Optional[str] = None,
    document_type_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Tüm document subtypes listesi"""
    query = db.query(DocumentSubtype)
    
    if is_active is not None:
        query = query.filter(DocumentSubtype.is_active == is_active)
    
    # document_type_id ile direkt filtrele (artık foreign key)
    if document_type_id:
        query = query.filter(DocumentSubtype.document_type_id == document_type_id)
    elif parent_code:
        # Geriye dönük uyumluluk için parent_code desteği
        doc_type = db.query(DocumentType).filter(DocumentType.code == parent_code).first()
        if doc_type:
            query = query.filter(DocumentSubtype.document_type_id == doc_type.id)
    
    subtypes = query.order_by(DocumentSubtype.document_type_id, DocumentSubtype.sort_order).all()
    
    # Pydantic modeli otomatik olarak dönüştürür
    return subtypes


@subtype_router.get("/{subtype_id}", response_model=DocumentSubtypeResponse)
def get_document_subtype(subtype_id: int, db: Session = Depends(get_db)):
    """Tek bir document subtype"""
    subtype = db.query(DocumentSubtype).filter(DocumentSubtype.id == subtype_id).first()
    if not subtype:
        raise HTTPException(status_code=404, detail="Document subtype not found")
    return subtype
