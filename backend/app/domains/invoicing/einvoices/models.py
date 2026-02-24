from sqlalchemy import Column, Integer, String, Date, Time, Numeric, Text, TIMESTAMP, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import select
from decimal import Decimal
from app.core.database import Base


class EInvoice(Base):
    """
    E-Fatura modeli - UBL-TR 1.2 şemasına uygun
    
    XML dosyalarından parse edilen e-fatura verileri bu tabloya kaydedilir.
    Her kayıt bir XML dosyasına karşılık gelir (xml_hash ile mükerrer kontrol).
    """
    __tablename__ = "einvoices"

    id = Column(Integer, primary_key=True, index=True)
    
    # ========== XML TRACKING ==========
    xml_file_path = Column(String(500), unique=False, nullable=True, 
                           comment='XML dosyasinin tam yolu (PDF-only için NULL)')
    xml_hash = Column(String(64), unique=False, nullable=True, index=True,
                     comment='SHA256 hash - mukerrer kontrol (PDF-only için NULL)')
    invoice_category = Column(String(50), default='incoming', index=True,
                             comment='incoming/outgoing/incoming-archive/outgoing-archive')
    
    # ========== INVOICE CORE (UBL-TR) ==========
    invoice_uuid = Column(String(36), unique=True, nullable=False, index=True,
                         comment='cbc:UUID - Fatura ETTN')
    invoice_number = Column(String(50), nullable=False, index=True,
                           comment='cbc:ID - Fatura numarasi')
    invoice_profile = Column(String(100),
                            comment='cbc:ProfileID - TEMELFATURA, TICARIFATURA, EARSIVFATURA')
    invoice_type = Column(String(50),
                         comment='cbc:InvoiceTypeCode - SATIS, IADE, TEVKIFAT')
    
    # ========== DATES ==========
    issue_date = Column(Date, nullable=False, index=True,
                       comment='cbc:IssueDate - Duzenlenme tarihi')
    issue_time = Column(Time,
                       comment='cbc:IssueTime - Duzenlenme saati')
    tax_point_date = Column(Date,
                           comment='cbc:TaxPointDate - Vergilendirme tarihi')
    signing_time = Column(TIMESTAMP,
                         comment='SigningTime - Fatura imzalanma zamani (XML SigningTime)')
    
    # ========== SUPPLIER (Satici) - 10 alan ==========
    supplier_tax_number = Column(String(11), index=True,
                                 comment='VKN/TCKN - Satici vergi kimlik no')
    supplier_id_scheme = Column(String(10),
                               comment='VKN veya TCKN')
    supplier_name = Column(String(255),
                          comment='Satici unvan')
    supplier_address = Column(Text,
                             comment='Satici adres')
    supplier_city = Column(String(100),
                          comment='Satici sehir')
    supplier_district = Column(String(100),
                              comment='Satici ilce')
    supplier_postal_code = Column(String(10),
                                  comment='Satici posta kodu')
    supplier_tax_office = Column(String(100),
                                 comment='Satici vergi dairesi')
    supplier_email = Column(String(255),
                           comment='Satici e-posta')
    supplier_phone = Column(String(20),
                           comment='Satici telefon')
    supplier_iban = Column(String(34),
                          comment='Satici IBAN numarasi (PayeeFinancialAccount/ID)')
    
    # ========== CUSTOMER (Alici) - 2 alan ==========
    customer_tax_number = Column(String(11),
                                 comment='VKN/TCKN - Alici vergi kimlik no')
    customer_name = Column(String(255),
                          comment='Alici unvan')
    
    # ========== AMOUNTS (Tutarlar) - 8 alan ==========
    currency_code = Column(String(3), default='TRY',
                          comment='Para birimi kodu (TRY, USD, EUR, vb)')
    exchange_rate = Column(Numeric(10, 4),
                          comment='Doviz kuru (varsa)')
    line_extension_amount = Column(Numeric(18, 2),
                                   comment='cbc:LineExtensionAmount - Mal hizmet toplam tutari')
    tax_exclusive_amount = Column(Numeric(18, 2),
                                  comment='cbc:TaxExclusiveAmount - Vergiler haric tutar')
    tax_inclusive_amount = Column(Numeric(18, 2),
                                  comment='cbc:TaxInclusiveAmount - Vergiler dahil tutar')
    payable_amount = Column(Numeric(18, 2),
                           comment='cbc:PayableAmount - Odenecek tutar')
    allowance_total = Column(Numeric(18, 2),
                            comment='Toplam indirim')
    charge_total = Column(Numeric(18, 2),
                         comment='Toplam artirim')
    
    # ========== TAX (Vergiler) - 4 alan ==========
    total_tax_amount = Column(Numeric(18, 2),
                             comment='KDV toplami')
    withholding_tax_amount = Column(Numeric(18, 2),
                                   comment='Tevkifat tutari')
    withholding_percent = Column(Numeric(5, 2),
                                comment='Tevkifat orani')
    withholding_code = Column(String(10),
                             comment='Tevkifat kodu')
    
    # ========== FOREIGN KEYS (Iliskiler) - 4 alan ========== 
    contact_id = Column(Integer, ForeignKey('contacts.id', ondelete='SET NULL'),
                       nullable=True, index=True,
                       comment='contacts tablosu ile iliski')
    transaction_id = Column(Integer, ForeignKey('transactions.id', ondelete='SET NULL'),
                           nullable=True, index=True,
                           comment='transactions tablosu ile iliski')
    cost_center_id = Column(Integer, ForeignKey('cost_centers.id', ondelete='SET NULL'),
                           nullable=True, index=True,
                           comment='cost_centers tablosu ile iliski (maliyet merkezi)')
    imported_by = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'),
                        nullable=True,
                        comment='Import eden kullanici')

    # Relationship
    cost_center = relationship('CostCenter', backref='einvoices')
    transaction_mappings = relationship(
        'InvoiceTransactionMapping',
        back_populates='einvoice',
        lazy='selectin'
    )
    
    # ========== PAYMENT TRACKING COMPUTED PROPERTIES ==========
    
    @hybrid_property
    def paid_amount(self) -> Decimal:
        """
        Faturaya yapılan toplam ödeme tutarı
        invoice_transaction_mappings tablosundaki payment_amount kolonlarının toplamı
        """
        from app.models import InvoiceTransactionMapping
        
        if not self.id:
            return Decimal('0.00')
        
        # Eğer relationship yüklenmişse onu kullan
        if hasattr(self, 'transaction_mappings') and self.transaction_mappings:
            total = sum(
                mapping.payment_amount or Decimal('0.00')
                for mapping in self.transaction_mappings
                if mapping.payment_amount is not None
            )
            return Decimal(str(total))
        
        # Yoksa query ile al
        from sqlalchemy.orm import Session
        from sqlalchemy import inspect
        
        session = inspect(self).session
        if session:
            result = session.execute(
                select(func.coalesce(func.sum(InvoiceTransactionMapping.payment_amount), 0))
                .where(InvoiceTransactionMapping.einvoice_id == self.id)
                .where(InvoiceTransactionMapping.payment_amount.isnot(None))
            ).scalar()
            return Decimal(str(result or 0))
        
        return Decimal('0.00')
    
    @hybrid_property
    def remaining_amount(self) -> Decimal:
        """
        Faturanın kalan ödenecek tutarı
        payable_amount - paid_amount
        """
        if not self.payable_amount:
            return Decimal('0.00')
        return Decimal(str(self.payable_amount)) - self.paid_amount
    
    @hybrid_property
    def payment_status(self) -> str:
        """
        Fatura ödeme durumu
        - UNPAID: Hiç ödeme yapılmamış
        - PARTIALLY_PAID: Kısmi ödeme yapılmış
        - PAID: Tam ödenmiş
        - OVERPAID: Fazla ödenmiş (hata durumu)
        """
        if not self.payable_amount or self.payable_amount <= 0:
            return 'UNKNOWN'
        
        paid = self.paid_amount
        total = Decimal(str(self.payable_amount))
        
        if paid <= 0:
            return 'UNPAID'
        elif paid < total:
            return 'PARTIALLY_PAID'
        elif paid == total:
            return 'PAID'
        else:
            return 'OVERPAID'
    
    @hybrid_property
    def payment_percentage(self) -> float:
        """
        Ödeme yüzdesi (0-100)
        """
        if not self.payable_amount or self.payable_amount <= 0:
            return 0.0
        
        paid = float(self.paid_amount)
        total = float(self.payable_amount)
        
        return min(100.0, (paid / total) * 100)
    
    # ========== STATUS (Durum) - 2 alan ==========
    processing_status = Column(String(50), default='IMPORTED', index=True,
                              comment='IMPORTED, MATCHED, TRANSACTION_CREATED, ERROR')
    error_message = Column(Text,
                          comment='Hata mesaji')
    
    # ========== RAW DATA (Ham veri) - 1 alan ==========
    raw_data = Column(JSON,
                     comment='Orijinal XML verisi JSON formatinda')
    
    # ========== PDF SUPPORT - 3 alan ==========
    pdf_path = Column(String(500), nullable=True, index=True,
                     comment='PDF dosyasinin relative path\'i (data/einvoice_pdfs/... dan itibaren)')
    has_xml = Column(Integer, default=1, nullable=False, index=True,
                    comment='XML dosyası var mı? 0 ise sadece PDF\'den parse edilmiş')
    source = Column(String(50), default='xml', nullable=False,
                   comment='Kaynak: xml, pdf_only, manual, api')
    
    # ========== METADATA - 2 alan ==========
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
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
from sqlalchemy import Column, Integer, String, TIMESTAMP, Numeric, ForeignKey, Enum, Text, Date
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class InvoiceTransactionMapping(Base):
    """
    Junction table for E-Invoice <-> Transaction relationships
    
    Preserves mappings even when transactions are recreated (e.g., during bordro updates).
    Allows many-to-many relationships and stores mapping metadata.
    
    PAYMENT TRACKING:
    - payment_amount NULL = Sadece muhasebe ilişkisi (örn: alış faturası kaydı)
    - payment_amount dolu = Ödeme kaydı (örn: banka havalesi, kasa ödeme)
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
    
    # PAYMENT TRACKING - Ödeme Takip Sistemi
    payment_amount = Column(Numeric(18, 2), nullable=True, index=True,
                          comment='Bu fiş ile yapılan ödeme tutarı (NULL = ödeme değil)')
    payment_date = Column(Date, nullable=True, index=True,
                        comment='Ödeme tarihi (transaction.transaction_date cache)')
    payment_status = Column(Enum('pending', 'completed', 'cancelled', name='payment_status_enum'),
                          default='completed', nullable=True,
                          comment='Ödeme durumu (opsiyonel)')
    
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
    einvoice = relationship("EInvoice", back_populates="transaction_mappings")
    transaction = relationship("Transaction", backref="invoice_mappings")
    mapped_by_user = relationship("User", foreign_keys=[mapped_by])
