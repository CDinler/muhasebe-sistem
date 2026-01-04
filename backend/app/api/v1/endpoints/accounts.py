# -*- coding: utf-8 -*-
"""Account API endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.crud import account as crud
from app.schemas.account import AccountCreate, AccountResponse

router = APIRouter()

@router.get("/", response_model=List[AccountResponse])
def list_accounts(
    skip: int = 0,
    limit: int = 200,
    is_active: bool = True,
    db: Session = Depends(get_db)
):
    """Hesap planını listele"""
    accounts = crud.get_accounts(db, skip=skip, limit=limit, is_active=is_active)
    return accounts

@router.get("/{account_id}", response_model=AccountResponse)
def get_account(account_id: int, db: Session = Depends(get_db)):
    """Tek hesap detayı"""
    account = crud.get_account(db, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account

@router.get("/code/{code}", response_model=AccountResponse)
def get_account_by_code(code: str, db: Session = Depends(get_db)):
    """Hesap koduna göre getir"""
    account = crud.get_account_by_code(db, code)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account

@router.post("/", response_model=AccountResponse, status_code=201)
def create_account(account: AccountCreate, db: Session = Depends(get_db)):
    """Yeni hesap oluştur"""
    # Hesap kodu kontrolü
    existing = crud.get_account_by_code(db, account.code)
    if existing:
        raise HTTPException(status_code=400, detail="Account code already exists")
    
    return crud.create_account(db, account)

@router.put("/{account_id}", response_model=AccountResponse)
def update_account(
    account_id: int,
    account: AccountCreate,
    db: Session = Depends(get_db)
):
    """Hesap güncelle"""
    updated = crud.update_account(db, account_id, account)
    if not updated:
        raise HTTPException(status_code=404, detail="Account not found")
    return updated

@router.delete("/{account_id}", status_code=204)
def delete_account(account_id: int, db: Session = Depends(get_db)):
    """Hesap sil (soft delete)"""
    deleted = crud.delete_account(db, account_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Account not found")
    return None
