from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.controllers import auth_controller, login_controller
from app.controllers import web_deployment
from app.controllers import history_controller
from itsdangerous import URLSafeSerializer
from pathlib import Path
from fastapi import Request

app = FastAPI()
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = "80085"
SALT = "auth"
templates = Jinja2Templates(directory=BASE_DIR / "templates")
serializer = URLSafeSerializer(SECRET_KEY, salt=SALT)

app.include_router(auth_controller.router)
app.include_router(login_controller.router)
app.include_router(history_controller.router)
app.include_router(web_deployment.router)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

serializer = URLSafeSerializer("80085") 

def get_current_user_from_cookie(request: Request):
    token = request.cookies.get("auth_token")
    if not token:
        return None
    try:
        data = serializer.loads(token)
        return data.get("username")
    except Exception:
        return None

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    token = request.cookies.get("auth_token")
    if token:
        try:
            data = serializer.loads(token)
            username = data.get("username")
            return templates.TemplateResponse("index.html", {"request": request, "username": username})
        except Exception:
            pass  # Токен невалідний
    return RedirectResponse("/login")

@app.get("/history", response_class=HTMLResponse)
async def get_history(request: Request):
    return templates.TemplateResponse("history.html", {"request": request})

@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return templates.TemplateResponse("404.html", {"request": request}, status_code=404)
    return HTMLResponse(content=str(exc.detail), status_code=exc.status_code)
