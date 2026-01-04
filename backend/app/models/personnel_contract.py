"""
PersonnelContract model - MOVED TO DOMAINS
This is a proxy file for backward compatibility
"""
from app.domains.personnel.models import (
    PersonnelContract,
    UcretNevi,
    CalismaTakvimi,
    MaasHesabi,
    Departman,
    KanunTipi
)

__all__ = ["PersonnelContract", "UcretNevi", "CalismaTakvimi", "MaasHesabi", "Departman", "KanunTipi"]
