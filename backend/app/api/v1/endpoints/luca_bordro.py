"""
Luca Bordro API endpoints
"""
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import pandas as pd
from datetime import datetime
import io

from app.core.database import get_db
from app.models.luca_bordro import LucaBordro
from app.models.personnel import Personnel
from app.schemas.luca_bordro import LucaBordroResponse, LucaBordroList

router = APIRouter()


@router.post("/upload")
async def upload_luca_bordro(
    file: UploadFile = File(...),
    donem: str = None,
    db: Session = Depends(get_db)
):
    """
    Luca'dan çekilen bordro Excel dosyasını yükle ve parse et
    
    Args:
        file: Excel dosyası
        donem: Bordro dönemi (YYYY-MM formatında, örn: 2025-11)
    """
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Sadece Excel dosyaları (.xlsx, .xls) yüklenebilir")
    
    if not donem:
        raise HTTPException(status_code=400, detail="Dönem parametresi zorunlu (örn: donem=2025-11)")
    
    # Dönem formatını kontrol et
    import re
    if not re.match(r'^\d{4}-\d{2}$', donem):
        raise HTTPException(status_code=400, detail="Dönem formatı hatalı. YYYY-MM formatında olmalı (örn: 2025-11)")
    
    try:
        # Excel dosyasını oku
        contents = await file.read()
        df = pd.read_excel(io.BytesIO(contents), header=9)  # Satır 9'dan başlıyor
        
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
                
                # Aynı dönem + TC için kayıt var mı kontrol et
                existing = db.query(LucaBordro).filter(
                    LucaBordro.donem == donem,
                    LucaBordro.tckn == tckn,
                    LucaBordro.ise_giris_tarihi == row['Giriş T']
                ).first()
                
                # Verileri hazırla
                data = {
                    'yil': donem_yil,
                    'ay': donem_ay,
                    'donem': donem,
                    'sira_no': int(row['#']) if pd.notna(row['#']) else None,
                    'adi_soyadi': str(row['Adı Soyadı']).strip(),
                    'tckn': tckn,
                    'sgk_sicil_no': str(row['SSK Sicil No']).strip() if pd.notna(row['SSK Sicil No']) else None,
                    'ise_giris_tarihi': pd.to_datetime(row['Giriş T']).date() if pd.notna(row['Giriş T']) else None,
                    'isten_cikis_tarihi': pd.to_datetime(row['Çıkış T']).date() if pd.notna(row['Çıkış T']) else None,
                    'toplam_gun': int(row['T.Gün']) if pd.notna(row['T.Gün']) else 0,
                    'normal_kazanc': float(row['Nor.Kazanç']) if pd.notna(row['Nor.Kazanç']) else 0,
                    'diger_kazanc': float(row['Diğ.Kazanç']) if pd.notna(row['Diğ.Kazanç']) else 0,
                    'toplam_kazanc': float(row['Top.Kazanç']) if pd.notna(row['Top.Kazanç']) else 0,
                    'ssk_matrahi': float(row['SSK M.']) if pd.notna(row['SSK M.']) else 0,
                    'gelir_vergisi_matrahi': float(row['G.V.M']) if pd.notna(row['G.V.M']) else 0,
                    'ssk_isci': float(row['SSK İşçi']) if pd.notna(row['SSK İşçi']) else 0,
                    'issizlik_isci': float(row['İşs.P.İşçi']) if pd.notna(row['İşs.P.İşçi']) else 0,
                    'gelir_vergisi': float(row['Gel.Ver.']) if pd.notna(row['Gel.Ver.']) else 0,
                    'damga_vergisi': float(row['Damga V']) if pd.notna(row['Damga V']) else 0,
                    'ozel_kesinti': float(row['Öz.Kesinti']) if pd.notna(row['Öz.Kesinti']) else 0,
                    'bes_kesintisi': float(row['Oto.Kat.BES']) if pd.notna(row['Oto.Kat.BES']) else 0,
                    'net_odenen': float(row['N.Ödenen']) if pd.notna(row['N.Ödenen']) else 0,
                    'isveren_maliyeti': float(row['İşveren Maliyeti']) if pd.notna(row['İşveren Maliyeti']) else 0,
                    'ssk_isveren': float(row['SSK İşveren']) if pd.notna(row['SSK İşveren']) else 0,
                    'issizlik_isveren': float(row['İşs.P.İşveren']) if pd.notna(row['İşs.P.İşveren']) else 0,
                    'file_name': file.filename,
                }
                
                # İcra ve Avans sütunları varsa ekle (case-insensitive)
                if 'icra' in df.columns or 'İcra' in df.columns:
                    icra_col = 'icra' if 'icra' in df.columns else 'İcra'
                    data['icra_kesintisi'] = float(row[icra_col]) if pd.notna(row[icra_col]) else 0
                if 'Avans' in df.columns or 'avans' in df.columns:
                    avans_col = 'Avans' if 'Avans' in df.columns else 'avans'
                    data['avans_kesintisi'] = float(row[avans_col]) if pd.notna(row[avans_col]) else 0
                
                # SSK Teşviki (Kanun sütunu varsa oradan çek)
                if 'Kanun' in df.columns:
                    kanun = str(row['Kanun']).strip() if pd.notna(row['Kanun']) else '00000'
                    data['kanun_tipi'] = kanun
                    
                    # Teşvik hesapla (basitleştirilmiş)
                    if kanun == '05510' and data['ssk_isveren'] > 0:
                        # %20.5 - gerçek ödenen fark = teşvik
                        teorik_isveren = data['ssk_matrahi'] * 0.205
                        data['ssk_tesviki'] = max(0, teorik_isveren - data['ssk_isveren'])
                
                if existing:
                    # Güncelle
                    for key, value in data.items():
                        setattr(existing, key, value)
                    updated_count += 1
                else:
                    # Yeni kayıt
                    bordro = LucaBordro(**data)
                    db.add(bordro)
                    uploaded_count += 1
                    
            except Exception as e:
                errors.append(f"Satır {idx + 10}: {str(e)}")
                continue
        
        db.commit()
        
        return {
            "success": True,
            "message": f"{uploaded_count} yeni kayıt, {updated_count} güncelleme yapıldı",
            "uploaded_count": uploaded_count,
            "updated_count": updated_count,
            "errors": errors[:10] if errors else []  # İlk 10 hata
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Dosya işleme hatası: {str(e)}")


@router.get("/list")
def list_luca_bordro(
    donem: str = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Luca bordro kayıtlarını listele
    """
    query = db.query(LucaBordro)
    
    if donem:
        query = query.filter(LucaBordro.donem == donem)
    
    total = query.count()
    records = query.order_by(LucaBordro.donem.desc(), LucaBordro.adi_soyadi).offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "bordro_list": records
    }


@router.get("/donemler")
def list_donemler(db: Session = Depends(get_db)):
    """
    Mevcut dönemleri listele
    """
    from sqlalchemy import distinct
    
    donemler = db.query(distinct(LucaBordro.donem)).order_by(LucaBordro.donem.desc()).all()
    
    return {
        "donemler": [d[0] for d in donemler]
    }


@router.post("/match-contracts")
def match_contracts(
    donem: str,
    db: Session = Depends(get_db)
):
    """
    Luca bordro kayıtlarını sözleşmelerle eşleştir (işe giriş tarihine göre)
    """
    bordro_records = db.query(LucaBordro).filter(LucaBordro.donem == donem).all()
    
    matched = 0
    unmatched = []
    
    for bordro in bordro_records:
        # TC + İşe giriş tarihine göre sözleşme bul
        contract = db.query(PersonnelContract).join(
            PersonnelContract.personnel
        ).filter(
            PersonnelContract.personnel.has(tckn=bordro.tckn),
            PersonnelContract.ise_giris_tarihi == bordro.ise_giris_tarihi,
            PersonnelContract.is_active == 1
        ).first()
        
        if contract:
            bordro.contract_id = contract.id
            bordro.kanun_tipi = contract.kanun_tipi.value
            matched += 1
        else:
            unmatched.append({
                "tckn": bordro.tckn,
                "adi_soyadi": bordro.adi_soyadi,
                "giris_tarihi": bordro.ise_giris_tarihi
            })
    
    db.commit()
    
    return {
        "success": True,
        "matched": matched,
        "unmatched_count": len(unmatched),
        "unmatched": unmatched[:20]  # İlk 20 eşleşmeyeni göster
    }


@router.delete("/{bordro_id}")
def delete_luca_bordro(
    bordro_id: int,
    db: Session = Depends(get_db)
):
    """
    Luca bordro kaydını sil
    """
    bordro = db.query(LucaBordro).filter(LucaBordro.id == bordro_id).first()
    
    if not bordro:
        raise HTTPException(status_code=404, detail="Kayıt bulunamadı")
    
    db.delete(bordro)
    db.commit()
    
    return {"success": True, "message": "Kayıt silindi"}
