"""
Transaction model - Fiş başlığı
Luca-compatible: transactions table
"""
from sqlalchemy import Column, Integer, String, Date, ForeignKey, Numeric, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


class Transaction(Base):
    """Muhasebe fişi (Fiş başlığı)"""
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    transaction_number = Column(String(50), unique=True, nullable=False, index=True)  # FİŞ NO
    transaction_date = Column(Date, nullable=False, index=True)  # EVRAK TARİHİ
    accounting_period = Column(String(7), nullable=False, index=True)  # İLGİLİ DÖNEM (2025-12)
    
    cost_center_id = Column(Integer, ForeignKey("cost_centers.id"))  # ŞANTİYE
    description = Column(Text)  # FİŞ AÇIKLAMA
    
    # Document info
    document_number = Column(String(100))  # EVRAK NO (dekont no, banka kayıt no, vb.)
    
    # DEPRECATED: Use invoice_transaction_mappings junction table instead
    # This field will be removed in future version
    related_invoice_number = Column(String(100))  # [DEPRECATED] İLGİLİ FATURA NO
    
    # Document type fields (normalized)
    document_type_id = Column(Integer, ForeignKey("document_types.id"), index=True)
    document_subtype_id = Column(Integer, ForeignKey("document_subtypes.id"), index=True)
    
    # Relationships
    lines = relationship("TransactionLine", back_populates="transaction", cascade="all, delete-orphan")
    cost_center = relationship("CostCenter", back_populates="transactions")
    doc_type = relationship("DocumentType", foreign_keys=[document_type_id])
    doc_subtype = relationship("DocumentSubtype", foreign_keys=[document_subtype_id])
    
    @property
    def document_type(self) -> str:
        """Evrak türü adı"""
        return self.doc_type.name if self.doc_type else None
    
    @property
    def document_subtype(self) -> str:
        """Evrak alt türü adı"""
        return self.doc_subtype.name if self.doc_subtype else None
    
    def __repr__(self):
        return f"<Transaction {self.transaction_number} - {self.accounting_period}>"
