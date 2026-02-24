"""
Bordro Yevmiye (Journal Entry) Service - YENİ SİSTEM
=======================================================

Her luca_bordro kaydı için:
- RESMİ KAYIT: Ayrı transaction oluşturulur
- TASLAK KAYIT: Eğer draft contract varsa ve elden ödeme varsa ayrı transaction oluşturulur

Onay Mekanizması: Personel bazında (bir personelin tüm bordroları için)
"""

from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from decimal import Decimal
from datetime import datetime, date
from calendar import monthrange

from app.models import LucaBordro
from app.models import Personnel
from app.models import PersonnelContract
from app.models import PersonnelDraftContract
from app.models import PersonnelPuantajGrid
from app.models import CostCenter
from app.models import Transaction
from app.models import TransactionLine
from app.models import Account
from app.models import DocumentType
from app.models import PayrollCalculation
from app.utils.transaction_numbering import get_next_transaction_number


class BordroYevmiyeService:
    """
    Bordro Yevmiye Servisi
    
    Algoritma:
    ---------
    ADIM 1: Her luca bordro için RESMİ KAYIT transaction'ı oluştur
    ADIM 2: Draft contract varsa TASLAK KAYIT transaction'ı oluştur (elden ödeme)
    """
    
    def __init__(self, db: Session):
        self.db = db
        
        # Sabit hesap ID'leri (accounts tablosundan)
        self.ACCOUNT_IDS = {
            'g_vergi_acc_id': 728,          # Gelir Vergisi
            'd_vergi_acc_id': 729,          # Damga Vergisi
            'sgk_isci_prim_acc_id': 731,    # SGK İşçi Primi
            'sgk_isveren_prim_acc_id': 732, # SGK İşveren Primi
            'sgk_isci_isz_acc_id': 733,     # SGK İşçi İşsizlik
            'sgk_isveren_isz_acc_id': 734,  # SGK İşveren İşsizlik
            'bes_kesinti_acc_id': 735,      # BES Kesintisi
            'icra_kesinti_acc_id': 736,     # İcra Kesintisi
            'haz_kat_payi_acc_id': 744      # Hazine Katkı Payı (SSK Teşviki)
        }
    
    def preview_yevmiye_for_personnel(
        self, 
        personnel_id: int, 
        yil: int, 
        ay: int
    ) -> Dict[str, Any]:
        """
        Bir personelin belirli dönemdeki TÜM bordrolarının yevmiye önizlemesini oluşturur
        
        Args:
            personnel_id: Personel ID
            yil: Yıl
            ay: Ay
            
        Returns:
            {
                "success": True,
                "personnel_id": int,
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
                "taslak_kayitlar": [
                    # Sadece draft contract olanlar için
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
                ]
            }
        """
        try:
            donem = f"{yil}-{ay:02d}"
            
            # Personelin bu dönemdeki tüm bordro kayıtlarını çek
            luca_bordros = self.db.query(LucaBordro).filter(
                LucaBordro.personnel_id == personnel_id,
                LucaBordro.yil == yil,
                LucaBordro.ay == ay
            ).all()
            
            if not luca_bordros:
                return {
                    "success": False,
                    "error": f"Personel ID {personnel_id} için {donem} döneminde bordro kaydı bulunamadı"
                }
            
            # Personel bilgisi
            personnel = self.db.query(Personnel).filter(Personnel.id == personnel_id).first()
            if not personnel:
                return {"success": False, "error": "Personel bulunamadı"}
            
            resmi_kayitlar = []
            taslak_kayitlar = []
            
            # Her luca bordro için ayrı RESMİ KAYIT önizlemesi
            for luca in luca_bordros:
                resmi = self._create_resmi_kayit_preview(luca, personnel, yil, ay)
                if resmi:
                    resmi_kayitlar.append(resmi)
            
            # TASLAK KAYIT - Personelin TÜM bordroları için TEK BİR taslak kayıt
            taslak = self._create_taslak_kayit_preview_combined(luca_bordros, personnel, yil, ay)
            if taslak:
                taslak_kayitlar.append(taslak)
            
            return {
                "success": True,
                "personnel_id": personnel_id,
                "personnel_name": f"{personnel.ad} {personnel.soyad}",
                "donem": donem,
                "resmi_kayitlar": resmi_kayitlar,
                "taslak_kayitlar": taslak_kayitlar
            }
            
        except Exception as e:
            import traceback
            print(f"❌ PREVIEW ERROR:\n{traceback.format_exc()}")
            return {"success": False, "error": str(e)}
    
    def save_yevmiye_for_personnel(
        self, 
        personnel_id: int, 
        yil: int, 
        ay: int
    ) -> Dict[str, Any]:
        """
        Bir personelin belirli dönemdeki TÜM bordrolarının yevmiye kayıtlarını database'e kaydeder
        
        Returns:
            {
                "success": True,
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
            donem = f"{yil}-{ay:02d}"
            
            # Personelin bu dönemdeki tüm bordro kayıtlarını çek
            luca_bordros = self.db.query(LucaBordro).filter(
                LucaBordro.personnel_id == personnel_id,
                LucaBordro.yil == yil,
                LucaBordro.ay == ay
            ).all()
            
            if not luca_bordros:
                return {
                    "success": False,
                    "error": f"Personel ID {personnel_id} için {donem} döneminde bordro kaydı bulunamadı"
                }
            
            # Personel bilgisi
            personnel = self.db.query(Personnel).filter(Personnel.id == personnel_id).first()
            if not personnel:
                return {"success": False, "error": "Personel bulunamadı"}
            
            created_transactions = []
            
            # Her luca bordro için RESMİ KAYIT transaction oluştur
            for luca in luca_bordros:
                resmi_tr = self._save_resmi_kayit(luca, personnel, yil, ay)
                
                # PayrollCalculation kaydını güncelle
                payroll_calc = self.db.query(PayrollCalculation).filter(
                    PayrollCalculation.personnel_id == personnel_id,
                    PayrollCalculation.yil == yil,
                    PayrollCalculation.ay == ay,
                    PayrollCalculation.luca_bordro_id == luca.id
                ).first()
                
                if resmi_tr:
                    # Transaction oluşturuldu
                    created_transactions.append({
                        "type": "RESMİ KAYIT",
                        "transaction_id": resmi_tr.id,
                        "transaction_number": resmi_tr.transaction_number,
                        "luca_bordro_id": luca.id,
                        "bolum": self._get_contract_bolum(luca)
                    })
                    
                    if payroll_calc:
                        payroll_calc.transaction_id = resmi_tr.id
                        payroll_calc.fis_no = resmi_tr.transaction_number
                        payroll_calc.yevmiye_tipi = "RESMİ"
                        self.db.flush()
                        print(f"✅ PayrollCalculation güncellendi: ID={payroll_calc.id}, transaction_id={resmi_tr.id}")
                else:
                    # Transaction oluşturulmadı (satır yok) - PayrollCalculation'ı işaretleme
                    if payroll_calc:
                        payroll_calc.transaction_id = None  # NULL bırak
                        payroll_calc.fis_no = None
                        payroll_calc.yevmiye_tipi = "SATIR YOK"
                        self.db.flush()
                        print(f"⚠️ PayrollCalculation satır yok olarak işaretlendi: ID={payroll_calc.id}")
            
            # TASLAK KAYIT - Personelin TÜM bordroları için TEK BİR combined taslak kayıt
            taslak_tr = self._save_taslak_kayit_combined(luca_bordros, personnel, yil, ay)
            if taslak_tr:
                created_transactions.append({
                    "type": "TASLAK KAYIT",
                    "transaction_id": taslak_tr.id,
                    "transaction_number": taslak_tr.transaction_number,
                    "luca_bordro_ids": [lb.id for lb in luca_bordros],
                    "bolum": "Draft Contract"
                })
            
            self.db.commit()
            
            return {
                "success": True,
                "personnel_id": personnel_id,
                "personnel_name": f"{personnel.ad} {personnel.soyad}",
                "donem": donem,
                "transactions": created_transactions
            }
            
        except Exception as e:
            self.db.rollback()
            import traceback
            print(f"❌ SAVE ERROR:\n{traceback.format_exc()}")
            return {"success": False, "error": str(e)}
    
    # ========================================================================
    # HELPER METHODS - RESMİ KAYIT
    # ========================================================================
    
    def _create_resmi_kayit_preview(
        self, 
        luca: LucaBordro, 
        personnel: Personnel,
        yil: int,
        ay: int
    ) -> Optional[Dict[str, Any]]:
        """RESMİ KAYIT önizlemesi oluşturur"""
        try:
            # Variables
            vars = self._get_variables(luca, personnel, yil, ay)
            
            # Transaction bilgileri
            tr_no = f"PREVIEW-{luca.id}"  # Preview için geçici
            tr_date = self._get_transaction_date(yil, ay)
            
            # Transaction lines
            lines = []
            
            # ---------- BORÇ (DEBIT) KAYITLARI ----------
            
            # Maliyet hesabı ID (cost_center_id'ye göre)
            maliyet_acc_id = 5556 if vars['tr_cc_id'] == 31 else 5535
            
            # Net Ödenen
            if vars['lc_n_odenen'] > 0:
                lines.append({
                    "account_code": self._get_account_code(maliyet_acc_id),
                    "description": "Net Ödenen",
                    "debit": float(vars['lc_n_odenen']),
                    "credit": 0
                })
            
            # İcra Kesintisi
            if vars['lc_icra'] > 0:
                lines.append({
                    "account_code": self._get_account_code(maliyet_acc_id),
                    "description": "İcra Kesintisi",
                    "debit": float(vars['lc_icra']),
                    "credit": 0
                })
            
            # BES Kesintisi
            if vars['lc_oto_kat_bes'] > 0:
                lines.append({
                    "account_code": self._get_account_code(maliyet_acc_id),
                    "description": "Bes Kesintisi",
                    "debit": float(vars['lc_oto_kat_bes']),
                    "credit": 0
                })
            
            # Avans Kesintisi
            if vars['lc_avans'] > 0:
                lines.append({
                    "account_code": self._get_account_code(maliyet_acc_id),
                    "description": "Avans Kesintisi",
                    "debit": float(vars['lc_avans']),
                    "credit": 0
                })
            
            # Gelir Vergisi
            if vars['lc_gel_ver'] > 0:
                lines.append({
                    "account_code": self._get_account_code(maliyet_acc_id),
                    "description": "Gelir Vergisi",
                    "debit": float(vars['lc_gel_ver']),
                    "credit": 0
                })
            
            # Damga Vergisi
            if vars['lc_damga_v'] > 0:
                lines.append({
                    "account_code": self._get_account_code(maliyet_acc_id),
                    "description": "Damga Vergisi",
                    "debit": float(vars['lc_damga_v']),
                    "credit": 0
                })
            
            # SSK İşçi Payı
            if vars['lc_ssk_isci'] > 0:
                lines.append({
                    "account_code": self._get_account_code(maliyet_acc_id),
                    "description": "Ssk İşçi Payı",
                    "debit": float(vars['lc_ssk_isci']),
                    "credit": 0
                })
            
            # İşsizlik Sigortası İşçi Payı
            if vars['lc_iss_p_isci'] > 0:
                lines.append({
                    "account_code": self._get_account_code(maliyet_acc_id),
                    "description": "İşsizlik Sigortası İşçi Payı",
                    "debit": float(vars['lc_iss_p_isci']),
                    "credit": 0
                })
            
            # SSK İşveren Payı
            if vars['lc_ssk_isveren'] > 0:
                lines.append({
                    "account_code": self._get_account_code(maliyet_acc_id),
                    "description": "Ssk İşveren Payı",
                    "debit": float(vars['lc_ssk_isveren']),
                    "credit": 0
                })
            
            # İşsizlik Sigortası İşveren Payı
            if vars['lc_iss_p_isveren'] > 0:
                lines.append({
                    "account_code": self._get_account_code(maliyet_acc_id),
                    "description": "İşsizlik Sigortası İşveren Payı",
                    "debit": float(vars['lc_iss_p_isveren']),
                    "credit": 0
                })
            
            # Personel hesabına BES
            pe_acc_id = vars['tr_per_acc_id']
            if vars['lc_oto_kat_bes'] > 0 and pe_acc_id:
                lines.append({
                    "account_code": self._get_account_code(pe_acc_id),
                    "description": "Bes Kesintisi",
                    "debit": float(vars['lc_oto_kat_bes']),
                    "credit": 0
                })
            
            # Personel hesabına İcra
            if vars['lc_icra'] > 0 and pe_acc_id:
                lines.append({
                    "account_code": self._get_account_code(pe_acc_id),
                    "description": "İcra Kesintisi",
                    "debit": float(vars['lc_icra']),
                    "credit": 0
                })
            
            # ---------- ALACAK (CREDIT) KAYITLARI ----------
            
            # Personel Net Kazanç
            net_kazanc = vars['lc_n_odenen'] + vars['lc_oto_kat_bes'] + vars['lc_icra'] + vars['lc_avans']
            if net_kazanc > 0 and pe_acc_id:
                lines.append({
                    "account_code": self._get_account_code(pe_acc_id),
                    "description": "Net Kazanç",
                    "debit": 0,
                    "credit": float(net_kazanc)
                })
            
            # SGK İşçi Primi
            if vars['lc_ssk_isci'] > 0:
                lines.append({
                    "account_code": self._get_account_code(self.ACCOUNT_IDS['sgk_isci_prim_acc_id']),
                    "description": "Ssk Ödenecek İşçi Payı",
                    "debit": 0,
                    "credit": float(vars['lc_ssk_isci'])
                })
            
            # SGK İşveren Primi (teşvik düşülmüş)
            od_ssk_isveren = vars['lc_ssk_isveren'] - vars['lc_ssk_tesviki']
            if od_ssk_isveren > 0:
                lines.append({
                    "account_code": self._get_account_code(self.ACCOUNT_IDS['sgk_isveren_prim_acc_id']),
                    "description": "Ssk Ödenecek İşveren Payı",
                    "debit": 0,
                    "credit": float(od_ssk_isveren)
                })
            
            # İşçi İşsizlik Sigortası
            if vars['lc_iss_p_isci'] > 0:
                lines.append({
                    "account_code": self._get_account_code(self.ACCOUNT_IDS['sgk_isci_isz_acc_id']),
                    "description": "İşçi İşsizlik Sigortası Payı",
                    "debit": 0,
                    "credit": float(vars['lc_iss_p_isci'])
                })
            
            # İşveren İşsizlik Sigortası
            if vars['lc_iss_p_isveren'] > 0:
                lines.append({
                    "account_code": self._get_account_code(self.ACCOUNT_IDS['sgk_isveren_isz_acc_id']),
                    "description": "İşveren İşsizlik sigortası Payı",
                    "debit": 0,
                    "credit": float(vars['lc_iss_p_isveren'])
                })
            
            # Damga Vergisi
            if vars['lc_damga_v'] > 0:
                lines.append({
                    "account_code": self._get_account_code(self.ACCOUNT_IDS['d_vergi_acc_id']),
                    "description": "Damga Vergisi",
                    "debit": 0,
                    "credit": float(vars['lc_damga_v'])
                })
            
            # Gelir Vergisi
            if vars['lc_gel_ver'] > 0:
                lines.append({
                    "account_code": self._get_account_code(self.ACCOUNT_IDS['g_vergi_acc_id']),
                    "description": "Gelir Vergisi",
                    "debit": 0,
                    "credit": float(vars['lc_gel_ver'])
                })
            
            # Hazine Katkı Payı (SSK Teşviki)
            if vars['lc_ssk_tesviki'] > 0:
                lines.append({
                    "account_code": self._get_account_code(self.ACCOUNT_IDS['haz_kat_payi_acc_id']),
                    "description": "Hazine Katkı Payı",
                    "debit": 0,
                    "credit": float(vars['lc_ssk_tesviki'])
                })
            
            # BES Kesintileri
            if vars['lc_oto_kat_bes'] > 0:
                lines.append({
                    "account_code": self._get_account_code(self.ACCOUNT_IDS['bes_kesinti_acc_id']),
                    "description": "Bes Kesintileri",
                    "debit": 0,
                    "credit": float(vars['lc_oto_kat_bes'])
                })
            
            # İcra Kesintileri
            if vars['lc_icra'] > 0:
                lines.append({
                    "account_code": self._get_account_code(self.ACCOUNT_IDS['icra_kesinti_acc_id']),
                    "description": "İcra Kesintileri",
                    "debit": 0,
                    "credit": float(vars['lc_icra'])
                })
            
            # Toplamları hesapla
            total_debit = sum(line['debit'] for line in lines)
            total_credit = sum(line['credit'] for line in lines)
            
            # Eğer hiç satır yoksa bu kaydı gösterme
            if not lines:
                return None
            
            donem = f"{yil}-{ay:02d}"
            
            # Cost Center name
            cost_center_name = "-"
            cost_center_id = vars.get('tr_cc_id')
            if cost_center_id:
                cost_center = self.db.query(CostCenter).filter(CostCenter.id == cost_center_id).first()
                if cost_center:
                    cost_center_name = cost_center.name
            
            # Gerçek transaction bilgilerini kontrol et (eğer varsa)
            payroll_calc = self.db.query(PayrollCalculation).filter(
                PayrollCalculation.luca_bordro_id == luca.id,
                PayrollCalculation.yil == yil,
                PayrollCalculation.ay == ay
            ).first()
            
            existing_transaction_id = None
            existing_fis_no = None
            if payroll_calc and payroll_calc.transaction_id:
                existing_transaction_id = payroll_calc.transaction_id
                existing_fis_no = payroll_calc.fis_no
                tr_no = existing_fis_no or tr_no  # Gerçek fiş numarasını göster
            
            return {
                "luca_bordro_id": luca.id,
                "bolum": vars.get('tr_bolum', '-'),
                "transaction_number": tr_no,
                "transaction_id": existing_transaction_id,  # Gerçek transaction_id
                "transaction_date": str(tr_date),
                "description": vars.get('tr_des_text', ''),
                "accounting_period": donem,
                "cost_center_id": cost_center_id,
                "cost_center_name": cost_center_name,
                "personnel_id": personnel.id,
                "document_type_id": 1,  # MAAŞ BORDROSU
                "document_type_name": "MAAŞ BORDROSU",
                "lines": lines,
                "total_debit": round(total_debit, 2),
                "total_credit": round(total_credit, 2),
                "balanced": abs(total_debit - total_credit) < 0.01
            }
            
        except Exception as e:
            import traceback
            print(f"❌ RESMİ KAYIT PREVIEW ERROR for luca_id={luca.id}:\n{traceback.format_exc()}")
            return None
    
    def _save_resmi_kayit(
        self, 
        luca: LucaBordro, 
        personnel: Personnel,
        yil: int,
        ay: int
    ) -> Optional[Transaction]:
        """RESMİ KAYIT transaction'ını database'e kaydeder"""
        try:
            vars = self._get_variables(luca, personnel, yil, ay)
            
            # Önce satır olup olmayacağını kontrol et
            maliyet_acc_id = 5556 if vars['tr_cc_id'] == 31 else 5535
            pe_acc_id = vars['tr_per_acc_id']
            
            # Satır sayısını hesapla
            line_count = 0
            if vars['lc_n_odenen'] > 0 and maliyet_acc_id: line_count += 1
            if vars['lc_icra'] > 0 and maliyet_acc_id: line_count += 1
            if vars['lc_oto_kat_bes'] > 0 and maliyet_acc_id: line_count += 1
            if vars['lc_avans'] > 0 and maliyet_acc_id: line_count += 1
            if vars['lc_gel_ver'] > 0 and maliyet_acc_id: line_count += 1
            if vars['lc_damga_v'] > 0 and maliyet_acc_id: line_count += 1
            if vars['lc_ssk_isci'] > 0 and maliyet_acc_id: line_count += 1
            if vars['lc_iss_p_isci'] > 0 and maliyet_acc_id: line_count += 1
            if vars['lc_ssk_isveren'] > 0 and maliyet_acc_id: line_count += 1
            if vars['lc_iss_p_isveren'] > 0 and maliyet_acc_id: line_count += 1
            if vars['lc_oto_kat_bes'] > 0 and pe_acc_id: line_count += 1
            if vars['lc_icra'] > 0 and pe_acc_id: line_count += 1
            
            net_kazanc = vars['lc_n_odenen'] + vars['lc_oto_kat_bes'] + vars['lc_icra'] + vars['lc_avans']
            if net_kazanc > 0 and pe_acc_id: line_count += 1
            if vars['lc_ssk_isci'] > 0: line_count += 1
            
            od_ssk_isveren = vars['lc_ssk_isveren'] - vars['lc_ssk_tesviki']
            if od_ssk_isveren > 0: line_count += 1
            if vars['lc_iss_p_isci'] > 0: line_count += 1
            if vars['lc_iss_p_isveren'] > 0: line_count += 1
            if vars['lc_damga_v'] > 0: line_count += 1
            if vars['lc_gel_ver'] > 0: line_count += 1
            if vars['lc_ssk_tesviki'] > 0: line_count += 1
            if vars['lc_oto_kat_bes'] > 0: line_count += 1
            if vars['lc_icra'] > 0: line_count += 1
            
            # Eğer hiç satır olmayacaksa transaction oluşturma
            if line_count == 0:
                print(f"⚠️ RESMİ KAYIT: Hiç satır olmayacak, transaction oluşturulmadı (luca_id={luca.id})")
                return None
            
            # Transaction oluştur
            tr_no = get_next_transaction_number(self.db)
            tr_date = self._get_transaction_date(yil, ay)
            donem = f"{yil}-{ay:02d}"
            
            # Document Type ID'sini al
            doc_type = self.db.query(DocumentType).filter(
                DocumentType.code == 'MAAS_BORDROSU'
            ).first()
            doc_type_id = doc_type.id if doc_type else None
            
            transaction = Transaction(
                transaction_number=tr_no,
                transaction_date=tr_date,
                accounting_period=donem,
                cost_center_id=vars['tr_cc_id'],
                personnel_id=personnel.id,
                description=vars.get('tr_des_text', ''),
                document_type_id=doc_type_id,
                document_number=f"BORDRO {donem}",
                related_invoice_number=None,
                draft=False  # Resmi kayıt
            )
            self.db.add(transaction)
            self.db.flush()  # ID almak için
            
            tr_id = transaction.id
            
            # Transaction Lines - BORÇ
            self._add_line_if_positive(tr_id, maliyet_acc_id, "Net Ödenen", vars['lc_n_odenen'], 0)
            self._add_line_if_positive(tr_id, maliyet_acc_id, "İcra Kesintisi", vars['lc_icra'], 0)
            self._add_line_if_positive(tr_id, maliyet_acc_id, "Bes Kesintisi", vars['lc_oto_kat_bes'], 0)
            self._add_line_if_positive(tr_id, maliyet_acc_id, "Avans Kesintisi", vars['lc_avans'], 0)
            self._add_line_if_positive(tr_id, maliyet_acc_id, "Gelir Vergisi", vars['lc_gel_ver'], 0)
            self._add_line_if_positive(tr_id, maliyet_acc_id, "Damga Vergisi", vars['lc_damga_v'], 0)
            self._add_line_if_positive(tr_id, maliyet_acc_id, "Ssk İşçi Payı", vars['lc_ssk_isci'], 0)
            self._add_line_if_positive(tr_id, maliyet_acc_id, "İşsizlik Sigortası İşçi Payı", vars['lc_iss_p_isci'], 0)
            self._add_line_if_positive(tr_id, maliyet_acc_id, "Ssk İşveren Payı", vars['lc_ssk_isveren'], 0)
            self._add_line_if_positive(tr_id, maliyet_acc_id, "İşsizlik Sigortası İşveren Payı", vars['lc_iss_p_isveren'], 0)
            
            if pe_acc_id:
                self._add_line_if_positive(tr_id, pe_acc_id, "Bes Kesintisi", vars['lc_oto_kat_bes'], 0)
                self._add_line_if_positive(tr_id, pe_acc_id, "İcra Kesintisi", vars['lc_icra'], 0)
            
            # Transaction Lines - ALACAK
            net_kazanc = vars['lc_n_odenen'] + vars['lc_oto_kat_bes'] + vars['lc_icra'] + vars['lc_avans']
            if pe_acc_id:
                self._add_line_if_positive(tr_id, pe_acc_id, "Net Kazanç", 0, net_kazanc)
            
            self._add_line_if_positive(tr_id, self.ACCOUNT_IDS['sgk_isci_prim_acc_id'], "Ssk Ödenecek İşçi Payı", 0, vars['lc_ssk_isci'])
            
            od_ssk_isveren = vars['lc_ssk_isveren'] - vars['lc_ssk_tesviki']
            self._add_line_if_positive(tr_id, self.ACCOUNT_IDS['sgk_isveren_prim_acc_id'], "Ssk Ödenecek İşveren Payı", 0, od_ssk_isveren)
            
            self._add_line_if_positive(tr_id, self.ACCOUNT_IDS['sgk_isci_isz_acc_id'], "İşçi İşsizlik Sigortası Payı", 0, vars['lc_iss_p_isci'])
            self._add_line_if_positive(tr_id, self.ACCOUNT_IDS['sgk_isveren_isz_acc_id'], "İşveren İşsizlik sigortası Payı", 0, vars['lc_iss_p_isveren'])
            self._add_line_if_positive(tr_id, self.ACCOUNT_IDS['d_vergi_acc_id'], "Damga Vergisi", 0, vars['lc_damga_v'])
            self._add_line_if_positive(tr_id, self.ACCOUNT_IDS['g_vergi_acc_id'], "Gelir Vergisi", 0, vars['lc_gel_ver'])
            self._add_line_if_positive(tr_id, self.ACCOUNT_IDS['haz_kat_payi_acc_id'], "Hazine Katkı Payı", 0, vars['lc_ssk_tesviki'])
            self._add_line_if_positive(tr_id, self.ACCOUNT_IDS['bes_kesinti_acc_id'], "Bes Kesintileri", 0, vars['lc_oto_kat_bes'])
            self._add_line_if_positive(tr_id, self.ACCOUNT_IDS['icra_kesinti_acc_id'], "İcra Kesintileri", 0, vars['lc_icra'])
            
            return transaction
            
        except Exception as e:
            import traceback
            print(f"❌ RESMİ KAYIT SAVE ERROR for luca_id={luca.id}:\n{traceback.format_exc()}")
            return None
    
    # ========================================================================
    # HELPER METHODS - TASLAK KAYIT
    # ========================================================================
    
    def _create_taslak_kayit_preview_combined(
        self, 
        luca_bordros: List[LucaBordro], 
        personnel: Personnel,
        yil: int,
        ay: int
    ) -> Optional[Dict[str, Any]]:
        """TASLAK KAYIT önizlemesi - TÜM bordroları birleştirip TEK KAYIT oluşturur"""
        try:
            print(f"🔍 TASLAK KAYIT - {personnel.ad} {personnel.soyad} için kontrol ediliyor...")
            
            # Draft contract kontrolü
            draft_contract = self.db.query(PersonnelDraftContract).filter(
                PersonnelDraftContract.personnel_id == personnel.id,
                PersonnelDraftContract.is_active == 1
            ).first()
            
            if not draft_contract:
                print(f"❌ Draft contract YOK - taslak kayıt oluşturulmayacak")
                return None
            
            print(f"✅ Draft contract bulundu: ID={draft_contract.id}, Cost Center={draft_contract.cost_center_id}")
            
            donem = f"{yil}-{ay:02d}"
            
            # Cost Center
            cost_center = None
            if draft_contract.cost_center_id:
                cost_center = self.db.query(CostCenter).filter(
                    CostCenter.id == draft_contract.cost_center_id
                ).first()
            
            # Puantaj Grid - try multiple contract sources
            ppg = None
            contract_ids_to_try = []
            
            # 1. Try draft contract ID first
            contract_ids_to_try.append(draft_contract.id)
            
            # 2. Try contract IDs from luca_bordros
            for lb in luca_bordros:
                if lb.contract_id and lb.contract_id not in contract_ids_to_try:
                    contract_ids_to_try.append(lb.contract_id)
            
            # 3. Try personnel's active contract
            # Puantaj ara (sadece personnel_id + donem)
            ppg = self.db.query(PersonnelPuantajGrid).filter(
                PersonnelPuantajGrid.personnel_id == personnel.id,
                PersonnelPuantajGrid.donem == donem
            ).first()
            
            if ppg:
                print(f"✅ Puantaj bulundu: personnel_id={personnel.id}, donem={donem}, ID={ppg.id}, Normal Çalışma={ppg.normal_calismasi}")
            else:
                print(f"❌ Puantaj Grid YOK - personnel_id={personnel.id}, donem={donem}")
                return None  # Puantaj yoksa taslak kayıt yok
            
            # Tüm Luca bordro değerlerini topla
            total_n_odenen = sum(Decimal(str(lb.n_odenen or 0)) for lb in luca_bordros)
            total_oto_kat_bes = sum(Decimal(str(lb.oto_kat_bes or 0)) for lb in luca_bordros)
            total_icra = sum(Decimal(str(lb.icra or 0)) for lb in luca_bordros)
            total_avans = sum(Decimal(str(lb.avans or 0)) for lb in luca_bordros)
            
            bordro_net_toplami = total_n_odenen + total_oto_kat_bes + total_icra + total_avans
            
            # PayrollCalculation'dan TÜM TASLAK kayıtları al ve topla
            # (Her luca_bordro için ayrı PayrollCalculation kaydı olabilir ama taslak yevmiye tek olmalı)
            payroll_calcs = self.db.query(PayrollCalculation).filter(
                PayrollCalculation.personnel_id == personnel.id,
                PayrollCalculation.yil == yil,
                PayrollCalculation.ay == ay,
                PayrollCalculation.yevmiye_tipi == "TASLAK"
            ).all()
            
            if not payroll_calcs:
                print(f"❌ PayrollCalculation TASLAK kaydı YOK - personnel_id={personnel.id}, {yil}-{ay}")
                return None
            
            # TÜM TASLAK kayıtlardan değerleri topla
            # Her luca_bordro için ayrı TASLAK kaydı var, hepsini toplamalıyız
            total_maas2 = sum(Decimal(str(pc.maas2_toplam or 0)) for pc in payroll_calcs)
            
            # Elden kalan: TOPLAM maas2 - Luca toplam
            elden_kalan = total_maas2 - bordro_net_toplami
            
            # Yuvarlama (100'e)
            elden_kalan_yuvarlanmis = (elden_kalan / 100).quantize(Decimal('1'), rounding='ROUND_HALF_UP') * 100
            elden_yuvarlamasi = elden_kalan_yuvarlanmis - elden_kalan
            
            net_maas_tutar = total_maas2
            
            # DEBUG
            print(f"🔍 TASLAK KAYIT DEBUG - {personnel.ad} {personnel.soyad}:")
            print(f"  TASLAK kayıt sayısı: {len(payroll_calcs)}")
            print(f"  PayrollCalculation TOPLAM:")
            print(f"    total_maas2: {total_maas2}")
            print(f"  Luca Bordro Toplamı:")
            print(f"    n_odenen: {total_n_odenen}")
            print(f"    Toplam: {bordro_net_toplami}")
            print(f"  Elden Ödeme:")
            print(f"    elden_kalan (ham): {elden_kalan}")
            print(f"    elden_kalan_yuvarlanmis: {elden_kalan_yuvarlanmis}")
            print(f"    elden_yuvarlamasi: {elden_yuvarlamasi}")
            
            # Yevmiye satırları
            lines = []
            maliyet_acc_id = 5556 if draft_contract.cost_center_id == 31 else 5535
            pe_acc_id = personnel.accounts_id
            
            # Elden Yuvarlama
            # Yuvarlama mantığı:
            # - elden_yuvarlama POZITIF (yukarı yuvarlandı): Personele ALACAK yaz (fazla ödeyeceğiz)
            # - elden_yuvarlama NEGATİF (aşağı yuvarlandı): Personele BORÇ yaz (az ödeyeceğiz)
            if abs(elden_yuvarlamasi) > 0.01 and pe_acc_id:
                if elden_yuvarlamasi > 0:
                    # Yukarı yuvarlandı: Personele ALACAK
                    lines.append({
                        "account_code": self._get_account_code(pe_acc_id),
                        "account_name": self._get_account_name(pe_acc_id),
                        "description": "Elden Yuvarlama",
                        "debit": 0,
                        "credit": float(elden_yuvarlamasi)
                    })
                else:
                    # Aşağı yuvarlandı: Personele BORÇ
                    lines.append({
                        "account_code": self._get_account_code(pe_acc_id),
                        "account_name": self._get_account_name(pe_acc_id),
                        "description": "Elden Yuvarlama",
                        "debit": float(abs(elden_yuvarlamasi)),
                        "credit": 0
                    })
            
            # Elden Ödenen
            if elden_kalan_yuvarlanmis > 0:
                lines.append({
                    "account_code": self._get_account_code(maliyet_acc_id),
                    "account_name": self._get_account_name(maliyet_acc_id),
                    "description": "Elden Ödenen",
                    "debit": float(elden_kalan_yuvarlanmis),
                    "credit": 0
                })
            
            # Kalan Ödemesi
            if elden_kalan > 0 and pe_acc_id:
                lines.append({
                    "account_code": self._get_account_code(pe_acc_id),
                    "account_name": self._get_account_name(pe_acc_id),
                    "description": "Kalan Ödemesi",
                    "debit": 0,
                    "credit": float(elden_kalan)
                })
            
            total_debit = sum(line['debit'] for line in lines) if lines else 0
            total_credit = sum(line['credit'] for line in lines) if lines else 0
            
            # Gerçek transaction bilgilerini kontrol et (eğer varsa)
            # Taslak kayıt için herhangi bir PayrollCalculation'dan bakabiliriz
            payroll_calc = self.db.query(PayrollCalculation).filter(
                PayrollCalculation.personnel_id == personnel.id,
                PayrollCalculation.yil == yil,
                PayrollCalculation.ay == ay,
                PayrollCalculation.yevmiye_tipi == "TASLAK"
            ).first()
            
            existing_transaction_id = None
            existing_fis_no = None
            tr_no = f"PREVIEW-TASLAK-{personnel.id}"
            
            if payroll_calc and payroll_calc.transaction_id:
                existing_transaction_id = payroll_calc.transaction_id
                existing_fis_no = payroll_calc.fis_no
                tr_no = existing_fis_no or tr_no  # Gerçek fiş numarasını göster
            
            return {
                "draft_contract_id": draft_contract.id,
                "cost_center_name": cost_center.name if cost_center else "-",
                "transaction_number": tr_no,
                "transaction_id": existing_transaction_id,  # Gerçek transaction_id
                "transaction_date": str(self._get_transaction_date(yil, ay)),
                "description": f"{donem} {personnel.ad} {personnel.soyad} Taslak Kayıt (Elden Ödeme)",
                "accounting_period": donem,
                "cost_center_id": draft_contract.cost_center_id,
                "cost_center_name": cost_center.name if cost_center else "-",
                "personnel_id": personnel.id,
                "document_type_id": 1,  # MAAŞ BORDROSU
                "document_type_name": "MAAŞ BORDROSU",
                "lines": lines,
                "total_debit": round(total_debit, 2),
                "total_credit": round(total_credit, 2),
                "balanced": abs(total_debit - total_credit) < 0.01
            }
            
        except Exception as e:
            import traceback
            print(f"❌ TASLAK KAYIT PREVIEW ERROR:\n{traceback.format_exc()}")
            return None
    
    def _save_taslak_kayit_combined(
        self, 
        luca_bordros: List[LucaBordro], 
        personnel: Personnel,
        yil: int,
        ay: int
    ) -> Optional[Transaction]:
        """TASLAK KAYIT transaction'ını database'e kaydeder - TÜM bordroları birleştirir"""
        try:
            print(f"💾 TASLAK KAYIT SAVE - {personnel.ad} {personnel.soyad} için kaydediliyor...")
            
            # Draft contract kontrolü
            draft_contract = self.db.query(PersonnelDraftContract).filter(
                PersonnelDraftContract.personnel_id == personnel.id,
                PersonnelDraftContract.is_active == 1
            ).first()
            
            if not draft_contract:
                print(f"❌ Draft contract YOK - taslak kayıt oluşturulmayacak")
                return None
            
            print(f"✅ Draft contract bulundu: ID={draft_contract.id}, Cost Center={draft_contract.cost_center_id}")
            
            donem = f"{yil}-{ay:02d}"
            
            # Cost Center
            cost_center = None
            if draft_contract.cost_center_id:
                cost_center = self.db.query(CostCenter).filter(
                    CostCenter.id == draft_contract.cost_center_id
                ).first()
            
            # Puantaj Grid - try multiple contract sources
            ppg = None
            contract_ids_to_try = []
            
            # 1. Try draft contract ID first
            contract_ids_to_try.append(draft_contract.id)
            
            # 2. Try contract IDs from luca_bordros
            for lb in luca_bordros:
                if lb.contract_id and lb.contract_id not in contract_ids_to_try:
                    contract_ids_to_try.append(lb.contract_id)
            
            # 3. Try personnel's latest contract (aktif/pasif farketmez)
            active_contract = self.db.query(PersonnelContract).filter(
                PersonnelContract.personnel_id == personnel.id
            ).order_by(PersonnelContract.ise_giris_tarihi.desc()).first()
            
            # Puantaj ara (sadece personnel_id + donem)
            ppg = self.db.query(PersonnelPuantajGrid).filter(
                PersonnelPuantajGrid.personnel_id == personnel.id,
                PersonnelPuantajGrid.donem == donem
            ).first()
            
            if ppg:
                print(f"✅ Puantaj bulundu: personnel_id={personnel.id}, donem={donem}, ID={ppg.id}")
            else:
                print(f"⚠️ Puantaj Grid YOK - personnel_id={personnel.id}, donem={donem}")
                print(f"⏭️ TASLAK KAYIT ATLANACAK - Puantaj bekliyor durumunda")
                return None
            
            # Tüm Luca bordro değerlerini topla
            total_n_odenen = sum(Decimal(str(lb.n_odenen or 0)) for lb in luca_bordros)
            total_oto_kat_bes = sum(Decimal(str(lb.oto_kat_bes or 0)) for lb in luca_bordros)
            total_icra = sum(Decimal(str(lb.icra or 0)) for lb in luca_bordros)
            total_avans = sum(Decimal(str(lb.avans or 0)) for lb in luca_bordros)
            
            bordro_net_toplami = total_n_odenen + total_oto_kat_bes + total_icra + total_avans
            
            # PayrollCalculation'dan TÜM TASLAK kayıtları al ve topla
            # (Her luca_bordro için ayrı PayrollCalculation kaydı olabilir ama taslak yevmiye tek olmalı)
            payroll_calcs = self.db.query(PayrollCalculation).filter(
                PayrollCalculation.personnel_id == personnel.id,
                PayrollCalculation.yil == yil,
                PayrollCalculation.ay == ay,
                PayrollCalculation.yevmiye_tipi == "TASLAK"
            ).all()
            
            if not payroll_calcs:
                print(f"❌ PayrollCalculation TASLAK kaydı YOK - personnel_id={personnel.id}, {yil}-{ay}")
                return None
            
            # TÜM TASLAK kayıtlardan değerleri topla
            # Her luca_bordro için ayrı TASLAK kaydı var, hepsini toplamalıyız
            total_maas2 = sum(Decimal(str(pc.maas2_toplam or 0)) for pc in payroll_calcs)
            
            # Elden kalan: TOPLAM maas2 - Luca toplam
            elden_kalan = total_maas2 - bordro_net_toplami
            
            # Yuvarlama (100'e)
            elden_kalan_yuvarlanmis = (elden_kalan / 100).quantize(Decimal('1'), rounding='ROUND_HALF_UP') * 100
            elden_yuvarlamasi = elden_kalan_yuvarlanmis - elden_kalan
            
            net_maas_tutar = total_maas2
            
            print(f"📊 TASLAK KAYIT SAVE - {personnel.ad} {personnel.soyad}:")
            print(f"  TASLAK kayıt sayısı: {len(payroll_calcs)}")
            print(f"  Toplam maas2: {total_maas2}")
            print(f"  Luca toplam: {bordro_net_toplami}")
            print(f"  Elden kalan: {elden_kalan}")
            print(f"  Elden yuvarlanmış: {elden_kalan_yuvarlanmis}")
            print(f"  Yuvarlama: {elden_yuvarlamasi}")
            
            # Minimum tutar kontrolü
            if abs(elden_kalan_yuvarlanmis) < 0.01:
                print(f"⚠️ TASLAK KAYIT: Elden kalan çok düşük ({elden_kalan_yuvarlanmis}), transaction oluşturulmadı")
                return None
            
            # Önce satır olup olmayacağını kontrol et
            maliyet_acc_id = 5556 if draft_contract.cost_center_id == 31 else 5535
            pe_acc_id = personnel.accounts_id
            
            line_count = 0
            if abs(elden_yuvarlamasi) > 0.01 and pe_acc_id: line_count += 1
            if elden_kalan_yuvarlanmis > 0 and maliyet_acc_id: line_count += 1
            if elden_kalan > 0 and pe_acc_id: line_count += 1
            
            # Eğer hiç satır olmayacaksa transaction oluşturma
            if line_count == 0:
                print(f"⚠️ TASLAK KAYIT: Hiç satır olmayacak, transaction oluşturulmadı")
                return None
            
            # Transaction oluştur
            tr_no = get_next_transaction_number(self.db)
            tr_date = self._get_transaction_date(yil, ay)
            
            # Document Type ID'sini al
            doc_type = self.db.query(DocumentType).filter(
                DocumentType.code == 'MAAS_BORDROSU'
            ).first()
            doc_type_id = doc_type.id if doc_type else None
            
            transaction = Transaction(
                transaction_number=tr_no,
                transaction_date=tr_date,
                accounting_period=donem,
                cost_center_id=draft_contract.cost_center_id,
                personnel_id=personnel.id,
                description=f"{donem} {personnel.ad} {personnel.soyad} - Taslak Kayıt (Elden Ödeme)",
                document_type_id=doc_type_id,
                document_number=f"BORDRO {donem} TASLAK",
                related_invoice_number=None,
                draft=True  # Taslak kayıt
            )
            self.db.add(transaction)
            self.db.flush()
            
            tr_id = transaction.id
            
            # Elden Yuvarlama
            # Yuvarlama mantığı:
            # - elden_yuvarlama POZİTİF (yukarı yuvarlandı): Personele ALACAK yaz (fazla ödeyeceğiz)
            # - elden_yuvarlama NEGATİF (aşağı yuvarlandı): Personele BORÇ yaz (az ödeyeceğiz)
            if abs(elden_yuvarlamasi) > 0.01 and pe_acc_id:
                if elden_yuvarlamasi > 0:
                    # Yukarı yuvarlandı: Personele ALACAK
                    self._add_line(tr_id, pe_acc_id, "Elden Yuvarlama", 0, elden_yuvarlamasi)
                else:
                    # Aşağı yuvarlandı: Personele BORÇ
                    self._add_line(tr_id, pe_acc_id, "Elden Yuvarlama", abs(elden_yuvarlamasi), 0)
            
            # Elden Ödenen
            if elden_kalan_yuvarlanmis > 0:
                self._add_line(tr_id, maliyet_acc_id, "Elden Ödenen", elden_kalan_yuvarlanmis, 0)
            
            # Kalan Ödemesi
            if elden_kalan > 0 and pe_acc_id:
                self._add_line(tr_id, pe_acc_id, "Kalan Ödemesi", 0, elden_kalan)
            
            print(f"✅ TASLAK KAYIT SAVED: Transaction ID={tr_id}, Number={tr_no}")
            return transaction
            
        except Exception as e:
            import traceback
            print(f"❌ TASLAK KAYIT SAVE ERROR:\n{traceback.format_exc()}")
            return None
    
    def _save_taslak_kayit(
        self, 
        luca: LucaBordro, 
        personnel: Personnel,
        yil: int,
        ay: int
    ) -> Optional[Transaction]:
        """TASLAK KAYIT transaction'ını database'e kaydeder"""
        try:
            vars = self._get_variables(luca, personnel, yil, ay)
            
            if not vars.get('has_draft_contract'):
                return None
            
            tr_elden_kalan = vars.get('tr_elden_kalan', 0)
            tr_elden_kalan_yuvarlanmis = vars.get('tr_elden_kalan_yuvarlanmis', 0)
            tr_elden_yuvarlamasi = vars.get('tr_elden_yuvarlamasi', 0)
            
            if abs(tr_elden_kalan_yuvarlanmis) < 0.01:
                return None
            
            # Transaction oluştur
            tr_no = get_next_transaction_number(self.db)
            tr_date = self._get_transaction_date(yil, ay)
            donem = f"{yil}-{ay:02d}"
            
            # Document Type ID'sini al
            doc_type = self.db.query(DocumentType).filter(
                DocumentType.code == 'MAAS_BORDROSU'
            ).first()
            doc_type_id = doc_type.id if doc_type else None
            
            transaction = Transaction(
                transaction_number=tr_no,
                transaction_date=tr_date,
                accounting_period=donem,
                cost_center_id=vars['tr_cc_id'],
                personnel_id=personnel.id,
                description=f"{vars.get('tr_des_text', '')} - Taslak Kayıt (Elden Ödeme)",
                document_type_id=doc_type_id,
                document_number=f"BORDRO {donem} TASLAK",
                related_invoice_number=None,
                draft=True  # Taslak kayıt
            )
            self.db.add(transaction)
            self.db.flush()
            
            tr_id = transaction.id
            maliyet_acc_id = 5556 if vars['tr_cc_id'] == 31 else 5535
            pe_acc_id = vars['tr_per_acc_id']
            
            # Elden Yuvarlama
            if abs(tr_elden_yuvarlamasi) > 0.01 and pe_acc_id:
                if tr_elden_yuvarlamasi > 0:
                    self._add_line(tr_id, pe_acc_id, "Elden Yuvarlama", tr_elden_yuvarlamasi, 0)
                else:
                    self._add_line(tr_id, pe_acc_id, "Elden Yuvarlama", 0, abs(tr_elden_yuvarlamasi))
            
            # Elden Ödenen
            if tr_elden_kalan_yuvarlanmis > 0:
                self._add_line(tr_id, maliyet_acc_id, "Elden Ödenen", tr_elden_kalan_yuvarlanmis, 0)
            
            # Kalan Ödemesi
            if tr_elden_kalan > 0 and pe_acc_id:
                self._add_line(tr_id, pe_acc_id, "Kalan Ödemesi", 0, tr_elden_kalan)
            
            return transaction
            
        except Exception as e:
            import traceback
            print(f"❌ TASLAK KAYIT SAVE ERROR for luca_id={luca.id}:\n{traceback.format_exc()}")
            return None
    
    # ========================================================================
    # UTILITY METHODS
    # ========================================================================
    
    def _get_variables(self, luca: LucaBordro, personnel: Personnel, yil: int, ay: int) -> Dict[str, Any]:
        """Tüm değişkenleri toplar"""
        donem = f"{yil}-{ay:02d}"
        
        # Personnel Draft Contract (TASLAK SÖZLEŞMESİ - ucret_nevi, fm_orani, tatil_orani burada)
        draft_contract = self.db.query(PersonnelDraftContract).filter(
            PersonnelDraftContract.personnel_id == personnel.id,
            PersonnelDraftContract.is_active == 1
        ).first()
        
        # Personnel Contract (bölüm bilgisi için - luca_bordro'nun contract_id'sini kullan)
        contract = None
        if luca.contract_id:
            contract = self.db.query(PersonnelContract).filter(
                PersonnelContract.id == luca.contract_id
            ).first()
        
        # Personnel Puantaj Grid (sadece personnel_id + donem)
        ppg = self.db.query(PersonnelPuantajGrid).filter(
            PersonnelPuantajGrid.personnel_id == personnel.id,
            PersonnelPuantajGrid.donem == donem
        ).first()
        
        # Cost Center
        cost_center = None
        tr_cc_id = None
        tr_cc_name = ""
        if draft_contract and draft_contract.cost_center_id:
            cost_center = self.db.query(CostCenter).filter(
                CostCenter.id == draft_contract.cost_center_id
            ).first()
            tr_cc_id = cost_center.id if cost_center else None
            tr_cc_name = cost_center.name if cost_center else ""
        
        # Bölüm bilgisi (personnel_contract'tan)
        tr_bolum = contract.bolum if contract and contract.bolum else tr_cc_name
        
        # Basic variables
        vars = {
            # Luca Bordro
            'lc_id': luca.id,
            'lc_yil': luca.yil,
            'lc_ay': luca.ay,
            'lc_donem': donem,
            'lc_adi_soyadi': luca.adi_soyadi,
            'lc_tckn': luca.tckn,
            'lc_ssk_sicil_no': luca.ssk_sicil_no or '',
            'lc_n_odenen': Decimal(str(luca.n_odenen or 0)),
            'lc_icra': Decimal(str(luca.icra or 0)),
            'lc_oto_kat_bes': Decimal(str(luca.oto_kat_bes or 0)),
            'lc_avans': Decimal(str(luca.avans or 0)),
            'lc_gel_ver': Decimal(str(luca.gel_ver or 0)),
            'lc_damga_v': Decimal(str(luca.damga_v or 0)),
            'lc_ssk_isci': Decimal(str(luca.ssk_isci or 0)),
            'lc_iss_p_isci': Decimal(str(luca.iss_p_isci or 0)),
            'lc_ssk_isveren': Decimal(str(luca.ssk_isveren or 0)),
            'lc_iss_p_isveren': Decimal(str(luca.iss_p_isveren or 0)),
            'lc_ssk_tesviki': Decimal(str(luca.ssk_tesviki or 0)),
            
            # Personnel
            'tr_per_id': personnel.id,
            'tr_per_ad': personnel.ad,
            'tr_per_soyad': personnel.soyad,
            'tr_per_acc_id': personnel.accounts_id,
            
            # Cost Center
            'tr_cc_id': tr_cc_id,
            'tr_cc_name': tr_cc_name,
            
            # Contract
            'tr_contracts_id': draft_contract.id if draft_contract else None,
            'tr_bolum': tr_bolum,  # PersonnelContract'tan bolum bilgisi
            'tr_ucret_nevi': draft_contract.ucret_nevi if draft_contract else 'aylik',
            'tr_maas2_tutar': Decimal(str(draft_contract.net_ucret or 0)) if draft_contract else Decimal('0'),
            'tr_fm_orani': Decimal(str(draft_contract.fm_orani or 1.5)) if draft_contract else Decimal('1.5'),
            'tr_tatil_orani': Decimal(str(draft_contract.tatil_orani or 1.0)) if draft_contract else Decimal('1.0'),
            
            # Has draft contract?
            'has_draft_contract': draft_contract is not None,
            
            # Description
            'tr_des_text': f"{donem} {personnel.ad} {personnel.soyad} {tr_cc_name} bordrosu",
        }
        
        # Puantaj Grid değerleri
        if ppg:
            vars.update({
                'ppg_normal_calismasi': Decimal(str(ppg.normal_calismasi or 0)),
                'ppg_fazla_calismasi': Decimal(str(ppg.fazla_calismasi or 0)),
                'ppg_yillik_izin_gun': Decimal(str(ppg.yillik_izin_gun or 0)),
                'ppg_resmi_tatil': Decimal(str(ppg.resmi_tatil or 0)),
                'ppg_hafta_tatili': Decimal(str(ppg.hafta_tatili or 0)),
                'ppg_tatil_calismasi': Decimal(str(ppg.tatil_calismasi or 0)),
                'ppg_yol': Decimal(str(ppg.yol or 0)),
                'ppg_prim': Decimal(str(ppg.prim or 0)),
                'ppg_ikramiye': Decimal(str(ppg.ikramiye or 0)),
                'ppg_bayram': Decimal(str(ppg.bayram or 0)),
                'ppg_kira': Decimal(str(ppg.kira or 0)),
            })
            
            # Elden kalan hesaplama
            if draft_contract:
                # Günlük ücret
                ucret_nevi = vars['tr_ucret_nevi']
                maas2_tutar = vars['tr_maas2_tutar']
                
                if ucret_nevi in ['aylik', 'sabit aylik']:
                    tr_gunluk_ucret = maas2_tutar / 30
                elif ucret_nevi == 'gunluk':
                    tr_gunluk_ucret = maas2_tutar
                else:
                    tr_gunluk_ucret = Decimal('0')
                
                # Hesaplamalar
                tr_normal_calisma_tutar = tr_gunluk_ucret * vars['ppg_normal_calismasi']
                tr_fazla_calisma_tutar = (tr_gunluk_ucret / 8) * vars['ppg_fazla_calismasi'] * vars['tr_fm_orani']
                tr_tatil_tutar = tr_gunluk_ucret * (vars['ppg_resmi_tatil'] + vars['ppg_hafta_tatili'] + vars['ppg_tatil_calismasi'])
                tr_tatil_calismasi_tutar = tr_gunluk_ucret * vars['ppg_tatil_calismasi'] * vars['tr_tatil_orani']
                tr_yillik_izin_gun_tutar = tr_gunluk_ucret * vars['ppg_yillik_izin_gun']
                
                tr_net_maas_tutar = (
                    vars['ppg_yol'] + vars['ppg_prim'] + vars['ppg_ikramiye'] + 
                    vars['ppg_bayram'] + vars['ppg_kira'] + tr_normal_calisma_tutar + 
                    tr_fazla_calisma_tutar + tr_tatil_tutar + tr_tatil_calismasi_tutar + 
                    tr_yillik_izin_gun_tutar
                )
                
                tr_bordro_net_toplami = vars['lc_n_odenen'] + vars['lc_oto_kat_bes'] + vars['lc_icra'] + vars['lc_avans']
                tr_elden_kalan = tr_net_maas_tutar - tr_bordro_net_toplami
                
                # Yuvarlama (100'e)
                tr_elden_kalan_yuvarlanmis = (tr_elden_kalan / 100).quantize(Decimal('1'), rounding='ROUND_HALF_UP') * 100
                tr_elden_yuvarlamasi = tr_elden_kalan - tr_elden_kalan_yuvarlanmis
                
                vars.update({
                    'tr_gunluk_ucret': tr_gunluk_ucret,
                    'tr_net_maas_tutar': tr_net_maas_tutar,
                    'tr_bordro_net_toplami': tr_bordro_net_toplami,
                    'tr_elden_kalan': tr_elden_kalan,
                    'tr_elden_kalan_yuvarlanmis': tr_elden_kalan_yuvarlanmis,
                    'tr_elden_yuvarlamasi': tr_elden_yuvarlamasi,
                })
        else:
            # Puantaj yoksa elden kalan 0
            vars.update({
                'tr_elden_kalan': Decimal('0'),
                'tr_elden_kalan_yuvarlanmis': Decimal('0'),
                'tr_elden_yuvarlamasi': Decimal('0'),
            })
        
        return vars
    
    def _get_transaction_date(self, yil: int, ay: int) -> date:
        """Transaction tarihini döndürür (ayın son günü)"""
        last_day = monthrange(yil, ay)[1]
        return date(yil, ay, last_day)
    
    def _get_account_code(self, account_id: Optional[int]) -> str:
        """Hesap ID'den hesap kodunu çeker"""
        if not account_id:
            return "?"
        account = self.db.query(Account).filter(Account.id == account_id).first()
        return account.code if account else str(account_id)
    
    def _get_account_name(self, account_id: Optional[int]) -> str:
        """Hesap ID'den hesap adını çeker"""
        if not account_id:
            return "?"
        account = self.db.query(Account).filter(Account.id == account_id).first()
        return account.name if account else "?"
    
    def _get_contract_bolum(self, luca: LucaBordro) -> str:
        """Luca bordro kaydından contract bölümünü çeker"""
        if not luca.contract_id:
            return "-"
        contract = self.db.query(PersonnelContract).filter(
            PersonnelContract.id == luca.contract_id
        ).first()
        return contract.bolum if contract else "-"
    
    def _add_line_if_positive(
        self, 
        transaction_id: int, 
        account_id: Optional[int], 
        description: str, 
        debit: Decimal, 
        credit: Decimal
    ):
        """Pozitif tutarsa transaction line ekler"""
        if (debit > 0 or credit > 0) and account_id:
            line = TransactionLine(
                transaction_id=transaction_id,
                account_id=account_id,
                description=description,
                debit=float(debit),
                credit=float(credit)
            )
            self.db.add(line)
    
    def _add_line(
        self, 
        transaction_id: int, 
        account_id: Optional[int], 
        description: str, 
        debit: Decimal, 
        credit: Decimal
    ):
        """Transaction line ekler"""
        if account_id:
            line = TransactionLine(
                transaction_id=transaction_id,
                account_id=account_id,
                description=description,
                debit=float(debit),
                credit=float(credit)
            )
            self.db.add(line)
