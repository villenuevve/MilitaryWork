from app.models.database import Base, engine

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    print("✅ База даних успішно створена!")
