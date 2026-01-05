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
        from app.models.invoice_transaction_mapping import InvoiceTransactionMapping
        
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
