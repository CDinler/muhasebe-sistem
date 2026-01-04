import sys
sys.path.insert(0, '.')

from app.utils.category_mapping import categorize_invoice_line, get_account_for_category

item_name = "Tarife ve Paket Ücretleri"
cost_center_name = "Merkez"

print(f"item_name: {item_name}")
print(f"cost_center_name: {cost_center_name}")

category = categorize_invoice_line(item_name)
print(f"Category: {category}")

account = get_account_for_category(category, item_name, cost_center_name)
print(f"Account: {account}")
