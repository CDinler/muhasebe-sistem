"""
Email Domain Router (V2)

Kullanıcı e-posta ayarları ve rapor gönderme işlemleri
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.auth import UserInDB
from app.domains.auth.dependencies import get_current_user
from app.domains.email.schemas import (
    EmailSettingsCreate,
    EmailSettingsUpdate,
    EmailSettingsResponse,
    SendReportRequest,
    TestEmailRequest,
    EmailResponse
)
from app.domains.email.service import email_service


router = APIRouter(tags=['Email (V2)'])


@router.get('/settings', response_model=EmailSettingsResponse)
def get_email_settings(
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Kullanıcının e-posta ayarlarını getir"""
    settings = email_service.get_user_settings(db, current_user.id)
    
    if not settings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="E-posta ayarları bulunamadı"
        )
    
    return settings


@router.post('/settings', response_model=EmailSettingsResponse, status_code=status.HTTP_201_CREATED)
def create_email_settings(
    settings_data: EmailSettingsCreate,
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """E-posta ayarları oluştur veya güncelle"""
    existing = email_service.get_user_settings(db, current_user.id)
    
    if existing:
        # Güncelle
        update_data = EmailSettingsUpdate(**settings_data.model_dump())
        return email_service.update_settings(db, existing, update_data)
    else:
        # Yeni oluştur
        return email_service.create_settings(db, current_user.id, settings_data)


@router.put('/settings', response_model=EmailSettingsResponse)
def update_email_settings(
    settings_data: EmailSettingsUpdate,
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """E-posta ayarlarını güncelle"""
    settings = email_service.get_user_settings(db, current_user.id)
    
    if not settings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="E-posta ayarları bulunamadı"
        )
    
    return email_service.update_settings(db, settings, settings_data)


@router.delete('/settings', status_code=status.HTTP_204_NO_CONTENT)
def delete_email_settings(
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """E-posta ayarlarını sil"""
    settings = email_service.get_user_settings(db, current_user.id)
    
    if not settings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="E-posta ayarları bulunamadı"
        )
    
    email_service.delete_settings(db, settings)


@router.post('/test', response_model=EmailResponse)
def test_email_connection(
    test_data: TestEmailRequest,
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """E-posta ayarlarını test et"""
    try:
        result = email_service.send_test_email(
            db=db,
            user_id=current_user.id,
            user_name=current_user.full_name or current_user.username,
            recipient_email=test_data.recipient_email
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"E-posta gönderilirken hata: {str(e)}"
        )


@router.post('/send-report', response_model=EmailResponse)
def send_cari_report(
    request: SendReportRequest,
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cari raporu e-posta ile gönder"""
    import traceback
    try:
        print(f"📧 E-posta gönderme isteği alındı - User: {current_user.username}")
        print(f"📧 Contact ID: {request.contact_id}, Type: {request.report_type}")
        
        result = email_service.send_cari_report(
            db=db,
            user_id=current_user.id,
            user_name=current_user.full_name or current_user.username,
            recipient_email=request.recipient_email,
            contact_id=request.contact_id,
            start_date=request.start_date,
            end_date=request.end_date,
            report_type=request.report_type,
            account_filter=request.account_filter,
            cc_recipients=request.cc_recipients,
            subject=request.subject,
            message=request.message
        )
        print(f"✅ E-posta başarıyla gönderildi")
        return result
    except Exception as e:
        print(f"❌ E-POSTA GÖNDERME HATASI:")
        print(f"   Hata mesajı: {str(e)}")
        print(f"   Hata tipi: {type(e).__name__}")
        print(f"   Traceback:")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Rapor gönderilirken hata: {str(e)}"
        )

