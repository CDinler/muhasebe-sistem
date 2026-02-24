"""E-Invoice domain schemas - Migrated from app.schemas.einvoice"""
from pydantic import BaseModel, Field, field_validator, computed_field
from typing import Optional, Dict, Any, List
from datetime import date, datetime
from decimal import Decimal


class TaxDetail(BaseModel):
    """Vergi detayı şeması"""
    id: Optional[int] = None
    tax_type_code: Optional[str] = None
    tax_name: Optional[str] = None
    tax_percent: Optional[float] = None
    taxable_amount: Optional[float] = None
    tax_amount: Optional[float] = None
    currency_code: Optional[str] = "TRY"
    exemption_reason_code: Optional[str] = None
    exemption_reason: Optional[str] = None
    
    class Config:
        from_attributes = True


class InvoiceLineItem(BaseModel):
    """Fatura satır kalemi şeması"""
    id: Optional[str] = None
    item_name: Optional[str] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None
    unit_price: Optional[float] = None
    currency: Optional[str] = "TRY"
    line_total: Optional[float] = None
    tax_amount: Optional[float] = None
    tax_percent: Optional[float] = None
    # İmport için ek alanlar
    category: Optional[str] = None  # hizmet_maliyet, genel_yonetim, ticari_mal, diger_stok, demirbaş, taşıt
    account_code: Optional[str] = None  # Seçilen hesap kodu
    fixed_asset_category: Optional[str] = None  # Demirbaş kategorisi (Konteyner, Makine, vb.)


class EInvoiceBase(BaseModel):
    """E-Fatura temel şeması"""
    invoice_number: str
    issue_date: date
    invoice_uuid: Optional[str] = None
    invoice_profile: Optional[str] = None
    invoice_type: Optional[str] = None
    
    buyer_name: Optional[str] = None
    buyer_tax_number: Optional[str] = None
    buyer_tax_office: Optional[str] = None
    
    supplier_name: str
    supplier_tax_number: Optional[str] = None
    supplier_tax_office: Optional[str] = None
    supplier_address: Optional[str] = None
    supplier_city: Optional[str] = None
    supplier_district: Optional[str] = None
    supplier_iban: Optional[str] = None
    
    customer_name: Optional[str] = None
    customer_tax_number: Optional[str] = None
    
    currency_code: str = "TRY"
    exchange_rate: Optional[Decimal] = None
    
    line_extension_amount: Decimal = Decimal("0")
    allowance_total: Optional[Decimal] = None
    charge_total: Optional[Decimal] = None
    tax_exclusive_amount: Optional[Decimal] = None
    tax_inclusive_amount: Optional[Decimal] = None
    payable_amount: Decimal
    
    total_tax_amount: Optional[Decimal] = None
    withholding_tax_amount: Optional[Decimal] = None
    withholding_percent: Optional[Decimal] = None
    withholding_code: Optional[str] = None
    cost_center_id: Optional[int] = None
    
    payment_due_date: Optional[date] = None
    order_number: Optional[str] = None
    order_date: Optional[date] = None
    waybill_number: Optional[str] = None
    waybill_date: Optional[date] = None
    signing_time: Optional[datetime] = None
    
    processing_status: str = "IMPORTED"


class EInvoiceCreate(EInvoiceBase):
    """E-Fatura oluşturma şeması"""
    pass


class EInvoiceUpdate(BaseModel):
    """E-Fatura güncelleme şeması"""
    processing_status: Optional[str] = None
    error_message: Optional[str] = None
    contact_id: Optional[int] = None
    transaction_id: Optional[int] = None
    cost_center_id: Optional[int] = None


class EInvoice(EInvoiceBase):
    """E-Fatura yanıt şeması"""
    id: int
    contact_id: Optional[int] = None
    contact_iban: Optional[str] = None  # Contact'tan gelen IBAN (öncelikli)
    transaction_id: Optional[int] = None
    cost_center_id: Optional[int] = None
    xml_file_path: Optional[str] = None
    pdf_path: Optional[str] = None
    invoice_category: Optional[str] = None
    processing_status: str
    error_message: Optional[str] = None
    raw_data: Optional[Any] = None  # JSON column - XML data as dict
    
    @computed_field
    @property
    def invoice_lines(self) -> List[InvoiceLineItem]:
        """raw_data'dan fatura kalemlerini parse et"""
        if not self.raw_data or not isinstance(self.raw_data, dict):
            return []
        
        lines = self.raw_data.get('invoice_lines', [])
        if not lines:
            return []
        
        return [InvoiceLineItem(**line) for line in lines if isinstance(line, dict)]
    
    @computed_field
    @property
    def tax_details(self) -> List[TaxDetail]:
        """raw_data'dan vergi detaylarını parse et"""
        if not self.raw_data or not isinstance(self.raw_data, dict):
            return []
        
        taxes = self.raw_data.get('tax_details', [])
        if not taxes:
            return []
        
        return [TaxDetail(**tax) for tax in taxes if isinstance(tax, dict)]
    
    class Config:
        from_attributes = True


class EInvoiceSummary(BaseModel):
    """E-Fatura özet şeması"""
    total_count: int
    total_amount: Decimal
    parsed_count: int
    imported_count: int
    error_count: int
    pending_count: int
    
    # Kategorilere göre ayrım
    incoming_count: int = 0
    incoming_amount: Decimal = Decimal("0")
    incoming_archive_count: int = 0
    incoming_archive_amount: Decimal = Decimal("0")
    outgoing_count: int = 0
    outgoing_amount: Decimal = Decimal("0")
    problematic_count: int = 0
    problematic_amount: Decimal = Decimal("0")


__all__ = [
    'TaxDetail',
    'InvoiceLineItem',
    'EInvoiceBase',
    'EInvoiceCreate',
    'EInvoiceUpdate',
    'EInvoice',
    'EInvoiceSummary',
]
