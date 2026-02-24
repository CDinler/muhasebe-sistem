"""
PersonnelPuantajGrid model - Excel benzeri puantaj girişi
"""
from sqlalchemy import Column, Integer, String, Enum, Index, ForeignKey, TIMESTAMP, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class PuantajDurum(str, enum.Enum):
    """Puantaj durum kodları - Luca uyumlu"""
    N = "N"  # Normal
    H = "H"  # Hafta Tatili
    T = "T"  # Resmi Tatil
    İ = "İ"  # İzinli
    S = "S"  # Yıllık İzin
    M = "M"  # Mesai
    R = "R"  # Raporlu
    E = "E"  # Eksik Gün
    Y = "Y"  # Yarım Gün
    G = "G"  # Gece Mesaisi
    O = "O"  # Gündüz Mesaisi
    K = "K"  # Yarım Gün Resmi Tatil
    C = "C"  # Yarım Gün Hafta Tatili
    MINUS = "-"  # Sigortası Olmayan Gün


class PersonnelPuantajGrid(Base):
    """Excel benzeri puantaj girişi - Her personel-dönem bir satır"""
    __tablename__ = "personnel_puantaj_grid"

    id = Column(Integer, primary_key=True, index=True)
    
    # Personel ve Dönem
    personnel_id = Column(Integer, ForeignKey('personnel.id'), nullable=False, index=True)
    # contract_id KALDIRILDI - Puantaj sadece personnel_id + donem ile ilişkilendirilir
    donem = Column(String(7), nullable=False, index=True)  # "2026-01"
    yil = Column(Integer, nullable=False)
    ay = Column(Integer, nullable=False)
    cost_center_id = Column(Integer, nullable=True, index=True)
    ayin_toplam_gun_sayisi = Column(Integer, default=30)
    
    # 31 Günlük Kolonlar
    gun_1 = Column(Enum(PuantajDurum), nullable=True)
    gun_2 = Column(Enum(PuantajDurum), nullable=True)
    gun_3 = Column(Enum(PuantajDurum), nullable=True)
    gun_4 = Column(Enum(PuantajDurum), nullable=True)
    gun_5 = Column(Enum(PuantajDurum), nullable=True)
    gun_6 = Column(Enum(PuantajDurum), nullable=True)
    gun_7 = Column(Enum(PuantajDurum), nullable=True)
    gun_8 = Column(Enum(PuantajDurum), nullable=True)
    gun_9 = Column(Enum(PuantajDurum), nullable=True)
    gun_10 = Column(Enum(PuantajDurum), nullable=True)
    gun_11 = Column(Enum(PuantajDurum), nullable=True)
    gun_12 = Column(Enum(PuantajDurum), nullable=True)
    gun_13 = Column(Enum(PuantajDurum), nullable=True)
    gun_14 = Column(Enum(PuantajDurum), nullable=True)
    gun_15 = Column(Enum(PuantajDurum), nullable=True)
    gun_16 = Column(Enum(PuantajDurum), nullable=True)
    gun_17 = Column(Enum(PuantajDurum), nullable=True)
    gun_18 = Column(Enum(PuantajDurum), nullable=True)
    gun_19 = Column(Enum(PuantajDurum), nullable=True)
    gun_20 = Column(Enum(PuantajDurum), nullable=True)
    gun_21 = Column(Enum(PuantajDurum), nullable=True)
    gun_22 = Column(Enum(PuantajDurum), nullable=True)
    gun_23 = Column(Enum(PuantajDurum), nullable=True)
    gun_24 = Column(Enum(PuantajDurum), nullable=True)
    gun_25 = Column(Enum(PuantajDurum), nullable=True)
    gun_26 = Column(Enum(PuantajDurum), nullable=True)
    gun_27 = Column(Enum(PuantajDurum), nullable=True)
    gun_28 = Column(Enum(PuantajDurum), nullable=True)
    gun_29 = Column(Enum(PuantajDurum), nullable=True)
    gun_30 = Column(Enum(PuantajDurum), nullable=True)
    gun_31 = Column(Enum(PuantajDurum), nullable=True)
    
    # Fazla Mesai Kolonları (FM = Fazla Mesai)
    fm_gun_1 = Column(Numeric(4, 1), nullable=True)
    fm_gun_2 = Column(Numeric(4, 1), nullable=True)
    fm_gun_3 = Column(Numeric(4, 1), nullable=True)
    fm_gun_4 = Column(Numeric(4, 1), nullable=True)
    fm_gun_5 = Column(Numeric(4, 1), nullable=True)
    fm_gun_6 = Column(Numeric(4, 1), nullable=True)
    fm_gun_7 = Column(Numeric(4, 1), nullable=True)
    fm_gun_8 = Column(Numeric(4, 1), nullable=True)
    fm_gun_9 = Column(Numeric(4, 1), nullable=True)
    fm_gun_10 = Column(Numeric(4, 1), nullable=True)
    fm_gun_11 = Column(Numeric(4, 1), nullable=True)
    fm_gun_12 = Column(Numeric(4, 1), nullable=True)
    fm_gun_13 = Column(Numeric(4, 1), nullable=True)
    fm_gun_14 = Column(Numeric(4, 1), nullable=True)
    fm_gun_15 = Column(Numeric(4, 1), nullable=True)
    fm_gun_16 = Column(Numeric(4, 1), nullable=True)
    fm_gun_17 = Column(Numeric(4, 1), nullable=True)
    fm_gun_18 = Column(Numeric(4, 1), nullable=True)
    fm_gun_19 = Column(Numeric(4, 1), nullable=True)
    fm_gun_20 = Column(Numeric(4, 1), nullable=True)
    fm_gun_21 = Column(Numeric(4, 1), nullable=True)
    fm_gun_22 = Column(Numeric(4, 1), nullable=True)
    fm_gun_23 = Column(Numeric(4, 1), nullable=True)
    fm_gun_24 = Column(Numeric(4, 1), nullable=True)
    fm_gun_25 = Column(Numeric(4, 1), nullable=True)
    fm_gun_26 = Column(Numeric(4, 1), nullable=True)
    fm_gun_27 = Column(Numeric(4, 1), nullable=True)
    fm_gun_28 = Column(Numeric(4, 1), nullable=True)
    fm_gun_29 = Column(Numeric(4, 1), nullable=True)
    fm_gun_30 = Column(Numeric(4, 1), nullable=True)
    fm_gun_31 = Column(Numeric(4, 1), nullable=True)
    
    # Özet Alanlar (trigger ile otomatik hesaplanır)
    calisilan_gun_sayisi = Column(Integer, default=0)
    ssk_gun_sayisi = Column(Integer, default=0)
    yillik_izin_gun = Column(Integer, default=0)
    izin_gun_sayisi = Column(Integer, default=0)
    rapor_gun_sayisi = Column(Integer, default=0)
    eksik_gun_sayisi = Column(Integer, default=0)
    yarim_gun_sayisi = Column(Numeric(3, 1), default=0)
    toplam_gun_sayisi = Column(Integer, default=0)
    
    # Çalışma Detayları
    normal_calismasi = Column(Numeric(5, 2), default=0)
    fazla_calismasi = Column(Numeric(7, 2), default=0)  # Fazla mesai saati
    eksik_calismasi = Column(Numeric(7, 2), default=0)  # Eksik mesai saati (fm_sum_base < 0 ise mutlak değeri)
    gece_calismasi = Column(Numeric(5, 2), default=0)
    tatil_calismasi = Column(Numeric(5, 2), default=0)
    sigorta_girmedigi = Column(Integer, default=0)
    hafta_tatili = Column(Integer, default=0)
    resmi_tatil = Column(Integer, default=0)
    
    # Ek Ödemeler
    yol = Column(Numeric(10, 2), default=0)
    prim = Column(Numeric(10, 2), default=0)
    ikramiye = Column(Numeric(10, 2), default=0)
    bayram = Column(Numeric(10, 2), default=0)
    kira = Column(Numeric(10, 2), default=0)
    
    # Maas2 Kazanç Hesaplamaları (Draft Contract için, trigger ile hesaplanır)
    maas2_gunluk_kazanc = Column(Numeric(10, 2), default=0)
    maas2_normal_kazanc = Column(Numeric(10, 2), default=0)
    maas2_mesai_kazanc = Column(Numeric(10, 2), default=0)
    maas2_eksik_kazanc = Column(Numeric(10, 2), default=0)  # Eksik mesai kesintisi
    maas2_tatil_kazanc = Column(Numeric(10, 2), default=0)
    maas2_tatil_mesai_kazanc = Column(Numeric(10, 2), default=0)
    maas2_toplam_kazanc = Column(Numeric(10, 2), default=0)
    
    # Timestamp
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    created_by = Column(Integer, nullable=True)
    updated_by = Column(Integer, nullable=True)
    
    # İlişkiler
    personnel = relationship("Personnel")
    
    # İndeksler
    __table_args__ = (
        Index('idx_personnel_donem', 'personnel_id', 'donem'),
        Index('idx_yil_ay', 'yil', 'ay'),
    )
    
    def __repr__(self):
        return f"<PersonnelPuantajGrid(personnel_id={self.personnel_id}, donem={self.donem})>"
