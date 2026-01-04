from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from datetime import date
from typing import Annotated
import io
from app.crud.report_740_service_costs import get_740_service_production_costs_excel
from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.models.user import User
from app.crud import reports as reports_crud
from app.schemas.reports import MizanReport, IncomeStatement, DebtorCreditorReport, CariReport, MuavinReport
from app.crud.cost_center_reports import get_cost_center_monthly_excel

router = APIRouter()

@router.get('/740-service-costs/excel')
def get_740_service_costs_excel_api(
    start_date: Annotated[date, Query(description='Başlangıç tarihi')],
    end_date: Annotated[date, Query(description='Bitiş tarihi')],
    cost_center_id: Annotated[int | None, Query(description='Maliyet Merkezi ID (opsiyonel)')] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    740 Hizmet ve Üretim Maliyetleri Excel raporu.
    - **start_date**: Dönem başlangıç tarihi
    - **end_date**: Dönem bitiş tarihi
    - **cost_center_id**: (Opsiyonel) Sadece seçili maliyet merkezi için
    """
    try:
        excel_file = get_740_service_production_costs_excel(db, start_date, end_date, cost_center_id)
        filename = f"740_service_costs_{start_date}_{end_date}{'_cc' + str(cost_center_id) if cost_center_id else ''}.xlsx"
        return StreamingResponse(
            io.BytesIO(excel_file),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Access-Control-Expose-Headers": "Content-Disposition"
            }
        )
    except Exception as e:
        import traceback
        print(f"Excel generation error: {e}")
        print(traceback.format_exc())
        raise

@router.get('/cost-center-monthly/excel')
def get_cost_center_monthly_excel_api(
    year: Annotated[int, Query(description='Yıl')],
    month: Annotated[int, Query(description='Ay (1-12)')],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Cost center bazında aylık hizmet üretim maliyetleri Excel raporu.
    - **year**: Rapor yılı
    - **month**: Rapor ayı (1-12)
    """
    try:
        excel_file = get_cost_center_monthly_excel(db, year, month)
        filename = f"cost_center_report_{year}_{month:02d}.xlsx"
        return StreamingResponse(
            io.BytesIO(excel_file),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Access-Control-Expose-Headers": "Content-Disposition"
            }
        )
    except Exception as e:
        import traceback
        print(f"Excel generation error: {e}")
        print(traceback.format_exc())
        raise



@router.get('/mizan', response_model=MizanReport)
def get_mizan(
    start_date: Annotated[date, Query(description='Başlangıç tarihi')],
    end_date: Annotated[date, Query(description='Bitiş tarihi')],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Mizan (Trial Balance) raporunu döndürür.
    
    - **start_date**: Rapor başlangıç tarihi
    - **end_date**: Rapor bitiş tarihi
    """
    return reports_crud.get_mizan_report(db, start_date, end_date)


@router.get('/income-statement', response_model=IncomeStatement)
def get_income_statement(
    start_date: Annotated[date, Query(description='Başlangıç tarihi')],
    end_date: Annotated[date, Query(description='Bitiş tarihi')],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Gelir-Gider tablosunu döndürür.
    
    - **start_date**: Rapor başlangıç tarihi
    - **end_date**: Rapor bitiş tarihi
    """
    return reports_crud.get_income_statement(db, start_date, end_date)


@router.get('/debtor-creditor', response_model=DebtorCreditorReport)
def get_debtor_creditor(
    start_date: Annotated[date, Query(description='Başlangıç tarihi')],
    end_date: Annotated[date, Query(description='Bitiş tarihi')],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Borçlu-Alacaklı raporunu döndürür.
    
    - **start_date**: Rapor başlangıç tarihi
    - **end_date**: Rapor bitiş tarihi
    """
    return reports_crud.get_debtor_creditor_report(db, start_date, end_date)


@router.get('/cari', response_model=CariReport)
def get_cari_report(
    start_date: Annotated[date, Query(description='Başlangıç tarihi')],
    end_date: Annotated[date, Query(description='Bitiş tarihi')],
    contact_id: Annotated[int | None, Query(description='Belirli bir cari için rapor')] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Cari Raporu - 120'li (Müşteriler) ve 320'li (Satıcılar) hesapları birleşik rapor.
    
    - **start_date**: Rapor başlangıç tarihi
    - **end_date**: Rapor bitiş tarihi
    - **contact_id**: (Opsiyonel) Belirli bir cari için rapor almak için
    
    Dönem başı, dönem içi hareketler ve dönem sonu bakiyeleri gösterir.
    """
    return reports_crud.get_cari_report(db, start_date, end_date, contact_id)


@router.get('/muavin', response_model=MuavinReport)
def get_muavin_report(
    account_code: Annotated[str, Query(description='Hesap kodu')],
    start_date: Annotated[date, Query(description='Başlangıç tarihi')],
    end_date: Annotated[date, Query(description='Bitiş tarihi')],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Muavin Defteri - Belirli bir hesap kodunun tüm işlemleri.
    
    - **account_code**: Hesap kodu (örn: "100", "120.00001")
    - **start_date**: Rapor başlangıç tarihi
    - **end_date**: Rapor bitiş tarihi
    
    Belirtilen hesabın dönem başı bakiyesi, dönem içi hareketler ve dönem sonu bakiyesi gösterilir.
    """
    return reports_crud.get_muavin_report(db, account_code, start_date, end_date)


@router.get('/yevmiye/excel')
def get_yevmiye_excel(
    start_date: Annotated[date | None, Query(description='Başlangıç tarihi')] = None,
    end_date: Annotated[date | None, Query(description='Bitiş tarihi')] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Yevmiye Defteri - Tüm muhasebe kayıtlarının kronolojik sırayla Excel raporu.
    
    - **start_date**: (Opsiyonel) Rapor başlangıç tarihi
    - **end_date**: (Opsiyonel) Rapor bitiş tarihi
    
    Tüm işlemleri tarih ve fiş numarasına göre sıralı şekilde Excel dosyası olarak döndürür.
    """
    try:
        excel_file = reports_crud.get_yevmiye_excel(db, start_date, end_date)
        
        start_str = start_date.strftime('%Y%m%d') if start_date else 'baslangic'
        end_str = end_date.strftime('%Y%m%d') if end_date else 'bitis'
        filename = f"yevmiye_defteri_{start_str}_{end_str}.xlsx"
        
        return StreamingResponse(
            io.BytesIO(excel_file),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Access-Control-Expose-Headers": "Content-Disposition"
            }
        )
    except Exception as e:
        import traceback
        print(f"Excel generation error: {e}")
        print(traceback.format_exc())
        raise


@router.get('/personnel-accounts/excel')
def get_personnel_accounts_excel(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    335 Personel Hesap Raporu Excel - Tüm personel hesapları ve bakiyeleri.
    
    Personellere ait 335.{TCKN} hesaplarının listesi ve bakiyeleri Excel olarak indirilir.
    """
    try:
        excel_file = reports_crud.get_personnel_accounts_excel(db)
        filename = f"personel_hesaplari_335.xlsx"
        
        return StreamingResponse(
            io.BytesIO(excel_file),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Access-Control-Expose-Headers": "Content-Disposition"
            }
        )
    except Exception as e:
        import traceback
        print(f"Excel generation error: {e}")
        print(traceback.format_exc())
        raise
