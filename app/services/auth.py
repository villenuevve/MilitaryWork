from sqlalchemy.orm import Session
from app.models.database import User
from typing import Optional
from fastapi import Request, Depends
from itsdangerous import URLSafeSerializer, BadSignature
from app.models.database import SessionLocal
from sqlalchemy.orm import Session
import bcrypt

serializer = URLSafeSerializer("09931871400")
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(request: Request, db: Session = Depends(get_db)) -> Optional[User]:
    token = request.cookies.get("auth_token")
    if not token:
        return None
    try:
        data = serializer.loads(token)
        username = data.get("username")
        return get_user_by_username(db, username)
    except BadSignature:
        return None


