"""
LucaBordro model - Luca'dan import edilen bordro kayıtları
"""
from sqlalchemy import Column, Integer, String, Date, Numeric, Index, TIMESTAMP
from sqlalchemy.sql import func
from app.core.database import Base


class LucaBordro(Base):
    """Luca'dan import edilen aylık bordro kayıtları"""
    __tablename__ = "luca_bordro"

    id = Column(Integer, primary_key=True, index=True)
    
    # Dönem
    yil = Column(Integer, nullable=False, index=True)
    ay = Column(Integer, nullable=False, index=True)
    donem = Column(String(7), nullable=False, index=True)  # "2026-01"
    
    # Personel
    sira_no = Column(Integer, nullable=True)
    adi_soyadi = Column(String(200), nullable=False)
    tckn = Column(String(11), nullable=False, index=True)
    ssk_sicil_no = Column(String(20), nullable=True)
    
    # Tarihler (Luca bordro eşleştirmesi için kritik)
    giris_t = Column(Date, nullable=True, index=True)
    cikis_t = Column(Date, nullable=True)
    
    # Çalışma günü
    t_gun = Column(Integer, default=30)
    
    # Kazanç
    nor_kazanc = Column(Numeric(18, 2), default=0)
    dig_kazanc = Column(Numeric(18, 2), default=0)
    top_kazanc = Column(Numeric(18, 2), default=0)
    ssk_m = Column(Numeric(18, 2), default=0)  # SSK Matrahı
    g_v_m = Column(Numeric(18, 2), default=0)  # Gelir Vergisi Matrahı
    
    # Kesintiler (İşçi payları)
    ssk_isci = Column(Numeric(18, 2), default=0)
    iss_p_isci = Column(Numeric(18, 2), default=0)
    gel_ver = Column(Numeric(18, 2), default=0)
    damga_v = Column(Numeric(18, 2), default=0)
    
    # Özel kesintiler
    oz_kesinti = Column(Numeric(18, 2), default=0)  # Toplam özel kesinti
    oto_kat_bes = Column(Numeric(18, 2), default=0)
    icra = Column(Numeric(18, 2), default=0)
    avans = Column(Numeric(18, 2), default=0)
    
    # Net ödenen
    n_odenen = Column(Numeric(18, 2), default=0)
    
    # İşveren payları
    isveren_maliyeti = Column(Numeric(18, 2), default=0)
    ssk_isveren = Column(Numeric(18, 2), default=0)
    iss_p_isveren = Column(Numeric(18, 2), default=0)
    
    # Kanun ve teşvik
    kanun = Column(String(10), default="05510")
    ssk_tesviki = Column(Numeric(18, 2), default=0)
    
    # Upload bilgisi
    upload_date = Column(TIMESTAMP, server_default=func.now())
    file_name = Column(String(500), nullable=True)
    
    # İşlem durumu
    is_processed = Column(Integer, default=0)
    contract_id = Column(Integer, nullable=True)
    
    # Sistem
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    created_by = Column(Integer, nullable=True)
    updated_by = Column(Integer, nullable=True)

    def __repr__(self):
        return f"<LucaBordro {self.donem} - {self.tckn}>"

    __table_args__ = (
        Index('ix_luca_donem_tckn', 'donem', 'tckn'),
        Index('ix_luca_donem_giris', 'donem', 'giris_t'),
    )
