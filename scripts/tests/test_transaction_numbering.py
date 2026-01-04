from app.core.database import SessionLocal
from app.utils.transaction_numbering import get_next_transaction_number

db = SessionLocal()

try:
    print("Testing transaction numbering...")
    
    # Get next number without commit (for preview)
    next_num = get_next_transaction_number(db, prefix="F", commit=False)
    print(f"✅ Next transaction number (no commit): {next_num}")
    
    # Rollback to not consume the number
    db.rollback()
    print("✅ Rollback successful - number not consumed")
    
    # Try again
    next_num2 = get_next_transaction_number(db, prefix="F", commit=False)
    print(f"✅ After rollback, next number: {next_num2}")
    
    # Should be the same
    if next_num == next_num2:
        print("✅ Rollback worked correctly! Numbers match.")
    else:
        print(f"❌ Numbers don't match: {next_num} vs {next_num2}")
    
    # Rollback again
    db.rollback()
    
    # Now commit one
    next_num3 = get_next_transaction_number(db, prefix="F", commit=True)
    print(f"✅ With commit: {next_num3}")
    
    # Next should be different
    next_num4 = get_next_transaction_number(db, prefix="F", commit=False)
    print(f"✅ After commit, next would be: {next_num4}")
    
    db.rollback()
    print("Test complete!")
        
finally:
    db.close()
