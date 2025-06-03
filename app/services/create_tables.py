from app.models.database import engine, Base
from app.models.detection_entity import Detection
from app.models.database import User

Base.metadata.create_all(bind=engine)
