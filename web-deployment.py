from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from ultralytics import YOLO
import numpy as np
import cv2

# Абсолютний шлях до каталогу проекту
BASE_DIR = Path(__file__).resolve().parent

# Ініціалізація FastAPI
app = FastAPI()

# Підключення статики і шаблонів
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")

# Завантаження моделі
model = YOLO(BASE_DIR / "app" / "models" / "military_detect_best.pt")  # <-- Обов'язково через BASE_DIR

# Список класів
CLASSES = ['helicopter', 'jet', 'sam', 'tank', 'truck']

# Головна сторінка
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Обробка передбачення
@app.post("/predict", response_class=HTMLResponse)
async def predict(request: Request, image: UploadFile = File(...)):
    try:
        contents = await image.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            return templates.TemplateResponse("error.html", {
                "request": request,
                "error_message": "Помилка обробки файлу. Завантажте коректне зображення."
            })

        results = model(img)
        result = results[0]

        # Перевірка наявності об'єкта
        if not result.obb or result.obb.cls is None or len(result.obb.cls) == 0:
            return templates.TemplateResponse("error.html", {
                "request": request,
                "error_message": "На зображенні не виявлено жодного об'єкта."
            })

        class_id = int(result.obb.cls[0])
        confidence = float(result.obb.conf[0]) * 100
        predicted_class = CLASSES[class_id]

        return templates.TemplateResponse("results.html", {
            "request": request,
            "predicted_class": predicted_class,
            "confidence": f"{confidence:.2f}"
        })

    except Exception as e:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "error_message": f"Внутрішня помилка сервера: {str(e)}"
        })
