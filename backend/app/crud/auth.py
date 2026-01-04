from sqlalchemy.orm import Session
from app.models.user import User
from app.core.security import verify_password
from typing import Optional


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """Kullanıcı kimlik doğrulaması yap"""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    if not user.is_active:
        return None
    return user


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Kullanıcıyı kullanıcı adına göre getir"""
    return db.query(User).filter(User.username == username).first()
