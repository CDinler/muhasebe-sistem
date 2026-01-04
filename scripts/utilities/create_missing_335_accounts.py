"""
Mevcut personellere 335.{TCKN} hesapları oluştur ve bağla
"""
from app.core.database import SessionLocal
from app.models.personnel import Personnel
from app.models.account import Account

db = SessionLocal()

try:
    # account_id NULL olan personelleri bul
    personnel_without_account = db.query(Personnel).filter(
        Personnel.account_id.is_(None),
        Personnel.tckn.isnot(None)
    ).all()
    
    print(f"Hesapsız personel sayısı: {len(personnel_without_account)}")
    
    created_count = 0
    linked_count = 0
    
    for p in personnel_without_account:
        account_code = f"335.{p.tckn}"
        
        # Hesap var mı kontrol et
        account = db.query(Account).filter(Account.code == account_code).first()
        
        if not account:
            # Hesap oluştur
            account = Account(
                code=account_code,
                name=f"{p.first_name} {p.last_name}",
                account_type="liability",
                is_active=True
            )
            db.add(account)
            db.flush()
            created_count += 1
            print(f"✅ Hesap oluşturuldu: {account_code} - {p.first_name} {p.last_name}")
        
        # Personnel'e bağla
        p.account_id = account.id
        linked_count += 1
    
    db.commit()
    
    print(f"\n✅ İşlem tamamlandı!")
    print(f"Oluşturulan hesap: {created_count}")
    print(f"Bağlanan personel: {linked_count}")
    
except Exception as e:
    db.rollback()
    print(f"❌ HATA: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
