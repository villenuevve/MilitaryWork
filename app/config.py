import os

class Config:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    
    SECRET_KEY = 'your_secret_key_here'
    
    UPLOAD_FOLDER = os.path.join(BASE_DIR, '..', 'uploads')
    MODEL_PATH = os.path.join(BASE_DIR, '..', 'yolov8n-obb.pt')
    DATABASE = os.path.join(BASE_DIR, '..', 'detections.db')
