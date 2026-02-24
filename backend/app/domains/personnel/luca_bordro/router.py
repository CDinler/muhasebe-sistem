"""Luca Bordro domain router (V2)"""
from fastapi import APIRouter, Depends, UploadFile, File, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import distinct
from typing import Optional
import pandas as pd
from datetime import datetime
import io
import re

from app.core.database import get_db
from app.domains.auth.dependencies import get_current_user
from app.schemas.auth import UserInDB
from app.models import LucaBordro
from app.models import Personnel
from app.models import PersonnelContract
from app.models import MonthlyPersonnelRecord

router = APIRouter(tags=["Personnel - Luca Bordro (V2)"])


@router.post("/upload")
async def upload_luca_bordro(
    file: UploadFile = File(...),
    donem: str = Query(..., description="Bordro dönemi (YYYY-MM formatında)"),
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Luca'dan çekilen bordro Excel dosyasını yükle ve parse et
    """
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Sadece Excel dosyaları (.xlsx, .xls) yüklenebilir")
    
    # Dönem formatını kontrol et
    if not re.match(r'^\d{4}-\d{2}$', donem):
        raise HTTPException(status_code=400, detail="Dönem formatı hatalı. YYYY-MM formatında olmalı (örn: 2025-11)")
    
    try:
        # Excel dosyasını oku - Birleştirilmiş hücreleri çözmek için openpyxl kullan
        contents = await file.read()
        
        # Önce openpyxl ile birleştirilmiş hücreleri çöz
        import openpyxl
        wb = openpyxl.load_workbook(io.BytesIO(contents))
        ws = wb.active
        
        # Birleştirilmiş hücreleri çöz (merged cells'i unmerge et)
        for merged_cell in list(ws.merged_cells.ranges):
            ws.unmerge_cells(str(merged_cell))
        
        # Çözülmüş Excel'i geçici buffer'a yaz
        temp_buffer = io.BytesIO()
        wb.save(temp_buffer)
        temp_buffer.seek(0)
        
        # Şimdi pandas ile oku (header=9, yani 10. satır başlık)
        df = pd.read_excel(temp_buffer, header=9)
        
        # Birleştirilmiş sütunları düzelt: Değerler bir sonraki sütunda
        # Oto.Kat.BES: Başlık col 23, değer col 24 (Unnamed: 23)
        # icra: Başlık col 25, değer col 26 (Unnamed: 25)
        # Avans: Başlık col 27, değer col 28 (Unnamed: 27)
        
        # Sütun isimlerini al
        columns = df.columns.tolist()
        
        # Birleştirilmiş sütunları bul ve değerleri taşı
        for i in range(len(columns)):
            col_name = str(columns[i])
            # Unnamed veya NaN olan sütunları bul
            if col_name.startswith('Unnamed:') or pd.isna(columns[i]):
                # Önceki sütun birleştirilmiş başlık olabilir
                if i > 0:
                    prev_col = columns[i-1]
                    # Değerleri önceki sütuna kopyala
                    if i < len(df.columns):
                        df[prev_col] = df.iloc[:, i]
        
        # Boş satırları temizle
        df = df.dropna(how='all')
        df = df[df['TCKN'].notna()]
        
        # Dönem parametresinden yıl ve ay çıkar
        donem_yil, donem_ay = donem.split('-')
        donem_yil = int(donem_yil)
        donem_ay = int(donem_ay)
        
        uploaded_count = 0
        updated_count = 0
        errors = []
        
        for idx, row in df.iterrows():
            try:
                tckn = str(int(row['TCKN'])) if pd.notna(row['TCKN']) else None
                
                if not tckn or len(tckn) != 11:
                    continue
                
                # TC ile personel bul
                personnel = db.query(Personnel).filter(Personnel.tc_kimlik_no == tckn).first()
                personnel_id = personnel.id if personnel else None
                
                # Contract ve monthly record bul (personnel_id + ise_giris_tarihi)
                monthly_record_id = None
                contract_id = None
                if personnel and pd.notna(row['Giriş T']):
                    giris_tarihi = pd.to_datetime(row['Giriş T']).date()
                    
                    # Contract bul (personnel_id + ise_giris_tarihi - unique)
                    contract = db.query(PersonnelContract).filter(
                        PersonnelContract.personnel_id == personnel.id,
                        PersonnelContract.ise_giris_tarihi == giris_tarihi
                    ).order_by(PersonnelContract.id.desc()).first()
                    
                    if contract:
                        contract_id = contract.id
                        monthly_record_id = contract.monthly_personnel_records_id
                
                # Aynı dönem + TC + giriş tarihi için kayıt var mı kontrol et
                existing = db.query(LucaBordro).filter(
                    LucaBordro.donem == donem,
                    LucaBordro.tckn == tckn,
                    LucaBordro.giris_t == pd.to_datetime(row['Giriş T']).date() if pd.notna(row['Giriş T']) else None
                ).first()
                
                data = {
                    'yil': donem_yil,
                    'ay': donem_ay,
                    'donem': donem,
                    'personnel_id': personnel_id,
                    'monthly_personnel_records_id': monthly_record_id,
                    'contract_id': contract_id,
                    'sira_no': int(row['#']) if pd.notna(row['#']) else None,
                    'adi_soyadi': str(row['Adı Soyadı']).strip(),
                    'tckn': tckn,
                    'ssk_sicil_no': str(row['SSK Sicil No']).strip() if pd.notna(row['SSK Sicil No']) else None,
                    'giris_t': pd.to_datetime(row['Giriş T']).date() if pd.notna(row['Giriş T']) else None,
                    'cikis_t': pd.to_datetime(row['Çıkış T']).date() if pd.notna(row['Çıkış T']) else None,
                    't_gun': int(row['T.Gün']) if pd.notna(row['T.Gün']) else 0,
                    'nor_kazanc': float(row['Nor.Kazanç']) if pd.notna(row['Nor.Kazanç']) else 0,
                    'dig_kazanc': float(row['Diğ.Kazanç']) if pd.notna(row['Diğ.Kazanç']) else 0,
                    'top_kazanc': float(row['Top.Kazanç']) if pd.notna(row['Top.Kazanç']) else 0,
                    'ssk_m': float(row['SSK M.']) if pd.notna(row['SSK M.']) else 0,
                    'g_v_m': float(row['G.V.M']) if pd.notna(row['G.V.M']) else 0,
                    'ssk_isci': float(row['SSK İşçi']) if pd.notna(row['SSK İşçi']) else 0,
                    'iss_p_isci': float(row['İşs.P.İşçi']) if pd.notna(row['İşs.P.İşçi']) else 0,
                    'gel_ver': float(row['Gel.Ver.']) if pd.notna(row['Gel.Ver.']) else 0,
                    'damga_v': float(row['Damga V']) if pd.notna(row['Damga V']) else 0,
                    'ozel_kesinti': float(row['Öz.Kesinti']) if pd.notna(row['Öz.Kesinti']) else 0,
                    'oto_kat_bes': float(row['Oto.Kat.BES']) if 'Oto.Kat.BES' in row and pd.notna(row['Oto.Kat.BES']) else 0,
                    'icra': float(row['icra']) if 'icra' in row and pd.notna(row['icra']) else 0,
                    'avans': float(row['Avans']) if 'Avans' in row and pd.notna(row['Avans']) else 0,
                    'n_odenen': float(row['N.Ödenen']) if pd.notna(row['N.Ödenen']) else 0,
                    'isveren_maliyeti': float(row['İşveren Maliyeti']) if pd.notna(row['İşveren Maliyeti']) else 0,
                    'ssk_isveren': float(row['SSK İşveren']) if pd.notna(row['SSK İşveren']) else 0,
                    'iss_p_isveren': float(row['İşs.P.İşveren']) if pd.notna(row['İşs.P.İşveren']) else 0,
                    'kanun': str(row['Kanun']).strip() if 'Kanun' in row and pd.notna(row['Kanun']) else None,
                    'ssk_tesviki': float(row['SSK Teşviki']) if pd.notna(row['SSK Teşviki']) else 0,
                    'upload_date': datetime.now(),
                    'file_name': file.filename,
                    'is_processed': 0
                }
                
                if existing:
                    for key, value in data.items():
                        setattr(existing, key, value)
                    updated_count += 1
                else:
                    new_bordro = LucaBordro(**data)
                    db.add(new_bordro)
                    uploaded_count += 1
                    
            except Exception as e:
                errors.append(f"Satır {idx + 10}: {str(e)}")
        
        db.commit()
        
        return {
            "success": True,
            "message": f"{uploaded_count} yeni kayıt eklendi, {updated_count} kayıt güncellendi",
            "uploaded": uploaded_count,
            "updated": updated_count,
            "errors": errors[:10] if errors else []
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dosya işlenirken hata: {str(e)}")


@router.get("/list")
async def list_luca_bordro(
    donem: Optional[str] = Query(None),
    page: int = Query(1),
    page_size: int = Query(100),
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Luca bordro kayıtlarını listele"""
    query = db.query(LucaBordro)
    
    if donem:
        query = query.filter(LucaBordro.donem == donem)
    
    total = query.count()
    skip = (page - 1) * page_size
    records = query.order_by(LucaBordro.donem.desc(), LucaBordro.adi_soyadi).offset(skip).limit(page_size).all()
    
    # Calculate summary statistics for the entire selected period
    summary = {
        "personel_sayisi": 0,
        "toplam_net_odenen": 0,
        "toplam_oto_kat_bes": 0,
        "toplam_icra": 0,
        "toplam_isveren_maliyeti": 0
    }
    
    if donem:
        all_records = db.query(LucaBordro).filter(LucaBordro.donem == donem).all()
        summary["personel_sayisi"] = len(all_records)
        summary["toplam_net_odenen"] = sum(r.n_odenen or 0 for r in all_records)
        summary["toplam_oto_kat_bes"] = sum(r.oto_kat_bes or 0 for r in all_records)
        summary["toplam_icra"] = sum(r.icra or 0 for r in all_records)
        summary["toplam_isveren_maliyeti"] = sum(r.isveren_maliyeti or 0 for r in all_records)
    
    return {
        "items": records,
        "total": total,
        "page": page,
        "page_size": page_size,
        "summary": summary
    }


@router.get("/donemler")
async def get_luca_bordro_donemler(
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mevcut dönemleri listele"""
    donemler = db.query(distinct(LucaBordro.donem)).order_by(LucaBordro.donem.desc()).all()
    
    return {
        "donemler": [d[0] for d in donemler]
    }


@router.post("/match-contracts")
async def match_bordro_contracts(
    yil: int = Query(...),
    ay: int = Query(...),
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Luca bordro kayıtlarını sözleşmelerle eşleştir"""
    donem = f"{yil}-{ay:02d}"
    bordro_records = db.query(LucaBordro).filter(LucaBordro.donem == donem).all()
    
    matched = 0
    unmatched = []
    
    for bordro in bordro_records:
        contract = db.query(PersonnelContract).join(
            PersonnelContract.personnel
        ).filter(
            PersonnelContract.personnel.has(tc_kimlik_no=bordro.tckn),
            PersonnelContract.ise_giris_tarihi == bordro.giris_t
        ).order_by(PersonnelContract.id.desc()).first()
        
        if contract:
            bordro.contract_id = contract.id
            bordro.is_processed = 1
            matched += 1
        else:
            unmatched.append({
                "tckn": bordro.tckn,
                "adi_soyadi": bordro.adi_soyadi,
                "giris_tarihi": str(bordro.giris_t) if bordro.giris_t else None
            })
    
    db.commit()
    
    return {
        "success": True,
        "matched": matched,
        "unmatched_count": len(unmatched),
        "unmatched": unmatched[:20]
    }


@router.delete("/{bordro_id}")
async def delete_luca_bordro(
    bordro_id: int,
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Luca bordro kaydını sil"""
    bordro = db.query(LucaBordro).filter(LucaBordro.id == bordro_id).first()
    
    if not bordro:
        raise HTTPException(status_code=404, detail="Kayıt bulunamadı")
    
    db.delete(bordro)
    db.commit()
    
    return {"success": True, "message": "Kayıt silindi"}
