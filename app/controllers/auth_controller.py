from fastapi import APIRouter, Request, Form, Depends, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi import Form
from sqlalchemy.orm import Session
from app.models.database import User
from app.services.hash_utils import hash_password
from app.services.auth import get_password_hash 
from app.models.database import SessionLocal
from app.services.auth import authenticate_user, get_user_by_username
from itsdangerous import URLSafeSerializer

serializer = URLSafeSerializer("80085") 
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

    token = serializer.dumps({
    "username": user.username,
    "user_id": user.id  
    })

    print("✅ Token set for user:", user.username, "| ID:", user.id)

    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    response.set_cookie(
    key="auth_token",
    value=token,
    httponly=True,
    samesite="lax", 
    secure=False     
)
    return response

@router.get("/register")
def show_register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request, "error": None})

@router.post("/register")
async def register(request: Request,
                    username: str = Form(...),
                    password: str = Form(...),
                    confirm_password: str = Form(...),
                    role: str = Form(...)):
    db = SessionLocal()

    if password != confirm_password:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": "❌ Паролі не співпадають."
        })

    if len(password) < 2:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": "❗ Пароль має містити щонайменше 2 символи."
        })

    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": "❌ Користувач з таким ім’ям вже існує."
        })

    hashed = get_password_hash(password)
    new_user = User(username=username, hashed_password=hashed, role=role)    
    db.add(new_user)
    db.commit()

    return RedirectResponse(url="/login?success=1", status_code=302)

@router.get("/logout")
def logout():
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie("auth_token")
    return response

