from app.models.detection_entity import Detection
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, Text, DateTime
from datetime import datetime
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.orm import relationship
DATABASE_URL = "sqlite:///app/models/detections.db"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    role = Column(String, default="user")
    hashed_password = Column(String, nullable=False)

    detection = relationship("Detection", back_populates="user")

class Detection(Base):
    __tablename__ = "detection"

    id = Column(Integer, primary_key=True, index=True)
    predicted_class = Column(String)
    confidence = Column(Float)
    meta_info = Column(Text)
    timestamp = Column(DateTime, default=datetime)
    user_id = Column(Integer, ForeignKey("user.id")) 

    user = relationship("User", back_populates="detection")

def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
