"""
Users Domain Router (V2)

Kullanıcı yönetimi endpoint'leri
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.domains.auth.dependencies import get_current_user
from app.domains.users.service import users_service
from app.schemas.auth import UserInDB, UserCreate, UserUpdate


router = APIRouter(tags=['Users (V2)'])


def require_admin(current_user: UserInDB = Depends(get_current_user)) -> UserInDB:
    """Admin yetkisi kontrolü"""
    if current_user.role not in ["admin", "muhasebeci"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu işlem için admin yetkisi gerekli"
        )
    return current_user


@router.get('/', response_model=List[UserInDB])
def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserInDB = Depends(require_admin)
):
    """Tüm kullanıcıları listele (Admin)"""
    users = users_service.get_users(db, skip, limit)
    return users


@router.get('/{user_id}', response_model=UserInDB)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserInDB = Depends(require_admin)
):
    """Kullanıcı detayını getir (Admin)"""
    user = users_service.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kullanıcı bulunamadı"
        )
    return user


@router.post('/', response_model=UserInDB, status_code=status.HTTP_201_CREATED)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: UserInDB = Depends(require_admin)
):
    """Yeni kullanıcı oluştur (Admin)"""
    return users_service.create_user(db, user_data)


@router.put('/{user_id}', response_model=UserInDB)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: UserInDB = Depends(require_admin)
):
    """Kullanıcı bilgilerini güncelle (Admin)"""
    return users_service.update_user(db, user_id, user_data)


@router.delete('/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserInDB = Depends(require_admin)
):
    """Kullanıcıyı sil (Admin)"""
    users_service.delete_user(db, user_id)

