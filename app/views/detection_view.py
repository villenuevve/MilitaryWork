from fastapi.requests import Request
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")

def render_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

def render_results(request: Request, result: dict):
    return templates.TemplateResponse("results.html", {"request": request, **result})

def render_error(request: Request, message: str):
    return templates.TemplateResponse("error.html", {"request": request, "message": message})

def render_404(request: Request):
    return templates.TemplateResponse("404.html", {"request": request})
