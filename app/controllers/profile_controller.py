from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from app.models.database import Detection, User
from fastapi.templating import Jinja2Templates
from app.models.database import get_db
from app.controllers.auth_controller import get_current_user

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/profile")
def profile(request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    detection = db.query(Detection).filter(Detection.user_id == user.id).order_by(Detection.timestamp.desc()).all()
    return templates.TemplateResponse("profile.html", {
        "request": request,
        "user": user.username,
        "detection": detection
    })
