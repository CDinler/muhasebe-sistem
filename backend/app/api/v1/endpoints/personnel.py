from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.personnel import Personnel
from app.schemas.personnel import (
    PersonnelCreate,
    PersonnelUpdate,
    PersonnelResponse,
    PersonnelList
)
from datetime import date, datetime

router = APIRouter()


@router.get("/", response_model=PersonnelList)
def get_personnel(
    skip: int = 0,
    limit: int = 1000,
    search: Optional[str] = None,
    period: Optional[str] = None,  # Format: "YYYY-MM" (örn: "2025-12")
    cost_center_id: Optional[int] = None,  # Cost Center ID filtresi
    db: Session = Depends(get_db)
):
    """
    Personel listesini getir (total count ile)
    
    Filters:
    - search: Ad, soyad, TC ile arama
    - period: Belirli dönemde çalışan personeller (YYYY-MM formatında)
    - cost_center_id: Cost center ID'ye göre filtreleme (personnel_contracts'tan)
    """
    query = db.query(Personnel)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Personnel.ad.like(search_term)) |
            (Personnel.soyad.like(search_term)) |
            (Personnel.tc_kimlik_no.like(search_term))
        )
    
    # Cost Center filtresi: Aktif contract'ı bu cost center'da olanlar
    if cost_center_id:
        from app.models.personnel_contract import PersonnelContract
        
        # Bu cost center'da aktif contract'ı olan personnel_id'leri bul
        personnel_ids_in_cc = db.query(PersonnelContract.personnel_id).filter(
            PersonnelContract.cost_center_id == cost_center_id,
            PersonnelContract.aktif == True
        ).distinct().all()
        
        personnel_ids = [p[0] for p in personnel_ids_in_cc]
        
        if personnel_ids:
            query = query.filter(Personnel.id.in_(personnel_ids))
        else:
            # Bu cost center'da kimse yoksa boş result dön
            query = query.filter(Personnel.id == -1)
    
    # Dönem filtresi: O dönemde sicil kaydı olan personeller
    if period:
        from app.models.monthly_personnel_record import MonthlyPersonnelRecord
        from datetime import datetime
        
        try:
            # Period: "2025-11" -> date formatına çevir
            period_date = datetime.strptime(f"{period}-01", "%Y-%m-%d").date()
            
            # O dönemdeki personnel_id'leri bul
            personnel_ids_in_period = db.query(MonthlyPersonnelRecord.personnel_id).filter(
                MonthlyPersonnelRecord.donem == period_date
            ).distinct().all()
            
            personnel_ids = [p[0] for p in personnel_ids_in_period]
            
            if personnel_ids:
                query = query.filter(Personnel.id.in_(personnel_ids))
            else:
                # O dönemde kimse yoksa boş result dön
                query = query.filter(Personnel.id == -1)
                
        except Exception as e:
            print(f"[PERIOD FILTER ERROR] {e}")
            pass  # Geçersiz period formatı, filtreleme yapma
    
    # Total count
    total = query.count()
    
    # Paginated results
    query = query.order_by(Personnel.ad, Personnel.soyad)
    personnel = query.offset(skip).limit(limit).all()
    
    return PersonnelList(
        total=total,
        page=skip // limit + 1 if limit > 0 else 1,
        page_size=limit,
        items=[PersonnelResponse.model_validate(p) for p in personnel]
    )


@router.get("/{personnel_id}", response_model=PersonnelResponse)
def get_personnel_by_id(personnel_id: int, db: Session = Depends(get_db)):
    """Personel detayını getir"""
    personnel = db.query(Personnel).filter(Personnel.id == personnel_id).first()
    
    if not personnel:
        raise HTTPException(status_code=404, detail="Personel bulunamadı")
    
    return personnel


@router.post("/", response_model=PersonnelResponse)
def create_personnel(personnel_data: PersonnelCreate, db: Session = Depends(get_db)):
    """Yeni personel oluştur"""
    # TC Kimlik No kontrolü
    if personnel_data.tc_kimlik_no:
        existing = db.query(Personnel).filter(Personnel.tc_kimlik_no == personnel_data.tc_kimlik_no).first()
        if existing:
            raise HTTPException(status_code=400, detail="Bu TC Kimlik No ile kayıtlı personel zaten var")
    
    personnel = Personnel(**personnel_data.model_dump())
    db.add(personnel)
    db.commit()
    db.refresh(personnel)
    
    return personnel


@router.put("/{personnel_id}", response_model=PersonnelResponse)
def update_personnel(
    personnel_id: int,
    personnel_data: PersonnelUpdate,
    db: Session = Depends(get_db)
):
    """Personel güncelle"""
    personnel = db.query(Personnel).filter(Personnel.id == personnel_id).first()
    
    if not personnel:
        raise HTTPException(status_code=404, detail="Personel bulunamadı")
    
    # TC Kimlik No kontrolü (başka biri kullanıyor mu?)
    if personnel_data.tc_kimlik_no and personnel_data.tc_kimlik_no != personnel.tc_kimlik_no:
        existing = db.query(Personnel).filter(
            Personnel.tc_kimlik_no == personnel_data.tc_kimlik_no,
            Personnel.id != personnel_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Bu TC Kimlik No ile kayıtlı başka personel var")
    
    # Sadece None olmayan değerleri güncelle
    update_data = personnel_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(personnel, key, value)
    
    db.commit()
    db.refresh(personnel)
    
    return personnel


@router.delete("/{personnel_id}")
def delete_personnel(personnel_id: int, db: Session = Depends(get_db)):
    """Personel sil"""
    personnel = db.query(Personnel).filter(Personnel.id == personnel_id).first()
    
    if not personnel:
        raise HTTPException(status_code=404, detail="Personel bulunamadı")
    
    # Kontrol: Bu personele ait contract var mı?
    from app.models.personnel_contract import PersonnelContract
    contracts = db.query(PersonnelContract).filter(PersonnelContract.personnel_id == personnel_id).count()
    if contracts > 0:
        raise HTTPException(status_code=400, detail="Bu personele ait sözleşme kayıtları var. Önce bunları silmelisiniz.")
    
    db.delete(personnel)
    db.commit()
    
    return {"message": "Personel başarıyla silindi", "id": personnel_id}
