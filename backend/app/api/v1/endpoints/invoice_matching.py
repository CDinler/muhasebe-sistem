"""
Invoice-Payment Matching API endpoints
Fatura-Ödeme Eşleştirme API
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.core.database import get_db
from app.crud import invoice_matching


router = APIRouter()


# ========== Request/Response Models ==========

class MatchSuggestionResponse(BaseModel):
    """Eşleştirme önerisi response"""
    payment: dict
    invoice: dict
    score: int
    reasons: List[str]
    confidence: str
    invoice_numbers_in_desc: List[str]
    dates_in_desc: List[str]


class AutoMatchResponse(BaseModel):
    """Otomatik eşleştirme response"""
    matched_count: int
    matches: List[dict]


class ApproveMatchRequest(BaseModel):
    """Manuel onay request"""
    transaction_id: int
    invoice_number: str


class UpdateRelatedInvoicesRequest(BaseModel):
    """Manuel düzenleme request"""
    transaction_id: int
    invoice_numbers: str  # Virgülle ayrılmış


# ========== Endpoints ==========

@router.get("/suggestions", response_model=List[MatchSuggestionResponse])
def get_matching_suggestions(
    min_score: int = Query(60, description="Minimum skor (60-100)"),
    limit: int = Query(100, description="Maksimum sonuç sayısı"),
    db: Session = Depends(get_db)
):
    """
    Fatura-ödeme eşleştirme önerilerini getir
    
    - **min_score**: Minimum eşleşme skoru (60=MEDIUM, 80=HIGH)
    - **limit**: Maksimum sonuç sayısı
    
    Skorlama:
    - 80-100: HIGH (otomatik eşleştirme önerilir)
    - 60-79: MEDIUM (manuel onay önerilir)
    - 0-59: LOW (gösterilmez)
    """
    try:
        suggestions = invoice_matching.get_matching_suggestions(
            db=db,
            min_score=min_score,
            limit=limit
        )
        return suggestions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/auto-match", response_model=AutoMatchResponse)
def apply_automatic_matching(
    min_score: int = Query(80, description="Minimum skor (önerilen: 80)"),
    db: Session = Depends(get_db)
):
    """
    Yüksek skorlu eşleştirmeleri otomatik uygula
    
    - **min_score**: Minimum skor (önerilen: 80 - HIGH confidence)
    
    İşlem:
    - Belirlenen skorun üstündeki eşleşmeleri otomatik olarak 
      transactions.related_invoice_number alanına yazar
    - Birden fazla fatura varsa virgülle ayrılmış olarak saklar
    """
    try:
        result = invoice_matching.apply_automatic_matching(
            db=db,
            min_score=min_score
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/approve")
def approve_match(
    request: ApproveMatchRequest,
    db: Session = Depends(get_db)
):
    """
    Bir eşleştirme önerisini manuel olarak onayla
    
    - **transaction_id**: Ödeme fişinin ID'si
    - **invoice_number**: Fatura numarası
    
    İşlem:
    - transactions.related_invoice_number alanına ekler
    - Mevcut değer varsa, virgülle ayrılmış olarak ekler
    """
    try:
        result = invoice_matching.approve_match(
            db=db,
            transaction_id=request.transaction_id,
            invoice_number=request.invoice_number
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reject")
def reject_match(
    request: ApproveMatchRequest,
    db: Session = Depends(get_db)
):
    """
    Bir eşleştirme önerisini reddet (hiçbir işlem yapılmaz, sadece log)
    
    - **transaction_id**: Ödeme fişinin ID'si
    - **invoice_number**: Fatura numarası
    """
    try:
        result = invoice_matching.reject_match(
            db=db,
            transaction_id=request.transaction_id,
            invoice_number=request.invoice_number
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/update-related-invoices")
def update_related_invoices(
    request: UpdateRelatedInvoicesRequest,
    db: Session = Depends(get_db)
):
    """
    Manuel olarak related_invoice_number güncelle
    
    - **transaction_id**: Ödeme fişinin ID'si
    - **invoice_numbers**: Virgülle ayrılmış fatura numaraları (örn: "ABC123,DEF456")
    
    İşlem:
    - transactions.related_invoice_number alanını günceller
    - Boş string gönderilirse NULL yapar
    """
    try:
        result = invoice_matching.update_related_invoices(
            db=db,
            transaction_id=request.transaction_id,
            invoice_numbers=request.invoice_numbers
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
