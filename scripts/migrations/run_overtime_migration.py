"""Fazla mesai migration runner"""
import sys
from sqlalchemy import text
from app.core.database import engine

def run_migration():
    """Run overtime migration"""
    sql_file = '../database/migrations/20251222_add_overtime_to_puantaj_grid.sql'
    
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # Split by delimiter
    statements = []
    current = []
    in_delimiter = False
    
    for line in sql_content.split('\n'):
        line_stripped = line.strip()
        
        if line_stripped.startswith('DELIMITER'):
            in_delimiter = not in_delimiter
            continue
        
        current.append(line)
        
        if not in_delimiter and line_stripped.endswith(';'):
            stmt = '\n'.join(current).strip()
            if stmt and not stmt.startswith('--'):
                statements.append(stmt)
            current = []
    
    # Execute
    with engine.begin() as conn:
        for stmt in statements:
            if stmt.strip():
                try:
                    result = conn.execute(text(stmt))
                    if result.returns_rows:
                        for row in result:
                            print(dict(row._mapping))
                except Exception as e:
                    print(f"Statement: {stmt[:100]}...")
                    print(f"Error: {e}")
                    # Continue with other statements
    
    print("\n✅ Migration completed!")

if __name__ == '__main__':
    run_migration()
