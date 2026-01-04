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

print("📊 Mevcut document_types Analizi")
print("=" * 80)

with engine.connect() as conn:
    # Tüm document_types
    types = conn.execute(text("""
        SELECT code, name, category 
        FROM document_types 
        ORDER BY category, code
    """)).fetchall()
    
    categories = {}
    for code, name, cat in types:
        if cat not in categories:
            categories[cat] = []
        categories[cat].append((code, name))
    
    for cat, items in sorted(categories.items()):
        print(f"\n📋 {cat}:")
        for code, name in items:
            print(f"  {code}: {name}")
    
    print("\n" + "=" * 80)
    print("\n📊 YEVMIYE_KAYDI_SABLONU.md ile Karşılaştırma:")
    
    # YEVMIYE_KAYDI_SABLONU.md'de olan
    expected_codes = {
        'FATURA': ['ALIS_FATURASI', 'SATIS_FATURASI', 'IADE_FATURASI', 'HAKEDIS_FATURASI', 'PROFORMA_FATURA'],
        'KASA': ['KASA_TAHSILAT', 'KASA_TEDIYE'],
        'BANKA': ['BANKA_TAHSILAT', 'BANKA_TEDIYE', 'DEKONT', 'VIRMAN'],
        'CEK_SENET': ['ALINAN_CEK', 'VERILEN_CEK', 'CEK_TAHSILAT_ODEME', 'ALINAN_SENET', 'VERILEN_SENET', 'SENET_TAHSILAT_ODEME'],
        'PERSONEL': ['MAAS_BORDROSU', 'SGK_BILDIRGESI'],
        'GIDER': ['GIDER_PUSULASI', 'SERBEST_MESLEK_MAKBUZU', 'MUSTAHSIL_MAKBUZU'],
        'VERGI': ['VERGI_BEYANNAMESI', 'VERGI_ODEME'],
        'MUHASEBE': ['MAHSUP_FISI', 'YEVMIYE_FISI', 'ACILIS_FISI', 'KAPANIS_FISI', 'DUZELTICI_FIS', 'TERS_KAYIT'],
        'STOK': ['STOK_GIRIS', 'STOK_CIKIS', 'SAYIM_FISI', 'AMORTISMAN_FISI']
    }
    
    current_codes = {cat: [code for code, _ in items] for cat, items in categories.items()}
    
    print("\n✅ MEVCUT (Tabloda var):")
    for cat in expected_codes:
        if cat in current_codes:
            existing = set(expected_codes[cat]) & set(current_codes[cat])
            if existing:
                print(f"  {cat}: {', '.join(sorted(existing))}")
    
    print("\n❌ EKSİK (Tabloda yok, eklenecek):")
    for cat in expected_codes:
        missing = set(expected_codes[cat]) - set(current_codes.get(cat, []))
        if missing:
            print(f"  {cat}: {', '.join(sorted(missing))}")
    
    print("\n⚠️  FAZLA (Tabloda var ama YEVMIYE'de yok - silinmeyecek, transactions kullanıyor):")
    for cat in current_codes:
        if cat in expected_codes:
            extra = set(current_codes[cat]) - set(expected_codes[cat])
            if extra:
                for code in sorted(extra):
                    # Transactions'da kullanılıyor mu kontrol et
                    usage = conn.execute(text(f"SELECT COUNT(*) FROM transactions WHERE document_type_id = (SELECT id FROM document_types WHERE code = '{code}')")).scalar()
                    print(f"  {cat}: {code} ({usage} transaction)")
        else:
            for code in sorted(current_codes[cat]):
                usage = conn.execute(text(f"SELECT COUNT(*) FROM transactions WHERE document_type_id = (SELECT id FROM document_types WHERE code = '{code}')")).scalar()
                print(f"  {cat}: {code} ({usage} transaction)")
