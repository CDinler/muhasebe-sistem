"""Bordro sistemi gerçek durum raporu"""
import sys
sys.path.insert(0, '.')
from app.core.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()

print("=" * 70)
print("BORDRO SİSTEMİ GERÇEK DURUM RAPORU")
print("=" * 70)

# 1. Personnel
personnel_count = db.execute(text("SELECT COUNT(*) FROM personnel")).scalar()
personnel_active = db.execute(text("SELECT COUNT(*) FROM personnel WHERE is_active = 1")).scalar()
print(f"\n1. PERSONEL KARTLARI: {personnel_count} kayıt ({personnel_active} aktif)")

if personnel_count > 0:
    sample = db.execute(text("SELECT first_name, last_name, tckn, department FROM personnel LIMIT 3")).fetchall()
    print("   Örnek kayıtlar:")
    for s in sample:
        print(f"     - {s[0]} {s[1]} ({s[2]}) - {s[3] or 'Departman yok'}")

# 2. Personnel Contracts
contract_count = db.execute(text("SELECT COUNT(*) FROM personnel_contracts")).scalar()
contract_active = db.execute(text("SELECT COUNT(*) FROM personnel_contracts WHERE is_active = 1")).scalar()
print(f"\n2. PERSONEL SÖZLEŞMELERİ: {contract_count} kayıt ({contract_active} aktif)")

if contract_count > 0:
    ucret_nevi = db.execute(text("SELECT ucret_nevi, COUNT(*) FROM personnel_contracts WHERE is_active = 1 GROUP BY ucret_nevi")).fetchall()
    print("   Ücret nevleri:")
    for nevi, count in ucret_nevi:
        print(f"     - {nevi or 'Belirtilmemiş'}: {count} sözleşme")
    
    maas2_count = db.execute(text("SELECT COUNT(*) FROM personnel_contracts WHERE is_active = 1 AND maas2_tutar > 0")).scalar()
    print(f"   Maaş2 (Elden) olan: {maas2_count} sözleşme")

# 3. Luca Bordro
luca_count = db.execute(text("SELECT COUNT(*) FROM luca_bordro")).scalar()
print(f"\n3. LUCA BORDRO: {luca_count} kayıt")

if luca_count > 0:
    donemler = db.execute(text("SELECT DISTINCT donem FROM luca_bordro ORDER BY donem DESC LIMIT 5")).fetchall()
    print(f"   Dönemler: {', '.join([d[0] for d in donemler])}")
    
    sample = db.execute(text("SELECT adi_soyadi, donem, net_odenen FROM luca_bordro LIMIT 3")).fetchall()
    print("   Örnek kayıtlar:")
    for s in sample:
        print(f"     - {s[0]} ({s[1]}): Net={s[2]:,.2f} TL")

# 4. Monthly Puantaj
puantaj_count = db.execute(text("SELECT COUNT(*) FROM monthly_puantaj")).scalar()
print(f"\n4. PUANTAJ KAYITLARI: {puantaj_count} kayıt")

if puantaj_count > 0:
    donemler = db.execute(text("SELECT DISTINCT donem FROM monthly_puantaj ORDER BY donem DESC LIMIT 5")).fetchall()
    print(f"   Dönemler: {', '.join([d[0] for d in donemler])}")
    
    sample = db.execute(text("SELECT adi_soyadi, donem, normal_gun, fazla_mesai_saat FROM monthly_puantaj LIMIT 3")).fetchall()
    print("   Örnek kayıtlar:")
    for s in sample:
        print(f"     - {s[0]} ({s[1]}): Normal={s[2]} gün, FM={s[3]} saat")
else:
    print("   ⚠️ HİÇ PUANTAJ KAYDI YOK!")

# 5. Payroll Calculations
calc_count = db.execute(text("SELECT COUNT(*) FROM payroll_calculations")).scalar()
print(f"\n5. BORDRO HESAPLAMALARI: {calc_count} kayıt")

if calc_count > 0:
    donemler = db.execute(text("SELECT DISTINCT donem FROM payroll_calculations ORDER BY donem DESC LIMIT 5")).fetchall()
    print(f"   Dönemler: {', '.join([d[0] for d in donemler])}")
    
    tipler = db.execute(text("SELECT yevmiye_tipi, COUNT(*) FROM payroll_calculations GROUP BY yevmiye_tipi")).fetchall()
    print("   Yevmiye tipleri:")
    for tip, count in tipler:
        print(f"     - Tip {tip or 'Belirtilmemiş'}: {count} bordro")
    
    stats = db.execute(text("""
        SELECT 
            SUM(CASE WHEN is_exported = 1 THEN 1 ELSE 0 END) as fise_aktarildi,
            SUM(CASE WHEN has_error = 1 THEN 1 ELSE 0 END) as hatali
        FROM payroll_calculations
    """)).fetchone()
    print(f"   Durum: Fişe Aktarıldı={stats[0]}, Hatalı={stats[1]}")

# 6. Monthly Personnel Records
mpr_count = db.execute(text("SELECT COUNT(*) FROM monthly_personnel_records")).scalar()
print(f"\n6. AYLIK PERSONEL SİCİL: {mpr_count} kayıt")

if mpr_count > 0:
    donemler = db.execute(text("SELECT DISTINCT donem FROM monthly_personnel_records ORDER BY donem DESC LIMIT 5")).fetchall()
    print(f"   Dönemler: {', '.join([d[0] for d in donemler])}")

print("\n" + "=" * 70)
print("EKSİKLER VE ÖNERİLER")
print("=" * 70)

eksikler = []

if puantaj_count == 0:
    eksikler.append("❌ PUANTAJ KAYDI YOK - Şantiyelerden puantaj Excel yükle")

if luca_count > 0 and calc_count == 0:
    eksikler.append("⚠️ Luca bordro var AMA hesaplama yok - Bordro hesaplat")

if luca_count == 0:
    eksikler.append("⚠️ Luca bordro yok - Luca Excel yükle")

if contract_active == 0:
    eksikler.append("❌ AKTİF SÖZLEŞME YOK")

if personnel_active == 0:
    eksikler.append("❌ AKTİF PERSONEL YOK")

if eksikler:
    for eksik in eksikler:
        print(f"\n  {eksik}")
else:
    print("\n  ✅ TÜM SİSTEM TAM VE HAZIR!")

print("\n" + "=" * 70)

db.close()
