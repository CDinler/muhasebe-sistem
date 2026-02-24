"""
Users Domain Service

Kullanıcı yönetimi business logic
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models import User
from app.core.security import get_password_hash
from app.schemas.auth import UserCreate, UserUpdate


class UsersService:
    """Users service"""
    
    def get_users(self, db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """Tüm kullanıcıları listele"""
        return db.query(User).offset(skip).limit(limit).all()
    
    def get_user_by_id(self, db: Session, user_id: int) -> Optional[User]:
        """ID'ye göre kullanıcı getir"""
        return db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_username(self, db: Session, username: str) -> Optional[User]:
        """Kullanıcı adına göre kullanıcı getir"""
        return db.query(User).filter(User.username == username).first()
    
    def get_user_by_email(self, db: Session, email: str) -> Optional[User]:
        """Email'e göre kullanıcı getir"""
        return db.query(User).filter(User.email == email).first()
    
    def create_user(self, db: Session, user_data: UserCreate) -> User:
        """Yeni kullanıcı oluştur"""
        # Kullanıcı adı kontrolü
        existing_user = self.get_user_by_username(db, user_data.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Bu kullanıcı adı zaten kullanılıyor"
            )
        
        # Email kontrolü
        if user_data.email:
            existing_email = self.get_user_by_email(db, user_data.email)
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Bu e-posta adresi zaten kullanılıyor"
                )
        
        # Yeni kullanıcı oluştur
        hashed_password = get_password_hash(user_data.password)
        
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=hashed_password,
            role=user_data.role
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return new_user
    
    def update_user(
        self, 
        db: Session, 
        user_id: int, 
        user_data: UserUpdate
    ) -> User:
        """Kullanıcı bilgilerini güncelle"""
        user = self.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Kullanıcı bulunamadı"
            )
        
        update_data = user_data.model_dump(exclude_unset=True)
        
        # Kullanıcı adı değişiyorsa kontrol et
        if 'username' in update_data and update_data['username'] != user.username:
            existing = self.get_user_by_username(db, update_data['username'])
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Bu kullanıcı adı zaten kullanılıyor"
                )
        
        # Email değişiyorsa kontrol et
        if 'email' in update_data and update_data['email'] != user.email:
            existing = self.get_user_by_email(db, update_data['email'])
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Bu e-posta adresi zaten kullanılıyor"
                )
        
        # Şifre değişiyorsa hash'le
        if 'password' in update_data:
            update_data['hashed_password'] = get_password_hash(update_data.pop('password'))
        
        # Güncelle
        for field, value in update_data.items():
            setattr(user, field, value)
        
        db.commit()
        db.refresh(user)
        
        return user
    
    def delete_user(self, db: Session, user_id: int) -> None:
        """Kullanıcıyı sil"""
        user = self.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Kullanıcı bulunamadı"
            )
        
        db.delete(user)
        db.commit()


# Service instance
users_service = UsersService()
