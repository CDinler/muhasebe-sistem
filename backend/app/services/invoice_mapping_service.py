"""
Invoice-Transaction Mapping Service

Handles all operations for linking e-invoices to accounting transactions
using the junction table (invoice_transaction_mappings).
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional, List, Dict
from app.models.einvoice import EInvoice
from app.models.transaction import Transaction
from app.models.invoice_transaction_mapping import InvoiceTransactionMapping


def create_mapping(
    db: Session,
    einvoice_id: int,
    transaction_id: int,
    mapping_type: str = 'auto',
    confidence_score: float = 1.00,
    mapped_by: Optional[int] = None,
    notes: Optional[str] = None
) -> InvoiceTransactionMapping:
    """
    Create a new invoice-transaction mapping
    
    Args:
        db: Database session
        einvoice_id: E-invoice ID
        transaction_id: Transaction ID
        mapping_type: 'auto' or 'manual'
        confidence_score: Match confidence (0.00-1.00)
        mapped_by: User ID who created the mapping (for manual mappings)
        notes: Optional notes
        
    Returns:
        Created mapping object
    """
    # Get invoice number for caching
    einvoice = db.query(EInvoice).filter(EInvoice.id == einvoice_id).first()
    document_number = einvoice.invoice_number if einvoice else None
    
    # Check if mapping already exists
    existing = db.query(InvoiceTransactionMapping).filter(
        and_(
            InvoiceTransactionMapping.einvoice_id == einvoice_id,
            InvoiceTransactionMapping.transaction_id == transaction_id
        )
    ).first()
    
    if existing:
        # Update existing mapping
        existing.mapping_type = mapping_type
        existing.confidence_score = confidence_score
        existing.mapped_by = mapped_by
        if notes:
            existing.notes = notes
        db.commit()
        db.refresh(existing)
        return existing
    
    # Create new mapping
    mapping = InvoiceTransactionMapping(
        einvoice_id=einvoice_id,
        transaction_id=transaction_id,
        document_number=document_number,
        mapping_type=mapping_type,
        confidence_score=confidence_score,
        mapped_by=mapped_by,
        notes=notes
    )
    
    db.add(mapping)
    db.commit()
    db.refresh(mapping)
    
    return mapping


def get_transaction_for_invoice(
    db: Session,
    einvoice_id: int
) -> Optional[Transaction]:
    """
    Get the linked transaction for an e-invoice
    
    Returns:
        Transaction object or None if not mapped
    """
    mapping = db.query(InvoiceTransactionMapping).filter(
        InvoiceTransactionMapping.einvoice_id == einvoice_id
    ).first()
    
    if mapping:
        return mapping.transaction
    return None


def get_invoices_for_transaction(
    db: Session,
    transaction_id: int
) -> List[EInvoice]:
    """
    Get all e-invoices linked to a transaction
    
    Returns:
        List of EInvoice objects
    """
    mappings = db.query(InvoiceTransactionMapping).filter(
        InvoiceTransactionMapping.transaction_id == transaction_id
    ).all()
    
    return [m.einvoice for m in mappings]


def delete_mapping(
    db: Session,
    einvoice_id: int,
    transaction_id: Optional[int] = None
) -> int:
    """
    Delete invoice-transaction mapping(s)
    
    Args:
        db: Database session
        einvoice_id: E-invoice ID
        transaction_id: Optional transaction ID. If None, deletes all mappings for the invoice
        
    Returns:
        Number of deleted mappings
    """
    query = db.query(InvoiceTransactionMapping).filter(
        InvoiceTransactionMapping.einvoice_id == einvoice_id
    )
    
    if transaction_id:
        query = query.filter(InvoiceTransactionMapping.transaction_id == transaction_id)
    
    count = query.delete()
    db.commit()
    
    return count


def auto_match_by_document_number(
    db: Session,
    einvoice_id: Optional[int] = None,
    batch_size: int = 1000
) -> Dict[str, int]:
    """
    Auto-match e-invoices to transactions using document_number
    
    Args:
        db: Database session
        einvoice_id: Optional - match only this invoice. If None, matches all unmatched invoices
        batch_size: Number of invoices to process at once
        
    Returns:
        Dict with stats: {'matched': count, 'skipped': count}
    """
    stats = {'matched': 0, 'skipped': 0}
    
    # Get unmatched e-invoices
    query = db.query(EInvoice).filter(EInvoice.invoice_category == 'incoming')
    
    if einvoice_id:
        query = query.filter(EInvoice.id == einvoice_id)
    else:
        # Only process invoices without mappings
        mapped_ids = db.query(InvoiceTransactionMapping.einvoice_id).distinct()
        query = query.filter(~EInvoice.id.in_(mapped_ids))
    
    query = query.limit(batch_size)
    einvoices = query.all()
    
    for einvoice in einvoices:
        # Find transaction with matching document_number
        transaction = db.query(Transaction).filter(
            Transaction.document_number == einvoice.invoice_number
        ).first()
        
        if transaction:
            create_mapping(
                db=db,
                einvoice_id=einvoice.id,
                transaction_id=transaction.id,
                mapping_type='auto',
                confidence_score=1.00
            )
            stats['matched'] += 1
        else:
            stats['skipped'] += 1
    
    return stats


def get_mapping_stats(db: Session) -> Dict[str, int]:
    """
    Get statistics about invoice-transaction mappings
    
    Returns:
        Dict with counts
    """
    total_invoices = db.query(EInvoice).filter(
        EInvoice.invoice_category == 'incoming'
    ).count()
    
    mapped_invoices = db.query(InvoiceTransactionMapping.einvoice_id).distinct().count()
    
    auto_mappings = db.query(InvoiceTransactionMapping).filter(
        InvoiceTransactionMapping.mapping_type == 'auto'
    ).count()
    
    manual_mappings = db.query(InvoiceTransactionMapping).filter(
        InvoiceTransactionMapping.mapping_type == 'manual'
    ).count()
    
    return {
        'total_invoices': total_invoices,
        'mapped_invoices': mapped_invoices,
        'unmapped_invoices': total_invoices - mapped_invoices,
        'auto_mappings': auto_mappings,
        'manual_mappings': manual_mappings,
        'total_mappings': auto_mappings + manual_mappings
    }
