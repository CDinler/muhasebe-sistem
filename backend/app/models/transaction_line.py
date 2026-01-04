"""
TransactionLine model - Fiş satırları
Luca-compatible: transaction_lines table
"""
from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, Text
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
