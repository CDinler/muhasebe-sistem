"""
E-Fatura PDF Upload API Endpoint
"""
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import Dict
import tempfile
import os

from app.core.database import get_db
from app.services.einvoice_pdf_processor import EInvoicePDFProcessor
from app.models.einvoice import EInvoice

router = APIRouter()


@router.post("/upload-pdf", response_model=Dict)
async def upload_invoice_pdf(
    *,
    db: Session = Depends(get_db),
    pdf_file: UploadFile = File(...),
    direction: str = 'incoming',  # incoming, outgoing, incoming-archive, outgoing-archive
):
    """
    E-Fatura/E-Arşiv PDF yükle (sadece PDF olan faturalar için)
    
    ⚠️ Otomatik format tespiti yapar - hem e-fatura hem e-arşiv için kullanılabilir!
    
    - PDF'den fatura bilgilerini çıkarır (otomatik e-fatura/e-arşiv tespiti)
    - Veritabanına kaydeder
    - PDF'i dosya sistemine saklar
    - Contact eşleştirmesi yapar (direction'a göre)
    - direction: incoming (gelen), outgoing (giden), incoming-archive, outgoing-archive
    """
    
    # Dosya türü kontrolü
    if not pdf_file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Sadece PDF dosyası yüklenebilir")
    
    # Geçici dosyaya kaydet
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        content = await pdf_file.read()
        tmp_file.write(content)
        tmp_path = tmp_file.name
    
    try:
        # PDF işle
        processor = EInvoicePDFProcessor(db)
        
        # save_invoice_from_pdf_only çağır (otomatik e-fatura/e-arşiv tespiti yapar)
        einvoice_id = processor.save_invoice_from_pdf_only(
            tmp_path, 
            original_filename=pdf_file.filename,
            direction=direction
        )
        
        if not einvoice_id:
            return {
                "success": False,
                "errors": ["PDF'den kritik bilgiler çıkarılamadı"],
                "message": "E-fatura kaydedilemedi"
            }
        
        # Kaydı getir
        einvoice = db.query(EInvoice).filter(EInvoice.id == einvoice_id).first()
        
        return {
            "success": True,
            "einvoice_id": einvoice_id,
            "invoice_number": einvoice.invoice_number,
            "ettn": einvoice.invoice_uuid,
            "issue_date": str(einvoice.issue_date) if einvoice.issue_date else None,
            "payable_amount": float(einvoice.payable_amount) if einvoice.payable_amount else 0.0,
            "currency_code": einvoice.currency_code or 'TRY',
            "direction": direction,
            "message": f"✅ E-fatura kaydedildi ({direction})"
        }
        
    finally:
        # Geçici dosyayı sil
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


@router.post("/attach-pdf/{einvoice_id}", response_model=Dict)
async def attach_pdf_to_einvoice(
    *,
    db: Session = Depends(get_db),
    einvoice_id: int,
    pdf_file: UploadFile = File(...),
):
    """
    Mevcut e-faturaya PDF ekle (XML zaten var, sadece PDF görüntüsü ekleniyor)
    """
    
    # Dosya türü kontrolü
    if not pdf_file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Sadece PDF dosyası yüklenebilir")
    
    # Geçici dosyaya kaydet
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        content = await pdf_file.read()
        tmp_file.write(content)
        tmp_path = tmp_file.name
    
    try:
        processor = EInvoicePDFProcessor(db)
        success = processor.attach_pdf_to_existing_einvoice(einvoice_id, tmp_path)
        
        if not success:
            raise HTTPException(status_code=404, detail="E-fatura bulunamadı")
        
        return {
            "success": True,
            "einvoice_id": einvoice_id,
            "message": "PDF başarıyla eşleştirildi"
        }
        
    finally:
        # Geçici dosyayı sil
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


@router.get("/pdf/{einvoice_id}")
async def get_einvoice_pdf(
    *,
    db: Session = Depends(get_db),
    einvoice_id: int,
):
    """
    E-fatura PDF'ini getir
    """
    einvoice = db.query(EInvoice).filter(EInvoice.id == einvoice_id).first()
    
    if not einvoice:
        raise HTTPException(status_code=404, detail="E-fatura bulunamadı")
    
    if not einvoice.pdf_path:
        raise HTTPException(status_code=404, detail="Bu faturanın PDF'i yok")
    
    processor = EInvoicePDFProcessor(db)
    pdf_path = processor.get_pdf_full_path(einvoice)
    
    if not pdf_path or not pdf_path.exists():
        raise HTTPException(status_code=404, detail="PDF dosyası bulunamadı")
    
    return FileResponse(
        path=str(pdf_path),
        media_type='application/pdf',
        filename=f"{einvoice.invoice_number}.pdf"
    )
