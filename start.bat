@echo off
echo ========================================
echo   Final Exam Reviewer - Starting...
echo ========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found! Please install Python 3.8+
    pause
    exit /b 1
)

echo [1/4] Checking dependencies...

REM 检查是否已安装依赖
cd backend
python -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo [2/4] Installing Python dependencies...
    pip install -r requirements.txt
) else (
    echo [2/4] Dependencies already installed
)

echo [3/4] Initializing database...
python -c "from app.database.models import init_db; init_db()"

echo [4/4] Starting server...
echo.
echo ========================================
echo   Server is starting...
echo   Backend API: http://localhost:8000
echo   Frontend: Open frontend/index.html
echo ========================================
echo.
echo Press Ctrl+C to stop the server
echo.

REM 启动服务器
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 --app-dir backend
