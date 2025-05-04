from database import engine, Base
from app.legacy_models import User

Base.metadata.create_all(bind=engine)
