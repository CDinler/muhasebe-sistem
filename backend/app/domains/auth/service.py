"""
Auth Domain Service

Kimlik doğrulama ve yetkilendirme business logic
"""
from datetime import timedelta
from typing import Optional
from sqlalchemy.orm import Session

from app.models import User
from app.core.security import verify_password, create_access_token, verify_token, ACCESS_TOKEN_EXPIRE_MINUTES
from app.schemas.auth import UserInDB


class AuthService:
    """Authentication service"""
    
    def authenticate_user(self, db: Session, username: str, password: str) -> Optional[User]:
        """
        Kullanıcı adı ve şifre ile kimlik doğrulama
        """
        user = db.query(User).filter(User.username == username).first()
        
        if not user:
            return None
        
        if not verify_password(password, user.hashed_password):
            return None
        
        return user
    
    def get_user_by_username(self, db: Session, username: str) -> Optional[User]:
        """
        Kullanıcı adına göre kullanıcı getir
        """
        return db.query(User).filter(User.username == username).first()
    
    def get_user_by_token(self, db: Session, token: str) -> Optional[UserInDB]:
        """
        Token'dan kullanıcı bilgilerini çıkar
        """
        username = verify_token(token)
        if not username:
            return None
        
        user = self.get_user_by_username(db, username)
        if not user:
            return None
        
        return UserInDB.model_validate(user)
    
    def create_login_token(self, username: str) -> str:
        """
        Kullanıcı için access token oluştur
        """
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": username}, 
            expires_delta=access_token_expires
        )
        return access_token


# Service instance
auth_service = AuthService()
