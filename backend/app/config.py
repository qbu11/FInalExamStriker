import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../../.env'))

class Settings:
    # API配置
    API_KEY = os.getenv("api_key")
    BASE_URL = os.getenv("base_url")
    GEMINI_MODEL = "google/gemini-3-flash-preview"

    # 数据库配置
    DATABASE_URL = "sqlite:///../../database/exam_reviewer.db"

    # 文件存储配置
    UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "../uploads")
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS = {".pdf"}

    # CORS配置
    CORS_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "null",  # 允许 file:// 协议访问
    ]

settings = Settings()

# 确保上传目录存在
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
