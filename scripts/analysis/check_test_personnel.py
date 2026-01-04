"""Check test personnel record"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from app.core.database import SessionLocal
from app.models.personnel_puantaj_grid import PersonnelPuantajGrid
from app.models.personnel import Personnel
from app.models.personnel_contract import PersonnelContract

db = SessionLocal()

# Grid'deki test kaydı
grid_record = db.query(PersonnelPuantajGrid).filter(
    PersonnelPuantajGrid.personnel_id == 999
).first()

if grid_record:
    print(f"Grid Record Found:")
    print(f"  Personnel ID: {grid_record.personnel_id}")
    print(f"  Donem: {grid_record.donem}")
    print(f"  Cost Center ID: {grid_record.cost_center_id}")
else:
    print("No grid record found for personnel_id=999")

# Personnel tablosunu kontrol et
person = db.query(Personnel).filter(Personnel.id == 999).first()
if person:
    print(f"\nPersonnel Record Found:")
    print(f"  ID: {person.id}")
    print(f"  Name: {person.first_name} {person.last_name}")
    print(f"  Active: {person.is_active}")
    
    # Contract kontrol et
    contract = db.query(PersonnelContract).filter(
        PersonnelContract.personnel_id == 999
    ).first()
    
    if contract:
        print(f"\nContract Found:")
        print(f"  Cost Center ID: {contract.cost_center_id}")
        print(f"  Start Date: {contract.ise_giris_tarihi}")
        print(f"  End Date: {contract.isten_cikis_tarihi}")
    else:
        print("\nNo contract found")
else:
    print("\nNo personnel record found for ID=999")

db.close()
