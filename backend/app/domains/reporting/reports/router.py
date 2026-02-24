"""
Reports Router
FastAPI endpoints for financial reports
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional
from pydantic import BaseModel, EmailStr
import io

from app.core.database import get_db
from app.domains.auth.dependencies import get_current_user
from app.schemas.auth import UserInDB
from app.domains.reporting.reports.schemas import (
    MizanReport,
    IncomeStatement,
    DebtorCreditorReport,
    CariReport,
    MuavinReport
)
from app.domains.reporting.reports.service import ReportsService
from app.services.email_service import EmailService
from app.models import UserEmailSettings
from app.models import Contact

router = APIRouter(tags=["Reports (V2)"])


class CariEmailRequest(BaseModel):
    """Cari rapor email gönderme request"""
    contact_id: int
    email: EmailStr
    cc: str | None = None
    subject: str
    message: str | None = None
    start_date: date
    end_date: date
    account_filter: str | None = None


@router.get('/mizan', response_model=MizanReport)
def get_mizan_report(
    start_date: date = Query(..., description='Başlangıç tarihi'),
    end_date: date = Query(..., description='Bitiş tarihi'),
    cost_center_id: Optional[int] = Query(None, description='Maliyet Merkezi ID'),
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mizan (Trial Balance) raporu"""
    # V1 CRUD doesn't support cost_center_id yet, ignore it for now
    return ReportsService(db).get_mizan_report( start_date, end_date)


@router.get('/income-statement', response_model=IncomeStatement)
def get_income_statement(
    start_date: date = Query(..., description='Başlangıç tarihi'),
    end_date: date = Query(..., description='Bitiş tarihi'),
    cost_center_id: Optional[int] = Query(None, description='Maliyet Merkezi ID'),
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Gelir Tablosu (Income Statement)"""
    return ReportsService(db).get_income_statement( start_date, end_date)


@router.get('/debtor-creditor', response_model=DebtorCreditorReport)
def get_debtor_creditor_report(
    start_date: date = Query(..., description='Başlangıç tarihi'),
    end_date: date = Query(..., description='Bitiş tarihi'),
    cost_center_id: Optional[int] = Query(None, description='Maliyet Merkezi ID'),
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Borç/Alacak raporu"""
    return ReportsService(db).get_debtor_creditor_report( start_date, end_date)


@router.get('/cari', response_model=CariReport)
def get_cari_report(
    start_date: date = Query(..., description='Başlangıç tarihi'),
    end_date: date = Query(..., description='Bitiş tarihi'),
    contact_id: Optional[int] = Query(None, description='Cari ID'),
    cost_center_id: Optional[int] = Query(None, description='Maliyet Merkezi ID'),
    account_filter: list[str] = Query(default=[], description='Hesap filtresi: 120, 320, collateral'),
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cari hesap raporu"""
    # Boş liste ise None olarak geç
    filter_param = account_filter if account_filter else None
    return ReportsService(db).get_cari_report( start_date, end_date, contact_id, filter_param)


@router.get('/cari/excel')
def get_cari_report_excel(
    start_date: date = Query(..., description='Başlangıç tarihi'),
    end_date: date = Query(..., description='Bitiş tarihi'),
    contact_id: Optional[int] = Query(None, description='Cari ID'),
    account_filter: list[str] = Query(default=[], description='Hesap filtresi: 120, 320, collateral'),
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cari raporu Excel çıktısı"""
    from app.utils.report_generators import generate_cari_excel
    
    # Boş liste ise None olarak geç
    filter_param = account_filter if account_filter else None
    # Backend zaten filtrelenmiş veriyi döndürüyor
    report = ReportsService(db).get_cari_report( start_date, end_date, contact_id, filter_param)
    
    # Excel oluştur
    excel_bytes = generate_cari_excel(report)
    
    filename = f"cari_ekstre_{report['contact_code'] or 'tumu'}_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.xlsx"
    
    return StreamingResponse(
        io.BytesIO(excel_bytes),
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': f'attachment; filename={filename}'}
    )


@router.get('/cari/pdf')
def get_cari_report_pdf(
    start_date: date = Query(..., description='Başlangıç tarihi'),
    end_date: date = Query(..., description='Bitiş tarihi'),
    contact_id: Optional[int] = Query(None, description='Cari ID'),
    account_filter: list[str] = Query(default=[], description='Hesap filtresi: 120, 320, collateral'),
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cari raporu PDF çıktısı"""
    from app.utils.report_generators import generate_cari_pdf
    
    # Boş liste ise None olarak geç
    filter_param = account_filter if account_filter else None
    # Backend zaten filtrelenmiş veriyi döndürüyor
    report = ReportsService(db).get_cari_report( start_date, end_date, contact_id, filter_param)
    
    # PDF oluştur
    pdf_bytes = generate_cari_pdf(report)
    
    filename = f"cari_ekstre_{report['contact_code'] or 'tumu'}_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.pdf"
    
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type='application/pdf',
        headers={'Content-Disposition': f'attachment; filename={filename}'}
    )


@router.get('/muavin', response_model=MuavinReport)
def get_muavin_report(
    account_code: str = Query(..., description='Hesap Kodu'),
    start_date: date = Query(..., description='Başlangıç tarihi'),
    end_date: date = Query(..., description='Bitiş tarihi'),
    cost_center_id: Optional[int] = Query(None, description='Maliyet Merkezi ID'),
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Muavin defteri (General Ledger)"""
    return ReportsService(db).get_muavin_report(start_date, end_date, account_code)


@router.post('/cari/email')
def send_cari_report_email(
    request: CariEmailRequest,
    db: Session = Depends(get_db),
    current_user: UserInDB = Depends(get_current_user)
):
    """Cari raporu PDF olarak email ile gönder."""
    try:
        # Kullanıcının email ayarlarını al
        email_settings = db.query(UserEmailSettings).filter(
            UserEmailSettings.user_id == current_user.id
        ).first()
        
        if not email_settings:
            raise HTTPException(
                status_code=400,
                detail="Email ayarları bulunamadı. Lütfen önce email ayarlarınızı yapılandırın."
            )
        
        # Raporu al ve PDF oluştur
        from app.utils.report_generators import generate_cari_pdf
        
        account_filter = [request.account_filter] if request.account_filter else None
        report = ReportsService(db).get_cari_report(
            request.start_date,
            request.end_date,
            request.contact_id,
            account_filter
        )
        
        pdf_content = generate_cari_pdf(report)
        
        # Contact bilgilerini al
        contact = db.query(Contact).filter(Contact.id == request.contact_id).first()
        if not contact:
            raise HTTPException(status_code=404, detail="Contact bulunamadı")
        
        # Email gönder
        email_service = EmailService(
            smtp_server=email_settings.smtp_server,
            smtp_port=email_settings.smtp_port,
            smtp_username=email_settings.smtp_username,
            smtp_password=email_settings.smtp_password,
            use_tls=email_settings.use_tls
        )
        
        filename = f"cari_ekstre_{contact.code}_{request.start_date.strftime('%Y%m%d')}_{request.end_date.strftime('%Y%m%d')}.pdf"
        
        # Kullanıcı konu ve mesaj sağlamışsa onları kullan
        subject = request.subject
        body = request.message if request.message else f"""Sayın {contact.name},

{request.start_date.strftime('%d.%m.%Y')} - {request.end_date.strftime('%d.%m.%Y')} tarihleri arasındaki cari hesap ekstreniz ekte yer almaktadır.

Saygılarımızla,
{current_user.username}"""
        
        # CC varsa parse et
        cc_list = None
        if request.cc:
            cc_list = [email.strip() for email in request.cc.split(',') if email.strip()]
        
        success = email_service.send_email(
            to_email=request.email,
            subject=subject,
            body=body,
            cc=cc_list,
            attachments=[(filename, pdf_content, 'application/pdf')]
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Email gönderilemedi")
        
        return {"message": "Email başarıyla gönderildi", "to": request.email, "cc": cc_list}
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Email gönderme hatası: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/cari/email-excel')
def send_cari_report_email_excel(
    request: CariEmailRequest,
    db: Session = Depends(get_db),
    current_user: UserInDB = Depends(get_current_user)
):
    """Cari raporu Excel olarak email ile gönder."""
    try:
        # Kullanıcının email ayarlarını al
        email_settings = db.query(UserEmailSettings).filter(
            UserEmailSettings.user_id == current_user.id
        ).first()
        
        if not email_settings:
            raise HTTPException(
                status_code=400,
                detail="Email ayarları bulunamadı. Lütfen önce email ayarlarınızı yapılandırın."
            )
        
        # Raporu al ve Excel oluştur
        from app.utils.report_generators import generate_cari_excel
        
        account_filter = [request.account_filter] if request.account_filter else None
        report = ReportsService(db).get_cari_report(
            request.start_date,
            request.end_date,
            request.contact_id,
            account_filter
        )
        
        excel_content = generate_cari_excel(report)
        
        # Contact bilgilerini al
        contact = db.query(Contact).filter(Contact.id == request.contact_id).first()
        if not contact:
            raise HTTPException(status_code=404, detail="Contact bulunamadı")
        
        # Email gönder
        email_service = EmailService(
            smtp_server=email_settings.smtp_server,
            smtp_port=email_settings.smtp_port,
            smtp_username=email_settings.smtp_username,
            smtp_password=email_settings.smtp_password,
            use_tls=email_settings.use_tls
        )
        
        filename = f"cari_ekstre_{contact.code}_{request.start_date.strftime('%Y%m%d')}_{request.end_date.strftime('%Y%m%d')}.xlsx"
        
        # Kullanıcı konu ve mesaj sağlamışsa onları kullan
        subject = request.subject
        body = request.message if request.message else f"""Sayın {contact.name},

{request.start_date.strftime('%d.%m.%Y')} - {request.end_date.strftime('%d.%m.%Y')} tarihleri arasındaki cari hesap ekstreniz ekte yer almaktadır.

Saygılarımızla,
{current_user.username}"""
        
        # CC varsa parse et
        cc_list = None
        if request.cc:
            cc_list = [email.strip() for email in request.cc.split(',') if email.strip()]
        
        success = email_service.send_email(
            to_email=request.email,
            subject=subject,
            body=body,
            cc=cc_list,
            attachments=[(filename, excel_content, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')]
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Email gönderilemedi")
        
        return {"message": "Email başarıyla gönderildi", "to": request.email, "cc": cc_list}
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Email gönderme hatası: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
