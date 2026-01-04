# -*- coding: utf-8 -*-
"""API v1 Router"""
from fastapi import APIRouter
from app.api.v1.endpoints import (
    transactions, accounts, cost_centers, contacts, auth, reports, einvoices, einvoice_pdf, invoice_matching,
    luca_bordro, system_config, personnel_contracts, puantaj, bordro_calculation, yevmiye_generation, bordro_yevmiye_v2, personnel, luca_sicil, puantaj_grid
)
from app.routes import document_types

api_router = APIRouter()

# Include endpoints
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(transactions.router, prefix="/transactions", tags=["transactions"])
api_router.include_router(accounts.router, prefix="/accounts", tags=["accounts"])
api_router.include_router(cost_centers.router, prefix="/cost-centers", tags=["cost-centers"])
api_router.include_router(contacts.router, prefix="/contacts", tags=["contacts"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(einvoices.router, tags=["E-Fatura"])
api_router.include_router(einvoice_pdf.router, prefix="/einvoices/pdf", tags=["E-Fatura PDF"])
api_router.include_router(invoice_matching.router, prefix="/invoice-matching", tags=["invoice-matching"])

# Document types (lookup tables)
api_router.include_router(document_types.router, tags=["document-types"])
api_router.include_router(document_types.subtype_router, tags=["document-subtypes"])

# Bordro endpoints
api_router.include_router(luca_bordro.router, prefix="/luca-bordro", tags=["Luca Bordro"])
api_router.include_router(luca_sicil.router, prefix="/luca-sicil", tags=["Luca Personel Sicil"])
api_router.include_router(system_config.router, prefix="/system-config", tags=["Sistem Ayarları"])
api_router.include_router(personnel.router, prefix="/personnel", tags=["Personel"])
api_router.include_router(personnel_contracts.router, prefix="/personnel-contracts", tags=["Personel Sözleşmeleri"])
api_router.include_router(puantaj.router, prefix="/puantaj", tags=["Puantaj"])
api_router.include_router(puantaj_grid.router, prefix="/puantaj-grid", tags=["Puantaj Grid"])
api_router.include_router(bordro_calculation.router, prefix="/bordro", tags=["Bordro Hesaplama"])
api_router.include_router(yevmiye_generation.router, prefix="/bordro", tags=["Bordro Yevmiye"])
api_router.include_router(bordro_yevmiye_v2.router, prefix="/bordro/v2", tags=["Bordro Yevmiye V2"])

@api_router.get("/test")
async def test_endpoint():
    """Test endpoint to verify API is working"""
    return {
        "status": "success",
        "message": "API v1 is working!",
        "database": "MySQL via XAMPP",
        "endpoints": {
            "transactions": "/api/v1/transactions",
            "accounts": "/api/v1/accounts",
            "test": "/api/v1/test",
            "info": "/api/v1/info"
        }
    }

@api_router.get("/info")
async def api_info():
    """API information"""
    return {
        "name": "Muhasebe API",
        "version": "1.0.0",
        "description": "Muhasebe Otomasyon Sistemi REST API",
        "tech_stack": {
            "backend": "FastAPI",
            "database": "MySQL (XAMPP)",
            "orm": "SQLAlchemy 2.0"
        },
        "models": [
            "Transaction",
            "TransactionLine",
            "Contact",
            "CostCenter",
            "Account",
            "User"
        ],
        "seed_data": {
            "accounts": 23,
            "cost_centers": 3,
            "users": 1
        }
    }
