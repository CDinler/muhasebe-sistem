"""
IcraTakip model - Personel icra takip kayıtları
"""
from sqlalchemy import Column, Integer, String, Date, Numeric, ForeignKey, Index, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class IcraTakip(Base):
    """Personel icra takip kayıtları"""
    __tablename__ = "icra_takip"

    id = Column(Integer, primary_key=True, index=True)
    personnel_id = Column(Integer, ForeignKey('personnel.id'), nullable=False, index=True)
    
    # İcra bilgileri
    dosya_no = Column(String(100), nullable=False)
    mahkeme = Column(String(200), nullable=True)
    
    # Tutarlar
    toplam_tutar = Column(Numeric(18, 2), nullable=False)
    odenen_tutar = Column(Numeric(18, 2), default=0)
    kalan_tutar = Column(Numeric(18, 2), nullable=False)
    
    # Sıra (aynı personelin birden fazla icrası olabilir)
    sira_no = Column(Integer, default=1)  # Öncelik sırası
    
    # Durum
    is_active = Column(Integer, default=1)  # Aktif mi?
    baslangic_tarihi = Column(Date, nullable=True)
    bitis_tarihi = Column(Date, nullable=True)  # Kapandıysa
    
    # Notlar
    notes = Column(String(500), nullable=True)
    
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # İlişkiler
    personnel = relationship("Personnel", backref="icra_kayitlari")

    def __repr__(self):
        return f"<IcraTakip {self.personnel_id} - {self.dosya_no}>"

    __table_args__ = (
        Index('ix_icra_personnel_sira', 'personnel_id', 'sira_no'),
    )
