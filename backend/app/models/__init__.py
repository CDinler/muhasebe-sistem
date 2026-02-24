"""
Models package - Backward compatibility layer
Import models lazily to avoid circular dependencies
"""

def __getattr__(name):
    """Lazy import models from domains"""
    # Accounting domain
    if name == 'Transaction':
        from app.domains.accounting.transactions.models import Transaction
        return Transaction
    elif name == 'TransactionLine':
        from app.domains.accounting.transactions.models import TransactionLine
        return TransactionLine
    elif name == 'Account':
        from app.domains.accounting.accounts.models import Account
        return Account
    
    # Partners domain
    elif name == 'Contact':
        from app.domains.partners.contacts.models import Contact
        return Contact
    elif name == 'CostCenter':
        from app.domains.partners.cost_centers.models import CostCenter
        return CostCenter
    
    # Users domain
    elif name == 'User':
        from app.domains.users.models import User
        return User
    elif name == 'UserEmailSettings':
        from app.domains.users.models import UserEmailSettings
        return UserEmailSettings
    
    # Personnel domain
    elif name == 'Personnel':
        from app.domains.personnel.models import Personnel
        return Personnel
    elif name == 'PersonnelContract':
        from app.domains.personnel.models import PersonnelContract
        return PersonnelContract
    elif name == 'PersonnelDraftContract':
        from app.domains.personnel.draft_contracts.models import PersonnelDraftContract
        return PersonnelDraftContract
    elif name == 'MonthlyPersonnelRecord':
        from app.domains.personnel.monthly_records.models import MonthlyPersonnelRecord
        return MonthlyPersonnelRecord
    elif name == 'LucaBordro':
        from app.domains.personnel.luca_bordro.models import LucaBordro
        return LucaBordro
    elif name == 'MonthlyPuantaj':
        from app.domains.personnel.puantaj.models import MonthlyPuantaj
        return MonthlyPuantaj
    elif name == 'PayrollCalculation':
        from app.domains.personnel.payroll.models import PayrollCalculation
        return PayrollCalculation
    elif name == 'PersonnelPuantajGrid':
        from app.domains.personnel.puantaj_grid.models import PersonnelPuantajGrid
        return PersonnelPuantajGrid
    elif name == 'PuantajDurum':
        from app.domains.personnel.puantaj_grid.models import PuantajDurum
        return PuantajDurum
    
    # Legal domain
    elif name == 'IcraTakip':
        from app.domains.legal.icra_takip.models import IcraTakip
        return IcraTakip
    
    # Settings domain
    elif name == 'SystemConfig':
        from app.domains.settings.config.models import SystemConfig
        return SystemConfig
    elif name == 'TaxBracket':
        from app.domains.settings.config.models import TaxBracket
        return TaxBracket
    elif name == 'DocumentType':
        from app.domains.settings.document_types.models import DocumentType
        return DocumentType
    elif name == 'TaxCode':
        from app.domains.settings.tax_codes.models import TaxCode
        return TaxCode
    
    # Invoicing domain
    elif name == 'EInvoice':
        from app.domains.invoicing.einvoices.models import EInvoice
        return EInvoice
    elif name == 'InvoiceTransactionMapping':
        from app.domains.invoicing.einvoices.models import InvoiceTransactionMapping
        return InvoiceTransactionMapping
    elif name == 'InvoiceTax':
        from app.domains.invoicing.einvoices.models import InvoiceTax
        return InvoiceTax
    
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    # Accounting
    "Transaction",
    "TransactionLine",
    "Account",
    # Partners
    "Contact",
    "CostCenter",
    # Users
    "User",
    "UserEmailSettings",
    # Personnel
    "Personnel",
    "PersonnelContract",
    "PersonnelDraftContract",
    "MonthlyPersonnelRecord",
    "LucaBordro",
    "MonthlyPuantaj",
    "PayrollCalculation",
    "PersonnelPuantajGrid",
    "PuantajDurum",
    # Legal
    "IcraTakip",
    # Settings
    "SystemConfig",
    "TaxBracket",
    "DocumentType",
    "TaxCode",
    # Invoicing
    "EInvoice",
    "InvoiceTransactionMapping",
    "InvoiceTax",
]
