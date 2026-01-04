"""
Luca Personel Sicil Import API
Luca'dan export edilen aylık personel sicil Excel dosyalarını import eder
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func
from typing import List, Optional
from datetime import datetime, date
import pandas as pd
import io
import time

from app.core.database import get_db
from app.models.personnel import Personnel
from app.models.monthly_personnel_record import MonthlyPersonnelRecord
from app.models.cost_center import CostCenter
from app.models.account import Account
from app.schemas.monthly_personnel_record import (
    MonthlyPersonnelRecordResponse,
    MonthlyPersonnelRecordList
)
from pydantic import BaseModel

router = APIRouter()


class LucaSicilImportResponse(BaseModel):
    """Luca sicil import yanıtı"""
    success: bool
    message: str
    donem: str
    total_rows: int
    imported_records: int
    updated_records: int
    skipped_records: int
    errors: List[dict] = []
    warnings: List[dict] = []


class MonthlyPersonnelRecordResponse(BaseModel):
    """Aylık personel kaydı yanıtı"""
    id: int
    personnel_id: int
    personnel_name: str
    donem: str
    bolum_adi: Optional[str]
    cost_center_code: Optional[str]
    ise_giris_tarihi: Optional[date]
    isten_cikis_tarihi: Optional[date]
    dogum_tarihi: Optional[date]
    calisilan_gun: Optional[int]
    ucret: Optional[float]
    ucret_tipi: Optional[str]
    isyeri: Optional[str]
    unvan: Optional[str]
    meslek_adi: Optional[str]
    meslek_kodu: Optional[str]
    sgk_no: Optional[str]
    
    class Config:
        from_attributes = True


def parse_luca_sicil_excel(file_content: bytes) -> pd.DataFrame:
    """
    Luca sicil Excel dosyasını parse et
    
    Beklenen kolonlar:
    - TC Kimlik No
    - Adı, Soyadı (ayrı kolonlar)
    - Bölüm
    - İşyeri
    - İşe Giriş Tarihi, İşten Çıkış Tarihi
    - Ücret, Net / Brüt
    - Ünvan, Meslek Adı
    """
    try:
        df = pd.read_excel(io.BytesIO(file_content))
        
        # Adı ve Soyadı varsa birleştir
        if 'Adı' in df.columns and 'Soyadı' in df.columns:
            df['Ad Soyad'] = df['Adı'].astype(str).str.strip() + ' ' + df['Soyadı'].astype(str).str.strip()
            df['Ad Soyad'] = df['Ad Soyad'].str.strip()
        
        # Gerekli kolonları kontrol et
        required_columns = ['TC Kimlik No', 'Bölüm', 'İşe Giriş Tarihi', 'Ücret']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise ValueError(f"Eksik kolonlar: {', '.join(missing_columns)}")
        
        return df
        
    except Exception as e:
        raise ValueError(f"Excel dosyası okunamadı: {str(e)}")


def extract_donem_from_dates(df: pd.DataFrame) -> str:
    """
    İşe giriş tarihlerinden dönem çıkar (YYYY-MM)
    En yaygın ayı dönem olarak al
    """
    # İşe giriş tarihlerini datetime'a çevir
    giris_tarihleri = pd.to_datetime(df['İşe Giriş Tarihi'], errors='coerce')
    
    # En yaygın yıl-ay kombinasyonunu bul
    donem_counts = giris_tarihleri.dt.to_period('M').value_counts()
    
    if len(donem_counts) == 0:
        # Tarihlerde hata varsa bugünün ayını al
        today = datetime.now()
        return f"{today.year}-{today.month:02d}"
    
    most_common_period = donem_counts.index[0]
    return str(most_common_period)


def match_cost_center(db: Session, bolum_adi: str) -> Optional[CostCenter]:
    """
    Bölüm adından maliyet merkezi bul - Mapping tablosunu kullanır
    
    Öncelik sırası:
    1. Tam eşleşme (luca_bolum_pattern = bolum_adi)
    2. Wildcard eşleşme (luca_bolum_pattern LIKE '%pattern%')
    3. Prefix eşleşme (bölüm adının başındaki sayı)
    """
    if not bolum_adi:
        return None
    
    from sqlalchemy import text
    
    # 1. Önce mapping tablosundan tam eşleşme ara
    result = db.execute(text("""
        SELECT cc.id, cc.code, cc.name
        FROM luca_bolum_cost_center_mapping lm
        JOIN cost_centers cc ON cc.id = lm.cost_center_id
        WHERE lm.is_active = 1
          AND lm.luca_bolum_pattern = :bolum_adi
        ORDER BY lm.priority
        LIMIT 1
    """), {"bolum_adi": bolum_adi}).fetchone()
    
    if result:
        return db.query(CostCenter).filter(CostCenter.id == result[0]).first()
    
    # 2. Wildcard eşleşme (%pattern%)
    result = db.execute(text("""
        SELECT cc.id, cc.code, cc.name, lm.priority
        FROM luca_bolum_cost_center_mapping lm
        JOIN cost_centers cc ON cc.id = lm.cost_center_id
        WHERE lm.is_active = 1
          AND lm.luca_bolum_pattern LIKE '%\\%%'
          AND :bolum_adi LIKE REPLACE(lm.luca_bolum_pattern, '%', '%%')
        ORDER BY lm.priority
        LIMIT 1
    """), {"bolum_adi": bolum_adi}).fetchone()
    
    if result:
        return db.query(CostCenter).filter(CostCenter.id == result[0]).first()
    
    # 3. Prefix eşleşme (fallback - eski mantık)
    parts = bolum_adi.split('-')
    if len(parts) > 0 and parts[0].strip().isdigit():
        prefix = parts[0].strip()
        
        result = db.execute(text("""
            SELECT cc.id, cc.code, cc.name
            FROM luca_bolum_cost_center_mapping lm
            JOIN cost_centers cc ON cc.id = lm.cost_center_id
            WHERE lm.is_active = 1
              AND lm.luca_bolum_prefix = :prefix
            ORDER BY lm.priority
            LIMIT 1
        """), {"prefix": prefix}).fetchone()
        
        if result:
            return db.query(CostCenter).filter(CostCenter.id == result[0]).first()
    
    return None


@router.post("/upload", response_model=LucaSicilImportResponse)
async def upload_luca_sicil(
    file: UploadFile = File(...),
    force_update: bool = False,
    donem: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Luca personel sicil Excel dosyasını import et
    
    **Parametreler:**
    - file: Luca sicil Excel dosyası (.xlsx)
    - force_update: Mevcut kayıtları güncelle (True) veya atla (False)
    - donem: Manuel dönem (YYYY-MM formatında, ör: 2025-01). Belirtilmezse otomatik tespit edilir.
    
    **Dönem Belirleme:**
    - donem parametresi verilirse: O dönem kullanılır
    - donem parametresi yoksa: Excel'deki "İşe Giriş Tarihi" kolonundan otomatik tespit edilir
    
    **Eşleştirme:**
    - Personnel: TC Kimlik No ile eşleştirilir
    - Cost Center: Bölüm adının başındaki kod ile eşleştirilir (örn: "34-HABAŞ" -> "34")
    
    **Unique Constraint:**
    (personnel_id, donem, bolum_adi) kombinasyonu unique'tir
    Aynı personel, aynı dönemde, aynı bölümde sadece 1 kayıt olabilir
    """
    errors = []
    warnings = []
    imported_count = 0
    updated_count = 0
    skipped_count = 0
    
    start_time = time.time()
    
    try:
        # Dosyayı oku
        t1 = time.time()
        content = await file.read()
        df = parse_luca_sicil_excel(content)
        print(f"⏱️ Excel parse: {time.time() - t1:.2f}s")
        
        # Dönemi belirle (manuel veya otomatik)
        t2 = time.time()
        if donem:
            # Manuel dönem kontrolü
            import re
            if not re.match(r'^\d{4}-\d{2}$', donem):
                raise HTTPException(400, "Dönem formatı hatalı. YYYY-MM formatında olmalı (örn: 2025-01)")
            final_donem = donem
        else:
            # Otomatik dönem tespiti
            final_donem = extract_donem_from_dates(df)
        print(f"⏱️ Dönem tespit: {time.time() - t2:.2f}s")
        
        # PERFORMANS: Tüm TC'leri topla ve tek sorguda personnel'leri al
        t3 = time.time()
        all_tcs = []
        for _, row in df.iterrows():
            tc = str(int(row['TC Kimlik No'])) if pd.notna(row.get('TC Kimlik No')) else None
            if tc:
                all_tcs.append(tc)
        
        personnel_map = {p.tckn: p for p in db.query(Personnel).filter(Personnel.tckn.in_(all_tcs)).all()}
        print(f"[UPLOAD] Found {len(personnel_map)} personnel out of {len(all_tcs)} TCs")
        print(f"⏱️ Personnel query: {time.time() - t3:.2f}s")
        
        # Existing records cache (tüm dönem kayıtlarını al)
        t4 = time.time()
        existing_records = db.query(MonthlyPersonnelRecord).filter(
            MonthlyPersonnelRecord.donem == final_donem
        ).all()
        # CRITICAL: Strip bolum_adi + giriş tarihi ile unique key (aynı kişi aynı ayda 2 kez giriş-çıkış yapabilir)
        existing_map = {
            (r.personnel_id, r.bolum_adi.strip() if r.bolum_adi else None, r.ise_giris_tarihi): r 
            for r in existing_records
        }
        print(f"[UPLOAD] Found {len(existing_map)} existing records for donem={final_donem}")
        print(f"⏱️ Existing records query: {time.time() - t4:.2f}s")
        
        # Cost center mapping'i şimdilik NULL bırak (tablo henüz yok)
        # TODO: luca_bolum_cost_center_mapping tablosu oluşturulunca aktif et
        
        # Her satırı işle
        t5 = time.time()
        print(f"[UPLOAD] Processing {len(df)} rows...")
        
        # Bulk insert için liste
        new_records = []
        
        for index, row in df.iterrows():
            try:
                # TC Kimlik No kontrolü
                tc = str(int(row['TC Kimlik No'])) if pd.notna(row['TC Kimlik No']) else None
                if not tc:
                    warnings.append({
                        "row": index + 2,  # Excel satır numarası (header + 1)
                        "message": "TC Kimlik No boş"
                    })
                    skipped_count += 1
                    print(f"[ROW {index+2}] SKIP: No TC")
                    continue
                
                # Personeli map'ten al (artık her satır için query yok!)
                personnel = personnel_map.get(tc)
                if not personnel:
                    # YENİ PERSONEL OLUŞTUR
                    # Luca sicil Excel'i authoritative source - varsa bizde de olmalı
                    ad_soyad = str(row.get('Ad Soyad', '')).strip() if pd.notna(row.get('Ad Soyad')) else ''
                    
                    # Ad Soyad'ı split et
                    parts = ad_soyad.split(maxsplit=1)
                    first_name = parts[0] if len(parts) > 0 else 'UNKNOWN'
                    last_name = parts[1] if len(parts) > 1 else ''
                    
                    # İşe Giriş/Çıkış tarihleri (Excel'den al)
                    ise_giris = pd.to_datetime(row.get('İşe Giriş Tarihi'), errors='coerce')
                    ise_giris_date = ise_giris.date() if pd.notna(ise_giris) else None
                    
                    isten_cikis = pd.to_datetime(row.get('İşten Çıkış Tarihi'), errors='coerce')
                    isten_cikis_date = isten_cikis.date() if pd.notna(isten_cikis) else None
                    
                    # Departman ve bölüm
                    bolum_adi = str(row.get('Bölüm')).strip() if pd.notna(row.get('Bölüm')) else None
                    
                    # 335.xxx hesabını oluştur (PERSONELE BORÇLAR)
                    account_code = f"335.{tc}"
                    account = db.query(Account).filter(Account.code == account_code).first()
                    if not account:
                        account = Account(
                            code=account_code,
                            name=f"{first_name} {last_name}",
                            account_type="liability",
                            is_active=True
                        )
                        db.add(account)
                        db.flush()
                    
                    personnel = Personnel(
                        code=new_code,
                        first_name=first_name,
                        last_name=last_name,
                        tckn=tc,
                        account_id=account.id,
                        start_date=ise_giris_date,
                        end_date=isten_cikis_date,
                        department=bolum_adi,
                        is_active=(isten_cikis_date is None)  # Çıkış tarihi yoksa aktif
                    )
                    db.add(personnel)
                    db.flush()  # ID'yi al
                    
                    # Map'e ekle (diğer satırlarda da kullan)
                    personnel_map[tc] = personnel
                    
                    warnings.append({
                        "row": index + 2,
                        "tc": tc,
                        "message": f"Yeni personel oluşturuldu: {ad_soyad} (ID={personnel.id})"
                    })
                    print(f"[ROW {index+2}] NEW PERSONNEL: TC={tc}, Name={ad_soyad}, ID={personnel.id}")
                
                # MEVCUT personel ise start_date ve end_date'i GÜNCELLE (en son bilgiyle)
                # Tarihleri parse et (tekrar parse etmeden önce)
                ise_giris_row = pd.to_datetime(row.get('İşe Giriş Tarihi'), errors='coerce')
                ise_giris_date_row = ise_giris_row.date() if pd.notna(ise_giris_row) else None
                
                isten_cikis_row = pd.to_datetime(row.get('İşten Çıkış Tarihi'), errors='coerce')
                isten_cikis_date_row = isten_cikis_row.date() if pd.notna(isten_cikis_row) else None
                
                bolum_adi_row = str(row.get('Bölüm')).strip() if pd.notna(row.get('Bölüm')) else None
                
                # Personnel kaydını güncelle
                if ise_giris_date_row:
                    # En erken giriş tarihini tut
                    if personnel.start_date is None or ise_giris_date_row < personnel.start_date:
                        personnel.start_date = ise_giris_date_row
                
                if isten_cikis_date_row:
                    # En son çıkış tarihini tut
                    if personnel.end_date is None or isten_cikis_date_row > personnel.end_date:
                        personnel.end_date = isten_cikis_date_row
                        personnel.is_active = False
                else:
                    # Çıkış tarihi yoksa aktif
                    if personnel.end_date is None:
                        personnel.is_active = True
                
                if bolum_adi_row and not personnel.department:
                    personnel.department = bolum_adi_row
                
                print(f"[ROW {index+2}] Processing TC={tc}, Personnel ID={personnel.id}")
                
                # Bölüm adı - STRIP trailing spaces
                bolum_adi = str(row.get('Bölüm')).strip() if pd.notna(row.get('Bölüm')) else None
                print(f"[ROW {index+2}] Bolum={bolum_adi}")
                
                # Cost center şimdilik NULL (mapping tablosu henüz yok)
                cost_center = None
                
                # Tarihleri parse et
                ise_giris = pd.to_datetime(row.get('İşe Giriş Tarihi'), errors='coerce')
                ise_giris_date = ise_giris.date() if pd.notna(ise_giris) else None
                
                isten_cikis = pd.to_datetime(row.get('İşten Çıkış Tarihi'), errors='coerce')
                isten_cikis_date = isten_cikis.date() if pd.notna(isten_cikis) else None
                
                dogum = pd.to_datetime(row.get('Doğum Tarihi'), errors='coerce')
                dogum_tarihi = dogum.date() if pd.notna(dogum) else None
                
                # Ücret
                ucret = float(row.get('Ücret')) if pd.notna(row.get('Ücret')) else None
                # Ücret Tipi - Net / Brüt kolonundan al
                ucret_tipi = row.get('Net / Brüt') if pd.notna(row.get('Net / Brüt')) else row.get('Ücret Tipi')
                
                # Meslek bilgileri - JSON'da kalacak, tabloya kaydetme
                # meslek_adi = row.get('Meslek Adı') if pd.notna(row.get('Meslek Adı')) else None
                # meslek_kodu = row.get('Meslek Kodu') if pd.notna(row.get('Meslek Kodu')) else None
                # SGK No - float olabilir, güvenli şekilde çevir
                try:
                    sgk_no = str(int(float(row.get('SSK No')))) if pd.notna(row.get('SSK No')) else None
                except:
                    sgk_no = str(row.get('SSK No')) if pd.notna(row.get('SSK No')) else None
                
                # Luca raw data (tüm kolonları JSON'a çevir) - BASITLEŞTIRILDI
                import json
                luca_data = row.to_dict()
                # NaN ve Timestamp'leri hızlıca düzelt
                for k, v in luca_data.items():
                    if pd.isna(v):
                        luca_data[k] = None
                    elif isinstance(v, (pd.Timestamp, datetime, date)):
                        luca_data[k] = v.isoformat()
                    elif isinstance(v, pd.Timedelta):
                        luca_data[k] = str(v)
                    elif isinstance(v, float) and (v != v):  # NaN check
                        luca_data[k] = None
                
                # Mevcut kaydı kontrol et (cache'den) - giriş tarihi ile unique
                existing = existing_map.get((personnel.id, bolum_adi, ise_giris_date))
                # Debug print sadece ilk 5 ve son 5 satır için
                # if index < 5 or index >= len(df) - 5:
                #     print(f"[ROW {index+2}] Existing check: key=({personnel.id}, '{bolum_adi}', {ise_giris_date}), found={existing is not None}")
                
                # DEBUG: Log to see what's happening
                # print(f"[DEBUG] Row {index+2}: TC={tc}, Personnel={personnel.id}, Existing={existing is not None}, Force={force_update}")
                
                if existing:
                    if force_update:
                        # Güncelle
                        existing.cost_center_id = cost_center.id if cost_center else None
                        existing.cost_center_code = cost_center.code if cost_center else None
                        existing.ise_giris_tarihi = ise_giris_date
                        existing.isten_cikis_tarihi = isten_cikis_date
                        existing.dogum_tarihi = dogum_tarihi
                        existing.ucret = ucret
                        existing.ucret_tipi = ucret_tipi
                        existing.luca_sicil_data = luca_data
                        existing.isyeri = row.get('İşyeri') if pd.notna(row.get('İşyeri')) else None
                        existing.unvan = row.get('Ünvan') if pd.notna(row.get('Ünvan')) else None
                        existing.meslek_adi = None  # JSON'da
                        existing.meslek_kodu = None  # JSON'da
                        existing.sgk_no = sgk_no
                        updated_count += 1
                        # print(f"[DEBUG] → Updated existing record")
                    else:
                        # Atla
                        skipped_count += 1
                        # print(f"[DEBUG] → Skipped (existing, no force)")
                        continue
                else:
                    # Yeni kayıt oluştur (bulk insert için listeye ekle)
                    record = MonthlyPersonnelRecord(
                        personnel_id=personnel.id,
                        donem=final_donem,
                        bolum_adi=bolum_adi,
                        cost_center_id=cost_center.id if cost_center else None,
                        cost_center_code=cost_center.code if cost_center else None,
                        ise_giris_tarihi=ise_giris_date,
                        isten_cikis_tarihi=isten_cikis_date,
                        dogum_tarihi=dogum_tarihi,
                        ucret=ucret,
                        ucret_tipi=ucret_tipi,
                        luca_sicil_data=luca_data,
                        isyeri=row.get('İşyeri') if pd.notna(row.get('İşyeri')) else None,
                        unvan=row.get('Ünvan') if pd.notna(row.get('Ünvan')) else None,
                        meslek_adi=None,  # JSON'da
                        meslek_kodu=None,  # JSON'da
                        sgk_no=sgk_no,
                    )
                    new_records.append(record)
                    imported_count += 1
                    # if index < 5 or index >= len(df) - 5:
                    #     print(f"[DEBUG] → Created new record (queued for bulk insert)")
                
            except Exception as e:
                print(f"[ROW {index+2}] ERROR: {str(e)}")
                import traceback
                traceback.print_exc()
                errors.append({
                    "row": index + 2,
                    "message": str(e)
                })
                continue
        
        print(f"⏱️ Row processing: {time.time() - t5:.2f}s")
        
        # Bulk insert (çok daha hızlı!)
        if new_records:
            t_bulk = time.time()
            db.bulk_save_objects(new_records)
            print(f"⏱️ Bulk insert ({len(new_records)} records): {time.time() - t_bulk:.2f}s")
        
        # Commit
        t6 = time.time()
        db.commit()
        print(f"⏱️ DB commit: {time.time() - t6:.2f}s")
        
        print(f"⏱️ TOTAL UPLOAD TIME: {time.time() - start_time:.2f}s")
        
        # Warnings'leri log dosyasına kaydet
        if warnings:
            import os
            log_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'logs')
            os.makedirs(log_dir, exist_ok=True)
            log_file = os.path.join(log_dir, f'sicil_upload_warnings_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt')
            
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write(f"LUCA SİCİL UPLOAD UYARILARI\n")
                f.write(f"Tarih: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Dosya: {file.filename}\n")
                f.write(f"Dönem: {final_donem}\n")
                f.write(f"İmport edilen: {imported_count}\n")
                f.write(f"Güncellenen: {updated_count}\n")
                f.write(f"Atlanan: {skipped_count}\n")
                f.write(f"Uyarı sayısı: {len(warnings)}\n")
                f.write(f"\n{'='*80}\n\n")
                
                for i, warning in enumerate(warnings, 1):
                    f.write(f"{i}. {warning}\n")
            
            print(f"⚠️  Warnings dosyaya kaydedildi: {log_file}")
        
        return LucaSicilImportResponse(
            success=True,
            message=f"{final_donem} dönemi sicil import tamamlandı",
            donem=final_donem,
            total_rows=len(df),
            imported_records=imported_count,
            updated_records=updated_count,
            skipped_records=skipped_count,
            errors=errors,
            warnings=warnings
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/records", response_model=List[MonthlyPersonnelRecordResponse])
def get_monthly_records(
    donem: Optional[str] = None,
    personnel_id: Optional[int] = None,
    cost_center_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 1000,
    db: Session = Depends(get_db)
):
    """
    Aylık personel sicil kayıtlarını listele
    
    **Filtreler:**
    - donem: YYYY-MM formatında (örn: "2025-10")
    - personnel_id: Personel ID
    - cost_center_id: Maliyet merkezi ID
    """
    # Eager loading ile personnel bilgilerini tek seferde al
    # luca_sicil_data field'ını yükleme - çok büyük (her kayıt ~1KB)
    query = db.query(MonthlyPersonnelRecord).options(
        joinedload(MonthlyPersonnelRecord.personnel)
    ).with_entities(
        MonthlyPersonnelRecord.id,
        MonthlyPersonnelRecord.personnel_id,
        MonthlyPersonnelRecord.donem,
        MonthlyPersonnelRecord.bolum_adi,
        MonthlyPersonnelRecord.cost_center_code,
        MonthlyPersonnelRecord.ise_giris_tarihi,
        MonthlyPersonnelRecord.isten_cikis_tarihi,
        MonthlyPersonnelRecord.dogum_tarihi,
        MonthlyPersonnelRecord.calisilan_gun,
        MonthlyPersonnelRecord.ucret,
        MonthlyPersonnelRecord.ucret_tipi,
        MonthlyPersonnelRecord.isyeri,
        MonthlyPersonnelRecord.unvan,
        MonthlyPersonnelRecord.sgk_no,
        Personnel.first_name,
        Personnel.last_name
    ).join(Personnel)
    
    if donem:
        query = query.filter(MonthlyPersonnelRecord.donem == donem)
    
    if personnel_id:
        query = query.filter(MonthlyPersonnelRecord.personnel_id == personnel_id)
    
    if cost_center_id:
        query = query.filter(MonthlyPersonnelRecord.cost_center_id == cost_center_id)
    
    records = query.offset(skip).limit(limit).all()
    
    # Response oluştur
    response = []
    for row in records:
        response.append(MonthlyPersonnelRecordResponse(
            id=row[0],
            personnel_id=row[1],
            personnel_name=f"{row[14]} {row[15]}",  # first_name + last_name
            donem=row[2],
            bolum_adi=row[3],
            cost_center_code=row[4],
            ise_giris_tarihi=row[5],
            isten_cikis_tarihi=row[6],
            dogum_tarihi=row[7],
            calisilan_gun=row[8],
            ucret=float(row[9]) if row[9] else None,
            ucret_tipi=row[10],
            isyeri=row[11],
            unvan=row[12],
            meslek_adi=None,
            meslek_kodu=None,
            sgk_no=row[13]
        ))
    
    return response


@router.get("/periods")
def get_available_periods(db: Session = Depends(get_db)):
    """
    Mevcut dönemleri listele
    """
    from sqlalchemy import distinct
    
    periods = db.query(distinct(MonthlyPersonnelRecord.donem))\
        .order_by(MonthlyPersonnelRecord.donem.desc())\
        .all()
    
    return {"periods": [p[0] for p in periods]}


@router.delete("/period/{donem}")
def delete_period_records(
    donem: str,
    db: Session = Depends(get_db)
):
    """
    Belirli dönemin tüm sicil kayıtlarını sil
    """
    deleted_count = db.query(MonthlyPersonnelRecord)\
        .filter(MonthlyPersonnelRecord.donem == donem)\
        .delete()
    
    db.commit()
    
    return {
        "success": True,
        "message": f"{donem} dönemi {deleted_count} kayıt silindi",
        "deleted_count": deleted_count
    }
