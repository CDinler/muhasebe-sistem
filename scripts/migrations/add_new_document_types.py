from sqlalchemy import create_engine, text
import os

# Database connection
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '3306')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_NAME = os.getenv('DB_NAME', 'muhasebe_sistem')

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
engine = create_engine(DATABASE_URL)

# Eklenecek yeni evrak türleri
new_types = [
    ('HAKEDIS_FATURASI', 'Hakediş Faturası', 'FATURA', 40),
    ('DEKONT', 'Dekont', 'BANKA', 140),
    ('VIRMAN', 'Virman Fişi', 'BANKA', 150),
    ('SENET_TAHSILAT_ODEME', 'Senet Tahsilat/Ödeme', 'CEK_SENET', 250),
    ('MAAS_BORDROSU', 'Maaş Bordrosu', 'PERSONEL', 300),
    ('SGK_BILDIRGESI', 'SGK Bildirgesi', 'PERSONEL', 310),
    ('GIDER_PUSULASI', 'Gider Pusulası', 'GIDER', 400),
    ('SERBEST_MESLEK_MAKBUZU', 'Serbest Meslek Makbuzu', 'GIDER', 410),
    ('MUSTAHSIL_MAKBUZU', 'Müstahsil Makbuzu', 'GIDER', 420),
    ('VERGI_BEYANNAMESI', 'Vergi Beyannamesi', 'VERGI', 500),
    ('VERGI_ODEME', 'Vergi Ödemesi', 'VERGI', 510),
    ('MAHSUP_FISI', 'Mahsup Fişi', 'MUHASEBE', 600),
    ('YEVMIYE_FISI', 'Yevmiye Fişi', 'MUHASEBE', 610),
    ('ACILIS_FISI', 'Açılış Fişi', 'MUHASEBE', 620),
    ('KAPANIS_FISI', 'Kapanış Fişi', 'MUHASEBE', 630),
    ('DUZELTICI_FIS', 'Düzeltici Fiş', 'MUHASEBE', 640),
    ('TERS_KAYIT', 'Ters Kayıt', 'MUHASEBE', 650),
    ('STOK_GIRIS', 'Stok Giriş Fişi', 'STOK', 700),
    ('STOK_CIKIS', 'Stok Çıkış Fişi', 'STOK', 710),
    ('SAYIM_FISI', 'Sayım Fişi', 'STOK', 720),
    ('AMORTISMAN_FISI', 'Amortisman Fişi', 'STOK', 730),
]

with engine.connect() as conn:
    added = 0
    skipped = 0
    
    for code, name, category, sort_order in new_types:
        # Önce code ve name var mı kontrol et
        code_exists = conn.execute(text(f"SELECT COUNT(*) FROM document_types WHERE code = '{code}'")).scalar()
        name_exists = conn.execute(text(f"SELECT COUNT(*) FROM document_types WHERE name = '{name}'")).scalar()
        
        if code_exists == 0 and name_exists == 0:
            conn.execute(text(
                f"INSERT INTO document_types (code, name, category, sort_order) "
                f"VALUES ('{code}', '{name}', '{category}', {sort_order})"
            ))
            conn.commit()
            print(f"  ✅ {code} - {name}")
            added += 1
        else:
            reason = "code" if code_exists else "name"
            print(f"  ℹ️  {code} atlandı ({reason} mevcut)")
            skipped += 1
    
    print(f"\n📊 Sonuç: {added} eklendi, {skipped} atlandı")
    
    # Güncel toplam
    total = conn.execute(text("SELECT COUNT(*) FROM document_types")).scalar()
    print(f"📋 Toplam document_types: {total}")
