"""
XML dosyalarından raw_data'yı senkronize et
"""
import sys
from pathlib import Path
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

# Backend app'i import et
sys.path.insert(0, str(Path(__file__).parent))
from app.models.einvoice import EInvoice
from app.core.config import settings

def sync_raw_data():
    """XML dosyalarından raw_data'yı güncelle"""
    engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))
    
    with Session(engine) as session:
        # XML file path'i olan tüm faturaları al
        stmt = select(EInvoice).where(EInvoice.xml_file_path.isnot(None))
        invoices = session.execute(stmt).scalars().all()
        
        print(f"Toplam {len(invoices)} fatura bulundu")
        
        updated_count = 0
        error_count = 0
        
        for invoice in invoices:
            try:
                xml_path = Path(invoice.xml_file_path)
                
                if not xml_path.exists():
                    print(f"⚠️  XML dosyası bulunamadı: {xml_path}")
                    error_count += 1
                    continue
                
                # XML dosyasını oku
                with open(xml_path, 'r', encoding='utf-8') as f:
                    xml_content = f.read()
                
                # raw_data'yı güncelle
                if invoice.raw_data != xml_content:
                    invoice.raw_data = xml_content
                    updated_count += 1
                    
                    if updated_count % 100 == 0:
                        print(f"✅ {updated_count} fatura güncellendi...")
                        session.commit()
                
            except Exception as e:
                print(f"❌ Hata (ID={invoice.id}): {e}")
                error_count += 1
        
        # Son commit
        session.commit()
        
        print(f"\n📊 SONUÇ:")
        print(f"   Güncellenen: {updated_count}")
        print(f"   Hata: {error_count}")
        print(f"   Toplam: {len(invoices)}")

if __name__ == '__main__':
    sync_raw_data()
