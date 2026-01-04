from app.services.einvoice_pdf_processor import EInvoicePDFProcessor
from app.core.database import SessionLocal

db = SessionLocal()
processor = EInvoicePDFProcessor(db)

pdf_path = r'C:\Users\CAGATAY\Downloads\2025_12\OZB2025000005993_37037fd7-a0e8-4a75-83e8-0b06d9798486.pdf'

try:
    data = processor.extract_invoice_data_from_pdf(pdf_path)
    print('✅ Data extracted:')
    print(f'  Invoice No: {data.get("invoice_no")}')
    print(f'  ETTN: {data.get("ettn")}')
    print(f'  Issue Date: {data.get("issue_date")}')
    print(f'  Payable Amount: {data.get("payable_amount")}')
    
    errors = processor.validate_extracted_data(data)
    if errors:
        print('\n❌ Validation Errors:')
        for error in errors:
            print(f'  - {error}')
    else:
        print('\n✅ Validation: OK')
        
except Exception as e:
    print(f'\n❌ EXCEPTION: {e}')
    import traceback
    traceback.print_exc()
finally:
    db.close()
