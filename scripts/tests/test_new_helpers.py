"""
Yeni yardımcı fonksiyonları test eder
"""
from decimal import Decimal
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from app.services.einvoice_accounting_service import (
    get_191_account_code,
    get_withholding_rate_from_code,
    calculate_invoice_balance_adjustment
)

print('=' * 80)
print('YENİ YARDIMCI FONKSİYONLAR TEST')
print('=' * 80)

# 1. 191 Hesap Kodu Testi
print('\n1. get_191_account_code() Testi:')
print('-' * 80)
test_cases = [
    (Decimal('0.01'), False, '191.01.001'),
    (Decimal('0.08'), False, '191.08.001'),
    (Decimal('0.10'), False, '191.10.001'),
    (Decimal('0.18'), False, '191.18.001'),
    (Decimal('0.20'), False, '191.20.001'),
    (Decimal('0.01'), True, '191.01.002'),
    (Decimal('0.20'), True, '191.20.002'),
]

for vat_rate, withholding, expected in test_cases:
    result = get_191_account_code(vat_rate, withholding)
    status = '✓' if result == expected else '✗'
    print(f'{status} KDV %{int(vat_rate*100)}, Tevkifat: {withholding} → {result} (beklenen: {expected})')

# 2. Tevkifat Oranı Testi
print('\n2. get_withholding_rate_from_code() Testi:')
print('-' * 80)
test_codes = [
    ('601', Decimal('0.40'), '4/10'),
    ('602', Decimal('0.90'), '9/10'),
    ('612', Decimal('0.90'), '9/10 - Temizlik'),
    ('624', Decimal('0.20'), '2/10 - Yük Taşımacılığı'),
    ('801', Decimal('1.00'), '10/10'),
]

for code, expected, desc in test_codes:
    result = get_withholding_rate_from_code(code)
    status = '✓' if result == expected else '✗'
    print(f'{status} Kod {code} ({desc}) → %{int(result*100) if result else "?"} (beklenen: %{int(expected*100)})')

# 3. Fark Hesaplama Testi
print('\n3. calculate_invoice_balance_adjustment() Testi:')
print('-' * 80)
test_balances = [
    (Decimal('795.896'), Decimal('795.90'), Decimal('0.004'), 'Pozitif fark (659 BORÇ)'),
    (Decimal('795.90'), Decimal('795.896'), Decimal('-0.004'), 'Negatif fark (679 ALACAK)'),
    (Decimal('1000.00'), Decimal('1000.00'), Decimal('0.00'), 'Fark yok'),
]

for total, payable, expected, desc in test_balances:
    result = calculate_invoice_balance_adjustment(total, payable)
    status = '✓' if result == expected else '✗'
    print(f'{status} {total} → {payable} = {result} ({desc})')

print('\n' + '=' * 80)
print('TEST TAMAMLANDI')
print('=' * 80)
