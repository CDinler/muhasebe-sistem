"""Account API router (V2)"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.domains.auth.dependencies import get_current_user
from app.schemas.auth import UserInDB
from .repository import account_repo
from .schemas import AccountCreate, AccountUpdate, AccountResponse
from .models import Account

router = APIRouter(tags=["Accounts (V2)"])

@router.get("/")
def get_accounts(
    skip: int = 0,
    limit: int = 1000,
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Hesapları listele"""
    accounts = account_repo.get_multi(db, skip, limit)
    total = account_repo.count(db)
    
    # SQLAlchemy objelerini dict'e çevir
    items = [
        {
            "id": acc.id,
            "code": acc.code,
            "name": acc.name,
            "account_type": acc.account_type,
            "is_active": acc.is_active
        }
        for acc in accounts
    ]
    
    return {"items": items, "total": total}

@router.get("/{account_id}")
def get_account(
    account_id: int,
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Tek hesap getir"""
    account = account_repo.get(db, account_id)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Account with id {account_id} not found"
        )
    
    return {
        "id": account.id,
        "code": account.code,
        "name": account.name,
        "account_type": account.account_type,
        "is_active": account.is_active
    }

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_account(
    account_data: AccountCreate,
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Yeni hesap oluştur"""
    # Aynı kodlu hesap var mı kontrol et
    existing = db.query(Account).filter(Account.code == account_data.code).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Account with code {account_data.code} already exists"
        )
    
    # Yeni hesap oluştur
    account = Account(
        code=account_data.code,
        name=account_data.name,
        account_type=account_data.account_type,
        is_active=True
    )
    db.add(account)
    db.commit()
    db.refresh(account)
    
    return {
        "id": account.id,
        "code": account.code,
        "name": account.name,
        "account_type": account.account_type,
        "is_active": account.is_active
    }

@router.put("/{account_id}")
def update_account(
    account_id: int,
    account_data: AccountUpdate,
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Hesap güncelle"""
    account = account_repo.get(db, account_id)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Account with id {account_id} not found"
        )
    
    # Kod değişiyorsa, başka hesap kullanmıyor mu kontrol et
    if account_data.code and account_data.code != account.code:
        existing = db.query(Account).filter(Account.code == account_data.code).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Account with code {account_data.code} already exists"
            )
    
    # Güncelle
    update_data = account_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(account, field, value)
    
    db.commit()
    db.refresh(account)
    
    return {
        "id": account.id,
        "code": account.code,
        "name": account.name,
        "account_type": account.account_type,
        "is_active": account.is_active
    }

@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_account(
    account_id: int,
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Hesap sil"""
    account = account_repo.get(db, account_id)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Account with id {account_id} not found"
        )
    
    db.delete(account)
    db.commit()
    return None
