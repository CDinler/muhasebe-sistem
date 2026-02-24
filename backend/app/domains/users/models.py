"""
User model - Sistem kullanıcıları
Luca-compatible: users table
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class User(Base):
    """Sistem Kullanıcısı"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=True)  # Nullable - email opsiyonel
    hashed_password = Column(String(200), nullable=False)
    
    full_name = Column(String(100))
    role = Column(String(50), default="muhasebeci")  # patron, muhasebeci, santiye
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # İlişkiler
    email_settings = relationship("UserEmailSettings", back_populates="user", uselist=False, lazy="select")
    
    def __repr__(self):
        return f"<User {self.username} - {self.role}>"
# -*- coding: utf-8 -*-
"""
User Email Settings Model
"""
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class UserEmailSettings(Base):
    """Kullanıcı E-posta Ayarları"""
    __tablename__ = "user_email_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    
    # SMTP Ayarları
    smtp_server = Column(String(100), default="smtp.gmail.com")
    smtp_port = Column(Integer, default=587)
    smtp_username = Column(String(100))  # Gönderen e-posta
    smtp_password = Column(String(200))  # Uygulama şifresi (encrypted olmalı)
    use_tls = Column(Boolean, default=True)
    
    # CC Ayarları (virgülle ayrılmış e-posta listesi)
    default_cc_recipients = Column(String(500), nullable=True)  # örn: "muhasebe@firma.com,yonetim@firma.com"
    
    # İlişkiler
    user = relationship("User", back_populates="email_settings")
    
    def __repr__(self):
        return f"<UserEmailSettings user_id={self.user_id} smtp={self.smtp_server}>"
