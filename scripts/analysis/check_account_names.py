import pymysql

conn = pymysql.connect(
    host='localhost',
    user='root',
    password='',
    database='muhasebe_sistem',
    charset='utf8mb4'
)

cursor = conn.cursor()
cursor.execute("SELECT code, name FROM accounts WHERE code IN ('740.00004', '770.00201')")
rows = cursor.fetchall()

print("Hesap Kodlari:")
for code, name in rows:
    print(f"{code}: {name}")

cursor.close()
conn.close()
