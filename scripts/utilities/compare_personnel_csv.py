import pandas as pd
from app.core.database import SessionLocal
from sqlalchemy import text

# CSV dosyasını oku
csv_path = r"C:\Users\CAGATAY\OneDrive\Desktop\MUHASEBE_ANALIZ_v2\muhasebe kayıtları PERSONEL HESAPNOLAR GUCEL.csv"

print("=" * 80)
print("335 PERSONEL HESAP KARŞILAŞTIRMASI - CSV vs DATABASE")
print("=" * 80)

try:
    # CSV'yi oku (delimiter ; ve encoding deneme)
    try:
        df = pd.read_csv(csv_path, sep=';', encoding='utf-8')
    except:
        try:
            df = pd.read_csv(csv_path, sep=';', encoding='cp1254')
        except:
            df = pd.read_csv(csv_path, sep=';', encoding='latin1')
    
    print(f"\n📄 CSV Dosyası: {len(df)} satır")
    print(f"📋 Kolonlar: {list(df.columns)}")
    
    # İlk 3 satırı göster
    print("\n🔍 CSV İlk 3 Satır:")
    print(df.head(3).to_string())
    
    # 335 ile başlayan hesapları bul
    df['Hesap Kodu'] = df['Hesap Kodu'].astype(str).str.strip()
    df_335 = df[df['Hesap Kodu'].str.startswith('335.')]
    
    print(f"\n📊 CSV'de 335 Hesap: {len(df_335)}")
    
    # Database kontrolü
    db = SessionLocal()
    
    # Database'deki 335 hesapları
    db_accounts = db.execute(text("""
        SELECT code, name
        FROM accounts
        WHERE code LIKE '335.%'
        ORDER BY code
    """)).fetchall()
    
    print(f"💾 Database'de 335 Hesap: {len(db_accounts)}")
    
    # CSV'deki hesap kodlarını al
    csv_codes = set(df_335['Hesap Kodu'].unique())
    db_codes = set([a.code for a in db_accounts])
    
    print(f"\n🔢 Unique Hesap Sayısı:")
    print(f"  CSV: {len(csv_codes)}")
    print(f"  DB:  {len(db_codes)}")
    
    # Farklar
    only_csv = csv_codes - db_codes
    only_db = db_codes - csv_codes
    
    if only_csv:
        print(f"\n⚠️  CSV'de OLUP DB'de OLMAYAN ({len(only_csv)} adet):")
        for code in sorted(list(only_csv)[:20]):
            # CSV'den detay bul
            row = df_335[df_335['Hesap Kodu'] == code].iloc[0]
            print(f"  {code:20} | {row.get('Hesap Adı', 'N/A')}")
        if len(only_csv) > 20:
            print(f"  ... ve {len(only_csv) - 20} hesap daha")
    
    if only_db:
        print(f"\n⚠️  DB'de OLUP CSV'de OLMAYAN ({len(only_db)} adet):")
        for code in sorted(list(only_db)[:20]):
            # DB'den detay bul
            acc = [a for a in db_accounts if a.code == code][0]
            print(f"  {code:20} | {acc.name}")
        if len(only_db) > 20:
            print(f"  ... ve {len(only_db) - 20} hesap daha")
    
    # Transaction_lines kontrolü
    print(f"\n📦 TRANSACTION KONTROLÜ:")
    
    # CSV'de olan ama DB'de olmayan hesaplarda transaction var mı?
    if only_csv:
        sample_codes = list(only_csv)[:5]
        for code in sample_codes:
            # Bu hesap kodu ile transaction var mı?
            tx_count = db.execute(text("""
                SELECT COUNT(tl.id)
                FROM transaction_lines tl
                JOIN accounts a ON tl.account_id = a.id
                WHERE a.code = :code
            """), {"code": code}).scalar()
            
            if tx_count > 0:
                print(f"  ❌ {code:20} | CSV'de var, DB'de YOK, {tx_count} TRANSACTION VAR!")
    
    # TCKN bazlı karşılaştırma (eğer CSV'de TCKN varsa)
    if 'TC Kimlik No' in df_335.columns or 'TCKN' in df_335.columns:
        tckn_col = 'TC Kimlik No' if 'TC Kimlik No' in df_335.columns else 'TCKN'
        
        print(f"\n👤 TCKN BAZLI KARŞILAŞTIRMA:")
        
        # CSV'den ilk 5 personel
        sample_personnel = df_335.head(10)
        
        for idx, row in sample_personnel.iterrows():
            tckn = str(row[tckn_col]).strip()
            csv_code = row['Hesap Kodu']
            
            # DB'de bu TCKN'ye ait hesap
            db_account = db.execute(text("""
                SELECT a.code, a.name
                FROM personnel p
                JOIN accounts a ON p.account_id = a.id
                WHERE p.tckn = :tckn
            """), {"tckn": tckn}).first()
            
            if db_account:
                db_code = db_account.code
                if csv_code != db_code:
                    print(f"  ⚠️  TCKN {tckn}:")
                    print(f"      CSV:  {csv_code}")
                    print(f"      DB:   {db_code}")
                    print(f"      FARKLI!")
            else:
                print(f"  ⚠️  TCKN {tckn} -> DB'de personnel kaydı YOK!")
    
    db.close()
    
    print("\n" + "=" * 80)
    print("KARŞILAŞTIRMA TAMAMLANDI")
    print("=" * 80)

except Exception as e:
    print(f"\n❌ HATA: {e}")
    import traceback
    traceback.print_exc()
