"""
Bordro Calculation Engine
Luca bordro + Puantaj + Sözleşme → Hesaplama + Yevmiye
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import date
from decimal import Decimal

from app.core.database import get_db
from app.models.luca_bordro import LucaBordro
from app.models.monthly_puantaj import MonthlyPuantaj
from app.models.personnel_contract import PersonnelContract
from app.models.payroll_calculation import PayrollCalculation
from app.models.personnel import Personnel
from app.models.system_config import SystemConfig

router = APIRouter()


class CalculateRequest(BaseModel):
    yil: int
    ay: int
    donem: str  # YYYY-MM


@router.post("/calculate")
def calculate_bordro(
    req: CalculateRequest,
    db: Session = Depends(get_db)
):
    """
    Bordro hesaplama: Luca + Puantaj + Sözleşme → PayrollCalculation
    """
    # 1. Luca bordro kayıtlarını al
    luca_records = db.query(LucaBordro).filter(
        LucaBordro.yil == req.yil,
        LucaBordro.ay == req.ay
    ).all()
    
    if not luca_records:
        raise HTTPException(400, f"{req.donem} dönemi için Luca bordro bulunamadı")
    
    # 2. Sistem ayarlarını al
    configs = {}
    for cfg in db.query(SystemConfig).all():
        configs[cfg.config_key] = float(cfg.config_value)
    
    elden_yuvarlama = configs.get('ELDEN_YUVARLAMA', 100)
    
    calculated_count = 0
    updated_count = 0
    errors = []
    
    for luca in luca_records:
        try:
            # Personnel bul
            personnel = db.query(Personnel).filter(Personnel.tckn == luca.tckn).first()
            if not personnel:
                errors.append(f"{luca.adi_soyadi}: Personel bulunamadı (TC: {luca.tckn})")
                continue
            
            # Sözleşme bul
            # Önce İşe Giriş Tarihi ile tam eşleşmeyi dene
            contract = db.query(PersonnelContract).filter(
                PersonnelContract.personnel_id == personnel.id,
                PersonnelContract.ise_giris_tarihi == luca.ise_giris_tarihi,
                PersonnelContract.is_active == 1
            ).first()
            
            # Bulunamadıysa en son aktif sözleşmeyi kullan
            if not contract:
                contract = db.query(PersonnelContract).filter(
                    PersonnelContract.personnel_id == personnel.id,
                    PersonnelContract.is_active == 1
                ).order_by(PersonnelContract.ise_giris_tarihi.desc()).first()
            
            if not contract:
                errors.append(f"{luca.adi_soyadi}: Sözleşme bulunamadı")
                # Yine de hesaplama kaydı oluştur (sadece Luca verileriyle)
                # continue yerine devam ediyoruz
            
            # Puantaj bul (varsa)
            puantaj = db.query(MonthlyPuantaj).filter(
                MonthlyPuantaj.personnel_id == personnel.id,
                MonthlyPuantaj.yil == req.yil,
                MonthlyPuantaj.ay == req.ay
            ).first()
            
            # Mevcut hesaplama var mı
            existing = db.query(PayrollCalculation).filter(
                PayrollCalculation.personnel_id == personnel.id,
                PayrollCalculation.yil == req.yil,
                PayrollCalculation.ay == req.ay
            ).first()
            
            # Hesaplama yap
            calc_data = {
                'yil': req.yil,
                'ay': req.ay,
                'donem': req.donem,
                'personnel_id': personnel.id,
                'contract_id': contract.id if contract else None,
                'luca_bordro_id': luca.id,
                'puantaj_id': puantaj.id if puantaj else None,
                'tckn': luca.tckn,
                'adi_soyadi': luca.adi_soyadi,
                'cost_center_id': contract.cost_center_id if contract else None,
                'santiye_adi': contract.cost_center_name if contract else None,
                'ucret_nevi': contract.ucret_nevi if contract else None,
                'kanun_tipi': contract.kanun_tipi if contract else None,
                
                # Maaş1 (Luca'dan)
                'maas1_net_odenen': float(luca.net_odenen) if luca.net_odenen else 0,
                'maas1_icra': float(luca.icra_kesintisi) if luca.icra_kesintisi else 0,
                'maas1_bes': float(luca.bes_kesintisi) if luca.bes_kesintisi else 0,
                'maas1_avans': float(luca.avans_kesintisi) if luca.avans_kesintisi else 0,
                'maas1_gelir_vergisi': float(luca.gelir_vergisi) if luca.gelir_vergisi else 0,
                'maas1_damga_vergisi': float(luca.damga_vergisi) if luca.damga_vergisi else 0,
                'maas1_ssk_isci': float(luca.ssk_isci) if luca.ssk_isci else 0,
                'maas1_issizlik_isci': float(luca.issizlik_isci) if luca.issizlik_isci else 0,
                'maas1_ssk_isveren': float(luca.ssk_isveren) if luca.ssk_isveren else 0,
                'maas1_issizlik_isveren': float(luca.issizlik_isveren) if luca.issizlik_isveren else 0,
                'maas1_ssk_tesviki': float(luca.ssk_tesviki) if luca.ssk_tesviki else 0,
            }
            
            # Elden kazanç hesaplama (Puantaj ve Sözleşme varsa)
            elden_ucret = 0
            if contract and puantaj and contract.maas2_tutar:
                maas2 = float(contract.maas2_tutar)
                
                # Günlük ücret (30 gün baz)
                gunluk_ucret = maas2 / 30
                
                # Normal çalışma
                normal_gun = float(puantaj.normal_gun) if puantaj.normal_gun else 0
                calc_data['normal_gun'] = normal_gun
                calc_data['maas2_normal_calısma'] = gunluk_ucret * normal_gun
                elden_ucret += gunluk_ucret * normal_gun
                
                # Hafta tatili
                hafta_tatili = float(puantaj.hafta_tatili_gun) if puantaj.hafta_tatili_gun else 0
                calc_data['hafta_tatili_gun'] = hafta_tatili
                calc_data['maas2_hafta_tatili'] = gunluk_ucret * hafta_tatili
                elden_ucret += gunluk_ucret * hafta_tatili
                
                # Fazla mesai (saat bazında, günlük ücreti saate böl)
                fm_saat = float(puantaj.fazla_mesai_saat) if puantaj.fazla_mesai_saat else 0
                fm_orani = float(contract.fm_orani) if contract.fm_orani else 1.5
                saatlik_ucret = gunluk_ucret / 8
                calc_data['fazla_mesai_saat'] = fm_saat
                calc_data['maas2_fazla_mesai'] = saatlik_ucret * fm_saat * fm_orani
                elden_ucret += saatlik_ucret * fm_saat * fm_orani
                
                # Tatil mesaisi
                tatil_gun = float(puantaj.tatil_mesai_gun) if puantaj.tatil_mesai_gun else 0
                tatil_orani = float(contract.tatil_orani) if contract.tatil_orani else 2.0
                calc_data['tatil_mesai_gun'] = tatil_gun
                calc_data['maas2_tatil_mesaisi'] = gunluk_ucret * tatil_gun * tatil_orani
                elden_ucret += gunluk_ucret * tatil_gun * tatil_orani
                
                # Ücretli izin
                yillik_izin = float(puantaj.yillik_izin_gun) if puantaj.yillik_izin_gun else 0
                calc_data['yillik_izin_gun'] = yillik_izin
                calc_data['maas2_ucretli_izin'] = gunluk_ucret * yillik_izin
                elden_ucret += gunluk_ucret * yillik_izin
                
                calc_data['maas2_anlaşilan'] = maas2
                calc_data['maas2_toplam'] = elden_ucret
            
            # Elden ücret yuvarlama
            if elden_ucret > 0:
                calc_data['elden_ucret_hesaplanan'] = elden_ucret
                
                # Yuvarla (100 TL'nin katına)
                yuvarlanmis = round(elden_ucret / elden_yuvarlama) * elden_yuvarlama
                calc_data['elden_ucret_yuvarlanmis'] = yuvarlanmis
                calc_data['elden_yuvarlama'] = yuvarlanmis - elden_ucret
                calc_data['elden_yuvarlama_yon'] = 'YUKARI' if yuvarlanmis > elden_ucret else 'ASAGI'
            
            # Hesap kodu
            calc_data['account_code_335'] = contract.account_code if contract else None
            
            # Yevmiye tipi belirleme
            # Tip A: Luca'da net ödenen var
            # Tip B: Sadece elden ücret var
            # Tip C: Her ikisi de var
            if calc_data['maas1_net_odenen'] > 0 and elden_ucret > 0:
                calc_data['yevmiye_tipi'] = 'C'
            elif calc_data['maas1_net_odenen'] > 0:
                calc_data['yevmiye_tipi'] = 'A'
            elif elden_ucret > 0:
                calc_data['yevmiye_tipi'] = 'B'
            else:
                calc_data['yevmiye_tipi'] = None
            
            if existing:
                for key, value in calc_data.items():
                    setattr(existing, key, value)
                updated_count += 1
            else:
                calc = PayrollCalculation(**calc_data)
                db.add(calc)
                calculated_count += 1
                
        except Exception as e:
            errors.append(f"{luca.adi_soyadi}: {str(e)}")
            continue
    
    db.commit()
    
    return {
        "success": True,
        "donem": req.donem,
        "calculated": calculated_count,
        "updated": updated_count,
        "total": calculated_count + updated_count,
        "errors": errors[:20] if errors else []
    }


@router.get("/list")
def list_calculations(
    yil: int,
    ay: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Hesaplanmış bordroları listele"""
    query = db.query(PayrollCalculation).filter(
        PayrollCalculation.yil == yil,
        PayrollCalculation.ay == ay
    )
    
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "items": [
            {
                "id": item.id,
                "personnel_id": item.personnel_id,
                "adi_soyadi": item.adi_soyadi,
                "tckn": item.tckn,
                "santiye": item.santiye_adi,
                "yevmiye_tipi": item.yevmiye_tipi,
                "maas1_net": float(item.maas1_net_odenen) if item.maas1_net_odenen else 0,
                "maas2_toplam": float(item.maas2_toplam) if item.maas2_toplam else 0,
                "elden_yuvarlanmis": float(item.elden_ucret_yuvarlanmis) if item.elden_ucret_yuvarlanmis else 0,
            }
            for item in items
        ]
    }
