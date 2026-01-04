"""
Transaction Router (V2 API)

Muhasebe fişleri için DDD mimarisine uygun endpoint'ler.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app.core.database import get_db
from app.domains.accounting.transactions.service import transaction_service
from app.schemas.transaction import (
    TransactionResponse,
    TransactionCreate
)


router = APIRouter(tags=['Transactions (V2)'])


@router.get('/summary')
def get_summary(
    date_from: Optional[date] = Query(None, description='Başlangıç tarihi'),
    date_to: Optional[date] = Query(None, description='Bitiş tarihi'),
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


@router.get('/', response_model=dict)
def get_transactions(
    skip: int = Query(0, ge=0, description='Atlanacak kayıt sayısı'),
    limit: int = Query(50, ge=1, le=500, description='Maksimum kayıt sayısı'),
    date_from: Optional[date] = Query(None, description='Başlangıç tarihi'),
    date_to: Optional[date] = Query(None, description='Bitiş tarihi'),
    cost_center_id: Optional[int] = Query(None, description='Masraf merkezi ID'),
    document_type_id: Optional[int] = Query(None, description='Evrak tipi ID'),
    search: Optional[str] = Query(None, description='Arama (fiş no, açıklama, evrak no)'),
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
        search=search
    )
    return result


@router.get('/{id}', response_model=TransactionResponse)
def get_transaction(
    id: int,
    db: Session = Depends(get_db)
):
    """
    ID'ye göre fiş getir (satırlarıyla birlikte)
    """
    transaction = transaction_service.get_transaction(db, id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Fiş bulunamadı")
    return transaction


@router.get('/by-number/{transaction_number}', response_model=TransactionResponse)
def get_by_number(
    transaction_number: str,
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
    db: Session = Depends(get_db)
):
    """
    Muhasebe fişini güncelle
    """
    return transaction_service.update_transaction(db, id, transaction_data)


@router.delete('/{id}', status_code=204)
def delete_transaction(
    id: int,
    db: Session = Depends(get_db)
):
    """
    Muhasebe fişini sil (satırları da cascade ile silinir)
    """
    transaction_service.delete_transaction(db, id)
    return None
