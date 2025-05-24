from sqlalchemy.orm import Session
from app.models.detection_entity import Detection
from app.models.database import SessionLocal, Detection

def get_detections_by_user(db: Session, user_id: int):
    return db.query(Detection).filter(Detection.user_id == user_id).order_by(Detection.timestamp.desc()).all()

def get_detections_by_username(db: Session, username: str):
    return db.query(Detection).join(User).filter(User.username == username).order_by(Detection.timestamp.desc()).all()


def delete_detection(db: Session, detection_id: int):
    detection = db.query(Detection).filter(Detection.id == detection_id).first()
    if detection:
        db.delete(detection)
        db.commit()
        return True
    return False

def save_detection(db, data: dict):
    detection = Detection(**data)
    db.add(detection)
    db.commit()
    db.refresh(detection)
    return detection

