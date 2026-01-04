"""
Cost center'a göre varsayılan hesap seçimi testi
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.utils.category_mapping import get_account_for_category

# Test senaryoları
test_cases = [
    # (category, item_name, cost_center_name, expected_account)
    ('diger', 'Test Ürünü', None, '770'),  # Belirtilmemiş → 770 (Merkez)
    ('diger', 'Test Ürünü', 'MERKEZ', '770'),  # Merkez → 770
    ('diger', 'Test Ürünü', 'Merkez', '770'),  # Merkez (küçük harf) → 770
    ('diger', 'Test Ürünü', 'HABAŞ_ALIAĞA', '740'),  # Şantiye → 740
    ('diger', 'Test Ürünü', 'ASSAN_ORHANLI', '740'),  # Şantiye → 740
    ('elektrik', 'Elektrik Tüketimi', 'HABAŞ_GEBZE', '740.00001'),  # Elektrik spesifik → 740.00001
    ('haberlesme', 'Turkcell Faturası', 'MERKEZ', '740.00004'),  # Haberleşme spesifik → 740.00004
]

print("🧪 COST CENTER'A GÖRE VARSAYILAN HESAP SEÇİMİ TESTİ\n")
print("=" * 100)

for category, item_name, cost_center_name, expected in test_cases:
    result = get_account_for_category(category, item_name, cost_center_name)
    status = "✅" if result == expected else "❌"
    cc_display = cost_center_name or "(Belirtilmemiş)"
    print(f"{status} {category:15} | {item_name:25} | {cc_display:20} → {result:15} (beklenen: {expected})")

print("\n" + "=" * 100)
print("\n📋 KURALLAR:")
print("  • Merkez/Belirtilmemiş → 770 (Genel Yönetim Gideri)")
print("  • Şantiye/Diğer → 740 (Hizmet Üretim Maliyeti)")
print("  • Spesifik kategori varsa (elektrik, haberleşme vb.) → O hesabı kullan")
print("\n✨ Test tamamlandı!")
