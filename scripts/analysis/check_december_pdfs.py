"""
2025-12 ayı PDF kayıtlarını kontrol et
"""
from app.core.database import SessionLocal
from sqlalchemy import func
from app.models.einvoice import EInvoice
from datetime import datetime

db = SessionLocal()

try:
    # 2025-12 tarih aralığı
    start_date = datetime(2025, 12, 1)
    end_date = datetime(2025, 12, 31, 23, 59, 59)
    
    print("\n" + "="*60)
    print("2025 ARALIK AYI E-FATURA PDF DURUMU")
    print("="*60)
    
    # Toplam fatura sayısı
    total = db.query(EInvoice).filter(
        EInvoice.issue_date >= start_date.date(),
        EInvoice.issue_date <= end_date.date()
    ).count()
    
    print(f"\n📊 Toplam Fatura: {total}")
    
    # PDF'li faturalar
    with_pdf = db.query(EInvoice).filter(
        EInvoice.issue_date >= start_date.date(),
        EInvoice.issue_date <= end_date.date(),
        EInvoice.pdf_path.isnot(None),
        EInvoice.pdf_path != ''
    ).count()
    
    print(f"✅ PDF'li Fatura: {with_pdf}")
    
    # PDF'siz faturalar
    without_pdf = db.query(EInvoice).filter(
        EInvoice.issue_date >= start_date.date(),
        EInvoice.issue_date <= end_date.date(),
        (EInvoice.pdf_path.is_(None)) | (EInvoice.pdf_path == '')
    ).count()
    
    print(f"❌ PDF'siz Fatura: {without_pdf}")
    
    # Direction'a göre dağılım
    print("\n📋 Direction Bazında Dağılım:")
    print("-" * 60)
    
    for category in ['incoming', 'outgoing', 'incoming-archive', 'outgoing-archive']:
        total_dir = db.query(EInvoice).filter(
            EInvoice.issue_date >= start_date.date(),
            EInvoice.issue_date <= end_date.date(),
            EInvoice.invoice_category == category
        ).count()
        
        with_pdf_dir = db.query(EInvoice).filter(
            EInvoice.issue_date >= start_date.date(),
            EInvoice.issue_date <= end_date.date(),
            EInvoice.invoice_category == category,
            EInvoice.pdf_path.isnot(None),
            EInvoice.pdf_path != ''
        ).count()
        
        print(f"{category:20s}: {with_pdf_dir:3d}/{total_dir:3d} PDF'li")
    
    # Son yüklenen 10 PDF
    print("\n🔹 Son Yüklenen 10 PDF:")
    print("-" * 60)
    
    recent_pdfs = db.query(EInvoice).filter(
        EInvoice.issue_date >= start_date.date(),
        EInvoice.issue_date <= end_date.date(),
        EInvoice.pdf_path.isnot(None),
        EInvoice.pdf_path != ''
    ).order_by(EInvoice.id.desc()).limit(10).all()
    
    for inv in recent_pdfs:
        print(f"ID: {inv.id:5d} | {inv.invoice_number:20s} | {inv.invoice_category:20s} | {inv.issue_date.strftime('%Y-%m-%d')}")
    
    print("\n" + "="*60)
    
finally:
    db.close()
