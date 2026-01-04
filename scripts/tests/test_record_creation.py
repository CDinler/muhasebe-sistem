"""
Excel'den bir örnek TC ile test - kayıt oluşturuluyor mu?
"""
from app.core.database import SessionLocal
from app.models.personnel import Personnel
from app.models.monthly_personnel_record import MonthlyPersonnelRecord
from sqlalchemy import and_
from datetime import date

# İlk TC'yi test edelim: 65476025612
tc = "65476025612"
donem = "2025-01"
bolum_adi = "34-HABAŞ 9 ALİAĞA"

db = SessionLocal()

try:
    # Personnel var mı?
    personnel = db.query(Personnel).filter(Personnel.tckn == tc).first()
    
    if not personnel:
        print(f"❌ TC {tc} personnel tablosunda yok!")
    else:
        print(f"✅ Personnel bulundu: {personnel.first_name} {personnel.last_name} (ID: {personnel.id})")
        
        # Mevcut kayıt var mı?
        existing = db.query(MonthlyPersonnelRecord).filter(
            and_(
                MonthlyPersonnelRecord.personnel_id == personnel.id,
                MonthlyPersonnelRecord.donem == donem,
                MonthlyPersonnelRecord.bolum_adi == bolum_adi
            )
        ).first()
        
        if existing:
            print(f"⚠️  Kayıt zaten var - ID: {existing.id}")
            print(f"   Dönem: {existing.donem}")
            print(f"   Bölüm: {existing.bolum_adi}")
        else:
            print(f"✅ Kayıt yok - yeni kayıt oluşturulabilir")
            
            # Test kaydı oluştur
            test_record = MonthlyPersonnelRecord(
                personnel_id=personnel.id,
                donem=donem,
                bolum_adi=bolum_adi,
                ucret=10000,
                ucret_tipi="N"
            )
            
            db.add(test_record)
            db.commit()
            
            print(f"✅ Test kaydı oluşturuldu - ID: {test_record.id}")
            
            # Silalım
            db.delete(test_record)
            db.commit()
            print(f"✅ Test kaydı silindi")
            
finally:
    db.close()
