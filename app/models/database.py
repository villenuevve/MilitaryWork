import sqlite3
from app.config import Config

def get_connection():
    conn = sqlite3.connect(Config.DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def insert_detection(detection):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO detections (class_name, confidence, angle)
        VALUES (?, ?, ?)
    """, (detection['class_name'], detection['confidence'], detection['angle']))
    conn.commit()
    conn.close()
