from fastapi import APIRouter, Depends, HTTPException, Form, Response, status
from fastapi.responses import RedirectResponse
from itsdangerous import URLSafeSerializer
from sqlalchemy.orm import Session
from app.models.database import SessionLocal
from app.services.auth import authenticate_user

router = APIRouter()
serializer = URLSafeSerializer("09931871400")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/login")
def login(response: Response, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = authenticate_user(db, username, password)
    if not user:
        raise HTTPException(status_code=400, detail="Невірний логін або пароль")
    
    token = serializer.dumps({"username": user.username})
    redirect = RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    redirect.set_cookie(key="auth_token", value=token)
    return redirect
