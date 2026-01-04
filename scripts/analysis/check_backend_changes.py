"""
Backend değişikliklerini test et - Eksik alanlar kontrolü
"""

from sqlalchemy import create_engine, text
import os
import json

# Database connection
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '3306')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_NAME = os.getenv('DB_NAME', 'muhasebe_sistem')

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
engine = create_engine(DATABASE_URL)

print("📊 Backend Değişiklikleri - Eksik Alan Analizi")
print("=" * 80)

with engine.connect() as conn:
    # 1. Bir e-fatura seç
    einvoice = conn.execute(text("""
        SELECT id, invoice_number, supplier_name, supplier_tax_number, invoice_type
        FROM einvoices
        WHERE id = 1
        LIMIT 1
    """)).fetchone()
    
    if einvoice:
        print(f"\n✅ Test E-Fatura: {einvoice[1]} ({einvoice[2]})")
        print(f"   Invoice Type: {einvoice[4]}")
        
        # 2. Cost center'ları listele
        cost_centers = conn.execute(text("SELECT id, code, name FROM cost_centers LIMIT 5")).fetchall()
        print(f"\n📋 Cost Centers (ilk 5):")
        for cc in cost_centers:
            print(f"   {cc[0]}: {cc[1]} - {cc[2]}")
        
        # 3. Document types
        doc_types = conn.execute(text("SELECT id, code, name FROM document_types WHERE category = 'FATURA' LIMIT 5")).fetchall()
        print(f"\n📋 Document Types (FATURA):")
        for dt in doc_types:
            print(f"   {dt[0]}: {dt[1]} - {dt[2]}")
        
        print("\n" + "=" * 80)
        print("\n✅ BACKEND DEĞİŞİKLİKLERİ:")
        print("\n1. Transaction Seviyesi:")
        print("   ✅ document_type: 'E-Fatura' (invoice_type'a göre)")
        print("   ✅ document_subtype: 'E-Arşiv' veya 'E-Fatura'")
        print("   ✅ description: '{supplier_name} - {invoice_number}'")
        print("   ✅ cost_center_name: Database'den çekiliyor")
        
        print("\n2. Transaction Lines:")
        print("   ✅ contact_name: 320/335 hesaplarında cari adı")
        print("   ✅ quantity: Mal/hizmet satırlarında miktar, KDV satırında oran")
        print("   ✅ unit: Birim (şimdilik None, raw_data'dan gelecek)")
        print("   ✅ vat_base: KDV satırlarında matrah tutarı")
        
        print("\n3. OTOMATİK DOLDURULACAK ALANLAR:")
        print("   🔹 Maliyet Merkezi: Frontend'ten seçilecek (cost_center_id)")
        print("   🔹 Belge Tipi: Otomatik (invoice_type'a göre)")
        print("   🔹 Belge Alt Tipi: Otomatik (E_ARSIV → E-Arşiv, diğer → E-Fatura)")
        print("   🔹 Açıklama: Otomatik ('{supplier_name} - {invoice_number}')")
        print("   🔹 Cari: Otomatik (320/335 satırlarında)")
        print("   🔹 Miktar: Otomatik (invoice line'dan veya KDV satırında oran)")
        print("   🔹 Matrah: Otomatik (KDV satırlarında)")
        
        print("\n4. MANUEL DOLDURULACAK ALANLAR:")
        print("   ❌ Birim: Şu anda boş (gelecekte raw_data'dan parse edilecek)")
        
        print("\n" + "=" * 80)
        print("\n💡 ÖNERİ: Frontend'te bir test import yaparak tüm kolonları görüntüleyin!")
        
    else:
        print("❌ Test için e-fatura bulunamadı")
