from fastapi import APIRouter, Request, Form, Depends, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi import Form
from sqlalchemy.orm import Session
from app.models.database import User
from app.services.hash_utils import hash_password
from app.models.database import SessionLocal
from app.services.auth import authenticate_user, get_user_by_username

router = APIRouter()
templates = Jinja2Templates(directory="templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/")
async def home(request: Request):
    token = request.cookies.get("auth_token")
    if not token:
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/login")
async def login_get(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = authenticate_user(db, username, password)
    if not user:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Невірне ім’я користувача або пароль."}, status_code=400)
    return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

@router.get("/register")
def show_register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request, "error": None})

@router.post("/register")
def register(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    existing_user = get_user_by_username(db, username)
    if existing_user:
        return templates.TemplateResponse("register.html", {"request": request, "error": "Користувач із таким ім’ям вже існує."}, status_code=400)
    user = User(username=username, hashed_password=hash_password(password))
    db.add(user)
    db.commit()
    return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

@router.get("/logout")
def logout():
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie("auth_token")
    return response

