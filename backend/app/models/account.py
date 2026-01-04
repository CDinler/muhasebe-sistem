"""
Account model - Hesap planı
Luca-compatible: accounts table
"""
from sqlalchemy import Column, Integer, String, Boolean
from app.core.database import Base


class Account(Base):
    """Hesap Planı"""
    __tablename__ = "accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)  # HESAP KODU (100, 320, etc.)
    name = Column(String(200), nullable=False)  # HESAP ADI
    account_type = Column(String(50), nullable=False)  # asset, liability, equity, income, expense
    is_active = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<Account {self.code} - {self.name}>"
