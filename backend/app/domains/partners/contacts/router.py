"""
Contacts Router
FastAPI endpoints for contacts
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.schemas.contact import ContactCreate, ContactResponse
from .service import ContactService

router = APIRouter()


@router.get("/", response_model=List[ContactResponse])
def list_contacts(
    skip: int = 0,
    limit: int = 10000,
    is_active: bool = True,
    contact_type: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Carileri listele"""
    service = ContactService(db)
    return service.list_contacts(
        skip=skip,
        limit=limit,
        is_active=is_active,
        contact_type=contact_type
    )


@router.get("/search")
def search_contacts(
    q: str = Query(..., min_length=2),
    is_active: bool = True,
    db: Session = Depends(get_db)
):
    """Cari ara (isim, vergi no, kod)"""
    service = ContactService(db)
    return service.search_contacts(q, is_active)


@router.get("/{contact_id}", response_model=ContactResponse)
def get_contact(contact_id: int, db: Session = Depends(get_db)):
    """Tek cari detayı"""
    service = ContactService(db)
    contact = service.get_contact(contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Cari bulunamadı")
    return contact


@router.get("/tax/{tax_number}", response_model=ContactResponse)
def get_by_tax_number(tax_number: str, db: Session = Depends(get_db)):
    """Vergi numarasına göre cari getir"""
    service = ContactService(db)
    contact = service.get_by_tax_number(tax_number)
    if not contact:
        raise HTTPException(status_code=404, detail="Cari bulunamadı")
    return contact


@router.post("/", response_model=ContactResponse, status_code=201)
def create_contact(contact: ContactCreate, db: Session = Depends(get_db)):
    """Yeni cari oluştur"""
    service = ContactService(db)
    try:
        return service.create_contact(contact.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{contact_id}", response_model=ContactResponse)
def update_contact(
    contact_id: int,
    contact: ContactCreate,
    db: Session = Depends(get_db)
):
    """Cari güncelle"""
    service = ContactService(db)
    try:
        updated = service.update_contact(contact_id, contact.model_dump())
        if not updated:
            raise HTTPException(status_code=404, detail="Cari bulunamadı")
        return updated
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{contact_id}", status_code=204)
def delete_contact(contact_id: int, db: Session = Depends(get_db)):
    """Cari sil (soft delete)"""
    service = ContactService(db)
    deleted = service.delete_contact(contact_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Cari bulunamadı")
    return None
