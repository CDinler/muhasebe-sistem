"""
Transaction Models - Accounting transactions and lines
"""
from sqlalchemy import Column, Integer, String, Date, ForeignKey, Numeric, Text, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base


class TransactionLine(Base):
    """Muhasebe fiş satırı"""
    __tablename__ = "transaction_lines"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=False, index=True)        
    
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False, index=True)  # HESAP       
    contact_id = Column(Integer, ForeignKey("contacts.id"), nullable=True)  # EVRAK UNVAN (cari)       

    description = Column(Text)  # AÇIKLAMA

    debit = Column(Numeric(18, 2), default=0)  # BORÇ
    credit = Column(Numeric(18, 2), default=0)  # ALACAK
    quantity = Column(Numeric(18, 4), nullable=True)  # MİKTAR
    unit = Column(String(20), nullable=True)  # BİRİM
    
    # KDV ve Tevkifat bilgileri
    vat_rate = Column(Numeric(5, 4), nullable=True)  # KDV Oranı (%1=0.01, %10=0.10, %20=0.20)
    withholding_rate = Column(Numeric(5, 4), nullable=True)  # Tevkifat Oranı (4/10=0.40, 9/10=0.90)
    vat_base = Column(Numeric(18, 2), nullable=True)  # KDV Matrahı (hesaplanan KDV için)

    # Relationships
    transaction = relationship("Transaction", back_populates="lines")
    account = relationship("Account")
    contact = relationship("Contact")

    def __repr__(self):
        return f"<TransactionLine {self.id} - Account: {self.account_id} - Debit: {self.debit} - Credit: {self.credit}>"


class Transaction(Base):
    """Muhasebe fişi (Fiş başlığı)"""
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    transaction_number = Column(String(50), unique=True, nullable=False, index=True)  # FİŞ NO
    transaction_date = Column(Date, nullable=False, index=True)  # EVRAK TARİHİ
    accounting_period = Column(String(7), nullable=False, index=True)  # İLGİLİ DÖNEM (2025-12)
    
    cost_center_id = Column(Integer, ForeignKey("cost_centers.id"))  # ŞANTİYE
    
    # Personel eşleştirmesi (bordro, avans, icra vb.)
    # Not: İsim yerine personnel_id kullanılır (aynı isimli personeller olabilir)
    personnel_id = Column(Integer, ForeignKey("personnel.id"), nullable=True, index=True)
    
    description = Column(Text)  # FİŞ AÇIKLAMA
    
    # Document info
    document_number = Column(String(100))  # EVRAK NO (dekont no, banka kayıt no, vb.)
    
    # DEPRECATED: Use invoice_transaction_mappings junction table instead
    # This field will be removed in future version
    related_invoice_number = Column(String(100))  # [DEPRECATED] İLGİLİ FATURA NO
    
    # Document type fields (normalized)
    document_type_id = Column(Integer, ForeignKey("document_types.id"), index=True)
    
    # Taslak yevmiye kaydı mı? (True: Taslak, False: Resmi)
    draft = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    lines = relationship("TransactionLine", back_populates="transaction", cascade="all, delete-orphan")
    cost_center = relationship("CostCenter", back_populates="transactions")
    doc_type = relationship("DocumentType", foreign_keys=[document_type_id])
    personnel = relationship("Personnel", back_populates="transactions")
    
    @property
    def document_type(self) -> str:
        """Evrak türü adı"""
        return self.doc_type.name if self.doc_type else None


__all__ = ['Transaction', 'TransactionLine']
