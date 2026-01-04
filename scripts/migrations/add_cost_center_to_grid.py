"""
Add cost_center_id column to personnel_puantaj_grid table
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from sqlalchemy import create_engine, text
from app.core.config import settings

def add_cost_center_column():
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        # Check if column exists
        result = conn.execute(text("""
            SELECT COUNT(*) as count
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = 'muhasebe_sistem'
              AND TABLE_NAME = 'personnel_puantaj_grid'
              AND COLUMN_NAME = 'cost_center_id'
        """))
        
        exists = result.fetchone()[0] > 0
        
        if exists:
            print("✓ cost_center_id column already exists")
            return
        
        print("Adding cost_center_id column...")
        
        # Add column
        conn.execute(text("""
            ALTER TABLE personnel_puantaj_grid
            ADD COLUMN cost_center_id INT NULL,
            ADD INDEX idx_cost_center (cost_center_id)
        """))
        
        conn.commit()
        print("✓ cost_center_id column added successfully")

if __name__ == "__main__":
    add_cost_center_column()
