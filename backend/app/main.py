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
from app.domains.invoicing.einvoices.router import router as einvoices_router

app.include_router(personnel_router, prefix="/api/v2/personnel", tags=["Personnel Domain"])
app.include_router(accounts_router, prefix="/api/v2/accounts", tags=["Accounting Domain"])
app.include_router(einvoices_router, prefix="/api/v2/invoicing/einvoices", tags=["Invoicing Domain"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
