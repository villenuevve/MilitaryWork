from sqlalchemy import Column, Integer, String, Float
from app.models.base import Base

class Detection(Base):
    __tablename__ = "detection"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    predicted_class = Column(String)
    confidence = Column(Float)
    meta_info = Column(String) 
    timestamp = Column(String)
