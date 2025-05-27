from ultralytics import YOLO
import numpy as np
import cv2
from PIL import Image
import io
import os
import uuid

model = YOLO('app/models/special.pt') 

def predict_image(file_storage):
    image_bytes = file_storage.read()
    img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
    img_array = np.array(img)

    results = model.predict(source=img_array, save=False, conf=0.1)

    boxes = results[0].obb if hasattr(results[0], 'obb') else results[0].boxes

    if boxes is None or len(boxes.cls) == 0:
        return "Не виявлено", 0.0, None

    best_idx = int(boxes.cls[0].item())
    confidence = float(boxes.conf[0].item())
    class_name = model.names[best_idx]

    # Збереження зображення
    annotated_img = results[0].plot()
    filename = f"{uuid.uuid4().hex}.jpg"
    save_dir = os.path.join('app', 'static', 'predictions')
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, filename)

    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    cv2.imwrite(save_path, cv2.cvtColor(annotated_img, cv2.COLOR_RGB2BGR))

    return class_name, confidence, save_path

