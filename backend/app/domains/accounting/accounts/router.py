"""Account API router"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from .repository import account_repo

router = APIRouter()

@router.get("/")
def get_accounts(skip: int = 0, limit: int = 1000, db: Session = Depends(get_db)):
    accounts = account_repo.get_multi(db, skip, limit)
    total = account_repo.count(db)
    return {"items": accounts, "total": total}

@router.get("/{account_id}")
def get_account(account_id: int, db: Session = Depends(get_db)):
    account = account_repo.get(db, account_id)
    if not account:
        from app.core.exceptions import NotFoundException
        raise NotFoundException("Account", account_id)
    return account
