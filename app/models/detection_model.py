from ultralytics import YOLO
from app.config import Config
import numpy as np
import cv2
import tempfile
from PIL import Image
import io

# Завантаження моделі один раз
model = YOLO('yolov8n-obb.pt')  # (важливо: правильний шлях до твоєї моделі!)

def predict_image(file_storage):
    image_bytes = file_storage.read()
    img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
    img_array = np.array(img)

    results = model.predict(source=img_array, save=False, conf=0.25)

    if len(results[0].boxes.cls) == 0:
        return "Не виявлено", 0.0

    best_idx = results[0].probs.top1
    confidence = results[0].probs.top1conf
    class_name = model.names[best_idx]

    return class_name, confidence
