"""Account repository"""
from app.shared.base.repository import CRUDBase
from app.models.account import Account
from pydantic import BaseModel

class AccountCreate(BaseModel):
    account_code: str
    account_name: str

class AccountUpdate(BaseModel):
    account_name: str | None = None

class AccountRepository(CRUDBase[Account, AccountCreate, AccountUpdate]):
    pass

account_repo = AccountRepository(Account)
