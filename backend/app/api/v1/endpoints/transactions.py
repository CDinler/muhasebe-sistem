# -*- coding: utf-8 -*-
"""Transaction API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app.core.database import get_db
from app.crud import transaction as crud
from app.schemas.transaction import TransactionCreate, TransactionResponse

router = APIRouter()

@router.get("/", response_model=List[TransactionResponse])
def list_transactions(
    skip: int = 0,
    limit: int = 100,  # Sayfa sayfa yükleme için
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    cost_center_id: Optional[int] = Query(None),
    order_by: Optional[str] = Query("date_desc", description="Sıralama: date_asc, date_desc, number_asc, number_desc"),
    search: Optional[str] = Query(None, description="Fiş no, açıklama, evrak türü/no ile arama"),
    db: Session = Depends(get_db)
):
    """Fişleri listele - Pagination ile"""
    transactions = crud.get_transactions(
        db, skip=skip, limit=limit,
        start_date=start_date, end_date=end_date,
        cost_center_id=cost_center_id,
        order_by=order_by,
        search=search
    )
    return transactions

@router.get("/count/total", response_model=dict)
def get_transactions_count(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    cost_center_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Toplam fiş sayısını döndür - Pagination için"""
    count = crud.get_transactions_count(
        db, start_date=start_date, end_date=end_date,
        cost_center_id=cost_center_id,
        search=search
    )
    return {"total": count}

@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(transaction_id: int, db: Session = Depends(get_db)):
    """Tek fiş detayı"""
    transaction = crud.get_transaction(db, transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction

@router.get("/number/{transaction_number}", response_model=TransactionResponse)
def get_transaction_by_number(transaction_number: str, db: Session = Depends(get_db)):
    """Fiş numarasına göre getir"""
    transaction = crud.get_transaction_by_number(db, transaction_number)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction

@router.post("/", response_model=TransactionResponse, status_code=201)
def create_transaction(transaction: TransactionCreate, db: Session = Depends(get_db)):
    """Yeni fiş oluştur"""
    # Fiş numarası kontrolü
    existing = crud.get_transaction_by_number(db, transaction.transaction_number)
    if existing:
        raise HTTPException(status_code=400, detail="Transaction number already exists")
    
    return crud.create_transaction(db, transaction)

@router.put("/{transaction_id}", response_model=TransactionResponse)
def update_transaction(
    transaction_id: int,
    transaction: TransactionCreate,
    db: Session = Depends(get_db)
):
    """Fişi güncelle"""
    updated = crud.update_transaction(db, transaction_id, transaction)
    if not updated:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return updated

@router.delete("/{transaction_id}", status_code=204)
def delete_transaction(transaction_id: int, db: Session = Depends(get_db)):
    """Fişi sil"""
    deleted = crud.delete_transaction(db, transaction_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return None
