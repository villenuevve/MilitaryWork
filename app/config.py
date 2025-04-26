import os

class Config:
    SECRET_KEY = 'your_secret_key_here'
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
    MODEL_PATH = os.path.join(os.getcwd(), 'yolov8n-obb.pt')
    DATABASE = os.path.join(os.getcwd(), 'detections.db')
