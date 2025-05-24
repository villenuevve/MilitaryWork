from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse, HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from app.models.database import SessionLocal, get_db
from app.models.detection_entity import Detection
from pathlib import Path
import json

BASE_DIR = Path(__file__).resolve().parent.parent.parent
templates = Jinja2Templates(directory=BASE_DIR / "templates")

router = APIRouter()

@router.get("/history", response_class=HTMLResponse)
async def history(request: Request):
    db: Session = next(get_db())

    # Фільтри
    from_date = request.query_params.get("from")
    to_date = request.query_params.get("to")
    class_filter = request.query_params.get("class")

    query = db.query(Detection)
    if from_date:
        query = query.filter(Detection.timestamp >= from_date)
    if to_date:
        query = query.filter(Detection.timestamp <= to_date)
    if class_filter:
        query = query.filter(Detection.predicted_class == class_filter)

    raw_detections = query.order_by(Detection.timestamp.desc()).all()

    detections = []
    for det in raw_detections:
        meta = json.loads(det.meta_info) if det.meta_info else {}
        detections.append({
            "id": det.id,
            "predicted_class": det.predicted_class,
            "confidence": det.confidence,
            "timestamp": det.timestamp,
            "image_url": meta.get("image_path", ""),
            "gps": meta.get("gps", "")
        })

    return templates.TemplateResponse("history.html", {
        "request": request,
        "detections": detections
    })


@router.get("/export/pdf")
async def export_pdf():
    db: Session = next(get_db())
    detections = db.query(Detection).order_by(Detection.timestamp.desc()).all()

    data = [["ID", "Клас", "Точність", "GPS", "Дата"]]
    for det in detections:
        meta = json.loads(det.meta_info) if det.meta_info else {}
        data.append([
            det.id,
            det.predicted_class,
            f"{det.confidence:.2f}%",
            meta.get("gps", "—"),
            det.timestamp
        ])

    pdf_path = "exports/detections.pdf"
    doc = SimpleDocTemplate(pdf_path, pagesize=A4)
    table = Table(data)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
    ]))
    doc.build([table])

    return FileResponse(pdf_path, media_type='application/pdf', filename="detections.pdf")

@router.post("/delete/{detection_id}")
async def delete_detection(detection_id: int):
    db = SessionLocal()
    detection = db.query(Detection).filter(Detection.id == detection_id).first()
    if detection:
        db.delete(detection)
        db.commit()
    return RedirectResponse(url="/history", status_code=302)
