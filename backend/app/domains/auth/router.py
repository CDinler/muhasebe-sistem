"""
Auth Domain Router (V2)

Kimlik doğrulama endpoint'leri
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.domains.auth.service import auth_service
from app.domains.auth.dependencies import get_current_user
from app.schemas.auth import Token, UserInDB


router = APIRouter(tags=['Auth (V2)'])


@router.post('/login', response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Kullanıcı girişi
    
    - **username**: Kullanıcı adı
    - **password**: Şifre
    """
    user = auth_service.authenticate_user(db, form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Kullanıcı adı veya şifre hatalı",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = auth_service.create_login_token(user.username)
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get('/me', response_model=UserInDB)
async def get_current_user_info(
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Mevcut kullanıcı bilgilerini getir
    
    Token ile kimlik doğrulaması gerekir
    """
    return current_user

