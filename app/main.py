from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse
from app.services.crud import delete_detection
from app.models.database import SessionLocal
from app.controllers import login_controller
from app.services.crud import save_detection
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.controllers import auth_controller
from starlette.exceptions import HTTPException as StarletteHTTPException
from pathlib import Path
from ultralytics import YOLO
import numpy as np
import cv2
import exifread
import io
import os

app = FastAPI()
app.include_router(login_controller.router)

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=BASE_DIR / "templates")

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
app.include_router(auth_controller.router)
model = YOLO(BASE_DIR / "app" / "models" / "military_detect_best.pt")
CLASSES = ['helicopter', 'jet', 'sam', 'tank', 'truck']

def convert_to_degrees(value):
    d, m, s = value
    degrees = float(d.num) / float(d.den)
    minutes = float(m.num) / float(m.den)
    seconds = float(s.num) / float(s.den)
    return degrees + (minutes / 60.0) + (seconds / 3600.0)

def extract_metadata(file_bytes, filename, username="анонім"):
    try:
        if filename.lower().endswith((".webp", ".png", ".bmp")):
            return {
                "datetime": "Невідомо",
                "gps_lat": "Немає",
                "gps_lon": "Немає",
                "gps_lat_decimal": None,
                "gps_lon_decimal": None,
                "camera_model": "Невідомо",
                "brightness": "Невідомо",
                "orientation": "Невідомо",
                "source_path": filename,
                "capture_type": "aerial" if "drone" in filename.lower() else "ground",
                "username": username
            }

        tags = exifread.process_file(io.BytesIO(file_bytes), details=False)

        lat = tags.get("GPS GPSLatitude")
        lon = tags.get("GPS GPSLongitude")

        gps_lat_decimal = convert_to_degrees(lat.values) if lat else None
        gps_lon_decimal = convert_to_degrees(lon.values) if lon else None

        return {
            "datetime": str(tags.get("EXIF DateTimeOriginal", "Невідомо")),
            "gps_lat": str(lat or "Немає"),
            "gps_lon": str(lon or "Немає"),
            "gps_lat_decimal": gps_lat_decimal,
            "gps_lon_decimal": gps_lon_decimal,
            "camera_model": str(tags.get("Image Model", "Невідомо")),
            "brightness": str(tags.get("EXIF BrightnessValue", "Невідомо")),
            "orientation": str(tags.get("Image Orientation", "Невідомо")),
            "source_path": filename,
            "capture_type": "aerial" if "drone" in filename.lower() else "ground",
            "username": username
        }

    except Exception as e:
        return {
            "datetime": "Невідомо",
            "gps_lat": "Немає",
            "gps_lon": "Немає",
            "gps_lat_decimal": None,
            "gps_lon_decimal": None,
            "camera_model": "Невідомо",
            "brightness": "Невідомо",
            "orientation": "Невідомо",
            "source_path": filename,
            "capture_type": "unknown",
            "username": username,
            "error": f"EXIF помилка: {str(e)}"
        }

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/predict", response_class=HTMLResponse)
async def predict(request: Request, image: UploadFile = File(...)):
    try:
        contents = await image.read()
        metadata = extract_metadata(contents, image.filename)

        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            return templates.TemplateResponse("error.html", {
                "request": request,
                "error_message": "Помилка обробки зображення.",
                "metadata": metadata
            })

        results = model(img)[0]

        save_path = BASE_DIR / "static" / "predictions" / image.filename
        results.save(filename=save_path)

        if not results.obb or results.obb.cls is None or len(results.obb.cls) == 0:
            return templates.TemplateResponse("error.html", {
                "request": request,
                "error_message": "Об'єктів не знайдено.",
                "metadata": metadata
            })

        class_id = int(results.obb.cls[0])
        confidence = float(results.obb.conf[0]) * 100
        predicted_class = CLASSES[class_id]

        return templates.TemplateResponse("results.html", {
            "request": request,
            "predicted_class": predicted_class,
            "confidence": f"{confidence:.2f}",
            "metadata": metadata
        })

    except Exception as e:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "error_message": f"Внутрішня помилка: {str(e)}",
            "metadata": {}
        })

@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return templates.TemplateResponse("404.html", {"request": request}, status_code=404)
    return HTMLResponse(content=str(exc.detail), status_code=exc.status_code)

@app.post("/delete/{detection_id}")
async def delete_detection_route(detection_id: int, request: Request):
    db = SessionLocal()
    delete_detection(db, detection_id)
    return RedirectResponse(url="/history", status_code=303)