"""
Otomatik yevmiye kaydı oluşturma testleri
"""
from decimal import Decimal
import sys
from pathlib import Path
import json

sys.path.append(str(Path(__file__).parent))

from app.services.einvoice_accounting_service import generate_transaction_lines_from_invoice
from unittest.mock import Mock

print('=' * 80)
print('OTOMATİK YEVMİYE KAYDI OLUŞTURMA TESTİ')
print('=' * 80)

# Mock objeler
db = Mock()
transaction = Mock()
transaction.id = 1

# Test 1: Normal Alış Faturası (KDV %20)
print('\n1. NORMAL ALIŞ FATURASI (KDV %20):')
print('-' * 80)

contact = Mock()
contact.code = '320.00001'
contact.name = 'Test Tedarikçi A.Ş.'
contact.type = 'supplier'

invoice = Mock()
invoice.invoice_type_code = 'SATIS'
invoice.taxable_amount = Decimal('1000.00')
invoice.tax_amount = Decimal('200.00')
invoice.total_amount = Decimal('1200.00')
invoice.payable_amount = Decimal('1200.00')
invoice.withholding_tax_amount = None
invoice.tax_exemption_reason_code = None
invoice.tax_exemption_reason = None
invoice.raw_data = json.dumps({'vat_rate': '0.20'})

lines = generate_transaction_lines_from_invoice(db, invoice, transaction, contact)
print(f'Toplam {len(lines)} satır:')
for i, line in enumerate(lines, 1):
    borc = f"{line['debit']:>10.2f}" if line['debit'] else " " * 10
    alacak = f"{line['credit']:>10.2f}" if line['credit'] else " " * 10
    print(f"  {i}. {line['account_code']:12} BORÇ: {borc} ALACAK: {alacak} {line['description']}")

# Denge kontrolü
total_debit = sum(line['debit'] for line in lines)
total_credit = sum(line['credit'] for line in lines)
balanced = abs(total_debit - total_credit) < Decimal('0.01')
print(f'\nDenge: BORÇ {total_debit:.2f} = ALACAK {total_credit:.2f} {"✓" if balanced else "✗"}')

# Test 2: İade Faturası
print('\n2. İADE FATURASI:')
print('-' * 80)

invoice2 = Mock()
invoice2.invoice_type_code = 'IADE'
invoice2.taxable_amount = Decimal('-500.00')
invoice2.tax_amount = Decimal('-100.00')
invoice2.total_amount = Decimal('-600.00')
invoice2.payable_amount = Decimal('-600.00')
invoice2.withholding_tax_amount = None
invoice2.tax_exemption_reason_code = None
invoice2.tax_exemption_reason = None
invoice2.raw_data = json.dumps({'vat_rate': '0.20'})

lines2 = generate_transaction_lines_from_invoice(db, invoice2, transaction, contact)
print(f'Toplam {len(lines2)} satır:')
for i, line in enumerate(lines2, 1):
    borc = f"{line['debit']:>10.2f}" if line['debit'] else " " * 10
    alacak = f"{line['credit']:>10.2f}" if line['credit'] else " " * 10
    print(f"  {i}. {line['account_code']:12} BORÇ: {borc} ALACAK: {alacak} {line['description']}")

total_debit2 = sum(line['debit'] for line in lines2)
total_credit2 = sum(line['credit'] for line in lines2)
balanced2 = abs(total_debit2 - total_credit2) < Decimal('0.01')
print(f'\nDenge: BORÇ {total_debit2:.2f} = ALACAK {total_credit2:.2f} {"✓" if balanced2 else "✗"}')

# Test 3: Turkcell Örneği (Özel Vergiler)
print('\n3. TURKCELL FATURASI (ÖZEL VERGİLER):')
print('-' * 80)

contact3 = Mock()
contact3.code = '320.12345'
contact3.name = 'Turkcell İletişim Hizmetleri A.Ş.'
contact3.type = 'supplier'

invoice3 = Mock()
invoice3.invoice_type_code = 'SATIS'
invoice3.taxable_amount = Decimal('538.46')
invoice3.tax_amount = Decimal('107.69')
invoice3.total_amount = Decimal('795.90')
invoice3.payable_amount = Decimal('795.90')
invoice3.withholding_tax_amount = None
invoice3.tax_exemption_reason_code = None
invoice3.tax_exemption_reason = None
invoice3.raw_data = json.dumps({
    'vat_rate': '0.20',
    'oiv': '53.85',
    'telsiz': '14.94',
    'aracilik': '81.00'
})

lines3 = generate_transaction_lines_from_invoice(db, invoice3, transaction, contact3)
print(f'Toplam {len(lines3)} satır:')
for i, line in enumerate(lines3, 1):
    borc = f"{line['debit']:>10.2f}" if line['debit'] else " " * 10
    alacak = f"{line['credit']:>10.2f}" if line['credit'] else " " * 10
    print(f"  {i}. {line['account_code']:12} BORÇ: {borc} ALACAK: {alacak} {line['description']}")

total_debit3 = sum(line['debit'] for line in lines3)
total_credit3 = sum(line['credit'] for line in lines3)
balanced3 = abs(total_debit3 - total_credit3) < Decimal('0.01')
print(f'\nDenge: BORÇ {total_debit3:.2f} = ALACAK {total_credit3:.2f} {"✓" if balanced3 else "✗"}')

# Test 4: KDV İstisnası
print('\n4. KDV İSTİSNASI:')
print('-' * 80)

invoice4 = Mock()
invoice4.invoice_type_code = 'SATIS'
invoice4.taxable_amount = Decimal('1000.00')
invoice4.tax_amount = Decimal('0.00')
invoice4.total_amount = Decimal('1000.00')
invoice4.payable_amount = Decimal('1000.00')
invoice4.withholding_tax_amount = None
invoice4.tax_exemption_reason_code = '350'
invoice4.tax_exemption_reason = 'İhracat'
invoice4.raw_data = json.dumps({'vat_rate': '0.00'})

lines4 = generate_transaction_lines_from_invoice(db, invoice4, transaction, contact)
print(f'Toplam {len(lines4)} satır (191 yok):')
for i, line in enumerate(lines4, 1):
    borc = f"{line['debit']:>10.2f}" if line['debit'] else " " * 10
    alacak = f"{line['credit']:>10.2f}" if line['credit'] else " " * 10
    print(f"  {i}. {line['account_code']:12} BORÇ: {borc} ALACAK: {alacak} {line['description']}")

total_debit4 = sum(line['debit'] for line in lines4)
total_credit4 = sum(line['credit'] for line in lines4)
balanced4 = abs(total_debit4 - total_credit4) < Decimal('0.01')
print(f'\nDenge: BORÇ {total_debit4:.2f} = ALACAK {total_credit4:.2f} {"✓" if balanced4 else "✗"}')

print('\n' + '=' * 80)
print('TEST TAMAMLANDI')
print('=' * 80)
