# -*- coding: utf-8 -*-
# Router ordering fix: Specific routes MUST be registered before generic /{personnel_id}
# Timestamp: 2026-01-15 force reload
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.shared.middleware.error_handler import register_exception_handlers

app = FastAPI(
    title="Muhasebe API",
    description="Muhasebe Otomasyon Sistemi API",
    version="2.0.0",  # Updated for new architecture
    docs_url="/docs",
    redoc_url="/redoc"
)

# Register exception handlers (P0 - Critical improvement)
register_exception_handlers(app)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Muhasebe API çalışıyor",
        "version": "2.0.0",
        "architecture": "Domain-Driven Design",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "2.0.0"}


# Domain routers (V2 - DDD Architecture)
from app.domains.personnel.router import router as personnel_router
from app.domains.accounting.accounts.router import router as accounts_router
from app.domains.accounting.transactions.router import router as transactions_router
from app.domains.invoicing.einvoices.router import router as einvoices_router
from app.domains.personnel.payroll.router import router as payroll_router
from app.domains.personnel.contracts.router import router as contracts_router
from app.domains.personnel.draft_contracts.router import router as draft_contracts_router
from app.domains.personnel.luca_bordro.router import router as luca_bordro_router
from app.domains.personnel.luca_sicil.router import router as luca_sicil_router
from app.domains.personnel.monthly_records.router import router as monthly_records_router
from app.domains.personnel.bordro_calculation.router import router as bordro_calculation_router
from app.domains.personnel.bordro_yevmiye.router import router as bordro_yevmiye_router
from app.domains.personnel.puantaj.router import router as puantaj_router
from app.domains.personnel.puantaj_grid.router import router as puantaj_grid_router
from app.domains.partners.contacts.router import router as contacts_router
from app.domains.partners.cost_centers.router import router as cost_centers_router
from app.domains.reporting.reports.router import router as reports_router
from app.domains.settings.config.router import router as config_router
from app.domains.settings.document_types.router import router as document_types_router
from app.domains.auth.router import router as auth_router
from app.domains.users.router import router as users_router
from app.domains.email.router import router as email_router

# Personnel sub-routers - daha spesifik route'lar önce kayıtlanmalı
app.include_router(payroll_router, prefix="/api/v2/personnel/payroll", tags=["Personnel Domain"])
app.include_router(contracts_router, prefix="/api/v2/personnel/contracts", tags=["Personnel Domain"])
app.include_router(draft_contracts_router, prefix="/api/v2/personnel/draft-contracts", tags=["Personnel Domain"])
app.include_router(luca_bordro_router, prefix="/api/v2/personnel/luca-bordro", tags=["Personnel Domain"])
app.include_router(luca_sicil_router, prefix="/api/v2/personnel/luca-sicil", tags=["Personnel Domain"])
app.include_router(monthly_records_router, prefix="/api/v2/personnel/monthly-records", tags=["Personnel Domain"])
app.include_router(bordro_calculation_router, prefix="/api/v2/personnel/bordro-calculation", tags=["Personnel Domain"])
app.include_router(bordro_yevmiye_router, prefix="/api/v2/personnel/bordro-yevmiye", tags=["Personnel Domain"])
app.include_router(puantaj_router, prefix="/api/v2/personnel/puantaj", tags=["Personnel Domain"])
app.include_router(puantaj_grid_router, prefix="/api/v2/personnel/puantaj-grid", tags=["Personnel Domain"])
# Ana personnel router en sonda - /{personnel_id} path var
app.include_router(personnel_router, prefix="/api/v2/personnel", tags=["Personnel Domain"])
app.include_router(accounts_router, prefix="/api/v2/accounts", tags=["Accounting Domain"])
app.include_router(transactions_router, prefix="/api/v2/accounting/transactions", tags=["Accounting Domain"])
app.include_router(einvoices_router, prefix="/api/v2/invoicing/einvoices", tags=["Invoicing Domain"])
app.include_router(contacts_router, prefix="/api/v2/partners/contacts", tags=["Partners Domain"])
app.include_router(cost_centers_router, prefix="/api/v2/partners/cost-centers", tags=["Partners Domain"])
app.include_router(reports_router, prefix="/api/v2/reporting/reports", tags=["Reporting Domain"])
app.include_router(config_router, prefix="/api/v2/settings/config", tags=["Settings Domain"])
app.include_router(document_types_router, prefix="/api/v2/settings/document-types", tags=["Settings Domain"])
app.include_router(auth_router, prefix="/api/v2/auth", tags=["Auth Domain"])
app.include_router(users_router, prefix="/api/v2/users", tags=["Users Domain"])
app.include_router(email_router, prefix="/api/v2/email", tags=["Email Domain"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
