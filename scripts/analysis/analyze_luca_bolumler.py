"""
Luca bölümlerini ve sistemdeki cost_centers'ı analiz et
"""
import pymysql
from collections import Counter

def analyze():
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='muhasebe_sistem',
        charset='utf8mb4'
    )
    
    cursor = conn.cursor()
    
    # 1. Luca bölümleri
    print("=" * 80)
    print("LUCA BÖLÜMLER (monthly_personnel_records)")
    print("=" * 80)
    
    cursor.execute("""
        SELECT bolum_adi, COUNT(*) as sayi
        FROM monthly_personnel_records
        WHERE donem = '2025-08'
        GROUP BY bolum_adi
        ORDER BY sayi DESC
    """)
    
    bolumler = cursor.fetchall()
    print(f"\nToplam {len(bolumler)} farklı bölüm:\n")
    
    for bolum, sayi in bolumler:
        print(f"  {sayi:3d} kişi - {bolum}")
    
    # 2. Sistemdeki Cost Centers
    print("\n" + "=" * 80)
    print("SİSTEMDEKİ MALİYET MERKEZLERİ (cost_centers)")
    print("=" * 80)
    
    cursor.execute("""
        SELECT id, code, name, is_active
        FROM cost_centers
        ORDER BY code
    """)
    
    cost_centers = cursor.fetchall()
    print(f"\nToplam {len(cost_centers)} maliyet merkezi:\n")
    
    for cc_id, code, name, active in cost_centers:
        status = "✓" if active else "✗"
        print(f"  {status} [{code:10s}] {name}")
    
    # 3. Eşleştirme önerileri
    print("\n" + "=" * 80)
    print("EŞLEŞTİRME ÖNERİLERİ")
    print("=" * 80)
    print("\nLuca bölüm prefix'leri:\n")
    
    prefixes = Counter()
    for bolum, _ in bolumler:
        if bolum and '-' in bolum:
            prefix = bolum.split('-')[0].strip()
            prefixes[prefix] += 1
    
    for prefix, count in prefixes.most_common():
        print(f"  {prefix:3s} → {count} kayıt")
    
    conn.close()

if __name__ == "__main__":
    analyze()
