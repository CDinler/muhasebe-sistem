"""
Transaction Models

Domain için model proxy - mevcut modelleri kullan
"""
from app.models.transaction import Transaction
from app.models.transaction_line import TransactionLine

__all__ = ['Transaction', 'TransactionLine']
