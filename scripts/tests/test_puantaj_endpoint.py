"""Test puantaj template endpoint"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.api.v1.endpoints.puantaj import download_puantaj_template

def test_template():
    db = SessionLocal()
    try:
        print("Testing download_puantaj_template for 2025-11...")
        response = download_puantaj_template("2025-11", db)
        print(f"✅ Success! Media type: {response.media_type}")
        print(f"Headers: {response.headers}")
    except Exception as e:
        print(f"❌ ERROR: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_template()
