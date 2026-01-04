"""
Bordro Sistemi Durum Kontrolü
"""
import sys
sys.path.insert(0, '.')

from app.core.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()

print("=" * 70)
print("BORDRO SİSTEMİ DURUM RAPORU")
print("=" * 70)

# 1. Puantaj tablosu
puantaj_exists = db.execute(text("""
    SELECT COUNT(*) FROM information_schema.tables 
    WHERE table_schema = 'muhasebe_luca' AND table_name = 'monthly_puantaj'
""")).scalar()

print(f"\n1. PUANTAJ SİSTEMİ: {'✅ VAR' if puantaj_exists else '❌ YOK'}")
if puantaj_exists:
    puantaj_count = db.execute(text('SELECT COUNT(*) FROM monthly_puantaj')).scalar()
    print(f"   Puantaj kayıt sayısı: {puantaj_count}")
    
    if puantaj_count > 0:
        donem_list = db.execute(text('SELECT DISTINCT donem FROM monthly_puantaj ORDER BY donem DESC LIMIT 5')).fetchall()
        print(f"   Dönemler: {', '.join([d[0] for d in donem_list])}")
        
        # Örnek kayıt
        sample = db.execute(text("""
            SELECT adi_soyadi, donem, normal_gun, fazla_mesai_saat, hafta_tatili_gun 
            FROM monthly_puantaj 
            LIMIT 1
        """)).fetchone()
        if sample:
            print(f"   Örnek: {sample[0]} - {sample[1]} - Normal:{sample[2]} gün, FM:{sample[3]} saat, HT:{sample[4]} gün")

# 2. LucaBordro tablosu
luca_exists = db.execute(text("""
    SELECT COUNT(*) FROM information_schema.tables 
    WHERE table_schema = 'muhasebe_luca' AND table_name = 'luca_bordro'
""")).scalar()

print(f"\n2. LUCA BORDRO: {'✅ VAR' if luca_exists else '❌ YOK'}")
if luca_exists:
    luca_count = db.execute(text('SELECT COUNT(*) FROM luca_bordro')).scalar()
    print(f"   Luca bordro kayıt sayısı: {luca_count}")
    
    if luca_count > 0:
        donem_list = db.execute(text('SELECT DISTINCT donem FROM luca_bordro ORDER BY donem DESC LIMIT 5')).fetchall()
        print(f"   Dönemler: {', '.join([d[0] for d in donem_list])}")
        
        # Örnek kayıt
        sample = db.execute(text("""
            SELECT adi_soyadi, donem, net_odenen, gelir_vergisi, ssk_isci 
            FROM luca_bordro 
            LIMIT 1
        """)).fetchone()
        if sample:
            print(f"   Örnek: {sample[0]} - {sample[1]} - Net:{sample[2]}, GV:{sample[3]}, SSK:{sample[4]}")

# 3. PersonnelContract tablosu
contract_exists = db.execute(text("""
    SELECT COUNT(*) FROM information_schema.tables 
    WHERE table_schema = 'muhasebe_luca' AND table_name = 'personnel_contracts'
""")).scalar()

print(f"\n3. PERSONEL SÖZLEŞMELERİ: {'✅ VAR' if contract_exists else '❌ YOK'}")
if contract_exists:
    contract_count = db.execute(text('SELECT COUNT(*) FROM personnel_contracts WHERE is_active = 1')).scalar()
    print(f"   Aktif sözleşme sayısı: {contract_count}")
    
    if contract_count > 0:
        ucret_nevi = db.execute(text('SELECT ucret_nevi, COUNT(*) FROM personnel_contracts WHERE is_active = 1 GROUP BY ucret_nevi')).fetchall()
        print(f"   Ücret nevleri:")
        for nevi, count in ucret_nevi:
            print(f"      - {nevi or 'NULL'}: {count} sözleşme")
        
        # Maaş2 (elden) olan sözleşmeler
        maas2_count = db.execute(text('SELECT COUNT(*) FROM personnel_contracts WHERE is_active = 1 AND maas2_tutar > 0')).scalar()
        print(f"   Maaş2 (Elden) olan: {maas2_count} sözleşme")

# 4. Personnel tablosu
personnel_exists = db.execute(text("""
    SELECT COUNT(*) FROM information_schema.tables 
    WHERE table_schema = 'muhasebe_luca' AND table_name = 'personnel'
""")).scalar()

print(f"\n4. PERSONEL KARTLARI: {'✅ VAR' if personnel_exists else '❌ YOK'}")
if personnel_exists:
    personnel_count = db.execute(text('SELECT COUNT(*) FROM personnel WHERE is_active = 1')).scalar()
    print(f"   Aktif personel sayısı: {personnel_count}")

# 5. PayrollCalculation tablosu
calc_exists = db.execute(text("""
    SELECT COUNT(*) FROM information_schema.tables 
    WHERE table_schema = 'muhasebe_luca' AND table_name = 'payroll_calculations'
""")).scalar()

print(f"\n5. BORDRO HESAPLAMALARI: {'✅ VAR' if calc_exists else '❌ YOK'}")
if calc_exists:
    calc_count = db.execute(text('SELECT COUNT(*) FROM payroll_calculations')).scalar()
    print(f"   Hesaplanmış bordro sayısı: {calc_count}")
    
    if calc_count > 0:
        donem_list = db.execute(text('SELECT DISTINCT donem FROM payroll_calculations ORDER BY donem DESC LIMIT 5')).fetchall()
        print(f"   Dönemler: {', '.join([d[0] for d in donem_list])}")
        
        # Yevmiye tipleri
        tipler = db.execute(text('SELECT yevmiye_tipi, COUNT(*) FROM payroll_calculations GROUP BY yevmiye_tipi')).fetchall()
        print(f"   Yevmiye tipleri:")
        for tip, count in tipler:
            print(f"      - Tip {tip or 'NULL'}: {count} bordro")
        
        # İstatistikler
        stats = db.execute(text("""
            SELECT 
                COUNT(*) as toplam,
                SUM(CASE WHEN is_exported = 1 THEN 1 ELSE 0 END) as fise_aktarildi,
                SUM(CASE WHEN has_error = 1 THEN 1 ELSE 0 END) as hatali
            FROM payroll_calculations
        """)).fetchone()
        print(f"   Durum: Toplam={stats[0]}, Fişe Aktarıldı={stats[1]}, Hatalı={stats[2]}")

print("\n" + "=" * 70)
print("EKSİK KONTROLLER")
print("=" * 70)

# Eksikleri tespit et
eksikler = []

if not puantaj_exists:
    eksikler.append("❌ PUANTAJ TABLOSU YOK")
elif puantaj_count == 0:
    eksikler.append("⚠️ PUANTAJ KAYDI YOK - Şantiyelerden puantaj Excel'i yüklenecek")

if not luca_exists:
    eksikler.append("❌ LUCA BORDRO TABLOSU YOK")
elif luca_count == 0:
    eksikler.append("⚠️ LUCA BORDRO YOK - Luca Excel'den bordro yüklenecek")

if not contract_exists:
    eksikler.append("❌ PERSONEL SÖZLEŞMELERİ TABLOSU YOK")
elif contract_count == 0:
    eksikler.append("⚠️ AKTİF SÖZLEŞME YOK")

if not personnel_exists:
    eksikler.append("❌ PERSONEL TABLOSU YOK")
elif personnel_count == 0:
    eksikler.append("⚠️ AKTİF PERSONEL YOK")

if not calc_exists:
    eksikler.append("❌ PAYROLL_CALCULATIONS TABLOSU YOK")

if eksikler:
    print("\nEKSİKLER:")
    for eksik in eksikler:
        print(f"  {eksik}")
else:
    print("\n✅ TÜM SİSTEM BİLEŞENLERİ MEVCUT")

print("\n" + "=" * 70)
print("BORDRO HESAPLAMA MANTIĞI")
print("=" * 70)
print("""
1. VERİ KAYNAKLARI (3 adet):
   ├─ Luca Bordro: Net ödenen, vergiler, kesintiler (MAAŞ 1)
   ├─ Puantaj: Normal gün, FM saat, hafta tatili, tatil çalışması, izin
   └─ Sözleşme: Maaş2 (elden), ücret nevi, FM oranı, tatil oranı

2. HESAPLAMA ADIMLARI:
   
   A) MAAŞ 1 (Luca'dan):
      - Net ödenen direkt alınır
      - Kesintiler: İcra, BES, Avans
      - Vergiler: Gelir vergisi, Damga vergisi
      - SGK: İşçi + İşveren + Teşvik
   
   B) MAAŞ 2 (Elden - Sözleşme + Puantaj):
      - Günlük ücret = Maaş2 / 30
      - Normal çalışma = Günlük × Normal gün
      - Hafta tatili = Günlük × Hafta tatili gün
      - Fazla mesai = (Günlük/8) × FM saat × FM oranı (1.5)
      - Tatil mesaisi = Günlük × Tatil gün × Tatil oranı (2.0)
      - Ücretli izin = Günlük × İzin gün
      - TOPLAM = Normal + HT + FM + Tatil + İzin
   
   C) ELDEN YUVARLAMA:
      - Hesaplanan elden ücreti 100 TL'nin katına yuvarla
      - Fark = Yuvarlanmış - Hesaplanan
      - Fark > 0 → YUKARI, Fark < 0 → AŞAĞI

3. YEVMİYE TİPİ:
   - Tip A: Sadece Luca'da net ödenen var (banka ödemesi)
   - Tip B: Sadece elden ücret var (nakit ödeme)
   - Tip C: Her ikisi de var (karma ödeme)

4. HESAP KODLARI:
   - 335.XXXXXXXXXXX (11 haneli TCKN)
   - Sözleşmede tanımlı account_code kullanılır

5. EKSİK DURUM YÖNETİMİ:
   - Puantaj yoksa → Sadece Luca bordro işlenir (Tip A)
   - Sözleşme yoksa → Hesaplama yapılır ama elden ücret 0
   - Personnel yoksa → HATA, bordro atlanır
""")

print("=" * 70)

db.close()
