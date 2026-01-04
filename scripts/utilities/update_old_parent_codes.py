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

print("🔄 Eski document_subtypes kayıtlarına parent_code ekleme")
print("=" * 100)

# Mapping: subtype_code → parent_code
# Transaction analizi ve mantık bazlı eşleştirme
mappings = {
    # E-Belge türleri → FATURA
    'E_FATURA': 'ALIS_FATURA',  # 3915 txn - Alış faturalarında kullanılıyor
    'E_ARSIV': 'ALIS_FATURA',    # 382 txn - Alış e-arşiv
    'E_IRSALIYE': 'ALIS_FATURA', # 0 txn - İrsaliyeler genelde alış
    'E_SMM': 'SERBEST_MESLEK_MAKBUZU', # 0 txn
    'KAGIT_MATBU': 'ALIS_FATURA',  # 206 txn - Kağıt faturalar
    
    # BANKA işlemleri
    'EFT_HAVALE': 'BANKA_TEDIYE',  # 10954 txn - Tediye işlemleri
    'KREDI_KARTI': 'BANKA_TEDIYE', # 1082 txn - Kredi kartı ödemeleri
    'DEKONT': 'DEKONT',  # 1 txn - Ana tür olarak DEKONT var
    'VIRMAN': 'BANKA_VIRMAN',  # 0 txn - Virman ana türü
    
    # KASA işlemleri
    'NAKIT': 'KASA_TAHSILAT',  # 4097 txn - Kasa tahsilatları
    'KASA_VIRMAN': 'KASA_TAHSILAT',  # 0 txn
    
    # ÇEK/SENET
    'MUSTERI_CEKI': 'ALINAN_CEK',  # 2 txn - Müşteriden alınan çek
    'TEDARIKCI_CEKI': 'VERILEN_CEK',  # 44 txn - Tedarikciye verilen çek
    'ODEME': 'CEK_TAHSILAT_ODEME',  # 2 txn - Çek ödemesi
    'TAHSILAT': 'CEK_TAHSILAT_ODEME',  # 0 txn - Çek tahsilatı
    
    # PERSONEL
    'PERSONEL_ODEME': 'MAAS_BORDROSU',  # 5260 txn - Maaş ödemeleri
    'MAAS': 'MAAS_BORDROSU',  # 0 txn
    'PRIM': 'MAAS_BORDROSU',  # 0 txn - Primler maaş bordrosunda
    'MESAI': 'MAAS_BORDROSU',  # 0 txn - Mesai ödemeleri bordro
    'AVANS': 'MAAS_BORDROSU',  # 0 txn - Avans ödemeleri
    
    # Diğer
    'SMM': 'SERBEST_MESLEK_MAKBUZU',  # 1 txn
    'DUZELTME_MAHSUP': 'MAHSUP',  # 298 txn - Mahsup fişleri
}

with engine.connect() as conn:
    updated = 0
    errors = []
    
    for subtype_code, parent_code in mappings.items():
        # Subtype var mı?
        subtype = conn.execute(text(f"SELECT id FROM document_subtypes WHERE code = '{subtype_code}'")).fetchone()
        
        if not subtype:
            errors.append(f"⚠️  {subtype_code}: Alt tür bulunamadı!")
            continue
        
        # Parent var mı?
        parent = conn.execute(text(f"SELECT id FROM document_types WHERE code = '{parent_code}'")).fetchone()
        
        if not parent:
            errors.append(f"❌ {subtype_code} → {parent_code}: Parent kod bulunamadı!")
            continue
        
        # Transaction sayısı
        txn_count = conn.execute(text(f"SELECT COUNT(*) FROM transactions WHERE document_subtype_id = {subtype[0]}")).scalar()
        
        # Update
        try:
            conn.execute(text(f"""
                UPDATE document_subtypes 
                SET parent_code = '{parent_code}'
                WHERE code = '{subtype_code}'
            """))
            conn.commit()
            print(f"✅ {subtype_code:25} → {parent_code:25} ({txn_count:5} txn)")
            updated += 1
        except Exception as e:
            errors.append(f"❌ {subtype_code}: {str(e)}")
    
    print(f"\n{'='*100}")
    print(f"📊 SONUÇ:")
    print(f"  ✅ {updated} kayıt güncellendi")
    
    if errors:
        print(f"\n⚠️  HATALAR ({len(errors)}):")
        for err in errors:
            print(f"  {err}")

# Doğrulama
print(f"\n{'='*100}")
print("🔍 Doğrulama:")
print(f"{'='*100}")

with engine.connect() as conn:
    # Hala NULL olanlar var mı?
    still_null = conn.execute(text("""
        SELECT code, name, 
               (SELECT COUNT(*) FROM transactions WHERE document_subtype_id = document_subtypes.id) AS txn_count
        FROM document_subtypes 
        WHERE parent_code IS NULL
    """)).fetchall()
    
    if still_null:
        print(f"\n⚠️  Hala parent_code NULL olan kayıtlar ({len(still_null)}):")
        for code, name, txn in still_null:
            print(f"  {code:30} ({name:40}) - {txn} txn")
    else:
        print("✅ Tüm document_subtypes kayıtlarında parent_code dolu!")
    
    # Toplam özet
    total = conn.execute(text("SELECT COUNT(*) FROM document_subtypes")).scalar()
    with_parent = conn.execute(text("SELECT COUNT(*) FROM document_subtypes WHERE parent_code IS NOT NULL")).scalar()
    
    print(f"\n📊 Final Durum:")
    print(f"  Toplam alt tür: {total}")
    print(f"  parent_code dolu: {with_parent}")
    print(f"  parent_code NULL: {total - with_parent}")
