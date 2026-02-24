"""
PayrollCalculation model - Hesaplanan aylık bordro kayıtları
"""
from sqlalchemy import Column, Integer, String, Date, Numeric, ForeignKey, Index, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class PayrollCalculation(Base):
    """Hesaplanmış aylık bordro kayıtları"""
    __tablename__ = "payroll_calculations"

    id = Column(Integer, primary_key=True, index=True)
    
    # Dönem
    yil = Column(Integer, nullable=False, index=True)
    ay = Column(Integer, nullable=False, index=True)
    donem = Column(String(7), nullable=False, index=True)  # "2025-12"
    
    # Personel ve sözleşme
    personnel_id = Column(Integer, ForeignKey('personnel.id'), nullable=False, index=True)
    contract_id = Column(Integer, ForeignKey('personnel_contracts.id'), nullable=True)  # Nullable: Sözleşme olmadan da bordro hesaplanabilir
    draft_contract_id = Column(Integer, ForeignKey('personnel_draft_contracts.id'), nullable=True)  # TASLAK kayıtlar için draft contract
    luca_bordro_id = Column(Integer, ForeignKey('luca_bordro.id'), nullable=True)
    puantaj_id = Column(Integer, ForeignKey('monthly_puantaj.id'), nullable=True)
    
    tckn = Column(String(11), nullable=False, index=True)
    adi_soyadi = Column(String(200), nullable=False)
    
    # Maliyet Merkezi
    cost_center_id = Column(Integer, ForeignKey('cost_centers.id'), nullable=True)
    maliyet_merkezi = Column(String(200), nullable=True)
    
    # Ücret tipi
    ucret_nevi = Column(String(20), nullable=True)  # MAKTU_AYLIK, AYLIK, GUNLUK (Nullable: Sözleşme yoksa NULL)
    kanun_tipi = Column(String(10), default="05510")
    
    # --- MAAŞ 1 (Luca'dan gelen) ---
    maas1_net_odenen = Column(Numeric(18, 2), default=0)
    maas1_icra = Column(Numeric(18, 2), default=0)
    maas1_bes = Column(Numeric(18, 2), default=0)
    maas1_avans = Column(Numeric(18, 2), default=0)
    maas1_gelir_vergisi = Column(Numeric(18, 2), default=0)
    maas1_damga_vergisi = Column(Numeric(18, 2), default=0)
    maas1_ssk_isci = Column(Numeric(18, 2), default=0)
    maas1_issizlik_isci = Column(Numeric(18, 2), default=0)
    maas1_ssk_isveren = Column(Numeric(18, 2), default=0)
    maas1_issizlik_isveren = Column(Numeric(18, 2), default=0)
    maas1_ssk_tesviki = Column(Numeric(18, 2), default=0)
    
    # --- MAAŞ 2 (Sözleşmede anlaşılan - hesaplanan) ---
    maas2_anlaşilan = Column(Numeric(18, 2), default=0)  # Sözleşmedeki ücret
    
    # Hesaplanan detaylar (335.xxxxx hesapları)
    maas2_normal_calismasi = Column(Numeric(18, 2), default=0)  # Normal çalışma ücreti
    maas2_hafta_tatili = Column(Numeric(18, 2), default=0)       # Hafta tatili ücreti
    maas2_fm_calismasi = Column(Numeric(18, 2), default=0)       # Fazla mesai ücreti
    maas2_em_calismasi = Column(Numeric(18, 2), default=0)       # Eksik mesai kesintisi
    maas2_resmi_tatil = Column(Numeric(18, 2), default=0)        # Resmi tatil ücreti
    maas2_tatil_calismasi = Column(Numeric(18, 2), default=0)    # Tatil çalışması ücreti
    maas2_toplam_tatil_calismasi = Column(Numeric(18, 2), default=0)  # Toplam tatil çalışması (hafta+resmi+tatil)
    maas2_yillik_izin = Column(Numeric(18, 2), default=0)        # Yıllık izin ücreti
    maas2_yol = Column(Numeric(18, 2), default=0)                # Yol parası
    maas2_prim = Column(Numeric(18, 2), default=0)               # Prim
    maas2_ikramiye = Column(Numeric(18, 2), default=0)           # İkramiye
    maas2_bayram = Column(Numeric(18, 2), default=0)             # Bayram harçlığı
    maas2_kira = Column(Numeric(18, 2), default=0)               # Kira yardımı
    maas2_toplam = Column(Numeric(18, 2), default=0)             # Yukarıdakilerin toplamı
    
    # Puantaj detayları (gün/saat) - ppg'den gelen değerler
    normal_gun = Column(Numeric(5, 2), default=0)
    hafta_tatili_gun = Column(Numeric(5, 2), default=0)
    fazla_mesai_saat = Column(Numeric(7, 2), default=0)
    eksik_mesai_saat = Column(Numeric(7, 2), default=0)  # Eksik mesai saati (ppg'den)
    tatil_mesai_gun = Column(Numeric(5, 2), default=0)
    yillik_izin_gun = Column(Numeric(5, 2), default=0)
    
    # --- ELDEN ÖDEME ---
    elden_ucret_ham = Column(Numeric(18, 2), default=0)         # Yuvarlama öncesi ham tutar
    elden_ucret_yuvarlanmis = Column(Numeric(18, 2), default=0) # 100'e yuvarlanmış
    elden_yuvarlama = Column(Numeric(18, 2), default=0)         # Fark (yuvarlanmış - ham)
    elden_yuvarlama_yon = Column(String(10), nullable=True)     # YUKARI / ASAGI
    
    # Hesap kodu
    account_code_335 = Column(String(20), nullable=True)  # 335.1305 gibi
    
    # Yevmiye tipi
    yevmiye_tipi = Column(String(10), nullable=True)  # A, B, C
    
    # Fiş bilgisi
    transaction_id = Column(Integer, ForeignKey('transactions.id'), nullable=True)
    fis_no = Column(String(50), nullable=True)
    
    # Durum
    is_approved = Column(Integer, default=0)  # Onaylandı mı?
    is_exported = Column(Integer, default=0)  # Fişe aktarıldı mı?
    has_error = Column(Integer, default=0)    # Hata var mı?
    error_message = Column(String(1000), nullable=True)
    
    # Notlar
    notes = Column(String(500), nullable=True)
    
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    calculated_by = Column(Integer, nullable=True)  # Kim hesapladı
    approved_by = Column(Integer, nullable=True)    # Kim onayladı
    
    # İlişkiler
    personnel = relationship("Personnel", back_populates="payroll_calculations")
    contract = relationship("PersonnelContract")
    luca_bordro = relationship("LucaBordro")
    puantaj = relationship("MonthlyPuantaj")
    cost_center = relationship("CostCenter")
    transaction = relationship("Transaction")

    def __repr__(self):
        return f"<PayrollCalculation {self.donem} - {self.tckn} - {self.yevmiye_tipi}>"

    __table_args__ = (
        Index('ix_payroll_donem_personnel', 'donem', 'personnel_id'),
        Index('ix_payroll_donem_santiye', 'donem', 'cost_center_id'),
    )
