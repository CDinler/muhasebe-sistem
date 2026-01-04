"""Update test personnel to be active and assign to cost center"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from app.core.database import SessionLocal
from app.models.personnel import Personnel
from app.models.personnel_contract import PersonnelContract
from app.models.personnel_puantaj_grid import PersonnelPuantajGrid
from datetime import date

db = SessionLocal()

# Personeli aktif yap
person = db.query(Personnel).filter(Personnel.id == 999).first()
if person:
    person.is_active = True
    print(f"✓ Personnel {person.first_name} {person.last_name} set to ACTIVE")

# Contract'ı güncelle - MERKEZ şantiyesine ata (ID=31)
contract = db.query(PersonnelContract).filter(
    PersonnelContract.personnel_id == 999
).first()

if contract:
    contract.cost_center_id = 31  # MERKEZ
    contract.ise_giris_tarihi = date(2024, 1, 1)
    contract.isten_cikis_tarihi = None  # Hala çalışıyor
    contract.is_active = True
    print(f"✓ Contract updated - Cost Center: 31 (MERKEZ), Start: 2024-01-01")

# Grid kaydını güncelle
grid = db.query(PersonnelPuantajGrid).filter(
    PersonnelPuantajGrid.personnel_id == 999,
    PersonnelPuantajGrid.donem == '2025-01'
).first()

if grid:
    grid.cost_center_id = 31
    print(f"✓ Grid record updated - Cost Center: 31 (MERKEZ)")

db.commit()
print("\n✅ All updates committed successfully")
print("\nNow select 'MERKEZ' cost center in the dropdown to see this personnel!")

db.close()
