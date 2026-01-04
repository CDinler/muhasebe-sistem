"""Pydantic schemas for API request/response models"""

# Account schemas
from app.schemas.account import *

# Auth schemas
from app.schemas.auth import *

# Contact schemas
from app.schemas.contact import *

# Cost Center schemas
from app.schemas.cost_center import (
    CostCenterBase,
    CostCenterCreate,
    CostCenterUpdate,
    CostCenterResponse,
)

# E-Invoice schemas
from app.schemas.einvoice import *

# Personnel schemas
from app.schemas.personnel import (
    PersonnelBase,
    PersonnelCreate,
    PersonnelUpdate,
    PersonnelResponse,
    PersonnelList,
)

# Personnel Contract schemas
from app.schemas.personnel_contract import (
    CalismaTakvimi,
    Departman,
    SigortaDurumu,
    MaasHesabi,
    PersonnelContractBase,
    PersonnelContractCreate,
    PersonnelContractUpdate,
    PersonnelContractResponse,
    PersonnelContractList,
)

# Monthly Personnel Record schemas
from app.schemas.monthly_personnel_record import (
    MonthlyPersonnelRecordBase,
    MonthlyPersonnelRecordCreate,
    MonthlyPersonnelRecordUpdate,
    MonthlyPersonnelRecordResponse,
    MonthlyPersonnelRecordList,
)

# Personnel Puantaj Grid schemas
from app.schemas.personnel_puantaj_grid import (
    PuantajGunBase,
    PersonnelPuantajGridBase,
    PersonnelPuantajGridCreate,
    PersonnelPuantajGridUpdate,
    PersonnelPuantajGridResponse,
    PersonnelPuantajGridList,
)

# Luca Bordro schemas
from app.schemas.luca_bordro import (
    LucaBordroBase,
    LucaBordroCreate,
    LucaBordroUpdate,
    LucaBordroResponse,
    LucaBordroList,
)

# Report schemas
from app.schemas.reports import *

# Transaction schemas
from app.schemas.transaction import *

__all__ = [
    # Cost Center
    "CostCenterBase",
    "CostCenterCreate",
    "CostCenterUpdate",
    "CostCenterResponse",
    # Personnel
    "PersonnelBase",
    "PersonnelCreate",
    "PersonnelUpdate",
    "PersonnelResponse",
    "PersonnelList",
    # Personnel Contract
    "CalismaTakvimi",
    "Departman",
    "SigortaDurumu",
    "MaasHesabi",
    "PersonnelContractBase",
    "PersonnelContractCreate",
    "PersonnelContractUpdate",
    "PersonnelContractResponse",
    "PersonnelContractList",
    # Monthly Personnel Record
    "MonthlyPersonnelRecordBase",
    "MonthlyPersonnelRecordCreate",
    "MonthlyPersonnelRecordUpdate",
    "MonthlyPersonnelRecordResponse",
    "MonthlyPersonnelRecordList",
    # Personnel Puantaj Grid
    "PuantajGunBase",
    "PersonnelPuantajGridBase",
    "PersonnelPuantajGridCreate",
    "PersonnelPuantajGridUpdate",
    "PersonnelPuantajGridResponse",
    "PersonnelPuantajGridList",
    # Luca Bordro
    "LucaBordroBase",
    "LucaBordroCreate",
    "LucaBordroUpdate",
    "LucaBordroResponse",
    "LucaBordroList",
]
