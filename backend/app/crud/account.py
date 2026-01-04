"""Account CRUD operations"""
from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.account import Account
from app.schemas.account import AccountCreate

def get_account(db: Session, account_id: int) -> Optional[Account]:
    """Tek hesap getir"""
    return db.query(Account).filter(Account.id == account_id).first()

def get_account_by_code(db: Session, code: str) -> Optional[Account]:
    """Hesap koduna göre getir"""
    return db.query(Account).filter(Account.code == code).first()

def get_accounts(db: Session, skip: int = 0, limit: int = 200, is_active: bool = True) -> List[Account]:
    """Hesapları listele"""
    query = db.query(Account)
    if is_active:
        query = query.filter(Account.is_active == True)
    return query.order_by(Account.code).offset(skip).limit(limit).all()

def create_account(db: Session, account: AccountCreate) -> Account:
    """Yeni hesap oluştur"""
    db_account = Account(**account.dict())
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account

def update_account(db: Session, account_id: int, account: AccountCreate) -> Optional[Account]:
    """Hesap güncelle"""
    db_account = get_account(db, account_id)
    if not db_account:
        return None
    
    for key, value in account.dict().items():
        setattr(db_account, key, value)
    
    db.commit()
    db.refresh(db_account)
    return db_account

def delete_account(db: Session, account_id: int) -> bool:
    """Hesap sil (soft delete - is_active=False)"""
    db_account = get_account(db, account_id)
    if not db_account:
        return False
    
    db_account.is_active = False
    db.commit()
    return True
