"""Email domain service"""
from typing import Optional
from sqlalchemy.orm import Session
from datetime import date

from app.models import UserEmailSettings
from app.domains.email.schemas import EmailSettingsCreate, EmailSettingsUpdate
from app.services.email_service import create_email_service
from app.core.config import settings as config_settings


class EmailSettingsService:
    """Email ayarları business logic"""
    
    def get_user_settings(self, db: Session, user_id: int) -> Optional[UserEmailSettings]:
        """Kullanıcının email ayarlarını getir"""
        return db.query(UserEmailSettings).filter(
            UserEmailSettings.user_id == user_id
        ).first()
    
    def create_settings(
        self, 
        db: Session, 
        user_id: int, 
        settings_data: EmailSettingsCreate
    ) -> UserEmailSettings:
        """Email ayarları oluştur"""
        new_settings = UserEmailSettings(
            user_id=user_id,
            smtp_server=settings_data.smtp_server,
            smtp_port=settings_data.smtp_port,
            smtp_username=settings_data.smtp_username,
            smtp_password=settings_data.smtp_password,  # TODO: Encrypt
            use_tls=settings_data.use_tls
        )
        
        db.add(new_settings)
        db.commit()
        db.refresh(new_settings)
        return new_settings
    
    def update_settings(
        self,
        db: Session,
        settings: UserEmailSettings,
        settings_data: EmailSettingsUpdate
    ) -> UserEmailSettings:
        """Email ayarlarını güncelle"""
        update_data = settings_data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(settings, field, value)
        
        db.commit()
        db.refresh(settings)
        return settings
    
    def delete_settings(self, db: Session, settings: UserEmailSettings) -> None:
        """Email ayarlarını sil"""
        db.delete(settings)
        db.commit()
    
    def get_smtp_config(self, db: Session, user_id: int) -> dict:
        """
        SMTP konfigürasyonunu getir
        Kullanıcı ayarları yoksa sistem varsayılanlarını kullan
        """
        user_settings = self.get_user_settings(db, user_id)
        
        if user_settings:
            return {
                'smtp_server': user_settings.smtp_server,
                'smtp_port': user_settings.smtp_port,
                'smtp_username': user_settings.smtp_username,
                'smtp_password': user_settings.smtp_password,
                'use_tls': user_settings.use_tls
            }
        else:
            # Sistem varsayılan ayarları
            return {
                'smtp_server': config_settings.SMTP_HOST,
                'smtp_port': config_settings.SMTP_PORT,
                'smtp_username': config_settings.SMTP_USER,
                'smtp_password': config_settings.SMTP_PASSWORD,
                'use_tls': config_settings.SMTP_USE_TLS
            }
    
    def send_test_email(
        self,
        db: Session,
        user_id: int,
        user_name: str,
        recipient_email: str
    ) -> dict:
        """Test email gönder"""
        smtp_config = self.get_smtp_config(db, user_id)
        user_settings = self.get_user_settings(db, user_id)
        
        email_service = create_email_service(**smtp_config)
        
        email_service.send_email(
            to_email=recipient_email,
            subject="Muhasebe Sistemi - Test E-postası",
            body=f"Test e-postası - {user_name}",
            html_body=f"""
            <h2>E-posta Ayarları Test Edildi</h2>
            <p>Merhaba,</p>
            <p>Bu bir test e-postasıdır. E-posta ayarlarınız başarıyla yapılandırılmıştır.</p>
            <p><strong>Gönderen:</strong> {user_name}</p>
            <p><strong>SMTP Sunucu:</strong> {smtp_config['smtp_server']}:{smtp_config['smtp_port']}</p>
            <hr>
            <p style="color: #888; font-size: 12px;">Muhasebe Otomasyon Sistemi</p>
            """
        )
        
        return {
            "success": True,
            "message": f"Test e-postası {recipient_email} adresine başarıyla gönderildi"
        }
    
    def send_cari_report(
        self,
        db: Session,
        user_id: int,
        user_name: str,
        recipient_email: str,
        contact_id: int,
        start_date: date,
        end_date: date,
        report_type: str = "PDF",
        account_filter: Optional[list[str]] = None,
        cc_recipients: Optional[str] = None,
        subject: Optional[str] = None,
        message: Optional[str] = None
    ) -> dict:
        """Cari raporu email ile gönder"""
        from app.domains.reporting.reports.service import ReportsService
        from app.utils.report_generators import generate_cari_pdf, generate_cari_excel
        
        smtp_config = self.get_smtp_config(db, user_id)
        email_service = create_email_service(**smtp_config)
        
        # Kullanıcının default CC'lerini al
        user_settings = self.get_user_settings(db, user_id)
        default_cc = user_settings.default_cc_recipients if user_settings else None
        
        print(f"📊 E-POSTA RAPOR İSTEĞİ:")
        print(f"   Contact ID: {contact_id}")
        print(f"   Account Filter: {account_filter}")
        print(f"   Report Type: {report_type}")
        
        # CC listesi oluştur
        cc_list = []
        if cc_recipients:
            cc_list.extend([email.strip() for email in cc_recipients.split(',') if email.strip()])
        elif default_cc:
            cc_list.extend([email.strip() for email in default_cc.split(',') if email.strip()])
        
        # Seçili her filtre için ayrı rapor oluştur
        if not account_filter or len(account_filter) == 0:
            # Hiçbir filtre seçilmemiş - tümünü göster
            filter_list = [[None]]
        else:
            # Her seçili filtre için ayrı rapor
            filter_list = [[f] for f in account_filter]
        
        print(f"📊 OLUŞTURULACAK RAPOR SAYISI: {len(filter_list)}")
        print(f"   Seçili Filtreler: {account_filter}")
        
        # Her filter için rapor oluştur
        attachments = []
        contact_name = None
        
        for idx, single_filter in enumerate(filter_list):
            print(f"📄 Rapor {idx+1}/{len(filter_list)} oluşturuluyor - Filter: {single_filter}")
            
            # Rapor datasını al
            reports_service = ReportsService(db)
            report_data = reports_service.get_cari_report(
                contact_id=contact_id,
                start_date=start_date,
                end_date=end_date
            )
            
            if contact_name is None:
                contact_name = report_data.contact_name
            
            print(f"   Contact: {report_data.contact_name}")
            print(f"   İşlem Sayısı: {len(report_data.items)}")
            print(f"   Açılış Bakiyesi: {report_data.opening_balance}")
            print(f"   Kapanış Bakiyesi: {report_data.closing_balance}")
            
            # Dosya adı - filter'a göre
            safe_name = "".join(c for c in contact_name if c.isalnum() or c in (' ', '-', '_'))
            date_str = end_date.strftime('%Y%m%d')
            
            # Filter adını belirle
            if single_filter and len(single_filter) > 0 and single_filter[0]:
                filter_name = single_filter[0].upper()
            else:
                filter_name = "TUM_HESAPLAR"
            
            # PDF veya Excel oluştur
            if report_type.upper() == "PDF":
                file_bytes = generate_cari_pdf(report_data)
                filename = f"CariEkstre_{filter_name}_{safe_name}_{date_str}.pdf"
                mimetype = 'application/pdf'
            else:
                file_bytes = generate_cari_excel(report_data)
                filename = f"CariEkstre_{filter_name}_{safe_name}_{date_str}.xlsx"
                mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            
            attachments.append((filename, file_bytes, mimetype))
            print(f"   ✅ Dosya oluşturuldu: {filename}")
        
        # Konu ve mesaj
        subject = subject or f"Cari Hesap Ekstresi - {contact_name}"
        message = message or f"""
        Merhaba,
        
        {start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')} 
        tarihleri arası {contact_name} cari hesap ekstreleri ektedir.
        
        Toplam {len(attachments)} dosya gönderilmiştir.
        
        Saygılarımızla,
        {user_name}
        """
        
        # E-posta gönder (tüm attachments ile)
        email_service.send_email(
            to_email=recipient_email,
            subject=subject,
            body=message,
            html_body=f"<html><body><pre>{message}</pre></body></html>",
            attachments=attachments,
            cc=cc_list if cc_list else None
        )
        
        print(f"✅ E-posta gönderildi - {len(attachments)} dosya eklendi")
        
        return {
            "success": True,
            "message": f"{len(attachments)} rapor {recipient_email} adresine başarıyla gönderildi",
            "files": [att[0] for att in attachments]
        }


# Service instance
email_service = EmailSettingsService()
