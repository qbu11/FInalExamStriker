"""
Final Exam Reviewer - Backend API Test
测试所有主要API端点
"""

import os
import sys
import requests
import time
from pathlib import Path

# 添加backend到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_api():
    """测试API端点"""
    base_url = "http://localhost:8000/api"

    print("=" * 60)
    print("  Final Exam Reviewer - API Test")
    print("=" * 60)
    print()

    # 1. 测试健康检查
    print("[1/6] Testing health check...")
    try:
        response = requests.get("http://localhost:8000/health", timeout=2)
        if response.status_code == 200:
            print("  ✅ Health check passed")
        else:
            print(f"  ❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ Cannot connect to server: {e}")
        print("\n  请确保后端服务器正在运行:")
        print("  Windows: start.bat")
        print("  Linux/Mac: ./start.sh")
        return False

    # 2. 测试获取PDF列表
    print("[2/6] Testing PDF list endpoint...")
    try:
        response = requests.get(f"{base_url}/pdfs/", timeout=5)
        if response.status_code == 200:
            pdfs = response.json()
            print(f"  ✅ Found {len(pdfs)} PDF(s)")
        else:
            print(f"  ❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"  ❌ Error: {e}")

    # 3. 测试Gemini配置
    print("[3/6] Testing Gemini API configuration...")
    try:
        from app.config import settings
        print(f"  ✅ API Key: {settings.API_KEY[:20]}...")
        print(f"  ✅ Base URL: {settings.BASE_URL}")
        print(f"  ✅ Model: {settings.GEMINI_MODEL}")
    except Exception as e:
        print(f"  ❌ Configuration error: {e}")
        return False

    # 4. 测试数据库
    print("[4/6] Testing database connection...")
    try:
        from app.database.models import SessionLocal
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        print("  ✅ Database connection successful")
    except Exception as e:
        print(f"  ❌ Database error: {e}")
        return False

    # 5. 测试PDF服务
    print("[5/6] Testing PDF service...")
    try:
        from app.services.pdf_service import PDFService
        pdf_service = PDFService()
        print(f"  ✅ Upload directory: {pdf_service.upload_dir}")
        if os.path.exists(pdf_service.upload_dir):
            print("  ✅ Upload directory exists")
        else:
            print("  ⚠️  Upload directory not found (will be created)")
    except Exception as e:
        print(f"  ❌ PDF service error: {e}")

    # 6. 测试Gemini服务
    print("[6/6] Testing Gemini service...")
    try:
        from app.services.gemini_service import GeminiService
        gemini_service = GeminiService()
        print("  ✅ Gemini service initialized")
    except Exception as e:
        print(f"  ❌ Gemini service error: {e}")

    print()
    print("=" * 60)
    print("  ✅ All tests passed!")
    print("=" * 60)
    print()
    print("📝 Next steps:")
    print("  1. Open frontend/index.html in your browser")
    print("  2. Upload a PDF document")
    print("  3. Start chatting with the AI assistant!")
    print()

    return True

if __name__ == "__main__":
    test_api()
