"""Monthly Personnel Records domain"""
from app.domains.personnel.monthly_records.router import router
from app.domains.personnel.monthly_records.service import MonthlyPersonnelRecordService
from app.domains.personnel.monthly_records.repository import MonthlyPersonnelRecordRepository

__all__ = [
    "router",
    "MonthlyPersonnelRecordService",
    "MonthlyPersonnelRecordRepository"
]
