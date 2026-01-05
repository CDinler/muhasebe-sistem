# -*- coding: utf-8 -*-
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


# API v1 router (legacy endpoints)
from app.api.v1.router import api_router
app.include_router(api_router, prefix="/api/v1", tags=["v1"])

# Domain routers (new architecture)
from app.domains.personnel.router import router as personnel_router
from app.domains.accounting.accounts.router import router as accounts_router
from app.domains.accounting.transactions.router import router as transactions_router
from app.domains.invoicing.einvoices.router import router as einvoices_router
from app.domains.personnel.payroll.router import router as payroll_router
from app.domains.partners.contacts.router import router as contacts_router
from app.domains.partners.cost_centers.router import router as cost_centers_router
from app.domains.reporting.reports.router import router as reports_router
from app.domains.settings.config.router import router as config_router

app.include_router(personnel_router, prefix="/api/v2/personnel", tags=["Personnel Domain"])
app.include_router(payroll_router, prefix="/api/v2/personnel/payroll", tags=["Personnel Domain"])
app.include_router(accounts_router, prefix="/api/v2/accounts", tags=["Accounting Domain"])
app.include_router(transactions_router, prefix="/api/v2/accounting/transactions", tags=["Accounting Domain"])
app.include_router(einvoices_router, prefix="/api/v2/invoicing/einvoices", tags=["Invoicing Domain"])
app.include_router(contacts_router, prefix="/api/v2/partners/contacts", tags=["Partners Domain"])
app.include_router(cost_centers_router, prefix="/api/v2/partners/cost-centers", tags=["Partners Domain"])
app.include_router(reports_router, prefix="/api/v2/reporting/reports", tags=["Reporting Domain"])
app.include_router(config_router, prefix="/api/v2/settings/config", tags=["Settings Domain"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
