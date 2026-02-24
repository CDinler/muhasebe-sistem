"""Transactions domain package"""
# Avoid circular imports - only export router
from app.domains.accounting.transactions.router import router

__all__ = ['router']
