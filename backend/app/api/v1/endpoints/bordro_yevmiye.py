"""
Bordro Yevmiye Generation
Hesaplanan bordrodan muhasebe kayıtları oluşturma
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from pydantic import BaseModel
from datetime import date, datetime
from decimal import Decimal

from app.core.database import get_db
from app.models.payroll_calculation import PayrollCalculation
from app.models.transaction import Transaction
from app.models.transaction_item import TransactionItem
from app.models.account import Account
from app.models.cost_center import CostCenter

router = APIRouter()


class GenerateYevmiyeRequest(BaseModel):
    yil: int
    ay: int
    donem: str
    islem_tarihi: Optional[str] = None  # YYYY-MM-DD, yoksa ayın son günü


class YevmiyeResponse(BaseModel):
    success: bool
    created_count: int
    updated_count: int
    total_transactions: int
    errors: List[str] = []


def get_or_create_account(db: Session, code: str, name: str = None) -> Account:
    """Hesap kodu varsa getir, yoksa oluştur"""
    account = db.query(Account).filter(Account.code == code).first()
    if not account:
        account = Account(
            code=code,
            name=name or f"Hesap {code}",
            account_type="ALT",
            is_active=True
        )
        db.add(account)
        db.flush()
    return account


@router.post("/generate-yevmiye", response_model=YevmiyeResponse)
def generate_yevmiye(
    req: GenerateYevmiyeRequest,
    db: Session = Depends(get_db)
):
    """
    Bordro hesaplamalarından yevmiye kayıtları oluştur
    
    TİP A: Luca Bordro (Maaş ödemesi)
    - 335.xxxxx / 100 (Net ödenen)
    - 335.xxxxx / 360-361 (Kesintiler: İcra, Avans, BES, Vergi, SSK, İşsizlik)
    - 770 / 335.xxxxx (Brüt ücret maliyeti)
    - 770 / 361 (SSK + İşsizlik İşveren)
    
    TİP B: Elden Ücret
    - 335.xxxxx / 100 (Elden ücret ödemesi)
    - 770 / 335.xxxxx (Elden ücret maliyeti)
    
    TİP C: A + B
    """
    
    # İşlem tarihi (yoksa ayın son günü)
    if req.islem_tarihi:
        islem_tarihi = datetime.strptime(req.islem_tarihi, "%Y-%m-%d").date()
    else:
        # Ayın son günü
        if req.ay == 12:
            next_month = date(req.yil + 1, 1, 1)
        else:
            next_month = date(req.yil, req.ay + 1, 1)
        from datetime import timedelta
        islem_tarihi = next_month - timedelta(days=1)
    
    # Hesaplanan bordroları al
    payrolls = db.query(PayrollCalculation).filter(
        PayrollCalculation.yil == req.yil,
        PayrollCalculation.ay == req.ay
    ).all()
    
    if not payrolls:
        raise HTTPException(400, f"{req.donem} dönemi için hesaplanmış bordro bulunamadı")
    
    # Evrak no: BORDRO-YYYY-MM-SEQ
    existing_count = db.query(func.count(Transaction.id)).filter(
        Transaction.evrak_no.like(f"BORDRO-{req.donem}-%")
    ).scalar()
    
    created_count = 0
    updated_count = 0
    errors = []
    
    for payroll in payrolls:
        try:
            # Yevmiye tipi kontrolü
            if not payroll.yevmiye_tipi:
                errors.append(f"{payroll.adi_soyadi}: Yevmiye tipi belirtilmemiş (net ödenen=0)")
                continue
            
            # Personel hesap kodu
            if not payroll.account_code_335:
                errors.append(f"{payroll.adi_soyadi}: 335 hesap kodu yok")
                continue
            
            # Mevcut yevmiye var mı kontrol et
            evrak_no = f"BORDRO-{req.donem}-{payroll.id}"
            existing_tx = db.query(Transaction).filter(
                Transaction.evrak_no == evrak_no
            ).first()
            
            if existing_tx:
                # Mevcut işlemi sil ve yeniden oluştur
                db.query(TransactionItem).filter(
                    TransactionItem.transaction_id == existing_tx.id
                ).delete()
                db.delete(existing_tx)
                updated_count += 1
            else:
                created_count += 1
            
            # Hesapları al/oluştur
            acc_335 = get_or_create_account(db, payroll.account_code_335, f"Personel - {payroll.adi_soyadi}")
            acc_100 = get_or_create_account(db, "100", "Kasa")
            acc_360 = get_or_create_account(db, "360", "Ödenecek Vergiler")
            acc_361 = get_or_create_account(db, "361", "Ödenecek SGK Primleri")
            acc_770 = get_or_create_account(db, "770", "Genel Üretim Giderleri")
            
            # Transaction oluştur
            tx = Transaction(
                transaction_date=islem_tarihi,
                evrak_no=evrak_no,
                description=f"{req.donem} Bordro - {payroll.adi_soyadi} ({payroll.yevmiye_tipi})",
                transaction_type="BORDRO",
                cost_center_id=payroll.cost_center_id,
                status="approved",
                is_balanced=True
            )
            db.add(tx)
            db.flush()
            
            items = []
            
            # TİP A veya C: Luca Bordro kayıtları
            if payroll.yevmiye_tipi in ['A', 'C']:
                net = float(payroll.maas1_net_odenen or 0)
                icra = float(payroll.maas1_icra or 0)
                bes = float(payroll.maas1_bes or 0)
                avans = float(payroll.maas1_avans or 0)
                gelir_v = float(payroll.maas1_gelir_vergisi or 0)
                damga_v = float(payroll.maas1_damga_vergisi or 0)
                ssk_isci = float(payroll.maas1_ssk_isci or 0)
                issizlik_isci = float(payroll.maas1_issizlik_isci or 0)
                ssk_isveren = float(payroll.maas1_ssk_isveren or 0)
                issizlik_isveren = float(payroll.maas1_issizlik_isveren or 0)
                
                # Brüt ücret = Net + Kesintiler
                brut = net + icra + bes + avans + gelir_v + damga_v + ssk_isci + issizlik_isci
                
                # 1. Ödeme kaydı: 335 / 100, 360, 361
                if brut > 0:
                    # Borç: 335 (Brüt)
                    items.append(TransactionItem(
                        transaction_id=tx.id,
                        account_id=acc_335.id,
                        debit=Decimal(str(brut)),
                        credit=Decimal('0'),
                        description=f"Brüt Ücret - {payroll.adi_soyadi}",
                        cost_center_id=payroll.cost_center_id
                    ))
                    
                    # Alacak: 100 (Net ödenen)
                    if net > 0:
                        items.append(TransactionItem(
                            transaction_id=tx.id,
                            account_id=acc_100.id,
                            debit=Decimal('0'),
                            credit=Decimal(str(net)),
                            description=f"Net Ödeme - {payroll.adi_soyadi}"
                        ))
                    
                    # Alacak: Kesintiler (360-361)
                    kesintiler = [
                        (icra, "İcra Kesintisi"),
                        (bes, "BES Kesintisi"),
                        (avans, "Avans Kesintisi"),
                        (gelir_v, "Gelir Vergisi"),
                        (damga_v, "Damga Vergisi"),
                    ]
                    
                    for tutar, aciklama in kesintiler:
                        if tutar > 0:
                            items.append(TransactionItem(
                                transaction_id=tx.id,
                                account_id=acc_360.id,
                                debit=Decimal('0'),
                                credit=Decimal(str(tutar)),
                                description=aciklama
                            ))
                    
                    # SSK + İşsizlik İşçi (361)
                    if ssk_isci > 0:
                        items.append(TransactionItem(
                            transaction_id=tx.id,
                            account_id=acc_361.id,
                            debit=Decimal('0'),
                            credit=Decimal(str(ssk_isci)),
                            description="SSK İşçi Payı"
                        ))
                    
                    if issizlik_isci > 0:
                        items.append(TransactionItem(
                            transaction_id=tx.id,
                            account_id=acc_361.id,
                            debit=Decimal('0'),
                            credit=Decimal(str(issizlik_isci)),
                            description="İşsizlik İşçi Payı"
                        ))
                
                # 2. Maliyet kaydı: 770 / 335, 361
                toplam_maliyet = brut + ssk_isveren + issizlik_isveren
                
                if toplam_maliyet > 0:
                    # Borç: 770 (Toplam maliyet)
                    items.append(TransactionItem(
                        transaction_id=tx.id,
                        account_id=acc_770.id,
                        debit=Decimal(str(toplam_maliyet)),
                        credit=Decimal('0'),
                        description=f"Personel Gideri - {payroll.adi_soyadi}",
                        cost_center_id=payroll.cost_center_id
                    ))
                    
                    # Alacak: 335 (Brüt ücret)
                    if brut > 0:
                        items.append(TransactionItem(
                            transaction_id=tx.id,
                            account_id=acc_335.id,
                            debit=Decimal('0'),
                            credit=Decimal(str(brut)),
                            description=f"Brüt Ücret - {payroll.adi_soyadi}",
                            cost_center_id=payroll.cost_center_id
                        ))
                    
                    # Alacak: 361 (SSK + İşsizlik İşveren)
                    if ssk_isveren > 0:
                        items.append(TransactionItem(
                            transaction_id=tx.id,
                            account_id=acc_361.id,
                            debit=Decimal('0'),
                            credit=Decimal(str(ssk_isveren)),
                            description="SSK İşveren Payı"
                        ))
                    
                    if issizlik_isveren > 0:
                        items.append(TransactionItem(
                            transaction_id=tx.id,
                            account_id=acc_361.id,
                            debit=Decimal('0'),
                            credit=Decimal(str(issizlik_isveren)),
                            description="İşsizlik İşveren Payı"
                        ))
            
            # TİP B veya C: Elden Ücret kayıtları
            if payroll.yevmiye_tipi in ['B', 'C']:
                elden = float(payroll.elden_ucret_yuvarlanmis or 0)
                
                if elden > 0:
                    # 1. Ödeme: 335 / 100
                    items.append(TransactionItem(
                        transaction_id=tx.id,
                        account_id=acc_335.id,
                        debit=Decimal(str(elden)),
                        credit=Decimal('0'),
                        description=f"Elden Ücret - {payroll.adi_soyadi}",
                        cost_center_id=payroll.cost_center_id
                    ))
                    
                    items.append(TransactionItem(
                        transaction_id=tx.id,
                        account_id=acc_100.id,
                        debit=Decimal('0'),
                        credit=Decimal(str(elden)),
                        description=f"Elden Ödeme - {payroll.adi_soyadi}"
                    ))
                    
                    # 2. Maliyet: 770 / 335
                    items.append(TransactionItem(
                        transaction_id=tx.id,
                        account_id=acc_770.id,
                        debit=Decimal(str(elden)),
                        credit=Decimal('0'),
                        description=f"Elden Personel Gideri - {payroll.adi_soyadi}",
                        cost_center_id=payroll.cost_center_id
                    ))
                    
                    items.append(TransactionItem(
                        transaction_id=tx.id,
                        account_id=acc_335.id,
                        debit=Decimal('0'),
                        credit=Decimal(str(elden)),
                        description=f"Elden Ücret - {payroll.adi_soyadi}",
                        cost_center_id=payroll.cost_center_id
                    ))
            
            # Transaction item'ları ekle
            for item in items:
                db.add(item)
            
            # Dengeyi kontrol et
            total_debit = sum(float(item.debit) for item in items)
            total_credit = sum(float(item.credit) for item in items)
            
            if abs(total_debit - total_credit) > 0.01:
                errors.append(f"{payroll.adi_soyadi}: Borç-Alacak dengesiz (B:{total_debit:.2f} A:{total_credit:.2f})")
                db.rollback()
                continue
                
        except Exception as e:
            errors.append(f"{payroll.adi_soyadi}: {str(e)}")
            db.rollback()
            continue
    
    db.commit()
    
    return YevmiyeResponse(
        success=True,
        created_count=created_count,
        updated_count=updated_count,
        total_transactions=created_count + updated_count,
        errors=errors[:20] if errors else []
    )


@router.get("/yevmiye-list")
def list_bordro_yevmiye(
    yil: int,
    ay: int,
    db: Session = Depends(get_db)
):
    """Bordro yevmiye kayıtlarını listele"""
    donem = f"{yil}-{ay:02d}"
    
    transactions = db.query(Transaction).filter(
        Transaction.evrak_no.like(f"BORDRO-{donem}-%")
    ).all()
    
    result = []
    for tx in transactions:
        items = db.query(TransactionItem).filter(
            TransactionItem.transaction_id == tx.id
        ).all()
        
        result.append({
            "id": tx.id,
            "evrak_no": tx.evrak_no,
            "transaction_date": tx.transaction_date,
            "description": tx.description,
            "total_debit": sum(float(item.debit) for item in items),
            "total_credit": sum(float(item.credit) for item in items),
            "item_count": len(items),
            "status": tx.status
        })
    
    return {
        "total": len(result),
        "items": result
    }
