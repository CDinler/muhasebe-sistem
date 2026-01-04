"""
Fatura vergi detayları modeli
XML'deki TaxSubtotal bilgilerini saklar
"""
from sqlalchemy import Column, Integer, String, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class InvoiceTax(Base):
    """
    E-Fatura vergi detayları
    
    XML'deki cac:TaxSubtotal elementlerinden parse edilen vergi bilgilerini saklar.
    Bir faturada birden fazla vergi tipi olabilir (KDV, ÖİV, ÖTV, Telsiz vb.)
    """
    __tablename__ = "invoice_taxes"

    id = Column(Integer, primary_key=True, index=True)
    
    # ========== İLİŞKİ ==========
    einvoice_id = Column(Integer, ForeignKey('einvoices.id', ondelete='CASCADE'),
                        nullable=False, index=True,
                        comment='Bağlı olduğu fatura')
    
    # ========== VERGİ BİLGİLERİ ==========
    tax_type_code = Column(String(10), nullable=False, index=True,
                          comment='Vergi kodu (0015=KDV, 4081=ÖİV, 8006=Telsiz, 9040=ÖTV vb)')
    tax_name = Column(String(100), nullable=False,
                     comment='Vergi adı (Katma Değer Vergisi, Özel İletişim Vergisi vb)')
    tax_percent = Column(Numeric(5, 2), nullable=False,
                        comment='Vergi oranı (%0, %1, %8, %10, %18, %20 vb)')
    
    # ========== TUTARLAR ==========
    taxable_amount = Column(Numeric(18, 2), nullable=False,
                           comment='Matrah tutarı (TaxableAmount)')
    tax_amount = Column(Numeric(18, 2), nullable=False,
                       comment='Hesaplanan vergi tutarı (TaxAmount)')
    
    currency_code = Column(String(3), default='TRY',
                          comment='Para birimi (genelde TRY)')
    
    # ========== EKSTRA BİLGİLER ==========
    exemption_reason_code = Column(String(10), nullable=True,
                                  comment='Vergi istisna kodu (varsa)')
    exemption_reason = Column(String(255), nullable=True,
                            comment='Vergi istisna sebebi (varsa)')
    
    # Relationship
    einvoice = relationship('EInvoice', backref='taxes')
