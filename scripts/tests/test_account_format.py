"""
Hesap kodu formatını test et: 191.01001
"""
from decimal import Decimal

def get_191_account_code(vat_rate: Decimal, has_withholding: bool) -> str:
    """191 hesap kodu döndürür (detaylı format)"""
    vat_pct = int(vat_rate * 100)
    vat_str = str(vat_pct).zfill(2)
    suffix = '002' if has_withholding else '001'
    return f"191.{vat_str}{suffix}"

# Test
print("🧪 Hesap kodu formatı testi:\n")

test_cases = [
    (Decimal('0.01'), False, '191.01001'),
    (Decimal('0.01'), True, '191.01002'),
    (Decimal('0.08'), False, '191.08001'),
    (Decimal('0.08'), True, '191.08002'),
    (Decimal('0.10'), False, '191.10001'),
    (Decimal('0.10'), True, '191.10002'),
    (Decimal('0.18'), False, '191.18001'),
    (Decimal('0.18'), True, '191.18002'),
    (Decimal('0.20'), False, '191.20001'),
    (Decimal('0.20'), True, '191.20002'),
]

for vat_rate, has_withholding, expected in test_cases:
    result = get_191_account_code(vat_rate, has_withholding)
    status = "✅" if result == expected else "❌"
    print(f"{status} KDV {int(vat_rate*100)}%, Tevkifat: {has_withholding} → {result} (beklenen: {expected})")

print("\n✨ Tamamlandı!")
