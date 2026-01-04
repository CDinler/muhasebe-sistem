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

print("🔄 document_subtypes Migration - MEVCUT CODE'LARA GÖRE")
print("=" * 80)

with engine.connect() as conn:
    # parent_code kolonu var mı kontrol et
    has_column = conn.execute(text("""
        SELECT COUNT(*) 
        FROM information_schema.COLUMNS 
        WHERE TABLE_SCHEMA = 'muhasebe_sistem' 
        AND TABLE_NAME = 'document_subtypes' 
        AND COLUMN_NAME = 'parent_code'
    """)).scalar()
    
    if has_column == 0:
        print("❌ parent_code kolonu yok! Önce ADIM 1'i çalıştır")
        exit(1)
    
    print("✅ parent_code kolonu mevcut")
    
    # 74 alt evrak türü (MEVCUT CODE'LARA GÖRE)
    subtypes = [
        # FATURA kategorisi - ALIS_FATURA (mevcut code)
        ('ALIS_E_FATURA', 'ALIS_FATURA', 'E-Fatura (Alış)', 'E_BELGE', 1),
        ('ALIS_E_ARSIV', 'ALIS_FATURA', 'E-Arşiv (Alış)', 'E_BELGE', 2),
        ('ALIS_KAGIT_MATBU', 'ALIS_FATURA', 'Kağıt/Matbu (Alış)', 'MANUEL', 3),
        ('ALIS_ITHALAT', 'ALIS_FATURA', 'İthalat Faturası', 'MANUEL', 4),
        
        # SATIS_FATURA (mevcut code)
        ('SATIS_E_FATURA', 'SATIS_FATURA', 'E-Fatura (Satış)', 'E_BELGE', 1),
        ('SATIS_E_ARSIV', 'SATIS_FATURA', 'E-Arşiv (Satış)', 'E_BELGE', 2),
        ('SATIS_KAGIT_MATBU', 'SATIS_FATURA', 'Kağıt/Matbu (Satış)', 'MANUEL', 3),
        ('SATIS_IHRACAT', 'SATIS_FATURA', 'İhracat Faturası', 'MANUEL', 4),
        
        # IADE_FATURA (mevcut code)
        ('IADE_ALIS', 'IADE_FATURA', 'Alış İade', 'MANUEL', 1),
        ('IADE_SATIS', 'IADE_FATURA', 'Satış İade', 'MANUEL', 2),
        
        # HAKEDIS_FATURASI
        ('HAKEDIS_GECICI', 'HAKEDIS_FATURASI', 'Geçici Hakediş', 'MANUEL', 1),
        ('HAKEDIS_KESIN', 'HAKEDIS_FATURASI', 'Kesin Hakediş', 'MANUEL', 2),
        
        # PROFORMA_FATURA
        ('PROFORMA_NORMAL', 'PROFORMA_FATURA', 'Normal Proforma', 'MANUEL', 1),
        
        # KASA kategorisi
        ('KASA_TAHSILAT_NAKIT', 'KASA_TAHSILAT', 'Nakit Tahsilat', 'MANUEL', 1),
        ('KASA_TAHSILAT_CEK', 'KASA_TAHSILAT', 'Çek Tahsilat', 'MANUEL', 2),
        ('KASA_TAHSILAT_SENET', 'KASA_TAHSILAT', 'Senet Tahsilat', 'MANUEL', 3),
        ('KASA_TEDIYE_NAKIT', 'KASA_TEDIYE', 'Nakit Ödeme', 'MANUEL', 1),
        ('KASA_TEDIYE_CEK', 'KASA_TEDIYE', 'Çek Ödeme', 'MANUEL', 2),
        ('KASA_TEDIYE_SENET', 'KASA_TEDIYE', 'Senet Ödeme', 'MANUEL', 3),
        
        # BANKA kategorisi
        ('BANKA_TAHSILAT_EFT', 'BANKA_TAHSILAT', 'EFT/Havale', 'OTOMATIK', 1),
        ('BANKA_TAHSILAT_KART', 'BANKA_TAHSILAT', 'Kredi Kartı', 'OTOMATIK', 2),
        ('BANKA_TAHSILAT_CEK', 'BANKA_TAHSILAT', 'Çek', 'OTOMATIK', 3),
        ('BANKA_TAHSILAT_SENET', 'BANKA_TAHSILAT', 'Senet', 'OTOMATIK', 4),
        ('BANKA_TEDIYE_EFT', 'BANKA_TEDIYE', 'EFT/Havale', 'OTOMATIK', 1),
        ('BANKA_TEDIYE_KART', 'BANKA_TEDIYE', 'Kredi Kartı', 'OTOMATIK', 2),
        ('BANKA_TEDIYE_CEK', 'BANKA_TEDIYE', 'Çek', 'OTOMATIK', 3),
        ('BANKA_TEDIYE_SENET', 'BANKA_TEDIYE', 'Senet', 'OTOMATIK', 4),
        ('DEKONT_FAIZ_GELIR', 'DEKONT', 'Faiz Geliri', 'OTOMATIK', 1),
        ('DEKONT_KOMISYON', 'DEKONT', 'Komisyon', 'OTOMATIK', 2),
        ('DEKONT_DIGER', 'DEKONT', 'Diğer', 'OTOMATIK', 3),
        ('VIRMAN_HESAPLAR_ARASI', 'BANKA_VIRMAN', 'Hesaplar Arası Virman', 'OTOMATIK', 1),
        
        # CEK_SENET kategorisi
        ('ALINAN_CEK_CIRO', 'ALINAN_CEK', 'Ciro', 'MANUEL', 1),
        ('ALINAN_CEK_PORTFOY', 'ALINAN_CEK', 'Portföy', 'MANUEL', 2),
        ('VERILEN_CEK_NORMAL', 'VERILEN_CEK', 'Normal Çek', 'MANUEL', 1),
        ('CEK_TAHSILAT', 'CEK_TAHSILAT_ODEME', 'Çek Tahsil', 'MANUEL', 1),
        ('CEK_ODEME', 'CEK_TAHSILAT_ODEME', 'Çek Ödeme', 'MANUEL', 2),
        ('ALINAN_SENET_CIRO', 'ALINAN_SENET', 'Ciro', 'MANUEL', 1),
        ('ALINAN_SENET_PORTFOY', 'ALINAN_SENET', 'Portföy', 'MANUEL', 2),
        ('VERILEN_SENET_NORMAL', 'VERILEN_SENET', 'Normal Senet', 'MANUEL', 1),
        ('SENET_TAHSILAT', 'SENET_TAHSILAT_ODEME', 'Senet Tahsil', 'MANUEL', 1),
        ('SENET_ODEME', 'SENET_TAHSILAT_ODEME', 'Senet Ödeme', 'MANUEL', 2),
        
        # PERSONEL kategorisi
        ('BORDRO_AYLIK', 'MAAS_BORDROSU', 'Aylık Bordro', 'OTOMATIK', 1),
        ('BORDRO_HAFTALIK', 'MAAS_BORDROSU', 'Haftalık Bordro', 'OTOMATIK', 2),
        ('BORDRO_GUNLUK', 'MAAS_BORDROSU', 'Günlük Bordro', 'OTOMATIK', 3),
        ('SGK_NORMAL', 'SGK_BILDIRGESI', 'Normal SGK', 'OTOMATIK', 1),
        ('SGK_EKLEME', 'SGK_BILDIRGESI', 'Ekleme Bildirge', 'OTOMATIK', 2),
        ('SGK_DUZELTME', 'SGK_BILDIRGESI', 'Düzeltme Bildirge', 'OTOMATIK', 3),
        ('SGK_IPTAL', 'SGK_BILDIRGESI', 'İptal Bildirge', 'OTOMATIK', 4),
        
        # GIDER kategorisi
        ('GIDER_YEMEK', 'GIDER_PUSULASI', 'Yemek Gideri', 'MANUEL', 1),
        ('GIDER_YAKIT', 'GIDER_PUSULASI', 'Yakıt Gideri', 'MANUEL', 2),
        ('GIDER_KIRTASIYE', 'GIDER_PUSULASI', 'Kırtasiye', 'MANUEL', 3),
        ('GIDER_ULASIM', 'GIDER_PUSULASI', 'Ulaşım', 'MANUEL', 4),
        ('GIDER_DIGER', 'GIDER_PUSULASI', 'Diğer Giderler', 'MANUEL', 5),
        ('SMM_NORMAL', 'SERBEST_MESLEK_MAKBUZU', 'Normal SMM', 'MANUEL', 1),
        ('SMM_TEVKIFATLI', 'SERBEST_MESLEK_MAKBUZU', 'Tevkifatlı SMM', 'MANUEL', 2),
        ('MUSTAHSIL_NORMAL', 'MUSTAHSIL_MAKBUZU', 'Normal Müstahsil', 'MANUEL', 1),
        
        # VERGI kategorisi
        ('BEYAN_KDV', 'VERGI_BEYANNAMESI', 'KDV Beyannamesi', 'OTOMATIK', 1),
        ('BEYAN_STOPAJ', 'VERGI_BEYANNAMESI', 'Stopaj Beyannamesi', 'OTOMATIK', 2),
        ('BEYAN_GELIR', 'VERGI_BEYANNAMESI', 'Gelir Vergisi', 'OTOMATIK', 3),
        ('BEYAN_KURUMLAR', 'VERGI_BEYANNAMESI', 'Kurumlar Vergisi', 'OTOMATIK', 4),
        ('BEYAN_GECICI', 'VERGI_BEYANNAMESI', 'Geçici Vergi', 'OTOMATIK', 5),
        ('BEYAN_DAMGA', 'VERGI_BEYANNAMESI', 'Damga Vergisi', 'OTOMATIK', 6),
        ('BEYAN_MTV', 'VERGI_BEYANNAMESI', 'MTV', 'OTOMATIK', 7),
        ('BEYAN_DIGER', 'VERGI_BEYANNAMESI', 'Diğer Vergiler', 'OTOMATIK', 8),
        ('VERGI_ODEME_KDV', 'VERGI_ODEME', 'KDV Ödemesi', 'MANUEL', 1),
        ('VERGI_ODEME_STOPAJ', 'VERGI_ODEME', 'Stopaj Ödemesi', 'MANUEL', 2),
        ('VERGI_ODEME_DIGER', 'VERGI_ODEME', 'Diğer Vergi Ödemesi', 'MANUEL', 3),
        ('VERGI_ODEME_TAHAKKUK', 'VERGI_ODEME', 'Vergi Tahakkuku', 'MANUEL', 4),
        
        # MUHASEBE kategorisi
        ('MAHSUP_CARI', 'MAHSUP', 'Cari Mahsup', 'MANUEL', 1),
        ('MAHSUP_HESAP', 'MAHSUP', 'Hesap Mahsup', 'MANUEL', 2),
        ('YEVMIYE_GENEL', 'YEVMIYE', 'Genel Yevmiye', 'MANUEL', 1),
        ('ACILIS_DONEM', 'ACILIS', 'Dönem Açılış', 'MANUEL', 1),
        ('KAPANIS_DONEM', 'KAPANIS_FISI', 'Dönem Kapanış', 'MANUEL', 1),
        ('KAPANIS_YILSONU', 'KAPANIS_FISI', 'Yılsonu Kapanış', 'MANUEL', 2),
        ('DUZELTME_HATA', 'DUZELTME', 'Hata Düzeltme', 'MANUEL', 1),
        ('DUZELTME_TAHAKKUK', 'DUZELTME', 'Tahakkuk Düzeltme', 'MANUEL', 2),
        ('TERS_KAYIT_IPTAL', 'TERS_KAYIT', 'İptal (Ters Kayıt)', 'MANUEL', 1),
        
        # STOK kategorisi
        ('STOK_GIRIS_ALIS', 'STOK_GIRIS', 'Alıştan Giriş', 'OTOMATIK', 1),
        ('STOK_GIRIS_IADE', 'STOK_GIRIS', 'İadeden Giriş', 'OTOMATIK', 2),
        ('STOK_GIRIS_FIRE', 'STOK_GIRIS', 'Fire/Fazla', 'MANUEL', 3),
        ('STOK_CIKIS_SATIS', 'STOK_CIKIS', 'Satıştan Çıkış', 'OTOMATIK', 1),
        ('STOK_CIKIS_IADE', 'STOK_CIKIS', 'İadeden Çıkış', 'OTOMATIK', 2),
        ('STOK_CIKIS_FIRE', 'STOK_CIKIS', 'Fire/Kayıp', 'MANUEL', 3),
        ('SAYIM_YILSONU', 'SAYIM_FISI', 'Yılsonu Sayım', 'MANUEL', 1),
        ('SAYIM_ARA', 'SAYIM_FISI', 'Ara Sayım', 'MANUEL', 2),
        ('AMORTISMAN_AYLIK', 'AMORTISMAN_FISI', 'Aylık Amortisman', 'OTOMATIK', 1),
        ('AMORTISMAN_YILSONU', 'AMORTISMAN_FISI', 'Yılsonu Amortisman', 'OTOMATIK', 2),
    ]
    
    print(f"\n📝 {len(subtypes)} alt evrak türü eklenecek...")
    
    added = 0
    skipped = 0
    errors = []
    
    for code, parent_code, name, category, sort_order in subtypes:
        # Var mı kontrol et
        exists = conn.execute(text(f"SELECT COUNT(*) FROM document_subtypes WHERE code = '{code}'")).scalar()
        
        if exists == 0:
            try:
                # parent_code var mı kontrol et
                parent_exists = conn.execute(text(f"SELECT COUNT(*) FROM document_types WHERE code = '{parent_code}'")).scalar()
                
                if parent_exists == 0:
                    errors.append(f"❌ {code}: Parent code '{parent_code}' bulunamadı!")
                    continue
                
                conn.execute(text(f"""
                    INSERT INTO document_subtypes (code, parent_code, name, category, sort_order, is_active)
                    VALUES ('{code}', '{parent_code}', '{name}', '{category}', {sort_order}, 1)
                """))
                conn.commit()
                added += 1
                
                if added % 10 == 0:
                    print(f"  ✅ {added} kayıt eklendi...")
                    
            except Exception as e:
                errors.append(f"❌ {code}: {str(e)}")
        else:
            skipped += 1
    
    print(f"\n📊 SONUÇ:")
    print(f"  ✅ {added} kayıt eklendi")
    print(f"  ⏭️  {skipped} kayıt atlandı (mevcut)")
    
    if errors:
        print(f"\n⚠️  HATALAR ({len(errors)}):")
        for err in errors[:10]:  # İlk 10 hatayı göster
            print(f"  {err}")

# Doğrulama
print("\n" + "=" * 80)
print("🔍 Doğrulama...")
print("=" * 80)

with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT 
            dt.code AS ana_evrak,
            dt.name AS ana_evrak_adi,
            COUNT(ds.id) AS alt_turu_sayisi
        FROM document_types dt
        LEFT JOIN document_subtypes ds ON ds.parent_code = dt.code
        GROUP BY dt.code, dt.name
        HAVING alt_turu_sayisi > 0
        ORDER BY alt_turu_sayisi DESC
    """)).fetchall()
    
    total_subtypes = 0
    for ana, adi, sayi in result:
        print(f"{ana:25} ({adi:30}): {sayi:2} alt tür")
        total_subtypes += sayi
    
    print(f"\n📊 TOPLAM: {total_subtypes} alt evrak türü")
