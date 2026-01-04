"""
Mevcut e-faturaların signing_time alanını XML'den parse edip günceller
"""
import sys
import os
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.einvoice import EInvoice
import xml.etree.ElementTree as ET
from datetime import datetime

# Database connection
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


def get_signing_time_from_xml(xml_path: str) -> datetime | None:
    """XML dosyasından SigningTime bilgisini parse eder"""
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        # SigningTime ara (namespace'siz)
        for elem in root.iter():
            if elem.tag.endswith('SigningTime') and elem.text:
                signing_time_str = elem.text
                try:
                    # ISO 8601 format: 2025-12-10T11:40:07.1066709Z
                    return datetime.fromisoformat(signing_time_str.replace('Z', '+00:00'))
                except:
                    try:
                        # Alternatif format
                        return datetime.strptime(signing_time_str[:19], '%Y-%m-%dT%H:%M:%S')
                    except:
                        pass
        
        return None
    except Exception as e:
        print(f"  ⚠️  XML parse hatası: {e}")
        return None


def update_signing_times():
    """E-faturaların signing_time bilgilerini günceller"""
    db = SessionLocal()
    
    try:
        # signing_time'ı NULL olan e-faturaları al
        einvoices = db.query(EInvoice).filter(
            EInvoice.signing_time == None
        ).all()
        
        print(f"📋 Toplam {len(einvoices)} e-fatura bulundu (signing_time NULL)")
        print()
        
        updated = 0
        not_found = 0
        
        for idx, einvoice in enumerate(einvoices, 1):
            if idx % 100 == 0:
                print(f"[{idx}/{len(einvoices)}] İşleniyor...")
            
            # XML dosya yolunu kontrol et
            if not einvoice.xml_file_path or not os.path.exists(einvoice.xml_file_path):
                not_found += 1
                continue
            
            # XML'den SigningTime parse et
            signing_time = get_signing_time_from_xml(einvoice.xml_file_path)
            
            if signing_time:
                einvoice.signing_time = signing_time
                updated += 1
            else:
                not_found += 1
            
            # Her 100 kayıtta bir commit
            if idx % 100 == 0:
                db.commit()
                print(f"  💾 {idx} kayıt işlendi, {updated} güncellendi")
        
        # Son commit
        db.commit()
        
        print()
        print("=" * 60)
        print(f"✅ İşlem tamamlandı!")
        print(f"📊 Güncellenen: {updated}")
        print(f"📊 SigningTime bulunamayan: {not_found}")
        print(f"📊 Toplam işlenen: {len(einvoices)}")
        print("=" * 60)
        
    except Exception as e:
        db.rollback()
        print(f"❌ Hata oluştu: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    update_signing_times()
