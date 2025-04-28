# run.py

from fastapi import FastAPI, UploadFile, File
from ultralytics import YOLO
import numpy as np
import cv2
import io

app = FastAPI()
model = YOLO("app/models/yolov8n-obb.pt")

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    results = model(img)
    return results[0].tojson()
