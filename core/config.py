import os

SECRET_KEY = os.getenv("SECRET_KEY", "change-this")
ALGORITHM = "HS256"
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./navi.db")