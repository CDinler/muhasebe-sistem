#!/usr/bin/env python3
"""Counter güncellemesini test et"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import Settings
from app.utils.transaction_numbering import get_next_transaction_number

settings = Settings()
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# Test
db = SessionLocal()

print("ÖNCE:")
result = db.execute(text("SELECT last_number FROM transaction_counter WHERE id = 1")).fetchone()
before = result[0] if result else 0
print(f"  Counter: {before}")

print("\nYENİ NUMARA AL:")
new_num = get_next_transaction_number(db, prefix="F", commit=True)
print(f"  Dönen numara: {new_num}")

print("\nSONRA:")
db2 = SessionLocal()  # Yeni session - counter güncellemesini görmek için
result = db2.execute(text("SELECT last_number FROM transaction_counter WHERE id = 1")).fetchone()
after = result[0] if result else 0
print(f"  Counter: {after}")
print(f"  Fark: {after - before}")

if after == before + 1:
    print("\n✅ BAŞARILI - Counter güncellendi!")
else:
    print(f"\n❌ BAŞARISIZ - Counter güncellenMEDİ! (Beklenen: {before+1}, Gerçek: {after})")

db.close()
db2.close()
