from sqlalchemy import create_engine, text
from app.core.config import get_settings

settings = get_settings()
engine = create_engine(settings.DATABASE_URL)
conn = engine.connect()

# Son işlemler
result = conn.execute(text("SELECT transaction_number, description, created_at FROM transactions WHERE transaction_number LIKE 'F00026%' ORDER BY transaction_number DESC LIMIT 5"))
print("\n--- SON 5 TRANSACTION ---")
for row in result:
    print(f"{row[0]} | {row[1][:50]} | {row[2]}")

# Counter durumu
counter = conn.execute(text("SELECT last_number FROM transaction_counter WHERE id = 1")).fetchone()
print(f"\n--- COUNTER ---")
print(f"Son numara: {counter[0] if counter else 'YOK'}")

conn.close()
