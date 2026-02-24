# -*- coding: utf-8 -*-
"""
E-posta Gönderme Servisi
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from typing import List, Optional
from pydantic import EmailStr
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """E-posta gönderme servisi"""
    
    def __init__(
        self,
        smtp_server: str,
        smtp_port: int,
        smtp_username: str,
        smtp_password: str,
        use_tls: bool = True
    ):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.smtp_username = smtp_username
        self.smtp_password = smtp_password
        self.use_tls = use_tls
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None,
        attachments: Optional[List[tuple]] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None
    ) -> bool:
        """
        E-posta gönder
        
        Args:
            to_email: Alıcı e-posta adresi
            subject: E-posta konusu
            body: Düz metin içerik
            html_body: HTML içerik (opsiyonel)
            attachments: Ekler [(filename, content, mimetype), ...]
            cc: CC alıcıları
            bcc: BCC alıcıları
            
        Returns:
            bool: Başarılı ise True
        """
        try:
            # E-posta mesajı oluştur
            msg = MIMEMultipart('alternative')
            msg['From'] = self.smtp_username
            msg['To'] = to_email
            msg['Subject'] = subject
            
            if cc:
                msg['Cc'] = ', '.join(cc)
            if bcc:
                msg['Bcc'] = ', '.join(bcc)
            
            # Metin içerik ekle
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # HTML içerik varsa ekle
            if html_body:
                msg.attach(MIMEText(html_body, 'html', 'utf-8'))
            
            # Ekleri ekle
            if attachments:
                logger.info(f"📎 {len(attachments)} adet dosya ekleniyor...")
                for idx, (filename, content, mimetype) in enumerate(attachments, 1):
                    part = MIMEApplication(content, _subtype=mimetype.split('/')[-1])
                    part.add_header('Content-Disposition', 'attachment', filename=filename)
                    msg.attach(part)
                    logger.info(f"   ✅ {idx}. Dosya eklendi: {filename} ({len(content)} bytes)")
                logger.info(f"📎 Toplam {len(attachments)} dosya e-postaya eklendi")
            
            # SMTP bağlantısı kur ve gönder
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                
                # Tüm alıcılar
                recipients = [to_email]
                if cc:
                    recipients.extend(cc)
                if bcc:
                    recipients.extend(bcc)
                
                server.sendmail(self.smtp_username, recipients, msg.as_string())
            
            logger.info(f"E-posta başarıyla gönderildi: {to_email}")
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            error_msg = f"SMTP Kimlik Doğrulama Hatası: {str(e)}\nKullanıcı: {self.smtp_username}\nSunucu: {self.smtp_server}:{self.smtp_port}\nGmail için uygulama şifresi kullandığınızdan emin olun!"
            logger.error(error_msg)
            raise Exception(error_msg)
        except smtplib.SMTPException as e:
            error_msg = f"SMTP Hatası: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"E-posta gönderme hatası: {str(e)}"
            logger.error(error_msg)
            import traceback
            logger.error(traceback.format_exc())
            raise Exception(error_msg)
    
    def send_report_email(
        self,
        to_email: str,
        contact_name: str,
        report_file: bytes,
        report_filename: str,
        report_type: str = "PDF",
        start_date = None,
        end_date = None,
        subject: str = None,
        custom_message: str = None,
        cc: Optional[List[str]] = None
    ) -> bool:
        """
        Cari raporu e-posta ile gönder
        
        Args:
            to_email: Alıcı e-posta
            contact_name: Cari adı
            report_file: Rapor dosyası (bytes)
            report_filename: Dosya adı
            report_type: Rapor tipi (PDF veya Excel)
            start_date: Başlangıç tarihi (opsiyonel)
            end_date: Bitiş tarihi (opsiyonel)
            subject: Özel konu (opsiyonel)
            custom_message: Özel mesaj (opsiyonel)
            cc: CC alıcıları (opsiyonel)
        """
        # Konu
        if not subject:
            subject = f"Cari Hesap Ekstresi - {contact_name}"
        
        # Mesaj
        if custom_message:
            body = custom_message
            html_body = f"<html><body><pre>{custom_message}</pre></body></html>"
        else:
            body = f"""
Sayın Yetkili,

Ekteki dosyada {contact_name} cari hesabına ait hesap ekstresi bulunmaktadır.

Bu e-posta otomatik olarak gönderilmiştir.

İyi çalışmalar.
"""
            
            html_body = f"""
<html>
<body>
    <p>Sayın Yetkili,</p>
    <p>Ekteki dosyada <strong>{contact_name}</strong> cari hesabına ait hesap ekstresi bulunmaktadır.</p>
    <p>Bu e-posta otomatik olarak gönderilmiştir.</p>
    <p>İyi çalışmalar.</p>
</body>
</html>
"""
        
        mimetype = 'application/pdf' if report_type == 'PDF' else 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        attachments = [(report_filename, report_file, mimetype)]
        
        return self.send_email(
            to_email=to_email,
            subject=subject,
            body=body,
            html_body=html_body,
            attachments=attachments,
            cc=cc
        )


def create_email_service(
    smtp_server: str,
    smtp_port: int,
    smtp_username: str,
    smtp_password: str,
    use_tls: bool = True
) -> EmailService:
    """EmailService factory"""
    return EmailService(
        smtp_server=smtp_server,
        smtp_port=smtp_port,
        smtp_username=smtp_username,
        smtp_password=smtp_password,
        use_tls=use_tls
    )
