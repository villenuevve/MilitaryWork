from fastapi import APIRouter, Request, Form, Depends, status, Response
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from itsdangerous import URLSafeSerializer, BadSignature
from sqlalchemy.orm import Session
from app.models.database import User, SessionLocal
from app.services.hash_utils import hash_password, verify_password

router = APIRouter()
templates = Jinja2Templates(directory="templates")
serializer = URLSafeSerializer("09931871400") 

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("auth_token")
    if not token:
        return None
    try:
        data = serializer.loads(token)
        username = data.get("username")
        user = db.query(User).filter(User.username == username).first()
        return user
    except BadSignature:
        return None


@router.get("/register", response_class=HTMLResponse)
def show_register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request, "error": None})

@router.post("/register")
def register(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": "Користувач із таким ім’ям вже існує."
        }, status_code=400)

    user = User(username=username, hashed_password=hash_password(password))
    db.add(user)
    db.commit()

    return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

@router.get("/login", response_class=HTMLResponse)
def show_login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})

@router.post("/login")
def login(
    request: Request,
    response: Response,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Невірне ім’я або пароль"
        }, status_code=400)

    token = serializer.dumps({"username": user.username})
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="auth_token", value=token)
    return response

@router.get("/logout")
def logout():
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie("auth_token")
    return response

@router.get("/", response_class=HTMLResponse, name="home")
def home(request: Request, current_user: User = Depends(get_current_user)):
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "username": current_user.username
    })