"""
E-fatura ve Contact eşleşme problemini detaylı analiz et
VKN, isim benzerliği, yevmiye kayıtları çapraz kontrolü
"""
from app.core.database import SessionLocal
from sqlalchemy import text
from difflib import SequenceMatcher

db = SessionLocal()

print('='*80)
print('E-FATURA VE CARİ EŞLEŞME DETAYLI ANALİZ')
print('='*80)

# 1. VKN bazlı kontrol
print('\n1. VKN BAZLI EŞLEŞME KONTROLÜ:')
print('-'*80)

# E-faturada olan ama contacts'ta olmayan VKN'ler
missing_vkns = db.execute(text("""
    SELECT DISTINCT
        e.supplier_tax_number as vkn,
        e.supplier_name as efatura_isim,
        COUNT(DISTINCT e.id) as fatura_sayisi
    FROM einvoices e
    LEFT JOIN contacts c ON e.supplier_tax_number = c.tax_number
    WHERE e.invoice_category = 'incoming'
    AND c.id IS NULL
    AND e.supplier_tax_number IS NOT NULL
    GROUP BY e.supplier_tax_number, e.supplier_name
    ORDER BY fatura_sayisi DESC
    LIMIT 20
""")).fetchall()

print(f'\n❌ Contacts tablosunda BULUNMAYAN {len(missing_vkns)} farklı VKN:')
for vkn in missing_vkns[:10]:
    print(f'  {vkn.vkn:12s} | {vkn.fatura_sayisi:3d} fatura | {vkn.efatura_isim}')

# 2. VKN format kontrolü (10 vs 11 hane)
print('\n2. VKN FORMAT ANALİZİ:')
print('-'*80)

vkn_formats = db.execute(text("""
    SELECT 
        LENGTH(supplier_tax_number) as vkn_uzunluk,
        COUNT(*) as adet,
        COUNT(DISTINCT supplier_tax_number) as unique_vkn
    FROM einvoices
    WHERE supplier_tax_number IS NOT NULL
    AND invoice_category = 'incoming'
    GROUP BY LENGTH(supplier_tax_number)
    ORDER BY adet DESC
""")).fetchall()

print('\nE-Fatura VKN uzunlukları:')
for fmt in vkn_formats:
    print(f'  {fmt.vkn_uzunluk} hane: {fmt.adet:,} fatura ({fmt.unique_vkn} farklı VKN)')

vkn_formats_contact = db.execute(text("""
    SELECT 
        LENGTH(tax_number) as vkn_uzunluk,
        COUNT(*) as adet
    FROM contacts
    WHERE tax_number IS NOT NULL
    GROUP BY LENGTH(tax_number)
    ORDER BY adet DESC
""")).fetchall()

print('\nContacts VKN uzunlukları:')
for fmt in vkn_formats_contact:
    print(f'  {fmt.vkn_uzunluk} hane: {fmt.adet:,} cari')

# 3. İSİM BENZERLİĞİ ANALİZİ - Eksik VKN'lerin benzer isimleri
print('\n3. İSİM BENZERLİĞİ KONTROLÜ (Eksik VKN\'ler için):')
print('-'*80)

# İlk 5 eksik VKN için benzer isimleri bul
for missing in missing_vkns[:5]:
    print(f'\n📋 VKN: {missing.vkn} | E-Fatura İsmi: {missing.efatura_isim}')
    
    # Contacts'taki tüm isimleri al
    all_contacts = db.execute(text("""
        SELECT id, name, tax_number
        FROM contacts
        WHERE tax_number IS NOT NULL
    """)).fetchall()
    
    # İsim benzerliği hesapla
    similarities = []
    for contact in all_contacts:
        ratio = SequenceMatcher(None, 
                               missing.efatura_isim.upper(), 
                               contact.name.upper()).ratio()
        if ratio > 0.5:  # %50'den fazla benzerlik
            similarities.append({
                'contact_id': contact.id,
                'contact_name': contact.name,
                'contact_vkn': contact.tax_number,
                'similarity': ratio
            })
    
    # En benzerleri göster
    similarities.sort(key=lambda x: x['similarity'], reverse=True)
    if similarities:
        print(f'  🔍 Benzer cariler:')
        for sim in similarities[:3]:
            print(f'    {sim["similarity"]*100:.1f}% → {sim["contact_name"]} (VKN: {sim["contact_vkn"]})')
    else:
        print('  ❌ Benzer cari bulunamadı')

# 4. YEVMİYE KAYITLARINDA VAR MI KONTROLÜ
print('\n4. YEVMİYE KAYITLARINDA KULLANIM ANALİZİ:')
print('-'*80)

# 320 hesaplarında bu VKN'ler kullanılmış mı?
print('\nEksik VKN\'lerin 320 hesaplardaki durumu:')

for missing in missing_vkns[:5]:
    # 320 hesap kodundan VKN çıkar (son 10-11 hane)
    vkn_usage = db.execute(text("""
        SELECT 
            a.code,
            a.name,
            COUNT(DISTINCT tl.transaction_id) as kullanim_sayisi,
            SUM(ABS(tl.credit)) as toplam_tutar
        FROM accounts a
        LEFT JOIN transaction_lines tl ON tl.account_id = a.id
        WHERE a.code LIKE :vkn_pattern
        GROUP BY a.id
    """), {'vkn_pattern': f'320.%{missing.vkn}%'}).fetchall()
    
    if vkn_usage:
        print(f'\n  VKN {missing.vkn}:')
        for usage in vkn_usage:
            if usage.kullanim_sayisi:
                print(f'    ✅ {usage.code} - {usage.name}')
                print(f'       {usage.kullanim_sayisi} işlem, Toplam: {usage.toplam_tutar:,.2f} TL')

# 5. HESAP KODUNDAN VKN ÇIKARMA - CONTACT_ID DOLDURMA POTANSİYELİ
print('\n5. TRANSACTION_LINES CONTACT_ID DOLDURMA ANALİZİ:')
print('-'*80)

# 320 hesaplarında contact_id NULL olanları say
null_contacts = db.execute(text("""
    SELECT 
        COUNT(*) as toplam,
        COUNT(DISTINCT a.code) as farkli_hesap,
        SUM(ABS(tl.credit)) as toplam_tutar
    FROM transaction_lines tl
    JOIN accounts a ON tl.account_id = a.id
    WHERE a.code LIKE '320.%'
    AND tl.contact_id IS NULL
    AND tl.credit > 0
""")).fetchone()

print(f'\n320 hesaplarda contact_id NULL:')
print(f'  Toplam satır: {null_contacts.toplam:,}')
print(f'  Farklı hesap: {null_contacts.farkli_hesap:,}')
print(f'  Toplam tutar: {null_contacts.toplam_tutar:,.2f} TL')

# Örnek hesap kodları ve çıkarılabilecek VKN'ler
sample_accounts = db.execute(text("""
    SELECT DISTINCT
        a.code,
        a.name,
        COUNT(DISTINCT tl.id) as satir_sayisi
    FROM accounts a
    JOIN transaction_lines tl ON tl.account_id = a.id
    WHERE a.code LIKE '320.%'
    AND tl.contact_id IS NULL
    GROUP BY a.id
    ORDER BY satir_sayisi DESC
    LIMIT 10
""")).fetchall()

print('\n320 hesap örnekleri (contact_id NULL olanlar):')
for acc in sample_accounts:
    # Son 10-11 haneyi VKN olarak çıkar
    code_parts = acc.code.split('.')
    if len(code_parts) > 1:
        potential_vkn = code_parts[-1]  # Son part
        # Contact'ta var mı kontrol et
        contact_check = db.execute(text("""
            SELECT id, name FROM contacts WHERE tax_number = :vkn LIMIT 1
        """), {'vkn': potential_vkn}).fetchone()
        
        status = '✅' if contact_check else '❌'
        contact_info = f'→ {contact_check.name}' if contact_check else '(contact yok)'
        print(f'  {status} {acc.code:20s} | VKN: {potential_vkn:12s} {contact_info}')

# 6. ÖNERİ RAPORU
print('\n' + '='*80)
print('ÖNERİLER:')
print('='*80)

print(f'\n1. ❌ {len(missing_vkns)} adet eksik VKN için contact oluşturulmalı')
print(f'2. ✅ {null_contacts.toplam:,} satırda contact_id doldurulabilir (320 hesap kodundan VKN çıkararak)')
print(f'3. 🔍 İsim benzerliği analizi ile bazı VKN\'ler manuel eşleştirilebilir')
print(f'4. 📊 VKN format standardizasyonu gerekebilir')

print('\nSONRAKİ ADIMLAR:')
print('  A) Eksik carileri e-faturadan otomatik oluştur')
print('  B) 320 hesap kodundan VKN çıkarıp contact_id doldur')
print('  C) E-fatura - yevmiye eşleştirmesini tekrar çalıştır')

db.close()
