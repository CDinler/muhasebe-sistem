from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

engine = create_engine('mysql+pymysql://root:@localhost:3306/muhasebe_sistem')
db = sessionmaker(bind=engine)()

try:
    result = db.execute(text("""
        UPDATE einvoices 
        SET invoice_uuid = LOWER(invoice_uuid) 
        WHERE invoice_uuid != LOWER(invoice_uuid)
    """))
    
    print(f"Updated: {result.rowcount} rows")
    db.commit()
    print("✅ UUID'ler lowercase yapıldı!")
    
except Exception as e:
    print(f"❌ Hata: {e}")
    db.rollback()
finally:
    db.close()
