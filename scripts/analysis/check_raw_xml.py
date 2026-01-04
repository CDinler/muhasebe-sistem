import pymysql

conn = pymysql.connect(
    host='localhost',
    user='root',
    password='',
    database='muhasebe_sistem',
    charset='utf8mb4'
)

cursor = conn.cursor()
cursor.execute("SELECT raw_data FROM einvoices WHERE invoice_uuid='9d24ecf5-fbaf-49e8-82ab-233761b7e67e'")
row = cursor.fetchone()

if row:
    raw_data = row[0]
    print(f"Type: {type(raw_data)}")
    print(f"Length: {len(raw_data)}")
    print("\nFirst 1000 chars:")
    print(raw_data[:1000])
    print("\n...")
    print("\nLast 500 chars:")
    print(raw_data[-500:])
else:
    print("No data")

cursor.close()
conn.close()
