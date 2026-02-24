"""Bordro Calculation domain router (V2)"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.domains.auth.dependencies import get_current_user
from app.schemas.auth import UserInDB
from app.domains.personnel.bordro_calculation.service import BordroCalculationService
from app.domains.personnel.bordro_calculation.yevmiye_service_bordro import BordroYevmiyeService

router = APIRouter(tags=["Personnel - Bordro Calculation (V2)"])


@router.post("/calculate")
async def calculate_bordro(
    yil: int = Query(...),
    ay: int = Query(...),
    # current_user: UserInDB = Depends(get_current_user),  # TODO: Re-enable auth
    db: Session = Depends(get_db)
):
    """
    Calculate payroll (bordro) for a specific period
    
    Args:
        yil: Year
        ay: Month
    
    Returns:
        Calculation results with breakdown
    """
    try:
        service = BordroCalculationService(db)
        result = service.calculate(yil, ay)
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error"))
        
        return result
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f"❌ BORDRO CALCULATION ERROR:\n{error_detail}")
        raise HTTPException(status_code=500, detail=f"Calculation error: {str(e)}")


@router.get("/list")
async def list_bordro_calculations(
    yil: Optional[int] = Query(None),
    ay: Optional[int] = Query(None),
    cost_center_id: Optional[int] = Query(None),
    skip: int = 0,
    limit: int = 1000,
    # current_user: UserInDB = Depends(get_current_user),  # TODO: Re-enable auth
    db: Session = Depends(get_db)
):
    """
    List bordro calculation results
    
    Args:
        yil: Filter by year
        ay: Filter by month
        cost_center_id: Filter by cost center (not implemented yet)
        skip: Pagination skip
        limit: Pagination limit
    
    Returns:
        {
            items: List of bordro calculations
            total: Total count
        }
    """
    if yil is None or ay is None:
        return {"total": 0, "items": []}
    
    service = BordroCalculationService(db)
    return service.list_calculations(yil, ay, cost_center_id, skip, limit)


@router.get("/list-grouped")
async def list_bordro_calculations_grouped(
    yil: Optional[int] = Query(None),
    ay: Optional[int] = Query(None),
    cost_center_id: Optional[int] = Query(None),
    skip: int = 0,
    limit: int = 1000,
    # current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List bordro calculations GROUPED BY PERSONNEL
    
    Birden fazla bordrosu olan personelleri tek satırda gösterir.
    Toplamları hesaplar, detaylar ayrı ayrı döner.
    
    Returns:
        {
            items: [
                {
                    personnel_id: int,
                    tckn: str,
                    adi_soyadi: str,
                    total_net_odenen: float,
                    total_bes: float,
                    total_icra: float,
                    total_elden_ucret: float,
                    total_kazanc: float,
                    total_isveren_maliyet: float,
                    calculations: [  # Detaylar
                        {id, maliyet_merkezi, ucret_nevi, ...}
                    ]
                }
            ],
            total: int
        }
    """
    if yil is None or ay is None:
        return {"total": 0, "items": []}
    
    from app.models import PayrollCalculation
    from app.models import Personnel
    from app.models import PersonnelDraftContract
    from app.models import PersonnelPuantajGrid
    from sqlalchemy import func
    
    # Aktif draft contract'ları önceden çek (performans için)
    active_drafts = db.query(PersonnelDraftContract.personnel_id).filter(
        PersonnelDraftContract.is_active == 1
    ).distinct().all()
    personnel_with_active_draft = {draft.personnel_id for draft in active_drafts}
    
    # Puantaj Grid'i olan personelleri çek (o dönem için)
    donem = f"{yil}-{ay:02d}"
    puantaj_grids = db.query(PersonnelPuantajGrid.personnel_id).filter(
        PersonnelPuantajGrid.donem == donem
    ).distinct().all()
    personnel_with_puantaj = {ppg.personnel_id for ppg in puantaj_grids}
    
    # Tüm hesaplamaları çek
    query = db.query(PayrollCalculation).filter(
        PayrollCalculation.yil == yil,
        PayrollCalculation.ay == ay
    )
    
    if cost_center_id:
        query = query.filter(PayrollCalculation.cost_center_id == cost_center_id)
    
    all_calcs = query.order_by(PayrollCalculation.adi_soyadi).all()
    
    # Personel bazında grupla
    grouped = {}
    for calc in all_calcs:
        pid = calc.personnel_id
        if pid not in grouped:
            grouped[pid] = {
                "personnel_id": pid,
                "tckn": calc.tckn,
                "adi_soyadi": calc.adi_soyadi,
                "has_active_draft_contract": pid in personnel_with_active_draft,
                "has_puantaj_grid": pid in personnel_with_puantaj,
                "total_net_odenen": 0,
                "total_bes": 0,
                "total_icra": 0,
                "total_elden_ucret": 0,
                "total_kazanc": 0,
                "total_isveren_maliyet": 0,
                "calculations": []
            }
        
        # Toplamları hesapla
        grouped[pid]["total_net_odenen"] += float(calc.maas1_net_odenen or 0)
        grouped[pid]["total_bes"] += float(calc.maas1_bes or 0)
        grouped[pid]["total_icra"] += float(calc.maas1_icra or 0)
        grouped[pid]["total_elden_ucret"] += float(calc.elden_ucret_yuvarlanmis or 0)
        
        # Toplam kazanç = maas2_toplam (sözleşmedeki brüt ücret)
        kazanc = float(calc.maas2_toplam or 0)
        grouped[pid]["total_kazanc"] += kazanc
        
        # İşveren maliyeti = kazanç + ssk işveren + işsizlik işveren
        maliyet = (kazanc +
                  float(calc.maas1_ssk_isveren or 0) +
                  float(calc.maas1_issizlik_isveren or 0))
        grouped[pid]["total_isveren_maliyet"] += maliyet
        
        # Detay kayıt ekle
        grouped[pid]["calculations"].append({
            "id": calc.id,
            "maliyet_merkezi": calc.maliyet_merkezi,
            "ucret_nevi": calc.ucret_nevi,
            "kanun_tipi": calc.kanun_tipi,
            "maas1_net_odenen": float(calc.maas1_net_odenen or 0),
            "maas1_bes": float(calc.maas1_bes or 0),
            "maas1_icra": float(calc.maas1_icra or 0),
            "maas1_ssk_isci": float(calc.maas1_ssk_isci or 0),
            "maas1_ssk_isveren": float(calc.maas1_ssk_isveren or 0),
            "maas1_issizlik_isci": float(calc.maas1_issizlik_isci or 0),
            "maas1_issizlik_isveren": float(calc.maas1_issizlik_isveren or 0),
            "maas1_gelir_vergisi": float(calc.maas1_gelir_vergisi or 0),
            "maas1_damga_vergisi": float(calc.maas1_damga_vergisi or 0),
            "elden_ucret_yuvarlanmis": float(calc.elden_ucret_yuvarlanmis or 0),
            "yevmiye_tipi": calc.yevmiye_tipi,
            "transaction_id": calc.transaction_id,
            "fis_no": calc.fis_no
        })
    
    items = list(grouped.values())
    
    return {
        "total": len(items),
        "items": items[skip:skip+limit] if limit else items[skip:]
    }


@router.get("/preview-yevmiye-personnel")
async def preview_yevmiye_personnel(
    personnel_id: int = Query(...),
    yil: int = Query(...),
    ay: int = Query(...),
    # current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Bir personelin belirli dönemdeki TÜM bordrolarının yevmiye önizlemesini oluşturur
    
    YENİ SİSTEM:
    - Her luca bordro için ayrı RESMİ KAYIT transaction
    - Draft contract varsa ayrı TASLAK KAYIT transaction (elden ödeme)
    - Bölüm bilgisi ile filtrelenebilir önizleme
    
    Args:
        personnel_id: Personel ID
        yil: Yıl
        ay: Ay
    
    Returns:
        {
            "success": True,
            "personnel_id": int,
            "personnel_name": str,
            "donem": str,
            "resmi_kayitlar": [
                {
                    "luca_bordro_id": int,
                    "bolum": str,
                    "transaction_number": str,
                    "transaction_date": str,
                    "lines": [...],
                    "total_debit": float,
                    "total_credit": float,
                    "balanced": bool
                },
                ...
            ],
            "taslak_kayitlar": [...]
        }
    """
    try:
        service = BordroYevmiyeService(db)
        result = service.preview_yevmiye_for_personnel(personnel_id, yil, ay)
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error"))
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f"❌ YEVMIYE PREVIEW PERSONNEL ERROR:\n{error_detail}")
        raise HTTPException(status_code=500, detail=f"Preview error: {str(e)}")


@router.post("/save-yevmiye-personnel")
async def save_yevmiye_personnel(
    personnel_id: int = Query(...),
    yil: int = Query(...),
    ay: int = Query(...),
    # current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Bir personelin belirli dönemdeki TÜM bordrolarının yevmiye kayıtlarını database'e kaydeder
    
    YENİ SİSTEM:
    - Her luca bordro için ayrı RESMİ KAYIT transaction oluşturur
    - Draft contract varsa ayrı TASLAK KAYIT transaction oluşturur
    - Personel bazında toplu onay mekanizması
    
    Args:
        personnel_id: Personel ID
        yil: Yıl
        ay: Ay
    
    Returns:
        {
            "success": True,
            "personnel_id": int,
            "personnel_name": str,
            "donem": str,
            "transactions": [
                {
                    "type": "RESMİ KAYIT",
                    "transaction_id": int,
                    "transaction_number": str,
                    "luca_bordro_id": int,
                    "bolum": str
                },
                ...
            ]
        }
    """
    try:
        service = BordroYevmiyeService(db)
        result = service.save_yevmiye_for_personnel(personnel_id, yil, ay)
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error"))
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f"❌ YEVMIYE SAVE PERSONNEL ERROR:\n{error_detail}")
        raise HTTPException(status_code=500, detail=f"Save error: {str(e)}")


@router.get("/bordro-data")
async def get_bordro_data(
    yil: int = Query(...),
    ay: int = Query(...),
    personnel_id: Optional[int] = Query(None),
    cost_center_id: Optional[int] = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Luca Bordro verilerini getir (Ham bordro kayıtları)
    
    Args:
        yil: Yıl
        ay: Ay
        personnel_id: Optional personel filtresi
        cost_center_id: Optional şantiye filtresi (gelecekte)
        skip: Pagination offset
        limit: Pagination limit
    
    Returns:
        {
            total: int,
            items: [
                {
                    id, personnel_id, contract_id, monthly_personnel_records_id,
                    ssk_sicil_no, giris_t, cikis_t, t_gun,
                    nor_kazanc, dig_kazanc, top_kazanc, ssk_m, g_v_m,
                    ssk_isci, iss_p_isci, gel_ver, damga_v,
                    ozel_kesinti, oto_kat_bes, icra, avans,
                    n_odenen, isveren_maliyeti, ssk_isveren, iss_p_isveren,
                    kanun, ssk_tesviki
                }
            ]
        }
    """
    from app.models import LucaBordro
    from app.models import PersonnelContract
    from app.models import CostCenter
    
    # Query oluştur - Contract ve CostCenter ile join et
    query = db.query(
        LucaBordro,
        PersonnelContract.bolum.label('contract_bolum'),
        CostCenter.name.label('maliyet_merkezi')
    ).outerjoin(
        PersonnelContract,
        LucaBordro.contract_id == PersonnelContract.id
    ).outerjoin(
        CostCenter,
        PersonnelContract.cost_center_id == CostCenter.id
    ).filter(
        LucaBordro.yil == yil,
        LucaBordro.ay == ay
    )
    
    if personnel_id:
        query = query.filter(LucaBordro.personnel_id == personnel_id)
    
    # Toplam sayı
    total = query.count()
    
    # Sayfalama ile kayıtları çek
    results = query.order_by(LucaBordro.adi_soyadi).offset(skip).limit(limit).all()
    
    # Response oluştur
    items = []
    for bordro, contract_bolum, maliyet_merkezi in results:
        items.append({
            "id": bordro.id,
            "personnel_id": bordro.personnel_id,
            "contract_id": bordro.contract_id,
            "monthly_personnel_records_id": bordro.monthly_personnel_records_id,
            "ssk_sicil_no": bordro.ssk_sicil_no,
            "giris_t": bordro.giris_t.isoformat() if bordro.giris_t else None,
            "cikis_t": bordro.cikis_t.isoformat() if bordro.cikis_t else None,
            "t_gun": bordro.t_gun,
            "nor_kazanc": float(bordro.nor_kazanc or 0),
            "dig_kazanc": float(bordro.dig_kazanc or 0),
            "top_kazanc": float(bordro.top_kazanc or 0),
            "ssk_m": float(bordro.ssk_m or 0),
            "g_v_m": float(bordro.g_v_m or 0),
            "ssk_isci": float(bordro.ssk_isci or 0),
            "iss_p_isci": float(bordro.iss_p_isci or 0),
            "gel_ver": float(bordro.gel_ver or 0),
            "damga_v": float(bordro.damga_v or 0),
            "ozel_kesinti": float(bordro.ozel_kesinti or 0),
            "oto_kat_bes": float(bordro.oto_kat_bes or 0),
            "icra": float(bordro.icra or 0),
            "avans": float(bordro.avans or 0),
            "n_odenen": float(bordro.n_odenen or 0),
            "isveren_maliyeti": float(bordro.isveren_maliyeti or 0),
            "ssk_isveren": float(bordro.ssk_isveren or 0),
            "iss_p_isveren": float(bordro.iss_p_isveren or 0),
            "kanun": bordro.kanun,
            "ssk_tesviki": float(bordro.ssk_tesviki or 0),
            # Ek bilgiler
            "adi_soyadi": bordro.adi_soyadi,
            "tckn": bordro.tckn,
            "bolum": contract_bolum or "Belirtilmemiş",
            "maliyet_merkezi": maliyet_merkezi or "Belirtilmemiş"
        })
    
    return {
        "total": total,
        "items": items
    }


@router.get("/puantaj-data")
async def get_puantaj_data(
    yil: int = Query(...),
    ay: int = Query(...),
    personnel_id: int = Query(...),
    db: Session = Depends(get_db)
):
    """
    Personelin ilgili dönemdeki puantaj grid verilerini getir
    
    Args:
        yil: Yıl
        ay: Ay
        personnel_id: Personel ID
    
    Returns:
        {
            personnel_id: int,
            donem: str,
            ucret_nevi: str,
            calisilan_gun_sayisi: int,
            yillik_izin_gun: int,
            izin_gun_sayisi: int,
            rapor_gun_sayisi: int,
            yarim_gun_sayisi: int,
            eksik_gun_sayisi: int,
            fazla_calismasi: int,
            tatil_calismasi: int,
            sigorta_girmedigi: int,
            hafta_tatili: int,
            resmi_tatil: int,
            normal_calismasi: int,
            toplam_tatiller: int,
            toplam_gun_sayisi: int,
            ssk_gun_sayisi: int,
            yol: float,
            prim: float,
            ikramiye: float,
            bayram: float,
            kira: float
        }
    """
    from app.models import PersonnelPuantajGrid
    from app.models import PersonnelDraftContract
    
    # Dönemi oluştur (YYYY-MM formatında)
    donem = f"{yil}-{ay:02d}"
    
    # Puantaj grid kaydını çek
    puantaj = db.query(PersonnelPuantajGrid).filter(
        PersonnelPuantajGrid.personnel_id == personnel_id,
        PersonnelPuantajGrid.donem == donem
    ).first()
    
    if not puantaj:
        raise HTTPException(
            status_code=404,
            detail=f"Personnel ID {personnel_id} için {donem} dönemine ait puantaj kaydı bulunamadı"
        )
    
    # Aktif draft contract'ı çek (ücret nevi için)
    draft = db.query(PersonnelDraftContract).filter(
        PersonnelDraftContract.personnel_id == personnel_id,
        PersonnelDraftContract.is_active == 1
    ).first()
    
    ucret_nevi = draft.ucret_nevi if draft else "aylik"
    
    # Hesaplamalar
    toplam_tatiller = (puantaj.hafta_tatili or 0) + (puantaj.resmi_tatil or 0) + (puantaj.tatil_calismasi or 0)
    toplam_gun_sayisi = 30 - (puantaj.sigorta_girmedigi or 0)  # Ayın toplam günü varsayılan 30
    ssk_gun_sayisi = toplam_gun_sayisi - (puantaj.eksik_gun_sayisi or 0)
    
    # Normal çalışma hesaplama
    ayin_toplam_gun_sayisi = 30  # Varsayılan, gerekirse calendar.monthrange ile hesaplanabilir
    eksik_gun_sayisi = puantaj.eksik_gun_sayisi or 0
    sigorta_girmedigi = puantaj.sigorta_girmedigi or 0
    calisilan_gun_sayisi = puantaj.calisilan_gun_sayisi or 0
    yarim_gun_sayisi = puantaj.yarim_gun_sayisi or 0
    
    # Normal çalışma formülü (yeni versiyon - aylık ve sabit aylık aynı)
    normal_calismasi = (
        30 if ((ucret_nevi == "aylik" or ucret_nevi == "sabit aylik") and eksik_gun_sayisi == 0 and ayin_toplam_gun_sayisi != 30 and sigorta_girmedigi == 0) else
        calisilan_gun_sayisi + yarim_gun_sayisi
    )
    
    return {
        "personnel_id": puantaj.personnel_id,
        "donem": puantaj.donem,
        "ucret_nevi": ucret_nevi,
        "calisilan_gun_sayisi": puantaj.calisilan_gun_sayisi or 0,
        "yillik_izin_gun": puantaj.yillik_izin_gun or 0,
        "izin_gun_sayisi": puantaj.izin_gun_sayisi or 0,
        "rapor_gun_sayisi": puantaj.rapor_gun_sayisi or 0,
        "yarim_gun_sayisi": puantaj.yarim_gun_sayisi or 0,
        "eksik_gun_sayisi": puantaj.eksik_gun_sayisi or 0,
        "fazla_calismasi": puantaj.fazla_calismasi or 0,
        "tatil_calismasi": puantaj.tatil_calismasi or 0,
        "sigorta_girmedigi": puantaj.sigorta_girmedigi or 0,
        "hafta_tatili": puantaj.hafta_tatili or 0,
        "resmi_tatil": puantaj.resmi_tatil or 0,
        "normal_calismasi": normal_calismasi,
        "toplam_tatiller": toplam_tatiller,
        "toplam_gun_sayisi": toplam_gun_sayisi,
        "ssk_gun_sayisi": ssk_gun_sayisi,
        "yol": float(puantaj.yol or 0),
        "prim": float(puantaj.prim or 0),
        "ikramiye": float(puantaj.ikramiye or 0),
        "bayram": float(puantaj.bayram or 0),
        "kira": float(puantaj.kira or 0)
    }


@router.get("/maas-hesabi-data")
async def get_maas_hesabi_data(
    yil: int = Query(...),
    ay: int = Query(...),
    personnel_id: int = Query(...),
    db: Session = Depends(get_db)
):
    """
    Personelin maaş hesabını draft contract ve puantaj verilerine göre hesapla
    
    Args:
        yil: Yıl
        ay: Ay
        personnel_id: Personel ID
    
    Returns:
        {
            draft_contracts_id: int,
            cc_id: int,
            cost_center_name: str,
            net_ucret: float,
            ucret_nevi: str,
            fm_orani: float,
            tatil_orani: float,
            
            # Puantaj verileri
            normal_calismasi: int,
            izin_gun_sayisi: int,
            fazla_calismasi: int,
            yillik_izin_gun: int,
            hafta_tatili: int,
            resmi_tatil: int,
            tatil_calismasi: int,
            yol: float,
            prim: float,
            ikramiye: float,
            bayram: float,
            kira: float,
            
            # Hesaplanan değerler
            gunluk_ucret: float,
            normal_kazanc: float,
            izin_kazanc: float,
            mesai_kazanc: float,
            tatil_kazanc: float,
            tatil_mesai_kazanc: float,
            yillik_izin_kazanc: float,
            toplam_kazanc: float
        }
    """
    from app.models import PersonnelPuantajGrid
    from app.models import PersonnelDraftContract
    from app.models import CostCenter
    
    # Aktif draft contract'ı çek
    draft = db.query(PersonnelDraftContract).filter(
        PersonnelDraftContract.personnel_id == personnel_id,
        PersonnelDraftContract.is_active == 1
    ).first()
    
    if not draft:
        raise HTTPException(
            status_code=404,
            detail=f"Personnel ID {personnel_id} için aktif taslak sözleşme bulunamadı"
        )
    
    # Maliyet merkezini çek
    cost_center = None
    cost_center_name = "Belirtilmemiş"
    if draft.cost_center_id:
        cost_center = db.query(CostCenter).filter(CostCenter.id == draft.cost_center_id).first()
        if cost_center:
            cost_center_name = cost_center.name
    
    # Dönemi oluştur (YYYY-MM formatında)
    donem = f"{yil}-{ay:02d}"
    
    # Puantaj grid kaydını çek
    puantaj = db.query(PersonnelPuantajGrid).filter(
        PersonnelPuantajGrid.personnel_id == personnel_id,
        PersonnelPuantajGrid.donem == donem
    ).first()
    
    if not puantaj:
        raise HTTPException(
            status_code=404,
            detail=f"Personnel ID {personnel_id} için {donem} dönemine ait puantaj kaydı bulunamadı"
        )
    
    # Draft contract verilerini al
    net_ucret = float(draft.net_ucret or 0)
    ucret_nevi = draft.ucret_nevi or 'aylik'
    fm_orani = float(draft.fm_orani or 1.5)
    tatil_orani = float(draft.tatil_orani or 1.0)
    
    # Puantaj verilerini al ve normal_calismasi'ni hesapla (tüm değerleri float/int'e çevir)
    calisilan_gun_sayisi = int(puantaj.calisilan_gun_sayisi or 0)
    yillik_izin_gun = int(puantaj.yillik_izin_gun or 0)
    izin_gun_sayisi = int(puantaj.izin_gun_sayisi or 0)  # İzin günleri (İ)
    yarim_gun_sayisi = float(puantaj.yarim_gun_sayisi or 0)
    eksik_gun_sayisi = int(puantaj.eksik_gun_sayisi or 0)
    rapor_gun_sayisi = int(puantaj.rapor_gun_sayisi or 0)
    sigorta_girmedigi = int(puantaj.sigorta_girmedigi or 0)
    fazla_calismasi = float(puantaj.fazla_calismasi or 0)
    eksik_calismasi = float(puantaj.eksik_calismasi or 0)
    hafta_tatili = int(puantaj.hafta_tatili or 0)
    resmi_tatil = int(puantaj.resmi_tatil or 0)
    tatil_calismasi = float(puantaj.tatil_calismasi or 0)
    yol = float(puantaj.yol or 0)
    prim = float(puantaj.prim or 0)
    ikramiye = float(puantaj.ikramiye or 0)
    bayram = float(puantaj.bayram or 0)
    kira = float(puantaj.kira or 0)
    
    # Normal çalışma hesaplama
    ayin_toplam_gun_sayisi = int(puantaj.ayin_toplam_gun_sayisi or 30)

    # Tatiller toplamı
    tatiller = hafta_tatili + resmi_tatil + tatil_calismasi

    # İzin günlerini 30 ile sınırla
    izin_gun_sinirli = min(izin_gun_sayisi, 30)

    # Normal çalışma formülü - Tam ay koşulları
    if (ucret_nevi == "aylik" or ucret_nevi == "sabit aylik") and \
       eksik_gun_sayisi == 0 and \
       ayin_toplam_gun_sayisi != 30 and \
       sigorta_girmedigi == 0 and \
       rapor_gun_sayisi == 0 and \
       yarim_gun_sayisi == 0:
        normal_calismasi = 30 - tatiller - izin_gun_sinirli - yillik_izin_gun
    else:
        normal_calismasi = calisilan_gun_sayisi + yarim_gun_sayisi

    
    # HESAPLAMALAR
    
    # Günlük kazanç (aylık ve sabit aylık aynı hesaplama)
    if ucret_nevi in ['aylik', 'sabit aylik']:
        gunluk_ucret = net_ucret / 30
    elif ucret_nevi == 'gunluk':
        gunluk_ucret = net_ucret
    else:
        gunluk_ucret = 0
    
    # Normal kazanç (sadece normal çalışma günleri)
    normal_kazanc = normal_calismasi * gunluk_ucret

    # Mesai kazancı
    mesai_kazanc = (fazla_calismasi * gunluk_ucret / 8) * fm_orani

    # Eksik mesai kesintisi
    eksik_mesai_kazanc = (eksik_calismasi * gunluk_ucret / 8)

    # İzin kazancı (İ günleri için - ücretli izin, 30 ile sınırlı)
    izin_kazanc = izin_gun_sinirli * gunluk_ucret
    
    # Tatil kazançı (H + T + M) - tatiller zaten yukarıda hesaplandı
    tatil_kazanc = tatiller * gunluk_ucret
    
    # Tatil mesai kazançı (sadece M günleri için)
    tatil_mesai_kazanc = tatil_calismasi * gunluk_ucret * tatil_orani
    
    # Yıllık izin kazançı (sadece S günleri için)
    yillik_izin_kazanc = gunluk_ucret * yillik_izin_gun
    
    # TOPLAM (eksik mesai çıkarılıyor)
    toplam_kazanc = (normal_kazanc + izin_kazanc + mesai_kazanc - eksik_mesai_kazanc + tatil_kazanc + 
                     tatil_mesai_kazanc + yillik_izin_kazanc +
                     yol + prim + ikramiye + bayram + kira)
    
    return {
        # Draft Contract Bilgileri
        "draft_contracts_id": draft.id,
        "cc_id": draft.cost_center_id,
        "cost_center_name": cost_center_name,
        "net_ucret": net_ucret,
        "ucret_nevi": ucret_nevi,
        "fm_orani": fm_orani,
        "tatil_orani": tatil_orani,
        
        # Puantaj Verileri
        "normal_calismasi": normal_calismasi,
        "izin_gun_sayisi": izin_gun_sayisi,
        "fazla_calismasi": fazla_calismasi,
        "eksik_calismasi": eksik_calismasi,
        "yillik_izin_gun": yillik_izin_gun,
        "hafta_tatili": hafta_tatili,
        "resmi_tatil": resmi_tatil,
        "tatil_calismasi": tatil_calismasi,
        "yol": yol,
        "prim": prim,
        "ikramiye": ikramiye,
        "bayram": bayram,
        "kira": kira,
        
        # Hesaplanan Değerler
        "gunluk_ucret": round(gunluk_ucret, 2),
        "normal_kazanc": round(normal_kazanc, 2),
        "izin_kazanc": round(izin_kazanc, 2),
        "mesai_kazanc": round(mesai_kazanc, 2),
        "eksik_mesai_kazanc": round(eksik_mesai_kazanc, 2),
        "tatil_kazanc": round(tatil_kazanc, 2),
        "tatil_mesai_kazanc": round(tatil_mesai_kazanc, 2),
        "yillik_izin_kazanc": round(yillik_izin_kazanc, 2),
        "toplam_kazanc": round(toplam_kazanc, 2)
    }
