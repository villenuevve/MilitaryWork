from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from itsdangerous import URLSafeSerializer
from fastapi import Request
from app.models.database import User  

serializer = URLSafeSerializer("80085")
SECRET_KEY = "80085" 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_user_by_username(db, username: str):
    return db.query(User).filter(User.username == username).first()

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def authenticate_user(db, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

def create_token(user: User):
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": user.username, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user_id_from_cookie(request: Request):
    token = request.cookies.get("auth_token")
    if not token:
        return None
    try:
        data = serializer.loads(token)
        return data.get("user_id")
    except:
        return None


