from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse, HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from app.models.database import SessionLocal, get_db, User
from app.models.detection_entity import Detection
from app.services.auth import get_current_user_id_from_cookie
from pathlib import Path
from datetime import datetime
import qrcode
import json
import csv 
import io

BASE_DIR = Path(__file__).resolve().parent.parent.parent
templates = Jinja2Templates(directory=BASE_DIR / "templates")
router = APIRouter()

@router.get("/history", response_class=HTMLResponse)
async def history(request: Request):
    db: Session = next(get_db())
    base_url = str(request.base_url)
    print(base_url)

    from_date = request.query_params.get("from")
    to_date = request.query_params.get("to")
    class_filter = request.query_params.get("class")

    user_id = get_current_user_id_from_cookie(request)
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        return RedirectResponse(url="/login", status_code=302)

    if user and user.role == "admin":
        users = db.query(User).all()
        user_infos = []
        for u in users:
            detections_count = db.query(Detection).filter(Detection.user_id == u.id).count()
            user_infos.append({
                "id": u.id,
                "username": u.username,
                "role": u.role,
                "detections_count": detections_count
            })
    else:
        user_infos = None

    if user and user.role == "admin":
        query = db.query(Detection)
    else:
        query = db.query(Detection).filter(Detection.user_id == user_id)

    if class_filter:
        query = query.filter(Detection.predicted_class == class_filter)

    if from_date:
        query = query.filter(Detection.timestamp >= from_date)
    if to_date:
        query = query.filter(Detection.timestamp <= to_date)
    if class_filter:
        query = query.filter(Detection.predicted_class == class_filter)

    raw_detections = query.order_by(Detection.timestamp.desc()).all()

    detections = []
    for det in raw_detections:
        try:
            meta = json.loads(det.meta_info) if det.meta_info else {}
        except json.JSONDecodeError:
            meta = {}

        detections.append({
        "id": det.id,
        "predicted_class": det.predicted_class,
        "confidence": det.confidence,
        "timestamp": det.timestamp,
        "image_url": meta.get("image_path", ""),
        "gps_lat_decimal": meta.get("gps_lat_decimal"),
        "gps_lon_decimal": meta.get("gps_lon_decimal"),
        "camera_model": meta.get("camera_model", "Невідомо"),
        "datetime": meta.get("datetime", "Невідомо"),
        "username": meta.get("username", "анонім"),
        "orientation": meta.get("orientation", "Невідомо"),
        "brightness": meta.get("brightness", "Невідомо"),
        "source_path": meta.get("source_path", "")
    })

    total = len(detections)
    avg_conf = round(sum([d["confidence"] for d in detections]) / total, 2) if total else 0
    classes = set([d["predicted_class"] for d in detections])

    return templates.TemplateResponse("history.html", {
    "request": request,
    "current_user": user,
    "detections": detections,
    "total": total,
    "avg_conf": avg_conf,
    "classes": classes,
    "username": user.username,
    "role": user.role,
    "user_infos": user_infos,
    "current_user_id": user.id,
})

@router.get("/export/pdf")
async def export_pdf(request: Request):
    db: Session = next(get_db())
    user_id = get_current_user_id_from_cookie(request)
    detections = db.query(Detection).filter(Detection.user_id == user_id).order_by(Detection.timestamp.desc()).all()
    user = db.query(User).filter(User.id == user_id).first()
    username = user.username if user else "anonymous"

    # Підготовка таблиці
    data = [["ID", "Class", "Confidence", "GPS", "Timestamp"]]
    for det in detections:
        meta = json.loads(det.meta_info) if det.meta_info else {}
        data.append([
            str(det.id),
            det.predicted_class,
            f"{det.confidence:.2f}%",
            meta.get("gps", "—"),
            str(det.timestamp)
        ])

    exports_dir = Path(__file__).resolve().parent.parent.parent / "exports"
    exports_dir.mkdir(exist_ok=True)
    pdf_path = exports_dir / "detections.pdf"

    doc = SimpleDocTemplate(str(pdf_path), pagesize=A4,
                            rightMargin=40, leftMargin=40, topMargin=60, bottomMargin=40)

    styles = getSampleStyleSheet()
    title = Paragraph("Detection Report: Special Equipment Recognition", styles["Title"])
    spacer = Spacer(1, 12)

    table = Table(data, colWidths=[50, 120, 80, 100, 150])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
        ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ]))

    qr_url = "http://192.168.31.19:8000/history"
    qr = qrcode.make(qr_url)
    qr_io = io.BytesIO()
    qr.save(qr_io, format="PNG")
    qr_io.seek(0)
    qr_img = Image(qr_io, width=60, height=60)

    footer = Paragraph(
        f"Generated for: {username} | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        styles["Normal"]
    )
    spacer_footer = Spacer(1, 24)

    doc.build([title, spacer, table, spacer_footer, qr_img, footer])

    return FileResponse(str(pdf_path), media_type='application/pdf', filename="detections.pdf")

@router.get("/export/csv")
async def export_csv(request: Request):
    db: Session = next(get_db())
    user_id = get_current_user_id_from_cookie(request)
    detections = db.query(Detection).filter(Detection.user_id == user_id).order_by(Detection.timestamp.desc()).all()

    exports_dir = BASE_DIR / "exports"
    exports_dir.mkdir(exist_ok=True)
    csv_path = exports_dir / "detections.csv"

    with open(csv_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["ID", "Class", "Confidence", "GPS", "Timestamp"])

        for det in detections:
            meta = json.loads(det.meta_info) if det.meta_info else {}
            writer.writerow([
                det.id,
                det.predicted_class,
                f"{det.confidence:.2f}%",
                meta.get("gps", "—"),
                det.timestamp
            ])

    return FileResponse(str(csv_path), media_type='text/csv', filename="detections.csv")

@router.post("/delete/{detection_id}")
async def delete_detection(request: Request, detection_id: int):
    db = SessionLocal()
    user_id = get_current_user_id_from_cookie(request)
    user = db.query(User).filter(User.id == user_id).first()

    if user and user.role == "admin":
        detection = db.query(Detection).filter(Detection.id == detection_id).first()
    else:
        detection = db.query(Detection).filter(Detection.id == detection_id, Detection.user_id == user_id).first()

    if detection:
        db.delete(detection)
        db.commit()

    return RedirectResponse(url="/history", status_code=302)

@router.post("/admin/update-role/{user_id}")
async def update_role(request: Request, user_id: int):
    db = SessionLocal()
    form = await request.form()
    new_role = form.get("new_role")
    user = db.query(User).filter(User.id == user_id).first()
    if user and new_role in ["user", "admin"]:
        user.role = new_role
        db.commit()
    return RedirectResponse(url="/history", status_code=302)

@router.post("/admin/delete-user/{user_id}")
async def delete_user(request: Request, user_id: int):
    db = SessionLocal()
    current_user_id = get_current_user_id_from_cookie(request)
    if user_id == current_user_id:
        return RedirectResponse(url="/history", status_code=302)
    user_to_delete = db.query(User).filter(User.id == user_id).first()
    if not user_to_delete or user_to_delete.role == "admin":
        return RedirectResponse(url="/history", status_code=302)

    db.query(Detection).filter(Detection.user_id == user_to_delete.id).delete()
    db.delete(user_to_delete)
    db.commit()

    return RedirectResponse(url="/history", status_code=302)
