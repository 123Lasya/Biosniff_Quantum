from typing import Optional
from sqlalchemy.orm import Session
from app.models.user import User, UserRole
from app.core.security import get_password_hash


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.user_id == user_id).first()

    def get_by_username(self, username: str) -> Optional[User]:
        return self.db.query(User).filter(User.username == username).first()

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def get_by_username_or_email(self, identifier: str) -> Optional[User]:
        return self.db.query(User).filter(
            (User.username == identifier) | (User.email == identifier)
        ).first()

    def create(
        self,
        username: str,
        email: str,
        password: str,
        role: UserRole = UserRole.FARMER,
        is_active: bool = True
    ) -> User:
        hashed_password = get_password_hash(password)
        db_user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            role=role,
            is_active=is_active
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
