# -*- coding: utf-8 -*-
"""Contact API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
import pandas as pd
import io

from app.core.database import get_db
from app.crud import contact as crud
from app.schemas.contact import ContactCreate, ContactResponse
from app.models.contact import Contact

router = APIRouter()

@router.get("/", response_model=List[ContactResponse])
def list_contacts(
    skip: int = 0,
    limit: int = 10000,  # Tüm carileri göster
    is_active: bool = True,
    contact_type: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Carileri listele"""
    contacts = crud.get_contacts(db, skip=skip, limit=limit, is_active=is_active, contact_type=contact_type)
    return contacts

@router.get("/{contact_id}", response_model=ContactResponse)
def get_contact(contact_id: int, db: Session = Depends(get_db)):
    """Tek cari detayı"""
    contact = crud.get_contact(db, contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact

@router.get("/tax/{tax_number}", response_model=ContactResponse)
def get_contact_by_tax_number(tax_number: str, db: Session = Depends(get_db)):
    """Vergi numarasına göre cari getir"""
    contact = crud.get_contact_by_tax_number(db, tax_number)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact

@router.post("/", response_model=ContactResponse, status_code=201)
def create_contact(contact: ContactCreate, db: Session = Depends(get_db)):
    """Yeni cari oluştur"""
    if contact.tax_number:
        existing = crud.get_contact_by_tax_number(db, contact.tax_number)
        if existing:
            raise HTTPException(status_code=400, detail="Tax number already exists")
    
    return crud.create_contact(db, contact)

@router.put("/{contact_id}", response_model=ContactResponse)
def update_contact(
    contact_id: int,
    contact: ContactCreate,
    db: Session = Depends(get_db)
):
    """Cari güncelle"""
    updated = crud.update_contact(db, contact_id, contact)
    if not updated:
        raise HTTPException(status_code=404, detail="Contact not found")
    return updated

@router.delete("/{contact_id}", status_code=204)
def delete_contact(contact_id: int, db: Session = Depends(get_db)):
    """Cari sil (soft delete)"""
    deleted = crud.delete_contact(db, contact_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Contact not found")
    return None

@router.post("/bulk-import")
async def bulk_import_contacts(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Toplu cari yükleme - Excel dosyasından"""
    
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Sadece Excel dosyası (.xlsx, .xls) yükleyebilirsiniz")
    
    try:
        # Excel'i oku
        contents = await file.read()
        df = pd.read_excel(io.BytesIO(contents))
        
        # Veri temizliği
        df['Cari Ünvanı'] = df['Cari Ünvanı'].str.strip().str.upper()
        df['Cari kodu 320'] = df['Cari kodu 320'].str.strip()
        df['Vergi Numarası'] = df['Vergi Numarası'].fillna(0).astype(int).astype(str).str.zfill(10)
        df['Vergi Numarası'] = df['Vergi Numarası'].replace('0000000000', None)
        df['Iban'] = df['Iban'].fillna('').str.strip().str.replace(' ', '').str.upper()
        df['Iban'] = df['Iban'].replace('', None)
        df['Vergi Dairesi'] = df['Vergi Dairesi'].fillna('').str.strip().str.upper()
        df['Vergi Dairesi'] = df['Vergi Dairesi'].replace('', None)
        df['Telefon'] = df['Telefon'].fillna(0).astype(int).astype(str)
        df['Telefon'] = df['Telefon'].replace('0', None)
        
        # Cari kodunu parse et (örnek: "320.00001 - Firma Adı" -> "320.00001")
        df['code'] = df['Cari kodu 320'].str.split(' - ').str[0].str.strip()
        
        added_count = 0
        updated_count = 0
        skipped_count = 0
        
        for idx, row in df.iterrows():
            code = row['code']
            name = row['Cari Ünvanı']
            vkn = row['Vergi Numarası'] if pd.notna(row['Vergi Numarası']) else None
            vergi_dairesi = row['Vergi Dairesi'] if pd.notna(row['Vergi Dairesi']) else None
            iban = row['Iban'] if pd.notna(row['Iban']) else None
            telefon = row['Telefon'] if pd.notna(row['Telefon']) else None
            
            # Mevcut kontrolü (code'a göre)
            existing = db.query(Contact).filter(Contact.code == code).first()
            
            if existing:
                # Güncelle
                existing.name = name
                existing.tax_number = vkn
                existing.tax_office = vergi_dairesi
                if iban:
                    existing.iban = iban
                if telefon:
                    existing.phone = telefon
                existing.manually_edited = True
                updated_count += 1
            else:
                # Yeni ekle
                new_contact = Contact(
                    code=code,
                    name=name,
                    tax_number=vkn,
                    tax_office=vergi_dairesi,
                    iban=iban,
                    phone=telefon,
                    contact_type='supplier',
                    is_active=True,
                    manually_edited=True
                )
                db.add(new_contact)
                added_count += 1
            
            # Her 100 kayıtta commit
            if (added_count + updated_count) % 100 == 0:
                db.commit()
        
        # Final commit
        db.commit()
        
        return {
            "success": True,
            "message": f"{added_count} cari eklendi, {updated_count} cari güncellendi",
            "added": added_count,
            "updated": updated_count,
            "total": len(df)
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Yükleme hatası: {str(e)}")
