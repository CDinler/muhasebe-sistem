import pymysql

conn = pymysql.connect(
    host='localhost',
    user='root',
    password='',
    database='muhasebe_sistem',
    charset='utf8mb4'
)

cursor = conn.cursor()
cursor.execute("SELECT line_extension_amount, tax_exclusive_amount, tax_inclusive_amount, payable_amount FROM einvoices WHERE invoice_uuid='9d24ecf5-fbaf-49e8-82ab-233761b7e67e'")
row = cursor.fetchone()

if row:
    line_ext, tax_exc, tax_inc, payable = row
    print(f"Line Extension Amount: {line_ext}")
    print(f"Tax Exclusive Amount: {tax_exc}")
    print(f"Tax Inclusive Amount: {tax_inc}")
    print(f"Payable Amount: {payable}")
    
    print("\nHesaplama:")
    print(f"Tarife + Diğer - Düzeltme + Aracılık = 666.15 + 0.04 - 0.05 + 134.00 = 800.14")
    print(f"Database Line Ext: {line_ext}")
    print(f"Fark: {line_ext - 800.14}")

cursor.close()
conn.close()
