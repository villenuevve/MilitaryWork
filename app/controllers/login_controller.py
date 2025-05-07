from fastapi import APIRouter, Request, Form, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.services.auth import authenticate_user, create_token

templates = Jinja2Templates(directory="templates")
router = APIRouter()


@router.get("/login")
async def login_get(request: Request):
    # Не передаємо error тут!
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
async def login_post(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, username, password)
    if not user:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Неправильний логін або пароль"},
            status_code=401
        )

    response = RedirectResponse(url="/", status_code=302)
    response.set_cookie("auth_token", create_token(user))
    return response


@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie("auth_token")
    return response
