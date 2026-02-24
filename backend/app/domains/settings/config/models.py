"""
SystemConfig model - Sistem konfigürasyon ayarları (oranlar vb)
"""
from sqlalchemy import Column, Integer, String, Numeric, Text, TIMESTAMP, Boolean
from sqlalchemy.sql import func
from app.core.database import Base


class SystemConfig(Base):
    """Sistem konfigürasyonu (SSK oranları, vergiler vb)"""
    __tablename__ = "system_config"

    id = Column(Integer, primary_key=True, index=True)
    
    config_key = Column(String(100), unique=True, nullable=False, index=True)
    config_value = Column(String(500), nullable=True)
    config_type = Column(String(50), default='STRING')  # STRING, NUMBER, JSON
    
    category = Column(String(100), nullable=True, index=True)  # SSK_ORANLAR, VERGI, vb
    description = Column(Text, nullable=True)
    
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<SystemConfig {self.config_key}={self.config_value}>"


class TaxBracket(Base):
    """Gelir Vergisi Dilimleri"""
    __tablename__ = "tax_bracket"

    id = Column(Integer, primary_key=True, index=True)
    
    # Dilim Bilgileri
    min_amount = Column(Numeric(15, 2), nullable=False, default=0)
    max_amount = Column(Numeric(15, 2), nullable=True)  # NULL = üst limit yok
    
    # Vergi Oranı
    tax_rate = Column(Numeric(5, 4), nullable=False)  # 0.15, 0.20, 0.27, 0.35, 0.40
    
    # Yıl
    year = Column(Integer, nullable=False, index=True)
    
    # Durum
    is_active = Column(Boolean, default=True)
    
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    def __repr__(self):
        return f"<TaxBracket {self.year}: {self.min_amount}-{self.max_amount} @ {self.tax_rate}>"


# Başlangıç verileri için örnek:
"""
SSK_ISCI_05510 = 0.14
SSK_ISVEREN_05510 = 0.2075
ISSIZLIK_ISCI_05510 = 0.01
ISSIZLIK_ISVEREN_05510 = 0.02
SSK_TESVIKI_05510 = 0.05

SSK_ISCI_00000 = 0.14
SSK_ISVEREN_00000 = 0.2075
ISSIZLIK_ISCI_00000 = 0.01
ISSIZLIK_ISVEREN_00000 = 0.02

SSK_ISCI_EMEKLI = 0.075
SSK_ISVEREN_EMEKLI = 0.2475
ISSIZLIK_ISCI_EMEKLI = 0
ISSIZLIK_ISVEREN_EMEKLI = 0
"""
