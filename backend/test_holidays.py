#!/usr/bin/env python
"""Test holiday query directly"""
import sys
from datetime import date
from pathlib import Path

# Backend klasörünü path'e ekle
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.models.personnel_daily_attendance import CalendarHoliday
from app.core.database import SessionLocal

def test_holidays():
    db = SessionLocal()
    try:
        # 2026-01 dönemi
        donem_ilk_gun = date(2026, 1, 1)
        donem_son_gun = date(2026, 1, 31)
        
        print(f"Querying holidays between {donem_ilk_gun} and {donem_son_gun}")
        
        holidays = db.query(CalendarHoliday).filter(
            CalendarHoliday.holiday_date >= donem_ilk_gun,
            CalendarHoliday.holiday_date <= donem_son_gun
        ).all()
        
        print(f"Found {len(holidays)} holidays:")
        for h in holidays:
            print(f"  - {h.holiday_date} {h.name} ({h.type})")
            
        # Holiday days
        holiday_days = {h.holiday_date.day for h in holidays}
        print(f"\nHoliday days: {sorted(holiday_days)}")
        
        # Response format
        holiday_list = [h.holiday_date.day for h in holidays]
        print(f"Response format: {holiday_list}")
        
    finally:
        db.close()

if __name__ == "__main__":
    test_holidays()
