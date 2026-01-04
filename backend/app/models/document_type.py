"""
Document Type models - Evrak sınıflandırma lookup tabloları
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class DocumentType(Base):
    """Ana evrak tipi lookup tablosu"""
    __tablename__ = "document_types"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)  # ALIS_FATURA, SATIS_FATURA, etc.
    name = Column(String(100), unique=True, nullable=False)  # Alış Faturası, Satış Faturası, etc.
    category = Column(String(50), nullable=False, index=True)  # FATURA, KASA, BANKA, PERSONEL, VERGI, DIGER
    is_active = Column(Boolean, default=True, index=True)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<DocumentType {self.code}: {self.name}>"


class DocumentSubtype(Base):
    """Alt evrak tipi lookup tablosu"""
    __tablename__ = "document_subtypes"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)  # E_FATURA, E_ARSIV, NAKIT, etc.
    parent_code = Column(String(50), nullable=True, index=True)  # ALIS_FATURA, SATIS_FATURA, etc. (parent document type code)
    name = Column(String(100), unique=True, nullable=False)  # E-Fatura, E-Arşiv, Nakit, etc.
    category = Column(String(50), nullable=False, index=True)  # E_BELGE, KASA, BANKA, DIGER
    is_active = Column(Boolean, default=True, index=True)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<DocumentSubtype {self.code}: {self.name}>"
