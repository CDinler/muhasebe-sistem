"""Invoicing domain main router"""
from fastapi import APIRouter
from app.domains.invoicing.einvoices.router import router as einvoices_router
from app.domains.invoicing.matching.router import router as matching_router

router = APIRouter()

# Include sub-routers
router.include_router(einvoices_router)
router.include_router(matching_router)
