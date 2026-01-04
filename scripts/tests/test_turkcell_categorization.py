from app.utils.category_mapping import categorize_invoice_line, get_account_for_category

test_items = [
    "Tarife ve Paket Ücretleri",
    "Turkcell Iletisim Hizmetleri A.S.",
    "Turkcell",
]

for item in test_items:
    category = categorize_invoice_line(item)
    account = get_account_for_category(category, item)
    print(f"{item:50} → {category:15} → {account}")
