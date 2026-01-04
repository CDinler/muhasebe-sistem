import sys
sys.path.insert(0, '.')

from app.core.database import SessionLocal
from app.crud import reports
from datetime import date, timedelta
from sqlalchemy import text

db = SessionLocal()
db.bind.echo = False

# İlk contact'ı al
contact = db.execute(text("SELECT id, code, name FROM contacts WHERE is_active = 1 LIMIT 1")).fetchone()
print(f"Test Contact: {contact[0]} - {contact[1]} - {contact[2]}")

# Son 1 yıl için rapor al
end_date = date.today()
start_date = end_date - timedelta(days=365)

print(f"\nRapor tarihleri: {start_date} - {end_date}")

try:
    report = reports.get_cari_report(db, start_date, end_date, contact[0])
    
    print(f"\n✅ Rapor Başarılı:")
    print(f"Contact ID: {report.contact_id}")
    print(f"Contact Code: {report.contact_code}")
    print(f"Contact Name: {report.contact_name}")
    print(f"Items: {len(report.items)}")
    
    if report.items:
        print(f"\nİlk 3 item:")
        for i, item in enumerate(report.items[:3]):
            print(f"  {i+1}. Account Code: {item.account_code}, Debit: {item.debit}, Credit: {item.credit}")
            
        # 120 ve 320 ayrımı
        items_120 = [i for i in report.items if i.account_code.startswith('120')]
        items_320 = [i for i in report.items if i.account_code.startswith('320')]
        
        print(f"\n120'li items: {len(items_120)}")
        print(f"320'li items: {len(items_320)}")
        
except Exception as e:
    print(f"\n❌ HATA: {e}")
    import traceback
    traceback.print_exc()

db.close()
