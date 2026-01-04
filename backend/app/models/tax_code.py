"""
UBL-TR Vergi Kodları Referans Tablosu
Resmi vergi kodları ve adlarını saklar
"""
from sqlalchemy import Column, String, Boolean
from app.core.database import Base


class TaxCode(Base):
    """
    Resmi UBL-TR Vergi Kodları Referans Tablosu
    Kaynak: UBL-TR Kod Listeleri - V 1.40 (Aralık 2025)
    """
    __tablename__ = "tax_codes"

    code = Column(String(10), primary_key=True, comment='Vergi Kodu (ör: 0015, 4081)')
    name = Column(String(200), nullable=False, comment='Resmi Vergi Adı')
    short_name = Column(String(50), nullable=True, comment='Kısa Ad/Kısaltma (ör: KDV GERCEK)')
    is_withholding = Column(Boolean, default=False, comment='Tevkifat kodu mu?')
    description = Column(String(500), nullable=True, comment='Açıklama')
    
    def __repr__(self):
        return f"<TaxCode {self.code}: {self.name}>"
