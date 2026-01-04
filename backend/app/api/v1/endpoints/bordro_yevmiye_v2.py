"""
Bordro Yevmiye Generation V2 - Detaylı Sistem
Kalem kalem borç kayıtları ile yevmiye oluşturur
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.core.database import get_db
from app.models.transaction import Transaction
from app.models.transaction_line import TransactionLine
from app.models.account import Account
from app.models.payroll_calculation import PayrollCalculation
from app.models.personnel import Personnel
from app.utils.transaction_numbering import get_next_transaction_number

router = APIRouter()


class GenerateYevmiyeRequest(BaseModel):
    """Yevmiye oluşturma isteği"""
    donem: str  # "2025-11"
    personnel_ids: Optional[List[int]] = None  # Belirli personeller için (opsiyonel)
    force_regenerate: bool = False  # Mevcut yevmiyeleri sil ve yeniden oluştur


class GenerateYevmiyeResponse(BaseModel):
    """Yevmiye oluşturma yanıtı"""
    success: bool
    message: str
    donem: str
    personnel_count: int
    transaction_count: int
    total_lines: int
    total_debit: Decimal
    total_credit: Decimal
    errors: List[str] = []


def get_or_create_personnel_account(db: Session, personnel: Personnel) -> Account:
    """
    Personel için 335 hesabını bul veya oluştur
    Format: 335.{tc_no} - {ad_soyad} {tc_no}
    
    ÖNEMLİ: Artık personnel.account_id kullanıyoruz (FK ile bağlı)
    """
    # Önce personnel.account_id var mı kontrol et
    if personnel.account_id:
        account = db.query(Account).filter(Account.id == personnel.account_id).first()
        if account:
            return account
    
    # account_id yoksa veya hesap bulunamadıysa, TC ile ara
    account_code = f"335.{personnel.tckn}"
    existing = db.query(Account).filter(Account.code == account_code).first()
    
    if existing:
        # Hesap var ama personnel.account_id boşsa, bağlantıyı kur
        if not personnel.account_id:
            personnel.account_id = existing.id
            db.flush()
        return existing
    
    # Yoksa oluştur ve personnel.account_id'yi güncelle
    new_account = Account(
        code=account_code,
        name=f"{personnel.first_name} {personnel.last_name} {personnel.tckn}",
        account_type="liability",
        is_active=True
    )
    db.add(new_account)
    db.flush()
    
    personnel.account_id = new_account.id
    db.flush()
    
    return new_account


def get_account_by_code(db: Session, code: str) -> Account:
    """Hesap kodunu bul"""
    account = db.query(Account).filter(Account.code == code).first()
    if not account:
        raise ValueError(f"Hesap kodu bulunamadı: {code}")
    return account


def create_yevmiye_luca_brut(
    db: Session,
    payroll: PayrollCalculation,
    personnel: Personnel,
    fis_no: str
) -> int:
    """
    LUCA BRÜT BORDRO YEVMİYESİ
    Kalem kalem borç kayıtları oluşturur
    
    BORÇ (740.00100):
    - Net Ödenen
    - İşçi SSK, İşçi İşsizlik
    - İşveren SSK, İşveren İşsizlik
    - Gelir Vergisi, Damga Vergisi
    - BES, İcra, Avans
    - Yıllık Ücretli İzinler (gelecekte)
    """
    # Hesapları bul
    acc_740 = get_account_by_code(db, "740.00100")
    acc_335 = get_or_create_personnel_account(db, personnel)
    acc_361_isci_ssk = get_account_by_code(db, "361.00001")
    acc_361_isveren_ssk = get_account_by_code(db, "361.00002")
    acc_361_isci_issizlik = get_account_by_code(db, "361.00003")
    acc_361_isveren_issizlik = get_account_by_code(db, "361.00004")
    acc_369_bes = get_account_by_code(db, "369.00001")
    acc_369_icra = get_account_by_code(db, "369.00002")
    acc_196_avans = get_account_by_code(db, "196")
    acc_360_gelir = get_account_by_code(db, "360.00004")
    acc_360_damga = get_account_by_code(db, "360.00005")
    
    # SSK Teşviki varsa
    acc_602_teşvik = None
    if payroll.maas1_ssk_tesviki and payroll.maas1_ssk_tesviki > 0:
        acc_602_teşvik = get_account_by_code(db, "602.00003")
    
    # Document type bul
    from app.models.document_type import DocumentType, DocumentSubtype
    doc_subtype = db.query(DocumentSubtype).filter(DocumentSubtype.code == "BORDRO_LUCA").first()
    
    # Transaction oluştur
    transaction = Transaction(
        transaction_number=fis_no,
        accounting_period=payroll.donem,
        document_type_id=doc_subtype.document_type_id if doc_subtype else None,
        document_subtype_id=doc_subtype.id if doc_subtype else None,
        transaction_date=datetime.now().date(),
        description=f"{payroll.donem} Dönemi Bordro - {personnel.first_name} {personnel.last_name}"
    )
    db.add(transaction)
    db.flush()
    
    lines = []
    line_count = 0
    
    # ============================================================
    # BORÇ KAYITLARI - 740.00100 (Kalem Kalem)
    # ============================================================
    
    # 1. Net Ödenen
    if payroll.maas1_net_odenen and payroll.maas1_net_odenen > 0:
        lines.append(TransactionLine(
            transaction_id=transaction.id,
            account_id=acc_740.id,
            debit=payroll.maas1_net_odenen,
            credit=Decimal(0),
            description="Net Ödenen"
        ))
        line_count += 1
    
    # 2. İşçi SSK Payı
    if payroll.maas1_ssk_isci and payroll.maas1_ssk_isci > 0:
        lines.append(TransactionLine(
            transaction_id=transaction.id,
            account_id=acc_740.id,
            debit=payroll.maas1_ssk_isci,
            credit=Decimal(0),
            description="Ssk İşçi Payı"
        ))
        line_count += 1
    
    # 3. İşçi İşsizlik Payı
    if payroll.maas1_issizlik_isci and payroll.maas1_issizlik_isci > 0:
        lines.append(TransactionLine(
            transaction_id=transaction.id,
            account_id=acc_740.id,
            debit=payroll.maas1_issizlik_isci,
            credit=Decimal(0),
            description="İşsizlik Sigortası İşçi Payı"
        ))
        line_count += 1
    
    # 4. BES Kesintisi
    if payroll.maas1_bes and payroll.maas1_bes > 0:
        lines.append(TransactionLine(
            transaction_id=transaction.id,
            account_id=acc_740.id,
            debit=payroll.maas1_bes,
            credit=Decimal(0),
            description="Bes Kesintileri"
        ))
        line_count += 1
    
    # 5. İcra Kesintisi
    if payroll.maas1_icra and payroll.maas1_icra > 0:
        lines.append(TransactionLine(
            transaction_id=transaction.id,
            account_id=acc_740.id,
            debit=payroll.maas1_icra,
            credit=Decimal(0),
            description="İcra Kesintileri"
        ))
        line_count += 1
    
    # 6. Avans Kesintisi
    if payroll.maas1_avans and payroll.maas1_avans > 0:
        lines.append(TransactionLine(
            transaction_id=transaction.id,
            account_id=acc_740.id,
            debit=payroll.maas1_avans,
            credit=Decimal(0),
            description="Avans Kesintisi"
        ))
        line_count += 1
    
    # 7. Gelir Vergisi
    if payroll.maas1_gelir_vergisi and payroll.maas1_gelir_vergisi > 0:
        lines.append(TransactionLine(
            transaction_id=transaction.id,
            account_id=acc_740.id,
            debit=payroll.maas1_gelir_vergisi,
            credit=Decimal(0),
            description="Gelir Vergisi"
        ))
        line_count += 1
    
    # 8. Damga Vergisi
    if payroll.maas1_damga_vergisi and payroll.maas1_damga_vergisi > 0:
        lines.append(TransactionLine(
            transaction_id=transaction.id,
            account_id=acc_740.id,
            debit=payroll.maas1_damga_vergisi,
            credit=Decimal(0),
            description="Damga Vergisi"
        ))
        line_count += 1
    
    # 9. İşveren SSK Payı
    if payroll.maas1_ssk_isveren and payroll.maas1_ssk_isveren > 0:
        lines.append(TransactionLine(
            transaction_id=transaction.id,
            account_id=acc_740.id,
            debit=payroll.maas1_ssk_isveren,
            credit=Decimal(0),
            description="Ssk İşveren Payı"
        ))
        line_count += 1
    
    # 10. İşveren İşsizlik Payı
    if payroll.maas1_issizlik_isveren and payroll.maas1_issizlik_isveren > 0:
        lines.append(TransactionLine(
            transaction_id=transaction.id,
            account_id=acc_740.id,
            debit=payroll.maas1_issizlik_isveren,
            credit=Decimal(0),
            description="İşsizlik Sigortası İşveren Payı"
        ))
        line_count += 1
    
    # ============================================================
    # ALACAK KAYITLARI
    # ============================================================
    
    # 11. 335 - Personel Net Ödeme (Luca bordrosundan)
    if payroll.maas1_net_odenen and payroll.maas1_net_odenen > 0:
        lines.append(TransactionLine(
            transaction_id=transaction.id,
            account_id=acc_335.id,
            debit=Decimal(0),
            credit=payroll.maas1_net_odenen,
            description="Net Ödenen"
        ))
        line_count += 1
    
    # 12. 361.00001 - İşçi SSK Payı
    if payroll.maas1_ssk_isci and payroll.maas1_ssk_isci > 0:
        lines.append(TransactionLine(
            transaction_id=transaction.id,
            account_id=acc_361_isci_ssk.id,
            debit=Decimal(0),
            credit=payroll.maas1_ssk_isci,
            description="Ssk İşçi Payı"
        ))
        line_count += 1
    
    # 13. 361.00002 - İşveren SSK Payı
    if payroll.maas1_ssk_isveren and payroll.maas1_ssk_isveren > 0:
        lines.append(TransactionLine(
            transaction_id=transaction.id,
            account_id=acc_361_isveren_ssk.id,
            debit=Decimal(0),
            credit=payroll.maas1_ssk_isveren,
            description="Ssk İşveren Payı Ödenecek"
        ))
        line_count += 1
    
    # 14. 361.00003 - İşçi İşsizlik Payı
    if payroll.maas1_issizlik_isci and payroll.maas1_issizlik_isci > 0:
        lines.append(TransactionLine(
            transaction_id=transaction.id,
            account_id=acc_361_isci_issizlik.id,
            debit=Decimal(0),
            credit=payroll.maas1_issizlik_isci,
            description="İşsizlik Sigortası İşçi Payı"
        ))
        line_count += 1
    
    # 15. 361.00004 - İşveren İşsizlik Payı
    if payroll.maas1_issizlik_isveren and payroll.maas1_issizlik_isveren > 0:
        lines.append(TransactionLine(
            transaction_id=transaction.id,
            account_id=acc_361_isveren_issizlik.id,
            debit=Decimal(0),
            credit=payroll.maas1_issizlik_isveren,
            description="İşsizlik Sigortası İşveren Payı"
        ))
        line_count += 1
    
    # 16. 369.00001 - BES Kesintileri
    if payroll.maas1_bes and payroll.maas1_bes > 0:
        lines.append(TransactionLine(
            transaction_id=transaction.id,
            account_id=acc_369_bes.id,
            debit=Decimal(0),
            credit=payroll.maas1_bes,
            description="Bes Kesintileri"
        ))
        line_count += 1
    
    # 17. 369.00002 - İcra Kesintileri
    if payroll.maas1_icra and payroll.maas1_icra > 0:
        lines.append(TransactionLine(
            transaction_id=transaction.id,
            account_id=acc_369_icra.id,
            debit=Decimal(0),
            credit=payroll.maas1_icra,
            description="İcra Kesintileri"
        ))
        line_count += 1
    
    # 18. 196 - Personel Avansları
    if payroll.maas1_avans and payroll.maas1_avans > 0:
        lines.append(TransactionLine(
            transaction_id=transaction.id,
            account_id=acc_196_avans.id,
            debit=Decimal(0),
            credit=payroll.maas1_avans,
            description="Avans Kesintisi"
        ))
        line_count += 1
    
    # 19. 360.00004 - Gelir Vergisi
    if payroll.maas1_gelir_vergisi and payroll.maas1_gelir_vergisi > 0:
        lines.append(TransactionLine(
            transaction_id=transaction.id,
            account_id=acc_360_gelir.id,
            debit=Decimal(0),
            credit=payroll.maas1_gelir_vergisi,
            description="Gelir Vergisi"
        ))
        line_count += 1
    
    # 20. 360.00005 - Damga Vergisi
    if payroll.maas1_damga_vergisi and payroll.maas1_damga_vergisi > 0:
        lines.append(TransactionLine(
            transaction_id=transaction.id,
            account_id=acc_360_damga.id,
            debit=Decimal(0),
            credit=payroll.maas1_damga_vergisi,
            description="Damga Vergisi"
        ))
        line_count += 1
    
    # 21. 602.00003 - SSK Teşviki (varsa)
    if acc_602_teşvik and payroll.maas1_ssk_tesviki > 0:
        lines.append(TransactionLine(
            transaction_id=transaction.id,
            account_id=acc_602_teşvik.id,
            debit=Decimal(0),
            credit=payroll.maas1_ssk_tesviki,
            description="Hazine Katkı Payı"
        ))
        line_count += 1
    
    # Tüm satırları ekle
    db.add_all(lines)
    db.flush()
    
    # Payroll'u güncelle
    payroll.transaction_id = transaction.id
    payroll.fis_no = fis_no
    payroll.is_exported = 1
    
    return line_count


def create_yevmiye_elden(
    db: Session,
    payroll: PayrollCalculation,
    personnel: Personnel,
    fis_no: str
) -> int:
    """
    ELDEN ÜCRET YEVMİYESİ
    Puantaj bazlı ödeme (Normal Çalışma + Hafta Tatili + Fazla Mesai + vb.)
    """
    # Hesapları bul
    acc_740 = get_account_by_code(db, "740.00100")
    acc_335 = get_or_create_personnel_account(db, personnel)
    
    # Document type bul
    from app.models.document_type import DocumentType, DocumentSubtype
    doc_subtype = db.query(DocumentSubtype).filter(DocumentSubtype.code == "BORDRO_ELDEN").first()
    
    # Transaction oluştur
    transaction = Transaction(
        transaction_number=fis_no,
        accounting_period=payroll.donem,
        document_type_id=doc_subtype.document_type_id if doc_subtype else None,
        document_subtype_id=doc_subtype.id if doc_subtype else None,
        transaction_date=datetime.now().date(),
        description=f"{payroll.donem} Dönemi Elden Ücret - {personnel.first_name} {personnel.last_name}"
    )
    db.add(transaction)
    db.flush()
    
    lines = []
    line_count = 0
    
    # ============================================================
    # BORÇ KAYITLARI - 740.00100
    # ============================================================
    
    # Elden Ücretler (Yuvarlanmış tutar)
    if payroll.elden_ucret_yuvarlanmis and payroll.elden_ucret_yuvarlanmis > 0:
        lines.append(TransactionLine(
            transaction_id=transaction.id,
            account_id=acc_740.id,
            debit=payroll.elden_ucret_yuvarlanmis,
            credit=Decimal(0),
            description="Elden Ücretler"
        ))
        line_count += 1
    
    # ============================================================
    # ALACAK KAYITLARI - 335.xxxxx (Kalem Kalem)
    # ============================================================
    
    # Normal Çalışma
    if payroll.maas2_normal_calısma and payroll.maas2_normal_calısma > 0:
        lines.append(TransactionLine(
            transaction_id=transaction.id,
            account_id=acc_335.id,
            debit=Decimal(0),
            credit=payroll.maas2_normal_calısma,
            description=f"Normal Çalışması ({payroll.normal_gun} Gün)"
        ))
        line_count += 1
    
    # Hafta Tatili
    if payroll.maas2_hafta_tatili and payroll.maas2_hafta_tatili > 0:
        lines.append(TransactionLine(
            transaction_id=transaction.id,
            account_id=acc_335.id,
            debit=Decimal(0),
            credit=payroll.maas2_hafta_tatili,
            description=f"Hafta Tatili ({payroll.hafta_tatili_gun} Gün)"
        ))
        line_count += 1
    
    # Fazla Mesai
    if payroll.maas2_fazla_mesai and payroll.maas2_fazla_mesai > 0:
        lines.append(TransactionLine(
            transaction_id=transaction.id,
            account_id=acc_335.id,
            debit=Decimal(0),
            credit=payroll.maas2_fazla_mesai,
            description=f"Fazla Çalışması ({payroll.fazla_mesai_saat} Saat)"
        ))
        line_count += 1
    
    # Tatil Mesaisi
    if payroll.maas2_tatil_mesaisi and payroll.maas2_tatil_mesaisi > 0:
        lines.append(TransactionLine(
            transaction_id=transaction.id,
            account_id=acc_335.id,
            debit=Decimal(0),
            credit=payroll.maas2_tatil_mesaisi,
            description=f"Tatil Çalışması ({payroll.tatil_mesai_gun} Gün)"
        ))
        line_count += 1
    
    # Ücretli İzin
    if payroll.maas2_ucretli_izin and payroll.maas2_ucretli_izin > 0:
        lines.append(TransactionLine(
            transaction_id=transaction.id,
            account_id=acc_335.id,
            debit=Decimal(0),
            credit=payroll.maas2_ucretli_izin,
            description=f"Ücretli İzin ({payroll.yillik_izin_gun} Gün)"
        ))
        line_count += 1
    
    # Elden Yuvarlaması
    if payroll.elden_yuvarlama and payroll.elden_yuvarlama != 0:
        if payroll.elden_yuvarlama_yon == "ALACAK":
            # Yukarı yuvarlandı, fazla ödedik → 335'e ALACAK
            lines.append(TransactionLine(
                transaction_id=transaction.id,
                account_id=acc_335.id,
                debit=Decimal(0),
                credit=abs(payroll.elden_yuvarlama),
                description="Elden Yuvarlaması"
            ))
            line_count += 1
        elif payroll.elden_yuvarlama_yon == "BORC":
            # Aşağı yuvarlandı, eksik ödedik → 335'e BORÇ
            lines.append(TransactionLine(
                transaction_id=transaction.id,
                account_id=acc_335.id,
                debit=abs(payroll.elden_yuvarlama),
                credit=Decimal(0),
                description="Elden Yuvarlaması"
            ))
            line_count += 1
    
    # Tüm satırları ekle
    db.add_all(lines)
    db.flush()
    
    # Payroll'u güncelle
    payroll.transaction_id = transaction.id
    payroll.fis_no = fis_no
    payroll.is_exported = 1
    
    return line_count


def create_yevmiye_karma(
    db: Session,
    payroll: PayrollCalculation,
    personnel: Personnel,
    fis_no_base: str
) -> int:
    """
    KARMA YEVMİYE (Luca + Elden)
    2 ayrı fiş oluşturur
    """
    total_lines = 0
    
    # 1. Luca Brüt Fişi
    fis_luca = f"{fis_no_base}-LUCA"
    lines_luca = create_yevmiye_luca_brut(db, payroll, personnel, fis_luca)
    total_lines += lines_luca
    
    # 2. Elden Fişi
    fis_elden = f"{fis_no_base}-ELDEN"
    lines_elden = create_yevmiye_elden(db, payroll, personnel, fis_elden)
    total_lines += lines_elden
    
    return total_lines


@router.post("/generate-yevmiye", response_model=GenerateYevmiyeResponse)
def generate_bordro_yevmiye(
    req: GenerateYevmiyeRequest,
    db: Session = Depends(get_db)
):
    """
    Bordro yevmiye kayıtlarını oluşturur
    
    - Kalem kalem borç kayıtları (Net, SSK, Vergi, vb. ayrı satırlar)
    - 335.{tc} otomatik hesap oluşturma
    - Elden yuvarlama işlemi
    - BORÇ = ALACAK kontrolü
    """
    try:
        # Payroll kayıtlarını getir
        query = db.query(PayrollCalculation).filter(
            PayrollCalculation.donem == req.donem
        )
        
        if req.personnel_ids:
            query = query.filter(PayrollCalculation.personnel_id.in_(req.personnel_ids))
        
        # Daha önce yevmiye oluşturulmuş mu kontrol et
        if not req.force_regenerate:
            query = query.filter(PayrollCalculation.is_exported == 0)
        
        payrolls = query.all()
        
        if not payrolls:
            return GenerateYevmiyeResponse(
                success=False,
                message="Yevmiye oluşturulacak bordro kaydı bulunamadı",
                donem=req.donem,
                personnel_count=0,
                transaction_count=0,
                total_lines=0,
                total_debit=Decimal(0),
                total_credit=Decimal(0)
            )
        
        # Force regenerate ise eski kayıtları sil
        if req.force_regenerate:
            # Transaction ID'leri topla
            transaction_ids = [p.transaction_id for p in payrolls if p.transaction_id]
            
            if transaction_ids:
                # Önce payroll'ları resetle (foreign key constraint için)
                for payroll in payrolls:
                    if payroll.transaction_id:
                        payroll.transaction_id = None
                        payroll.fis_no = None
                        payroll.is_exported = 0
                db.flush()
                
                # Şimdi transaction'ları silebiliriz
                # Transaction lines'ı sil
                db.query(TransactionLine).filter(
                    TransactionLine.transaction_id.in_(transaction_ids)
                ).delete(synchronize_session=False)
                # Transaction'ları sil
                db.query(Transaction).filter(
                    Transaction.id.in_(transaction_ids)
                ).delete(synchronize_session=False)
                db.commit()
        
        # Yevmiye oluştur
        transaction_count = 0
        total_lines = 0
        errors = []
        
        for payroll in payrolls:
            try:
                # Personeli bul
                personnel = db.query(Personnel).filter(
                    Personnel.id == payroll.personnel_id
                ).first()
                
                if not personnel:
                    errors.append(f"Personel bulunamadı: ID {payroll.personnel_id}")
                    continue
                
                # MERKEZI FİŞ NUMARASI SİSTEMİ
                # Fiş numarası sıralı ve kesintisiz: F00000001, F00000002, ...
                fis_no = get_next_transaction_number(db)
                
                # Yevmiye tipine göre işlem yap
                maas1 = float(payroll.maas1_net_odenen or 0)
                elden = float(payroll.elden_ucret_yuvarlanmis or 0)
                
                if maas1 > 0 and elden == 0:
                    # TİP 1: Sadece Luca Brüt
                    lines = create_yevmiye_luca_brut(db, payroll, personnel, fis_no)
                    total_lines += lines
                    transaction_count += 1
                    
                elif maas1 == 0 and elden > 0:
                    # TİP 2: Sadece Elden
                    lines = create_yevmiye_elden(db, payroll, personnel, fis_no)
                    total_lines += lines
                    transaction_count += 1
                    
                elif maas1 > 0 and elden > 0:
                    # TİP 3: Karma (Luca + Elden)
                    lines = create_yevmiye_karma(db, payroll, personnel, fis_no)
                    total_lines += lines
                    transaction_count += 2  # 2 fiş
                    
                else:
                    errors.append(f"Yevmiye tipi belirlenemedi: {personnel.first_name} {personnel.last_name} (maas1={maas1}, elden={elden})")
                    continue
                
            except Exception as e:
                errors.append(f"{personnel.first_name} {personnel.last_name}: {str(e)}")
                db.rollback()
                continue
        
        # Commit
        db.commit()
        
        # Document subtype ID'leri bul
        from app.models.document_type import DocumentSubtype
        luca_subtype = db.query(DocumentSubtype).filter(DocumentSubtype.code == "BORDRO_LUCA").first()
        elden_subtype = db.query(DocumentSubtype).filter(DocumentSubtype.code == "BORDRO_ELDEN").first()
        subtype_ids = [s.id for s in [luca_subtype, elden_subtype] if s]
        
        # Toplam borç/alacak hesapla
        total_debit = db.query(func.sum(TransactionLine.debit)).join(Transaction).filter(
            Transaction.accounting_period == req.donem,
            Transaction.document_subtype_id.in_(subtype_ids)
        ).scalar() or Decimal(0)
        
        total_credit = db.query(func.sum(TransactionLine.credit)).join(Transaction).filter(
            Transaction.accounting_period == req.donem,
            Transaction.document_subtype_id.in_(subtype_ids)
        ).scalar() or Decimal(0)
        
        return GenerateYevmiyeResponse(
            success=True,
            message=f"{len(payrolls)} personel için yevmiye oluşturuldu",
            donem=req.donem,
            personnel_count=len(payrolls),
            transaction_count=transaction_count,
            total_lines=total_lines,
            total_debit=total_debit,
            total_credit=total_credit,
            errors=errors
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
