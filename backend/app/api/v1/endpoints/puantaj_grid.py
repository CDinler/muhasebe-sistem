"""
Personnel Puantaj Grid API endpoints
31 günlük Excel benzeri puantaj grid sistemi
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from pydantic import BaseModel
from datetime import date, datetime
import calendar

from app.core.database import get_db
from app.models.personnel_puantaj_grid import PersonnelPuantajGrid, PuantajDurum
from app.models.personnel import Personnel
from app.models.personnel_contract import PersonnelContract
from app.models.cost_center import CostCenter

router = APIRouter()


# =====================================================
# PYDANTIC SCHEMAS
# =====================================================

class GridSaveRequest(BaseModel):
    """Grid kaydetme request'i"""
    donem: str
    records: List[dict]


class CalendarHoliday(BaseModel):
    """Resmi tatil günü"""
    holiday_date: date
    name: str
    day_of_week: Optional[str] = None


# =====================================================
# ENDPOINTS
# =====================================================

@router.get("/grid")
async def get_grid_data(
    donem: str = Query(..., description="Dönem (YYYY-MM)"),
    cost_center_id: Optional[int] = Query(None, description="Şantiye filtresi"),
    db: Session = Depends(get_db)
):
    """
    Excel benzeri grid için personel listesi ve günlük durumlarını getir
    Sadece ilgili dönemde aktif olan personelleri gösterir
    """
    try:
        # Dönem parse et
        year, month = map(int, donem.split('-'))
        donem_ilk_gun = date(year, month, 1)
        
        # Son gün hesapla
        son_gun = calendar.monthrange(year, month)[1]
        donem_son_gun = date(year, month, son_gun)
        
        # Resmi tatilleri döndürelim (şimdilik boş, gerekirse calendar_holidays tablosundan çekebiliriz)
        holiday_days = set()  # Resmi tatil günleri
        
        # Önce grid tablosundaki kayıtları al
        grid_query = db.query(PersonnelPuantajGrid).filter(
            PersonnelPuantajGrid.donem == donem
        )
        
        # Cost center filtresi varsa uygula
        if cost_center_id:
            grid_query = grid_query.filter(
                PersonnelPuantajGrid.cost_center_id == cost_center_id
            )
        
        grid_records = grid_query.all()
        
        result = []
        
        if grid_records:
            # Grid kayıtları varsa - Tüm personnel ve contract'ları tek seferde çek
            personnel_ids = [g.personnel_id for g in grid_records]
            
            # Personnel'leri toplu çek
            personnel_dict = {p.id: p for p in db.query(Personnel).filter(
                Personnel.id.in_(personnel_ids)
            ).all()}
            
            # Contract'ları toplu çek
            contracts = db.query(PersonnelContract).filter(
                PersonnelContract.personnel_id.in_(personnel_ids),
                PersonnelContract.baslangic_tarihi <= donem_son_gun,
                or_(
                    PersonnelContract.bitis_tarihi == None,
                    PersonnelContract.bitis_tarihi >= donem_ilk_gun
                )
            ).order_by(PersonnelContract.personnel_id, PersonnelContract.baslangic_tarihi.desc()).all()
            
            # Her personnel için en son contract'ı bul
            contract_dict = {}
            for c in contracts:
                if c.personnel_id not in contract_dict:
                    contract_dict[c.personnel_id] = c
            
            # Grid kayıtlarını işle
            for grid in grid_records:
                person = personnel_dict.get(grid.personnel_id)
                contract = contract_dict.get(grid.personnel_id)
                
                if person:
                    row = {
                        'id': person.id,
                        'adi_soyadi': f"{person.ad} {person.soyad}",
                        'tc_kimlik_no': person.tc_kimlik_no or '',
                        'cost_center_id': contract.cost_center_id if contract else None
                    }
                else:
                    row = {
                        'id': grid.personnel_id,
                        'adi_soyadi': f'Personel {grid.personnel_id}',
                        'tc_kimlik_no': '',
                        'cost_center_id': None
                    }
                
                # 31 günlük kolonları ekle (grid'den)
                for i in range(1, 32):
                    gun_col = f'gun_{i}'
                    fm_col = f'fm_gun_{i}'
                    
                    val = getattr(grid, gun_col, None)
                    
                    # Eğer değer boşsa ve o gün resmi tatilse, 'T' olarak işaretle
                    if (val is None or val == '') and i in holiday_days:
                        row[gun_col] = 'T'  # Resmi Tatil
                    else:
                        row[gun_col] = val.value if hasattr(val, 'value') else val
                    
                    fm_val = getattr(grid, fm_col, None)
                    row[fm_col] = float(fm_val) if fm_val is not None else None
                
                result.append(row)
        else:
            # Grid'de kayıt yoksa, personnel'den al
            # Önce cost center kriterine uyan personnel_id'leri bul
            contract_subquery = db.query(PersonnelContract.personnel_id).filter(
                PersonnelContract.baslangic_tarihi <= donem_son_gun,
                or_(
                    PersonnelContract.bitis_tarihi == None,
                    PersonnelContract.bitis_tarihi >= donem_ilk_gun
                ),
                PersonnelContract.aktif == True
            )
            
            # Cost center filtresi varsa uygula
            if cost_center_id:
                contract_subquery = contract_subquery.filter(
                    PersonnelContract.cost_center_id == cost_center_id
                )
            
            personnel_ids = [p[0] for p in contract_subquery.distinct().all()]
            
            if personnel_ids:
                # Personnel'leri toplu çek
                personnel_list = db.query(Personnel).filter(
                    Personnel.id.in_(personnel_ids)
                ).all()
                
                # Contract'ları toplu çek
                contracts = db.query(PersonnelContract).filter(
                    PersonnelContract.personnel_id.in_(personnel_ids),
                    PersonnelContract.baslangic_tarihi <= donem_son_gun,
                    or_(
                        PersonnelContract.bitis_tarihi == None,
                        PersonnelContract.bitis_tarihi >= donem_ilk_gun
                    )
                ).order_by(PersonnelContract.personnel_id, PersonnelContract.baslangic_tarihi.desc()).all()
                
                # Her personnel için en son contract'ı bul
                contract_dict = {}
                for c in contracts:
                    if c.personnel_id not in contract_dict:
                        contract_dict[c.personnel_id] = c
                
                for person in personnel_list:
                    contract = contract_dict.get(person.id)
                    
                    row = {
                        'id': person.id,
                        'adi_soyadi': f"{person.ad} {person.soyad}",
                        'tc_kimlik_no': person.tc_kimlik_no or '',
                        'cost_center_id': contract.cost_center_id if contract else None
                    }
                    
                    # 31 günlük kolonlar - resmi tatilleri otomatik 'T' yap
                    for i in range(1, 32):
                        # Resmi tatil mi kontrol et
                        if i in holiday_days:
                            row[f'gun_{i}'] = 'T'  # Resmi Tatil
                        else:
                            row[f'gun_{i}'] = None
                        row[f'fm_gun_{i}'] = None
                    
                    result.append(row)
        
        return {
            "success": True,
            "donem": donem,
            "total": len(result),
            "records": result,
            "holidays": list(holiday_days)  # Resmi tatil günlerini frontend'e gönder
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/grid/save")
async def save_grid_data(
    request: GridSaveRequest,
    db: Session = Depends(get_db)
):
    """
    Excel benzeri grid'den gelen verileri kaydet
    Her personel için 31 günlük veriyi INSERT/UPDATE yap
    """
    try:
        year, month = map(int, request.donem.split('-'))
        saved_count = 0
        updated_count = 0
        
        for record in request.records:
            personnel_id = record['id']
            
            # Mevcut kayıt var mı kontrol et
            existing = db.query(PersonnelPuantajGrid).filter(
                and_(
                    PersonnelPuantajGrid.personnel_id == personnel_id,
                    PersonnelPuantajGrid.donem == request.donem
                )
            ).first()
            
            # 31 günlük verileri hazırla
            gun_data = {}
            for i in range(1, 32):
                gun_col = f'gun_{i}'
                val = record.get(gun_col)
                
                # Boş değerleri None yap
                if val in [None, '', '-']:
                    gun_data[gun_col] = None
                else:
                    # Enum'a çevir
                    try:
                        gun_data[gun_col] = PuantajDurum(val)
                    except:
                        gun_data[gun_col] = None
            
            if existing:
                # UPDATE
                for key, value in gun_data.items():
                    setattr(existing, key, value)
                existing.updated_at = datetime.now()
                updated_count += 1
            else:
                # INSERT
                new_record = PersonnelPuantajGrid(
                    personnel_id=personnel_id,
                    donem=request.donem,
                    yil=year,
                    ay=month,
                    **gun_data
                )
                db.add(new_record)
                saved_count += 1
        
        db.commit()
        
        return {
            "success": True,
            "donem": request.donem,
            "saved": saved_count,
            "updated": updated_count,
            "total": saved_count + updated_count
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
