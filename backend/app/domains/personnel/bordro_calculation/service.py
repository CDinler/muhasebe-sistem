"""Bordro Calculation Service"""
from sqlalchemy.orm import Session, joinedload
from typing import Dict, Any, List
from decimal import Decimal

from app.models import LucaBordro
from app.models import MonthlyPuantaj
from app.models import PersonnelContract
from app.models import PayrollCalculation
from app.models import Personnel
from app.models import PersonnelDraftContract
from app.models import SystemConfig
from app.models import PersonnelPuantajGrid
from app.models import CostCenter


class BordroCalculationService:
    """Service for bordro calculation logic"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def _calculate_ppg_summary(self, ppg: PersonnelPuantajGrid, ay: int) -> Dict[str, float]:
        """
        Puantaj grid'den özet alanları al (trigger tarafından hesaplanmış)
        
        Returns: personnel_puantaj_grid tablosundaki tüm özet alanlar
        """
        # Özet alanlarını direkt puantaj grid'den al (trigger ile hesaplanmış)
        hafta_tatili = int(ppg.hafta_tatili or 0)
        resmi_tatil = int(ppg.resmi_tatil or 0)
        tatil_calismasi = float(ppg.tatil_calismasi or 0)
        
        return {
            # Gün sayıları
            'calisilan_gun_sayisi': int(ppg.calisilan_gun_sayisi or 0),
            'ssk_gun_sayisi': int(ppg.ssk_gun_sayisi or 0),
            'yillik_izin_gun': int(ppg.yillik_izin_gun or 0),
            'izin_gun_sayisi': int(ppg.izin_gun_sayisi or 0),
            'rapor_gun_sayisi': int(ppg.rapor_gun_sayisi or 0),
            'eksik_gun_sayisi': int(ppg.eksik_gun_sayisi or 0),
            'yarim_gun_sayisi': float(ppg.yarim_gun_sayisi or 0),
            'toplam_gun_sayisi': int(ppg.toplam_gun_sayisi or 0),
            'ayin_toplam_gun_sayisi': int(ppg.ayin_toplam_gun_sayisi or 30),
            
            # Çalışma detayları
            'normal_calismasi': float(ppg.normal_calismasi or 0),
            'fazla_calismasi': float(ppg.fazla_calismasi or 0),
            'eksik_calismasi': float(ppg.eksik_calismasi or 0),  # Eksik mesai saati
            'gece_calismasi': float(ppg.gece_calismasi or 0),
            'tatil_calismasi': tatil_calismasi,
            'sigorta_girmedigi': int(ppg.sigorta_girmedigi or 0),
            'hafta_tatili': hafta_tatili,
            'resmi_tatil': resmi_tatil,
            
            # Toplam tatil hesaplama
            'toplam_tatil': hafta_tatili + resmi_tatil + tatil_calismasi,
            
            # Ek ödemeler
            'yol': float(ppg.yol or 0),
            'prim': float(ppg.prim or 0),
            'ikramiye': float(ppg.ikramiye or 0),
            'bayram': float(ppg.bayram or 0),
            'kira': float(ppg.kira or 0),
        }
    
    def calculate(self, yil: int, ay: int) -> Dict[str, Any]:
        """
        Calculate bordro: Luca + Puantaj + Contract → PayrollCalculation
        
        Args:
            yil: Year
            ay: Month
            
        Returns:
            {
                success: bool,
                donem: str,
                calculated: int,
                updated: int,
                total: int,
                errors: List[str]
            }
        """
        donem = f"{yil}-{ay:02d}"
        
        # 1. Get Luca bordro records
        luca_records = self.db.query(LucaBordro).filter(
            LucaBordro.yil == yil,
            LucaBordro.ay == ay
        ).all()
        
        if not luca_records:
            return {
                "success": False,
                "error": f"{donem} dönemi için Luca bordro bulunamadı"
            }
        
        # 2. Get system configs
        configs = {}
        for cfg in self.db.query(SystemConfig).all():
            configs[cfg.config_key] = float(cfg.config_value)
        
        elden_yuvarlama = configs.get('ELDEN_YUVARLAMA', 100)
        
        calculated_count = 0
        updated_count = 0
        errors = []
        
        for luca in luca_records:
            try:
                # Find personnel
                personnel = self.db.query(Personnel).options(
                    joinedload(Personnel.account)
                ).filter(
                    Personnel.tc_kimlik_no == luca.tckn
                ).first()
                
                if not personnel:
                    errors.append(f"{luca.adi_soyadi}: Personel bulunamadı (TC: {luca.tckn})")
                    continue
                
                # Find contract
                # Önce Luca'da kayıtlı contract_id varsa kullan
                if luca.contract_id:
                    contract = self.db.query(PersonnelContract).filter(
                        PersonnelContract.id == luca.contract_id
                    ).first()
                else:
                    # Yoksa eski yöntemle bul (fallback)
                    contract = self._find_contract(personnel.id, luca.giris_t)
                    
                    # Contract bulunduysa luca kaydına kaydet
                    if contract:
                        luca.contract_id = contract.id
                
                if not contract:
                    errors.append(f"{luca.adi_soyadi}: Sözleşme bulunamadı")
                    continue
                
                
                # Find puantaj grid (personnel_puantaj_grid) - ppg değişkenleri için
                ppg = None
                puantaj = None  # RESMİ kayıtlar için puantaj kullanılmıyor (None)
                if contract:
                    # Sadece personnel_id ve donem ile puantaj grid'i bul
                    # Çünkü bir personelin bir dönemde tek puantaj kaydı olmalı
                    ppg = self.db.query(PersonnelPuantajGrid).filter(
                        PersonnelPuantajGrid.personnel_id == personnel.id,
                        PersonnelPuantajGrid.donem == donem
                    ).first()
                
                # Check existing calculation
                # Bir personelin birden fazla bordrosu olabilir (farklı şantiyeler)
                # Her Luca kaydı = ayrı bordro, unique key: personnel + dönem + luca_bordro_id
                existing = self.db.query(PayrollCalculation).filter(
                    PayrollCalculation.personnel_id == personnel.id,
                    PayrollCalculation.yil == yil,
                    PayrollCalculation.ay == ay,
                    PayrollCalculation.luca_bordro_id == luca.id
                ).first()
                
                # Calculate
                calc_data = self._calculate_bordro(
                    yil, ay, donem, personnel, luca, contract, puantaj, ppg, elden_yuvarlama
                )
                
                if existing:
                    for key, value in calc_data.items():
                        setattr(existing, key, value)
                    updated_count += 1
                else:
                    calc = PayrollCalculation(**calc_data)
                    self.db.add(calc)
                    calculated_count += 1
                    
            except Exception as e:
                import traceback
                error_msg = f"{luca.adi_soyadi}: {str(e)}"
                errors.append(error_msg)
                print(f"❌ HATA: {error_msg}")
                print(traceback.format_exc())
                continue
        
        # TASLAK KAYITLARI OLUŞTUR
        # Draft contract olan personeller için TÜM luca kayıtlarını toplayıp TEK TASLAK kayıt oluştur
        print(f"\n📋 TASLAK kayıtları oluşturuluyor (yil={yil}, ay={ay})...")
        
        # RESMİ kayıtları DB'ye flush et ki TASLAK sorguları görebilsin
        self.db.flush()
        
        self._create_taslak_records(yil, ay, donem, elden_yuvarlama)
        
        self.db.commit()
        
        return {
            "success": True,
            "donem": donem,
            "calculated": calculated_count,
            "updated": updated_count,
            "total": calculated_count + updated_count,
            "errors": errors[:20] if errors else []
        }
    
    def list_calculations(
        self, 
        yil: int, 
        ay: int,
        skip: int = 0, 
        limit: int = 100
    ) -> Dict[str, Any]:
        """List calculated bordro records with all fields"""
        query = self.db.query(PayrollCalculation).filter(
            PayrollCalculation.yil == yil,
            PayrollCalculation.ay == ay
        )
        
        total = query.count()
        items = query.offset(skip).limit(limit).all()
        
        return {
            "total": total,
            "items": [
                {
                    # Basic info
                    "id": item.id,
                    "personnel_id": item.personnel_id,
                    "adi_soyadi": item.adi_soyadi,
                    "tckn": item.tckn,
                    
                    # Dönem
                    "yil": item.yil,
                    "ay": item.ay,
                    "donem": item.donem,
                    
                    # IDs - Relations
                    "contract_id": item.contract_id,
                    "draft_contract_id": item.draft_contract_id,
                    "luca_bordro_id": item.luca_bordro_id,
                    "puantaj_id": item.puantaj_id,
                    "cost_center_id": item.cost_center_id,
                    
                    # Maliyet & Ücret
                    "maliyet_merkezi": item.maliyet_merkezi,
                    "ucret_nevi": item.ucret_nevi,
                    "kanun_tipi": item.kanun_tipi,
                    "yevmiye_tipi": item.yevmiye_tipi,
                    
                    # Maas1 fields (from Luca)
                    "maas1_net_odenen": float(item.maas1_net_odenen) if item.maas1_net_odenen else 0,
                    "maas1_icra": float(item.maas1_icra) if item.maas1_icra else 0,
                    "maas1_bes": float(item.maas1_bes) if item.maas1_bes else 0,
                    "maas1_avans": float(item.maas1_avans) if item.maas1_avans else 0,
                    "maas1_gelir_vergisi": float(item.maas1_gelir_vergisi) if item.maas1_gelir_vergisi else 0,
                    "maas1_damga_vergisi": float(item.maas1_damga_vergisi) if item.maas1_damga_vergisi else 0,
                    "maas1_ssk_isci": float(item.maas1_ssk_isci) if item.maas1_ssk_isci else 0,
                    "maas1_issizlik_isci": float(item.maas1_issizlik_isci) if item.maas1_issizlik_isci else 0,
                    "maas1_ssk_isveren": float(item.maas1_ssk_isveren) if item.maas1_ssk_isveren else 0,
                    "maas1_issizlik_isveren": float(item.maas1_issizlik_isveren) if item.maas1_issizlik_isveren else 0,
                    "maas1_ssk_tesviki": float(item.maas1_ssk_tesviki) if item.maas1_ssk_tesviki else 0,
                    "maas1_diger_kesintiler": float(item.maas1_icra or 0) + float(item.maas1_bes or 0) + float(item.maas1_avans or 0),
                    
                    # Maas2 fields (from PPG calculation)
                    "maas2_anlaşilan": float(item.maas2_anlaşilan) if item.maas2_anlaşilan else 0,
                    "maas2_normal_calismasi": float(item.maas2_normal_calismasi) if item.maas2_normal_calismasi else 0,
                    "maas2_hafta_tatili": float(item.maas2_hafta_tatili) if item.maas2_hafta_tatili else 0,
                    "maas2_fm_calismasi": float(item.maas2_fm_calismasi) if item.maas2_fm_calismasi else 0,
                    "maas2_em_calismasi": float(item.maas2_em_calismasi) if item.maas2_em_calismasi else 0,
                    "maas2_resmi_tatil": float(item.maas2_resmi_tatil) if item.maas2_resmi_tatil else 0,
                    "maas2_tatil_calismasi": float(item.maas2_tatil_calismasi) if item.maas2_tatil_calismasi else 0,
                    "maas2_toplam_tatil_calismasi": float(item.maas2_toplam_tatil_calismasi) if item.maas2_toplam_tatil_calismasi else 0,
                    "maas2_yillik_izin": float(item.maas2_yillik_izin) if item.maas2_yillik_izin else 0,
                    "maas2_yol": float(item.maas2_yol) if item.maas2_yol else 0,
                    "maas2_prim": float(item.maas2_prim) if item.maas2_prim else 0,
                    "maas2_ikramiye": float(item.maas2_ikramiye) if item.maas2_ikramiye else 0,
                    "maas2_bayram": float(item.maas2_bayram) if item.maas2_bayram else 0,
                    "maas2_kira": float(item.maas2_kira) if item.maas2_kira else 0,
                    "maas2_toplam": float(item.maas2_toplam) if item.maas2_toplam else 0,
                    
                    # Puantaj details (gün/saat)
                    "normal_gun": float(item.normal_gun) if item.normal_gun else 0,
                    "hafta_tatili_gun": float(item.hafta_tatili_gun) if item.hafta_tatili_gun else 0,
                    "fazla_mesai_saat": float(item.fazla_mesai_saat) if item.fazla_mesai_saat else 0,
                    "eksik_mesai_saat": float(item.eksik_mesai_saat) if item.eksik_mesai_saat else 0,
                    "tatil_mesai_gun": float(item.tatil_mesai_gun) if item.tatil_mesai_gun else 0,
                    "yillik_izin_gun": float(item.yillik_izin_gun) if item.yillik_izin_gun else 0,
                    
                    # Elden calculation
                    "elden_ucret_ham": float(item.elden_ucret_ham) if item.elden_ucret_ham else 0,
                    "elden_ucret_yuvarlanmis": float(item.elden_ucret_yuvarlanmis) if item.elden_ucret_yuvarlanmis else 0,
                    "elden_yuvarlama": float(item.elden_yuvarlama) if item.elden_yuvarlama else 0,
                    "elden_yuvarlama_yon": item.elden_yuvarlama_yon,
                    
                    # Account code
                    "account_code_335": item.account_code_335,
                    
                    # Transaction info
                    "transaction_id": item.transaction_id,
                    "fis_no": item.fis_no,
                    
                    # Status
                    "is_approved": item.is_approved,
                    "is_exported": item.is_exported,
                    "has_error": item.has_error,
                    "error_message": item.error_message,
                    
                    # Metadata
                    "notes": item.notes,
                    "created_at": item.created_at.isoformat() if item.created_at else None,
                    "updated_at": item.updated_at.isoformat() if item.updated_at else None,
                    "calculated_by": item.calculated_by,
                    "approved_by": item.approved_by,
                }
                for item in items
            ]
        }
    
    def _find_contract(self, personnel_id: int, ise_giris_tarihi) -> PersonnelContract:
        """Find contract for personnel"""
        # Try exact match with ise_giris_tarihi
        contract = self.db.query(PersonnelContract).filter(
            PersonnelContract.personnel_id == personnel_id,
            PersonnelContract.ise_giris_tarihi == ise_giris_tarihi
        ).order_by(PersonnelContract.id.desc()).first()
        
        # If not found, use latest contract
        if not contract:
            contract = self.db.query(PersonnelContract).filter(
                PersonnelContract.personnel_id == personnel_id
            ).order_by(PersonnelContract.ise_giris_tarihi.desc()).first()
        
        return contract
    
    def _calculate_bordro(
        self,
        yil: int,
        ay: int,
        donem: str,
        personnel: Personnel,
        luca: LucaBordro,
        contract: PersonnelContract,
        puantaj: MonthlyPuantaj,
        ppg: PersonnelPuantajGrid,
        elden_yuvarlama: float
    ) -> Dict[str, Any]:
        """
        Calculate bordro data for one personnel - RESMİ kayıt
        Bu fonksiyon her luca_bordro kaydı için RESMİ tip kayıt oluşturur.
        Sadece Luca'dan gelen veriler (maas1_*) kaydedilir.
        maas2_* hesaplamaları TASLAK kayıtlar için _create_taslak_records'da yapılır.
        """
        
        # Get cost center name (contract'tan, draft_contract'a bakmaya gerek yok)
        maliyet_merkezi = None
        cost_center_id = None
        
        if contract and contract.cost_center_id:
            cost_center_id = contract.cost_center_id
            cost_center = self.db.query(CostCenter).filter(
                CostCenter.id == cost_center_id
            ).first()
            if cost_center:
                maliyet_merkezi = cost_center.name
        
        # RESMİ kayıt - sadece Luca verileri
        calc_data = {
            'yil': yil,
            'ay': ay,
            'donem': donem,
            'personnel_id': personnel.id,
            'contract_id': contract.id if contract else None,
            'luca_bordro_id': luca.id,
            'puantaj_id': None,  # RESMİ kayıtlarda puantaj kullanılmaz
            'tckn': luca.tckn,
            'adi_soyadi': luca.adi_soyadi,
            'cost_center_id': cost_center_id,
            'maliyet_merkezi': maliyet_merkezi,
            'ucret_nevi': None,  # RESMİ kayıtlarda ucret_nevi yok
            'kanun_tipi': contract.kanun_tipi if contract else None,
            
            # Maas1 (from Luca) - RESMİ kayıtlarda sadece bunlar var
            'maas1_net_odenen': float(luca.n_odenen) if luca.n_odenen else 0,
            'maas1_icra': float(luca.icra) if luca.icra else 0,
            'maas1_bes': float(luca.oto_kat_bes) if luca.oto_kat_bes else 0,
            'maas1_avans': float(luca.avans) if luca.avans else 0,
            'maas1_gelir_vergisi': float(luca.gel_ver) if luca.gel_ver else 0,
            'maas1_damga_vergisi': float(luca.damga_v) if luca.damga_v else 0,
            'maas1_ssk_isci': float(luca.ssk_isci) if luca.ssk_isci else 0,
            'maas1_issizlik_isci': float(luca.iss_p_isci) if luca.iss_p_isci else 0,
            'maas1_ssk_isveren': float(luca.ssk_isveren) if luca.ssk_isveren else 0,
            'maas1_issizlik_isveren': float(luca.iss_p_isveren) if luca.iss_p_isveren else 0,
            'maas1_ssk_tesviki': float(luca.ssk_tesviki) if luca.ssk_tesviki else 0,
            
            # Maas2 alanları RESMİ kayıtlarda NULL (0) - TASLAK kayıtlarda hesaplanacak
            'maas2_anlaşilan': 0,
            'maas2_normal_calismasi': 0,
            'maas2_fm_calismasi': 0,
            'maas2_resmi_tatil': 0,
            'maas2_hafta_tatili': 0,
            'maas2_tatil_calismasi': 0,
            'maas2_toplam_tatil_calismasi': 0,
            'maas2_yillik_izin': 0,
            'maas2_yol': 0,
            'maas2_prim': 0,
            'maas2_ikramiye': 0,
            'maas2_bayram': 0,
            'maas2_kira': 0,
            'maas2_toplam': 0,
            
            # Puantaj detayları RESMİ kayıtlarda yok (0)
            'normal_gun': 0,
            'hafta_tatili_gun': 0,
            'fazla_mesai_saat': 0,
            'tatil_mesai_gun': 0,
            'yillik_izin_gun': 0,
            
            # Elden ücret RESMİ kayıtlarda yok
            'elden_ucret_ham': 0,
            'elden_ucret_yuvarlanmis': 0,
            'elden_yuvarlama': 0,
            'elden_yuvarlama_yon': None,
            
            # Account code
            'account_code_335': personnel.account.code if personnel and personnel.account else None,
            
            # Yevmiye tipi - Her luca_bordro için RESMİ
            'yevmiye_tipi': 'RESMİ',
        }
        
        return calc_data
    
    def _create_taslak_records(self, yil: int, ay: int, donem: str, elden_yuvarlama: float):
        """
        Draft contract olan personeller için TASLAK kayıtları oluşturur.
        Her personel için TÜM luca kayıtlarını toplar ve TEK BİR TASLAK kayıt oluşturur.
        
        Args:
            yil: Yıl
            ay: Ay
            donem: Dönem string (YYYY-MM)
            elden_yuvarlama: Yuvarlama miktarı (örn: 100)
        """
        # Draft contract olan personelleri bul
        draft_contracts = self.db.query(PersonnelDraftContract).filter(
            PersonnelDraftContract.is_active == 1
        ).all()
        
        if not draft_contracts:
            print(f"⚠️ Aktif draft contract bulunamadı")
            return
        
        print(f"✅ {len(draft_contracts)} adet draft contract bulundu")
        
        taslak_created = 0
        taslak_updated = 0
        taslak_skipped = 0
        
        for draft_contract in draft_contracts:
            try:
                personnel_id = draft_contract.personnel_id
                
                # Bu personelin bu dönemdeki TÜM RESMİ kayıtlarını al
                resmi_records = self.db.query(PayrollCalculation).filter(
                    PayrollCalculation.personnel_id == personnel_id,
                    PayrollCalculation.yil == yil,
                    PayrollCalculation.ay == ay,
                    PayrollCalculation.yevmiye_tipi == 'RESMİ'
                ).all()
                
                if not resmi_records:
                    print(f"⚠️ Personnel {personnel_id} - RESMİ kayıt bulunamadı, atlanıyor")
                    taslak_skipped += 1
                    continue  # Bu personelin bu dönemde bordrosu yok
                
                # RESMİ kayıtlardan sadece luca_bordro_id'leri al, Luca kayıtlarını çek
                luca_ids = [rec.luca_bordro_id for rec in resmi_records if rec.luca_bordro_id]
                luca_records = self.db.query(LucaBordro).filter(
                    LucaBordro.id.in_(luca_ids)
                ).all() if luca_ids else []
                
                # Luca toplamları
                total_n_odenen = sum(Decimal(str(lb.n_odenen or 0)) for lb in luca_records)
                total_oto_kat_bes = sum(Decimal(str(lb.oto_kat_bes or 0)) for lb in luca_records)
                total_icra = sum(Decimal(str(lb.icra or 0)) for lb in luca_records)
                total_avans = sum(Decimal(str(lb.avans or 0)) for lb in luca_records)
                
                bordro_net_toplami = total_n_odenen + total_oto_kat_bes + total_icra + total_avans
                
                # Personnel bilgisi al
                personnel = self.db.query(Personnel).filter(Personnel.id == personnel_id).first()
                if not personnel:
                    print(f"⚠️ Personnel {personnel_id} - Personnel kaydı bulunamadı, atlanıyor")
                    taslak_skipped += 1
                    continue
                
                # PersonnelContract'tan kanun_tipi al (son contract - aktif/pasif farketmez)
                personnel_contract = self.db.query(PersonnelContract).filter(
                    PersonnelContract.personnel_id == personnel_id
                ).order_by(PersonnelContract.ise_giris_tarihi.desc()).first()
                kanun_tipi = personnel_contract.kanun_tipi if personnel_contract else None
                
                # Puantaj grid'i bul - TASLAK hesaplamalar için gerekli
                ppg = self.db.query(PersonnelPuantajGrid).filter(
                    PersonnelPuantajGrid.personnel_id == personnel_id,
                    PersonnelPuantajGrid.donem == donem
                ).first()
                
                # Puantaj özeti hesapla (maas2 hesaplamaları için)
                ppg_summary = self._calculate_ppg_summary(ppg, ay) if ppg else {
                    'calisilan_gun_sayisi': 0, 'ssk_gun_sayisi': 0, 'yillik_izin_gun': 0,
                    'izin_gun_sayisi': 0, 'rapor_gun_sayisi': 0, 'eksik_gun_sayisi': 0,
                    'yarim_gun_sayisi': 0, 'toplam_gun_sayisi': 0, 'ayin_toplam_gun_sayisi': 30,
                    'normal_calismasi': 0, 'fazla_calismasi': 0, 'gece_calismasi': 0,
                    'tatil_calismasi': 0, 'sigorta_girmedigi': 0, 'hafta_tatili': 0,
                    'resmi_tatil': 0, 'toplam_tatil': 0, 'yol': 0, 'prim': 0, 
                    'ikramiye': 0, 'bayram': 0, 'kira': 0
                }
                
                # Draft contract'tan ücret bilgilerini al
                net_ucret = Decimal(str(draft_contract.net_ucret or 0))
                # Günlük ücret hesapla - ucret_nevi'ye göre
                if draft_contract.ucret_nevi == 'gunluk':
                    gunluk_ucret = net_ucret
                else:  # 'aylik' veya 'sabit aylik'
                    gunluk_ucret = net_ucret / 30 if net_ucret else Decimal('0')
                
                # Normal çalışma günü - PPG'den al (trigger tarafından hesaplanmış)
                normal_calisma_gunu = Decimal(str(ppg_summary['normal_calismasi']))
                yarim_gun_sayisi = Decimal(str(ppg_summary.get('yarim_gun_sayisi', 0)))
                eksik_gun_sayisi = Decimal(str(ppg_summary.get('eksik_gun_sayisi', 0)))
                rapor_gun_sayisi = Decimal(str(ppg_summary.get('rapor_gun_sayisi', 0)))
                sigorta_girmedigi = Decimal(str(ppg_summary.get('sigorta_girmedigi', 0)))
                ayin_toplam_gun_sayisi = ppg_summary.get('ayin_toplam_gun_sayisi', 30)
                
                # Maas2 hesaplamaları (draft contract üzerinden)
                maas2_normal = gunluk_ucret * normal_calisma_gunu
                maas2_fm = gunluk_ucret / 8 * Decimal(str(ppg_summary.get('fazla_calismasi', 0))) * Decimal(str(draft_contract.fm_orani or 1.5))
                maas2_em = gunluk_ucret / 8 * Decimal(str(ppg_summary.get('eksik_calismasi', 0)))
                
                # Tatil günleri (Hafta tatili + Resmi tatil + Tatil çalışması base)
                maas2_toplam_tatil_calismasi = gunluk_ucret * (
                    Decimal(str(ppg_summary.get('hafta_tatili', 0))) +
                    Decimal(str(ppg_summary.get('resmi_tatil', 0))) +
                    Decimal(str(ppg_summary.get('tatil_calismasi', 0)))
                )
                
                # Tatil çalışması ek ödemesi (base zaten toplam_tatil_calismasi'da)
                tatil_calismasi_gun = Decimal(str(ppg_summary.get('tatil_calismasi', 0)))
                maas2_tatil_calismasi = gunluk_ucret * tatil_calismasi_gun * Decimal(str(draft_contract.tatil_orani or 1.0))
                
                # Yıllık izin
                maas2_yillik_izin = gunluk_ucret * Decimal(str(ppg_summary['yillik_izin_gun']))
                
                # Yarım gün
                maas2_yarim_gun = gunluk_ucret * yarim_gun_sayisi * Decimal('0.5')
                
                # Ek ödemeler (puantaj grid'den)
                maas2_yol = Decimal(str(ppg_summary['yol']))
                maas2_prim = Decimal(str(ppg_summary['prim']))
                maas2_ikramiye = Decimal(str(ppg_summary['ikramiye']))
                maas2_bayram = Decimal(str(ppg_summary['bayram']))
                maas2_kira = Decimal(str(ppg_summary['kira']))
                
                # Toplam hesaplama
                maas2_toplam = (
                    maas2_normal +
                    maas2_yarim_gun +
                    maas2_toplam_tatil_calismasi +
                    maas2_tatil_calismasi +
                    maas2_yillik_izin +
                    maas2_fm +
                    maas2_em +
                    maas2_yol + maas2_prim + maas2_ikramiye + maas2_bayram + maas2_kira
                )
                
                # Elden kalan hesapla
                elden_ucret_ham = maas2_toplam - bordro_net_toplami
                
                if elden_ucret_ham <= 0:
                    print(f"⚠️ {personnel.ad} {personnel.soyad}- Elden ödeme yok (maas2={maas2_toplam}, bordro_net={bordro_net_toplami}), atlanıyor")
                    taslak_skipped += 1
                    continue  # Elden ödeme yoksa taslak kayıt oluşturma
                
                # Yuvarlama
                elden_ucret_yuvarlanmis = round(elden_ucret_ham / Decimal(str(elden_yuvarlama))) * Decimal(str(elden_yuvarlama))
                elden_yuvarlama_tutar = elden_ucret_yuvarlanmis - elden_ucret_ham
                elden_yuvarlama_yon = 'YUKARI' if elden_ucret_yuvarlanmis > elden_ucret_ham else 'ASAGI'
                
                # TASLAK kayıt var mı kontrol et
                existing_taslak = self.db.query(PayrollCalculation).filter(
                    PayrollCalculation.personnel_id == personnel_id,
                    PayrollCalculation.yil == yil,
                    PayrollCalculation.ay == ay,
                    PayrollCalculation.yevmiye_tipi == 'TASLAK'
                ).first()
                
                # Maliyet merkezi bilgisi al (draft_contract'tan)
                maliyet_merkezi_adi = None
                if draft_contract.cost_center_id:
                    cost_center = self.db.query(CostCenter).filter(
                        CostCenter.id == draft_contract.cost_center_id
                    ).first()
                    if cost_center:
                        maliyet_merkezi_adi = cost_center.name
                
                # TASLAK kayıt verilerini hazırla
                taslak_data = {
                    'personnel_id': personnel_id,
                    'yil': yil,
                    'ay': ay,
                    'donem': donem,
                    'yevmiye_tipi': 'TASLAK',
                    'tckn': personnel.tc_kimlik_no if personnel.tc_kimlik_no else '',
                    'adi_soyadi': f"{personnel.ad} {personnel.soyad}",
                    # ID'ler - TASLAK kayıtlar için
                    'puantaj_id': ppg.id if ppg else None,  # personnel_puantaj_grid ID
                    'draft_contract_id': draft_contract.id,
                    'luca_bordro_id': None,  # TASLAK kayıt tek luca'ya bağlı değil
                    'contract_id': None,
                    # Maliyet & Ücret bilgileri
                    'cost_center_id': draft_contract.cost_center_id,
                    'maliyet_merkezi': maliyet_merkezi_adi,
                    'ucret_nevi': draft_contract.ucret_nevi,
                    'kanun_tipi': 0,
                    # Maas1 alanları TASLAK'ta 0 (Luca'dan gelmiyor)
                    'maas1_net_odenen': 0,
                    'maas1_icra': 0,
                    'maas1_bes': 0,
                    'maas1_avans': 0,
                    'maas1_gelir_vergisi': 0,
                    'maas1_damga_vergisi': 0,
                    'maas1_ssk_isci': 0,
                    'maas1_issizlik_isci': 0,
                    'maas1_ssk_isveren': 0,
                    'maas1_issizlik_isveren': 0,
                    'maas1_ssk_tesviki': 0,
                    # Maas2 hesaplamaları (draft contract bazlı) - DÜZELTİLDİ
                    'maas2_anlaşilan': float(net_ucret),
                    'maas2_toplam': float(maas2_toplam),
                    'maas2_normal_calismasi': float(maas2_normal),
                    'maas2_fm_calismasi': float(maas2_fm),
                    'maas2_em_calismasi': float(maas2_em),  # Artık doğru kesinti
                    'maas2_hafta_tatili': float(maas2_hafta_tatili),
                    'maas2_resmi_tatil': float(maas2_resmi_tatil),
                    'maas2_toplam_tatil_calismasi': float(maas2_toplam_tatil_calismasi),  # H+T+M base
                    'maas2_tatil_calismasi': float(maas2_tatil_calismasi),  # Sadece M*TATIL_ORANI ek ödemesi
                    'maas2_yillik_izin': float(maas2_yillik_izin),
                    'maas2_yol': float(maas2_yol),
                    'maas2_prim': float(maas2_prim),
                    'maas2_ikramiye': float(maas2_ikramiye),
                    'maas2_bayram': float(maas2_bayram),
                    'maas2_kira': float(maas2_kira),
                    # Puantaj bilgileri (gün/saat)
                    'normal_gun': float(normal_calisma_gunu),
                    'hafta_tatili_gun': ppg_summary['hafta_tatili'],
                    'fazla_mesai_saat': ppg_summary['fazla_calismasi'],
                    'eksik_mesai_saat': ppg_summary.get('eksik_calismasi', 0),  # Eksik mesai saati
                    'tatil_mesai_gun': ppg_summary['tatil_calismasi'],
                    'yillik_izin_gun': ppg_summary['yillik_izin_gun'],
                    # Elden ücret
                    'elden_ucret_ham': float(elden_ucret_ham),
                    'elden_ucret_yuvarlanmis': float(elden_ucret_yuvarlanmis),
                    'elden_yuvarlama': float(elden_yuvarlama_tutar),
                    'elden_yuvarlama_yon': elden_yuvarlama_yon,
                    # Diğer bilgiler
                    'cost_center_id': draft_contract.cost_center_id,
                    'account_code_335': personnel.account.code if personnel.account else None,
                }
                
                if existing_taslak:
                    # Güncelle
                    for key, value in taslak_data.items():
                        setattr(existing_taslak, key, value)
                    print(f"✅ TASLAK kayıt güncellendi: {personnel.ad} {personnel.soyad}, elden={elden_ucret_ham}")
                    taslak_updated += 1
                else:
                    # Yeni oluştur
                    taslak_calc = PayrollCalculation(**taslak_data)
                    self.db.add(taslak_calc)
                    print(f"✅ TASLAK kayıt oluşturuldu: {personnel.ad} {personnel.soyad}, elden={elden_ucret_ham}")
                    taslak_created += 1
                    
            except Exception as e:
                import traceback
                print(f"❌ TASLAK kayıt hatası (personnel_id={draft_contract.personnel_id}): {str(e)}")
                print(traceback.format_exc())
                taslak_skipped += 1
                continue
        
        print(f"📊 TASLAK kayıt özeti: Oluşturulan={taslak_created}, Güncellenen={taslak_updated}, Atlanan={taslak_skipped}")
