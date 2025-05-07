from sqlalchemy.orm import Session
from app.models.detection_entity import Detection
from app.models.database import SessionLocal, Detection

def get_detections_by_user(db: Session, user_id: int):
    return db.query(Detection).filter(Detection.user_id == user_id).order_by(Detection.timestamp.desc()).all()

def delete_detection(db: Session, detection_id: int):
    detection = db.query(Detection).filter(Detection.id == detection_id).first()
    if detection:
        db.delete(detection)
        db.commit()
        return True
    return False

def save_detection(data: dict):
    db = SessionLocal()
    try:
        detection = Detection(**data)
        db.add(detection)
        db.commit()
        db.refresh(detection)
        return detection
    finally:
        db.close()
