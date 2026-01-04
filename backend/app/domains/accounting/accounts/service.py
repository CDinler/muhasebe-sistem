"""Account service - Business logic"""
from sqlalchemy.orm import Session
from app.core.exceptions import BusinessException
from .repository import account_repo, AccountCreate

class AccountService:
    def create_account(self, db: Session, data: AccountCreate):
        # Business rule: Account code must be unique
        existing = db.query(account_repo.model).filter_by(account_code=data.account_code).first()
        if existing:
            raise BusinessException(f"Hesap kodu {data.account_code} zaten mevcut")
        return account_repo.create(db, data)

account_service = AccountService()
