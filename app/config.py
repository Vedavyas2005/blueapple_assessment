import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "fallback-secret")
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{os.environ.get('DB_USER', 'root')}"
        f":{os.environ.get('DB_PASSWORD', '')}"
        f"@{os.environ.get('DB_HOST', 'localhost')}"
        f":{os.environ.get('DB_PORT', '3306')}"
        f"/{os.environ.get('DB_NAME', 'blueapple_db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True
    ADMIN_SECRET = os.environ.get("ADMIN_SECRET", "adminauth")