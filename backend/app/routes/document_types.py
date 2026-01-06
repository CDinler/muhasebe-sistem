"""
Document Type ve Subtype API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.document_type import DocumentType
from pydantic import BaseModel

router = APIRouter(prefix="/document-types", tags=["document-types"])


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
