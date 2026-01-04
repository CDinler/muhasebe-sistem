"""
Personnel model - MOVED TO DOMAINS
This is a proxy file for backward compatibility
"""
from app.domains.personnel.models import (
    Personnel,
    UcretNevi,
    CalismaTakvimi,
    MaasHesabi,
    Departman,
    KanunTipi
)

__all__ = ["Personnel", "UcretNevi", "CalismaTakvimi", "MaasHesabi", "Departman", "KanunTipi"]
