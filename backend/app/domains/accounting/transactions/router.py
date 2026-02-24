"""
Transaction Router (V2 API)

Muhasebe fişleri için DDD mimarisine uygun endpoint'ler.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app.core.database import get_db
from app.domains.auth.dependencies import get_current_user
from app.schemas.auth import UserInDB
from app.domains.accounting.transactions.service import transaction_service
from app.domains.accounting.transactions.schemas import (
    TransactionResponse,
    TransactionCreate,
    TransactionListResponse
)


router = APIRouter(tags=['Transactions (V2)'])


@router.get('/summary')
def get_summary(
    date_from: Optional[date] = Query(None, description='Başlangıç tarihi'),
    date_to: Optional[date] = Query(None, description='Bitiş tarihi'),
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Muhasebe fişi özet istatistikleri
    
    - **date_from**: Başlangıç tarihi (opsiyonel)
    - **date_to**: Bitiş tarihi (opsiyonel)
    """
    return transaction_service.get_summary(
        db,
        date_from=date_from,
        date_to=date_to
    )


@router.get('/', response_model=TransactionListResponse)
def get_transactions(
    skip: int = Query(0, ge=0, description='Atlanacak kayıt sayısı'),
    limit: int = Query(50, ge=1, le=500, description='Maksimum kayıt sayısı'),
    date_from: Optional[date] = Query(None, description='Başlangıç tarihi'),
    date_to: Optional[date] = Query(None, description='Bitiş tarihi'),
    cost_center_id: Optional[int] = Query(None, description='Masraf merkezi ID'),
    document_type_id: Optional[int] = Query(None, description='Evrak tipi ID'),
    search: Optional[str] = Query(None, description='Arama (fiş no, açıklama, evrak no)'),
    order_by: Optional[str] = Query(None, description='Sıralama (date_asc, date_desc)'),
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Muhasebe fişlerini listele (filtreleme ve pagination)
    
    - **skip**: Kaç kayıt atlanacak (pagination için)
    - **limit**: Maksimum kayıt sayısı
    - **date_from**: Başlangıç tarihi
    - **date_to**: Bitiş tarihi
    - **cost_center_id**: Masraf merkezi filtresi
    - **document_type_id**: Evrak tipi filtresi
    - **search**: Fiş no, açıklama veya evrak numarasında arama
    """
    result = transaction_service.list_transactions(
        db=db,
        skip=skip,
        limit=limit,
        date_from=date_from,
        date_to=date_to,
        cost_center_id=cost_center_id,
        document_type_id=document_type_id,
        search=search,
        order_by=order_by
    )
    return result


@router.get('/{id}')
def get_transaction(
    id: int,
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    ID'ye göre fiş getir (satırlarıyla birlikte)
    """
    transaction = transaction_service.get_transaction(db, id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Fiş bulunamadı")
    
    # Manuel serialize - account_code ve account_name için
    return {
        "id": transaction.id,
        "transaction_number": transaction.transaction_number,
        "transaction_date": transaction.transaction_date.isoformat(),
        "accounting_period": transaction.accounting_period,
        "cost_center_id": transaction.cost_center_id,
        "description": transaction.description,
        "document_type": transaction.document_type,
        "document_number": transaction.document_number,
        "related_invoice_number": transaction.related_invoice_number,
        "document_type_id": transaction.document_type_id,
        "lines": [
            {
                "id": line.id,
                "transaction_id": line.transaction_id,
                "account_id": line.account_id,
                "account_code": line.account.code if line.account else None,
                "account_name": line.account.name if line.account else None,
                "contact_id": line.contact_id,
                "description": line.description,
                "debit": float(line.debit) if line.debit else 0,
                "credit": float(line.credit) if line.credit else 0,
                "quantity": float(line.quantity) if line.quantity else None,
                "unit": line.unit,
                "vat_rate": float(line.vat_rate) if line.vat_rate else None,
                "withholding_rate": float(line.withholding_rate) if line.withholding_rate else None,
                "vat_base": float(line.vat_base) if line.vat_base else None,
            }
            for line in transaction.lines
        ]
    }


@router.get('/by-number/{transaction_number}', response_model=TransactionResponse)
def get_by_number(
    transaction_number: str,
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Fiş numarasına göre fiş getir
    """
    transaction = transaction_service.get_by_number(db, transaction_number)
    if not transaction:
        raise HTTPException(status_code=404, detail="Fiş bulunamadı")
    return transaction


@router.post('/', response_model=TransactionResponse, status_code=201)
def create_transaction(
    transaction_data: TransactionCreate,
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Yeni muhasebe fişi oluştur
    
    Fiş satırlarını da birlikte oluşturur (cascade).
    """
    return transaction_service.create_transaction(db, transaction_data)


@router.put('/{id}', response_model=TransactionResponse)
def update_transaction(
    id: int,
    transaction_data: TransactionCreate,
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Muhasebe fişini güncelle
    """
    return transaction_service.update_transaction(db, id, transaction_data)


@router.delete('/{id}', status_code=204)
def delete_transaction(
    id: int,
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Muhasebe fişini sil (satırları da cascade ile silinir)
    """
    transaction_service.delete_transaction(db, id)
    return None
