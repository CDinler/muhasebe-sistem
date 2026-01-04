"""
Monthly Puantaj API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
from pydantic import BaseModel
from datetime import date
import pandas as pd
import io

from app.core.database import get_db
from app.models.monthly_puantaj import MonthlyPuantaj

router = APIRouter()


class PuantajCreate(BaseModel):
    personnel_id: int
    yil: int
    ay: int
    normal_gun: int = 0
    fazla_mesai_saat: float = 0
    hafta_tatili_gun: int = 0
    tatil_mesai_gun: int = 0
    yillik_izin_gun: int = 0
    ucretsiz_izin_gun: int = 0
    rapor_gun: int = 0


@router.post("/test-upload")
async def test_upload_puantaj(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    TEST MODE: Excel'i parse et, hesaplamaları göster AMA VERİTABANINA YAZMA
    Sözleşme, bordro, maliyet hesaplamalarını test et
    """
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(400, "Excel dosyası (.xlsx) gerekli")
    
    content = await file.read()
    df = pd.read_excel(io.BytesIO(content))
    
    # Sütun kontrolü
    required = ['TC', 'Yıl', 'Ay']
    if not all(col in df.columns for col in required):
        raise HTTPException(400, f"Gerekli sütunlar: {required}")
    
    from app.models.personnel import Personnel
    from app.models.personnel_contract import PersonnelContract
    from app.models.luca_bordro import LucaBordro
    
    test_results = []
    summary = {
        'toplam_personel': 0,
        'bulunan_personel': 0,
        'sozlesme_var': 0,
        'luca_bordro_var': 0,
        'hatalar': []
    }
    
    for idx, row in df.iterrows():
        try:
            tckn = str(row['TC']).strip()
            yil = int(row['Yıl'])
            ay = int(row['Ay'])
            donem = f"{yil}-{ay:02d}"
            
            # Personnel bul
            personnel = db.query(Personnel).filter(Personnel.tckn == tckn).first()
            if not personnel:
                summary['hatalar'].append(f"Satır {idx+2}: TC {tckn} bulunamadı")
                continue
            
            summary['toplam_personel'] += 1
            summary['bulunan_personel'] += 1
            
            # Sözleşme bul
            contract = db.query(PersonnelContract).filter(
                PersonnelContract.personnel_id == personnel.id,
                PersonnelContract.is_active == 1
            ).first()
            
            # Luca Bordro bul
            luca = db.query(LucaBordro).filter(
                LucaBordro.tckn == tckn,
                LucaBordro.yil == yil,
                LucaBordro.ay == ay
            ).first()
            
            # Puantaj verileri (NaN'leri 0'a çevir)
            import math
            normal_gun = float(row.get('Normal Gün', 0) or 0)
            if math.isnan(normal_gun): normal_gun = 0
            
            fm_saat = float(row.get('FM Saat', 0) or 0)
            if math.isnan(fm_saat): fm_saat = 0
            
            hafta_tatili = float(row.get('Hafta Tatili', 0) or 0)
            if math.isnan(hafta_tatili): hafta_tatili = 0
            
            # HESAPLAMALAR
            hesaplama = {
                'tckn': tckn,
                'ad_soyad': row.get('Ad Soyad', ''),
                'normal_gun': normal_gun,
                'fm_saat': fm_saat,
                'hafta_tatili': hafta_tatili,
                
                # Sözleşme bilgileri
                'sozlesme_var': contract is not None,
                'sozlesme_ucret': float(contract.maas1_tutar) if (contract and contract.maas1_tutar) else 0,
                'sozlesme_ucret_tipi': contract.maas1_tip if contract else None,
                'sozlesme_baslangic': str(contract.ise_giris_tarihi) if contract else None,
                'ucret_nevi': contract.ucret_nevi.value if contract else None,
                
                # Luca Bordro bilgileri
                'luca_bordro_var': luca is not None,
                'luca_net_odenen': float(luca.net_odenen) if luca else 0,
                'luca_isveren_maliyeti': float(luca.isveren_maliyeti) if luca else 0,
                
                # Hesaplanan değerler (basit örnek)
                'gunluk_ucret': float(contract.maas1_tutar) / 30 if (contract and contract.maas1_tutar) else 0,
                'normal_gun_toplam': (float(contract.maas1_tutar) / 30 * normal_gun) if (contract and contract.maas1_tutar) else 0,
                'fm_ucret_saat': (float(contract.maas1_tutar) / 30 / 8 * 1.5 * fm_saat) if (contract and contract.maas1_tutar) else 0,
            }
            
            if contract:
                summary['sozlesme_var'] += 1
            if luca:
                summary['luca_bordro_var'] += 1
            
            test_results.append(hesaplama)
            
        except Exception as e:
            summary['hatalar'].append(f"Satır {idx+2}: {str(e)}")
    
    return {
        "success": True,
        "test_mode": True,
        "summary": summary,
        "results": test_results[:50],  # İlk 50 kayıt
        "message": "TEST MODE: Veritabanına hiçbir değişiklik yapılmadı"
    }


@router.post("/upload")
async def upload_puantaj(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Excel'den puantaj yükle
    Sütunlar: TC, Yıl, Ay, Normal Gün, FM Saat, Hafta Tatili, Tatil Mesai, Yıllık İzin, Ücretsiz İzin, Rapor
    """
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(400, "Excel dosyası (.xlsx) gerekli")
    
    content = await file.read()
    df = pd.read_excel(io.BytesIO(content))
    
    # Sütun eşleme
    required = ['TC', 'Yıl', 'Ay']
    if not all(col in df.columns for col in required):
        raise HTTPException(400, f"Gerekli sütunlar: {required}")
    
    uploaded = 0
    updated = 0
    errors = []
    
    for idx, row in df.iterrows():
        try:
            from app.models.personnel import Personnel
            from app.models.cost_centers import CostCenter
            
            # Personnel ID bul
            tckn = str(row['TC']).strip()
            personnel = db.query(Personnel).filter(Personnel.tckn == tckn).first()
            if not personnel:
                errors.append(f"Satır {idx+2}: TC {tckn} bulunamadı")
                continue
            
            # Bölüm/Şantiye bilgisi varsa cost_center_id bul
            cost_center_id = None
            bolum_adi = str(row.get('Bölüm/Şantiye', '')).strip()
            if bolum_adi:
                cost_center = db.query(CostCenter).filter(CostCenter.name == bolum_adi).first()
                if cost_center:
                    cost_center_id = cost_center.id
            
            # Mevcut kayıt var mı? (TC + Yıl + Ay + Bölüm kombinasyonu)
            existing = db.query(MonthlyPuantaj).filter(
                MonthlyPuantaj.personnel_id == personnel.id,
                MonthlyPuantaj.yil == int(row['Yıl']),
                MonthlyPuantaj.ay == int(row['Ay']),
                MonthlyPuantaj.santiye_adi == bolum_adi if bolum_adi else MonthlyPuantaj.santiye_adi.is_(None)
            ).first()
            
            data = {
                'personnel_id': personnel.id,
                'tckn': tckn,
                'adi_soyadi': str(row.get('Ad Soyad', '')),
                'santiye_adi': bolum_adi,
                'cost_center_id': cost_center_id,
                'yil': int(row['Yıl']),
                'ay': int(row['Ay']),
                'donem': f"{int(row['Yıl'])}-{int(row['Ay']):02d}",
                'normal_gun': float(row.get('Normal Gün', 0)),
                'fazla_mesai_saat': float(row.get('FM Saat', 0)),
                'hafta_tatili_gun': float(row.get('Hafta Tatili', 0)),
                'tatil_mesai_gun': float(row.get('Tatil Mesai', 0)),
                'yillik_izin_gun': float(row.get('Yıllık İzin', 0)),
                'ucretsiz_izin_gun': float(row.get('Ücretsiz İzin', 0)),
                'rapor_gun': float(row.get('Rapor', 0))
            }
            
            if existing:
                for key, value in data.items():
                    setattr(existing, key, value)
                updated += 1
            else:
                db.add(MonthlyPuantaj(**data))
                uploaded += 1
                
        except Exception as e:
            errors.append(f"Satır {idx+2}: {str(e)}")
            continue
    
    db.commit()
    
    return {
        "success": True,
        "uploaded": uploaded,
        "updated": updated,
        "errors": errors[:50] if errors else [],
        "message": f"{uploaded} yeni, {updated} güncelleme yapıldı" + (f", {len(errors)} hata" if errors else "")
    }


@router.get("/list")
def list_puantaj(
    yil: int,
    ay: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Puantaj listele"""
    from app.models.personnel import Personnel
    
    query = db.query(MonthlyPuantaj).filter(
        MonthlyPuantaj.yil == yil,
        MonthlyPuantaj.ay == ay
    )
    
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    
    result = []
    for item in items:
        personnel = db.query(Personnel).filter(Personnel.id == item.personnel_id).first()
        result.append({
            "id": item.id,
            "personnel_id": item.personnel_id,
            "personnel_name": f"{personnel.first_name} {personnel.last_name}" if personnel else "?",
            "tckn": personnel.tckn if personnel else None,
            "yil": item.yil,
            "ay": item.ay,
            "normal_gun": item.normal_gun,
            "fazla_mesai_saat": item.fazla_mesai_saat,
            "hafta_tatili_gun": item.hafta_tatili_gun,
            "tatil_mesai_gun": item.tatil_mesai_gun,
            "yillik_izin_gun": item.yillik_izin_gun,
            "ucretsiz_izin_gun": item.ucretsiz_izin_gun,
            "rapor_gun": item.rapor_gun
        })
    
    return {
        "total": total,
        "items": result
    }


@router.get("/template/{donem}")
def download_puantaj_template(
    donem: str,  # YYYY-MM format
    db: Session = Depends(get_db)
):
    """
    Puantaj Excel şablonu indir (dönem personel listesi ile birlikte)
    """
    from app.models.personnel import Personnel
    from app.models.luca_bordro import LucaBordro
    
    try:
        yil, ay = donem.split('-')
        yil = int(yil)
        ay = int(ay)
    except:
        raise HTTPException(400, "Dönem formatı YYYY-MM olmalı (örn: 2025-11)")
    
    # O dönemde monthly_personnel_records kayıtlarını al (HER BÖLÜM AYRI SATIR)
    from app.models.monthly_personnel_record import MonthlyPersonnelRecord
    
    mpr_records = db.query(MonthlyPersonnelRecord).filter(
        MonthlyPersonnelRecord.donem == donem
    ).order_by(MonthlyPersonnelRecord.personnel_id, MonthlyPersonnelRecord.bolum_adi).all()
    
    # Excel şablonu oluştur
    data = []
    
    # Luca bordro + MonthlyPersonnelRecord birleştir (bölüm bilgisi için)
    luca_records = db.query(LucaBordro).filter(
        LucaBordro.yil == yil,
        LucaBordro.ay == ay
    ).order_by(LucaBordro.adi_soyadi).all()
    
    if luca_records:
        # TC'ye göre MonthlyPersonnelRecord map oluştur
        mpr_map = {}
        for mpr in mpr_records:
            personnel = db.query(Personnel).filter(Personnel.id == mpr.personnel_id).first()
            if personnel and personnel.tckn:
                if personnel.tckn not in mpr_map:
                    mpr_map[personnel.tckn] = []
                mpr_map[personnel.tckn].append(mpr)
        
        for luca in luca_records:
            tckn = luca.tckn or ''
            bolum = ''
            
            # TC'den bölüm bilgisini al
            if tckn and tckn in mpr_map:
                # İlk kaydın bölümünü al
                bolum = mpr_map[tckn][0].bolum_adi or ''
            
            data.append({
                'TC': tckn,
                'Ad Soyad': luca.adi_soyadi or '',
                'Bölüm/Şantiye': bolum,
                'Departman': '',
                'Yıl': yil,
                'Ay': ay,
                'Normal Gün': 0,
                'FM Saat': 0.0,
                'Hafta Tatili': 0,
                'Tatil Mesai': 0,
                'Yıllık İzin': 0,
                'Ücretsiz İzin': 0,
                'Rapor': 0
            })
    else:
        # Luca yoksa: Aktif personelleri al
        personnel_list = db.query(Personnel).filter(Personnel.is_active == 1).order_by(Personnel.first_name).all()
        for p in personnel_list:
            data.append({
                'TC': p.tckn or '',
                'Ad Soyad': f"{p.first_name or ''} {p.last_name or ''}".strip(),
                'Bölüm/Şantiye': '',
                'Departman': p.department or '',
                'Yıl': yil,
                'Ay': ay,
                'Normal Gün': 0,
                'FM Saat': 0.0,
                'Hafta Tatili': 0,
                'Tatil Mesai': 0,
                'Yıllık İzin': 0,
                'Ücretsiz İzin': 0,
                'Rapor': 0
            })
    
    if not data:
        raise HTTPException(400, f"Dönem {donem} için personel bulunamadı")
    
    df = pd.DataFrame(data)
    
    # Excel dosyası oluştur
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Puantaj')
        
        # Sütun genişliklerini ayarla
        worksheet = writer.sheets['Puantaj']
        worksheet.column_dimensions['A'].width = 15  # TC
        worksheet.column_dimensions['B'].width = 30  # Ad Soyad
        worksheet.column_dimensions['C'].width = 45  # Bölüm/Şantiye
        worksheet.column_dimensions['D'].width = 35  # Departman
        worksheet.column_dimensions['E'].width = 8   # Yıl
        worksheet.column_dimensions['F'].width = 8   # Ay
        worksheet.column_dimensions['G'].width = 12  # Normal Gün
        worksheet.column_dimensions['H'].width = 12  # FM Saat
        worksheet.column_dimensions['I'].width = 12  # Hafta Tatili
        worksheet.column_dimensions['J'].width = 12  # Tatil Mesai
        worksheet.column_dimensions['K'].width = 12  # Yıllık İzin
        worksheet.column_dimensions['L'].width = 14  # Ücretsiz İzin
        worksheet.column_dimensions['M'].width = 10  # Rapor
    
    output.seek(0)
    
    filename = f"Puantaj_Sablonu_{donem}_{len(data)}_Personel.xlsx"
    
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
