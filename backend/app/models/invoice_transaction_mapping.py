from sqlalchemy import Column, Integer, String, TIMESTAMP, Numeric, ForeignKey, Enum, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class InvoiceTransactionMapping(Base):
    """
    Junction table for E-Invoice <-> Transaction relationships
    
    Preserves mappings even when transactions are recreated (e.g., during bordro updates).
    Allows many-to-many relationships and stores mapping metadata.
    """
    __tablename__ = "invoice_transaction_mappings"

    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign keys
    einvoice_id = Column(Integer, ForeignKey('einvoices.id', ondelete='CASCADE'), 
                        nullable=False, index=True)
    transaction_id = Column(Integer, ForeignKey('transactions.id', ondelete='CASCADE'), 
                           nullable=False, index=True)
    
    # Cached data for quick lookups
    document_number = Column(String(100), index=True,
                           comment='Cached invoice number for quick filtering')
    
    # Mapping metadata
    mapping_type = Column(Enum('auto', 'manual', name='mapping_type_enum'), 
                         default='auto', index=True,
                         comment='auto=system matched, manual=user created')
    confidence_score = Column(Numeric(3, 2), default=1.00,
                            comment='Match confidence: 0.00-1.00')
    mapped_by = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True,
                      comment='User who created manual mapping')
    mapped_at = Column(TIMESTAMP, server_default=func.now(),
                      comment='When mapping was created')
    notes = Column(Text, nullable=True,
                  comment='Optional notes about the mapping')
    
    # Relationships
    einvoice = relationship("EInvoice", backref="transaction_mappings")
    transaction = relationship("Transaction", backref="invoice_mappings")
    mapped_by_user = relationship("User", foreign_keys=[mapped_by])
