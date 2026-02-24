"""
Auth Domain Dependencies

V2 için auth dependency'leri
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.domains.auth.service import auth_service
from app.schemas.auth import UserInDB


# OAuth2 scheme - V2 için
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v2/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)
) -> UserInDB:
    """
    V2 - Mevcut kullanıcıyı token'dan al
    
    Tüm V2 endpoint'lerde kullanılacak
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Kimlik doğrulanamadı",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    user = auth_service.get_user_by_token(db, token)
    if not user:
        raise credentials_exception
    
    return user


async def get_current_active_user(
    current_user: UserInDB = Depends(get_current_user)
) -> UserInDB:
    """
    Aktif kullanıcı kontrolü (gelecekte kullanılabilir)
    """
    # İleride is_active kontrolü eklenebilir
    return current_user
