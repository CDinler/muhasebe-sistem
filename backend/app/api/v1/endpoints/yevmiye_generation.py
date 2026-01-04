"""
Yevmiye Generation - Basitleştirilmiş versiyon
Bordro hesaplamalarından yevmiye kayıtları oluşturur
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from decimal import Decimal

from app.core.database import get_db
from app.models.payroll_calculation import PayrollCalculation
from app.models.transaction import Transaction
from app.models.transaction_line import TransactionLine
from app.models.account import Account

router = APIRouter()


class GenerateYevmiyeRequest(BaseModel):
    yil: int
    ay: int
    donem: str
    personnel_ids: Optional[List[int]] = None  # Boşsa tümü


@router.post("/generate-yevmiye")
def generate_yevmiye(
    req: GenerateYevmiyeRequest,
    db: Session = Depends(get_db)
):
    """
    Bordro hesaplamalarından yevmiye kayıtları oluştur
    
    Tip A: Luca bordro (net ödenen + kesintiler)
    Tip B: Elden kazanç (saha ödemesi)
    Tip C: İkisi birlikte
    """
    
    # Payroll kayıtlarını al
    query = db.query(PayrollCalculation).filter(
        PayrollCalculation.yil == req.yil,
        PayrollCalculation.ay == req.ay
    )
    
    if req.personnel_ids:
        query = query.filter(PayrollCalculation.personnel_id.in_(req.personnel_ids))
    
    payrolls = query.all()
    
    if not payrolls:
        raise HTTPException(400, "Hesaplanmış bordro bulunamadı")
    
    transaction_count = 0
    yevmiye_count = 0
    
    for payroll in payrolls:
        # Tip A veya C: Luca bordro var
        if payroll.yevmiye_tipi in ['A', 'C'] and payroll.maas1_net_odenen > 0:
            transaction_count += 1
            yevmiye_count += create_type_a_transaction(db, payroll)
        
        # Tip B veya C: Elden kazanç var
        if payroll.yevmiye_tipi in ['B', 'C'] and payroll.elden_ucret_yuvarlanmis and payroll.elden_ucret_yuvarlanmis > 0:
            transaction_count += 1
            yevmiye_count += create_type_b_transaction(db, payroll)
    
    db.commit()
    
    return {
        "success": True,
        "donem": req.donem,
        "transaction_count": transaction_count,
        "yevmiye_count": yevmiye_count,
        "summary": {
            "A": sum(1 for p in payrolls if p.yevmiye_tipi == 'A'),
            "B": sum(1 for p in payrolls if p.yevmiye_tipi == 'B'),
            "C": sum(1 for p in payrolls if p.yevmiye_tipi == 'C'),
        }
    }


def create_type_a_transaction(db: Session, payroll: PayrollCalculation) -> int:
    """
    Tip A: Luca bordro yevmiyesi
    
    BORÇ: 770 Genel Yönetim Giderleri
    ALACAK: 335 Personel Hesabı (Net)
    ALACAK: 360 Ödenecek Vergiler (Gelir + Damga)
    ALACAK: 361 Ödenecek SSK (İşçi + İşveren)
    """
    
    # Fiş numarası oluştur
    last_trans = db.query(Transaction).order_by(Transaction.id.desc()).first()
    next_num = (last_trans.id + 1) if last_trans else 1
    
    # Document type bul
    from app.models.document_type import DocumentSubtype
    doc_subtype = db.query(DocumentSubtype).filter(DocumentSubtype.code == "BORDRO_A").first()
    
    # İşlem oluştur
    transaction = Transaction(
        transaction_number=f"BORDRO-A-{payroll.donem}-{next_num}",
        transaction_date=datetime(payroll.yil, payroll.ay, 28).date(),
        accounting_period=payroll.donem,
        description=f"Bordro - {payroll.adi_soyadi}",
        document_type_id=doc_subtype.document_type_id if doc_subtype else None,
        document_subtype_id=doc_subtype.id if doc_subtype else None,
        cost_center_id=payroll.cost_center_id
    )
    db.add(transaction)
    db.flush()
    
    entry_count = 0
    
    # Brüt maliyet hesapla
    brut_maliyet = (
        float(payroll.maas1_net_odenen or 0) +
        float(payroll.maas1_gelir_vergisi or 0) +
        float(payroll.maas1_damga_vergisi or 0) +
        float(payroll.maas1_ssk_isci or 0) +
        float(payroll.maas1_ssk_isveren or 0) +
        float(payroll.maas1_issizlik_isci or 0) +
        float(payroll.maas1_issizlik_isveren or 0)
    )
    
    # BORÇ: 770 Genel Yönetim Giderleri
    acc_770 = db.query(Account).filter(Account.code == "770").first()
    if acc_770:
        db.add(TransactionLine(
            transaction_id=transaction.id,
            account_id=acc_770.id,
            description=f"Personel maaş gideri - {payroll.adi_soyadi}",
            debit=Decimal(str(brut_maliyet)),
            credit=Decimal('0')
        ))
        entry_count += 1
    
    # ALACAK: 335 Personel (Net ödenen)
    account_code = payroll.account_code_335 if payroll.account_code_335 else "335"
    acc_335 = db.query(Account).filter(Account.code == account_code).first()
    if acc_335:
        db.add(TransactionLine(
            transaction_id=transaction.id,
            account_id=acc_335.id,
            description=f"Net maaş - {payroll.adi_soyadi}",
            debit=Decimal('0'),
            credit=Decimal(str(payroll.maas1_net_odenen))
        ))
        entry_count += 1
    
    # ALACAK: 360 Vergiler (Gelir + Damga)
    toplam_vergi = float(payroll.maas1_gelir_vergisi or 0) + float(payroll.maas1_damga_vergisi or 0)
    if toplam_vergi > 0:
        acc_360 = db.query(Account).filter(Account.code == "360").first()
        if acc_360:
            db.add(TransactionLine(
                transaction_id=transaction.id,
                account_id=acc_360.id,
                description=f"Gelir ve damga vergisi - {payroll.adi_soyadi}",
                debit=Decimal('0'),
                credit=Decimal(str(toplam_vergi))
            ))
            entry_count += 1
    
    # ALACAK: 361 SSK (İşçi + İşveren + İşsizlik)
    toplam_ssk = (
        float(payroll.maas1_ssk_isci or 0) +
        float(payroll.maas1_ssk_isveren or 0) +
        float(payroll.maas1_issizlik_isci or 0) +
        float(payroll.maas1_issizlik_isveren or 0)
    )
    if toplam_ssk > 0:
        acc_361 = db.query(Account).filter(Account.code == "361").first()
        if acc_361:
            db.add(TransactionLine(
                transaction_id=transaction.id,
                account_id=acc_361.id,
                description=f"SSK ve işsizlik - {payroll.adi_soyadi}",
                debit=Decimal('0'),
                credit=Decimal(str(toplam_ssk))
            ))
            entry_count += 1
    
    return entry_count


def create_type_b_transaction(db: Session, payroll: PayrollCalculation) -> int:
    """
    Tip B: Elden kazanç yevmiyesi
    
    BORÇ: 730 Genel Üretim Giderleri
    ALACAK: 335 Personel Hesabı (Elden)
    """
    
    # Fiş numarası oluştur
    last_trans = db.query(Transaction).order_by(Transaction.id.desc()).first()
    next_num = (last_trans.id + 1) if last_trans else 1
    
    # Document type bul
    from app.models.document_type import DocumentSubtype
    doc_subtype = db.query(DocumentSubtype).filter(DocumentSubtype.code == "BORDRO_B").first()
    
    transaction = Transaction(
        transaction_number=f"BORDRO-B-{payroll.donem}-{next_num}",
        transaction_date=datetime(payroll.yil, payroll.ay, 28).date(),
        accounting_period=payroll.donem,
        description=f"Bordro Elden - {payroll.adi_soyadi}",
        document_type_id=doc_subtype.document_type_id if doc_subtype else None,
        document_subtype_id=doc_subtype.id if doc_subtype else None,
        cost_center_id=payroll.cost_center_id
    )
    db.add(transaction)
    db.flush()
    
    entry_count = 0
    elden_tutar = float(payroll.elden_ucret_yuvarlanmis or 0)
    
    # BORÇ: 730 Genel Üretim Giderleri
    acc_730 = db.query(Account).filter(Account.code == "730").first()
    if acc_730:
        db.add(TransactionLine(
            transaction_id=transaction.id,
            account_id=acc_730.id,
            description=f"Elden kazanç - {payroll.adi_soyadi}",
            debit=Decimal(str(elden_tutar)),
            credit=Decimal('0')
        ))
        entry_count += 1
    
    # ALACAK: 335 Personel
    account_code = payroll.account_code_335 if payroll.account_code_335 else "335"
    acc_335 = db.query(Account).filter(Account.code == account_code).first()
    if acc_335:
        db.add(TransactionLine(
            transaction_id=transaction.id,
            account_id=acc_335.id,
            description=f"Elden ödeme - {payroll.adi_soyadi}",
            debit=Decimal('0'),
            credit=Decimal(str(elden_tutar))
        ))
        entry_count += 1
    
    return entry_count
