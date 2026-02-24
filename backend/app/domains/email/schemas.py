"""Email domain schemas"""
from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import date


class EmailSettingsBase(BaseModel):
    """Email ayarları base schema"""
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str
    smtp_password: str
    use_tls: bool = True
    default_cc_recipients: Optional[str] = None  # Virgülle ayrılmış e-posta listesi


class EmailSettingsCreate(EmailSettingsBase):
    """Email ayarları oluşturma"""
    pass


class EmailSettingsUpdate(BaseModel):
    """Email ayarları güncelleme"""
    smtp_server: Optional[str] = None
    smtp_port: Optional[int] = None
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    use_tls: Optional[bool] = None
    default_cc_recipients: Optional[str] = None


class EmailSettingsResponse(BaseModel):
    """Email ayarları response"""
    id: int
    user_id: int
    smtp_server: str
    smtp_port: int
    smtp_username: str
    use_tls: bool
    default_cc_recipients: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class SendReportRequest(BaseModel):
    """Rapor gönderme request"""
    recipient_email: EmailStr
    cc_recipients: Optional[str] = None  # Virgülle ayrılmış e-posta listesi
    contact_id: int
    start_date: date
    end_date: date
    report_type: str = "PDF"  # PDF veya Excel
    account_filter: Optional[list[str]] = None  # ["120", "320", "collateral"] veya None
    subject: Optional[str] = None
    message: Optional[str] = None


class TestEmailRequest(BaseModel):
    """Test email request"""
    recipient_email: EmailStr


class EmailResponse(BaseModel):
    """Generic email response"""
    success: bool
    message: str
    filename: Optional[str] = None
