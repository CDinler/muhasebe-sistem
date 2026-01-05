"""
Document Type models - Evrak sınıflandırma lookup tabloları
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class DocumentType(Base):
    """Ana evrak tipi lookup tablosu"""
    __tablename__ = "document_types"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)  # ALIS_FATURA, SATIS_FATURA, etc.
    name = Column(String(100), unique=True, nullable=False)  # Alış Faturası, Satış Faturası, etc.
    category = Column(String(50), nullable=False, index=True)  # FATURA, KASA, BANKA, PERSONEL, VERGI, DIGER
    requires_subtype = Column(Boolean, default=False)  # Alt evrak türü seçimi zorunlu mu?
    is_active = Column(Boolean, default=True, index=True)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    subtypes = relationship("DocumentSubtype", back_populates="document_type", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<DocumentType {self.code}: {self.name}>"


class DocumentSubtype(Base):
    """Alt evrak tipi lookup tablosu"""
    __tablename__ = "document_subtypes"
    
    id = Column(Integer, primary_key=True, index=True)
    document_type_id = Column(Integer, ForeignKey('document_types.id', ondelete='CASCADE'), nullable=False, index=True)
    code = Column(String(50), nullable=False, index=True)  # E_FATURA, E_ARSIV, NAKIT, etc.
    parent_code = Column(String(50), nullable=True, index=True)  # DEPRECATED: Geriye dönük uyumluluk için tutuldu
    name = Column(String(100), nullable=False)  # E-Fatura, E-Arşiv, Nakit, etc.
    category = Column(String(50), nullable=True, index=True)  # E_BELGE, KASA, BANKA, DIGER (opsiyonel)
    is_active = Column(Boolean, default=True, index=True)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    document_type = relationship("DocumentType", back_populates="subtypes")
    
    def __repr__(self):
        return f"<DocumentSubtype {self.code}: {self.name}>"
