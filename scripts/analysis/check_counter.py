from app.core.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()

# Check if transaction_counter exists
result = db.execute(text("SHOW TABLES LIKE 'transaction_counter'")).fetchall()
print("transaction_counter table exists:", len(result) > 0)

if len(result) > 0:
    # Get current counter value
    counter = db.execute(text("SELECT * FROM transaction_counter")).fetchall()
    print("Counter data:", counter)
else:
    print("Table doesn't exist yet - will be created on first use")

db.close()
