from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import HTMLResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from ultralytics import YOLO
import numpy as np
import cv2
import exifread
import io

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI()

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")

model = YOLO(BASE_DIR / "app" / "models" / "military_detect_best.pt")

CLASSES = ['helicopter', 'jet', 'sam', 'tank', 'truck']


def convert_to_degrees(value):
    """Перетворення EXIF координат у десяткові градуси"""
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
                "gps_lat_decimal": gps_lat_decimal,  
                "gps_lon_decimal": gps_lon_decimal,
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

        if lat and lon:
            gps_lat_decimal = convert_to_degrees(lat.values)
            gps_lon_decimal = convert_to_degrees(lon.values)
        else:
            gps_lat_decimal = None
            gps_lon_decimal = None

        metadata = {
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

        return metadata

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
        print("DEBUG METADATA:", metadata)
        print("DEBUG GPS decimal:", metadata.get("gps_lat_decimal"), metadata.get("gps_lon_decimal"))

        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            return templates.TemplateResponse("error.html", {
                "request": request,
                "error_message": "Помилка обробки файлу. Завантажте коректне зображення.",
                "metadata": metadata
            })

        results = model(img)
        result = results[0]

        if not result.obb or result.obb.cls is None or len(result.obb.cls) == 0:
            return templates.TemplateResponse("error.html", {
                "request": request,
                "error_message": "На зображенні не виявлено жодного об'єкта.",
                "metadata": metadata
            })

        class_id = int(result.obb.cls[0])
        confidence = float(result.obb.conf[0]) * 100
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
            "error_message": f"Внутрішня помилка сервера: {str(e)}",
            "metadata": metadata
        })

@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return templates.TemplateResponse("404.html", {"request": request}, status_code=404)
    return HTMLResponse(content=str(exc.detail), status_code=exc.status_code)