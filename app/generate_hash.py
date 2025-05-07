from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
hashed_password = pwd_context.hash("9971")  # ← свій пароль
print("Хеш:", hashed_password)
