"""
personnel_daily_attendance tablosunu kontrol et
"""
import pymysql

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'muhasebe_sistem',
    'charset': 'utf8mb4'
}

connection = pymysql.connect(**DB_CONFIG)
cursor = connection.cursor()

cursor.execute("SHOW COLUMNS FROM personnel_daily_attendance")
columns = cursor.fetchall()

print("\n📋 personnel_daily_attendance KOLONLARI:\n")
for col in columns:
    print(f"   {col[0]:30} {col[1]:40} {col[2]:8} {col[3]:10}")

cursor.close()
connection.close()
