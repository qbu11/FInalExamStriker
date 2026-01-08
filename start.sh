#!/bin/bash

echo "========================================"
echo "  Final Exam Reviewer - Starting..."
echo "========================================"
echo ""

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python not found! Please install Python 3.8+"
    exit 1
fi

echo "[1/4] Checking dependencies..."

# 进入backend目录
cd backend

# 检查是否已安装依赖
if ! python3 -c "import fastapi" &> /dev/null; then
    echo "[2/4] Installing Python dependencies..."
    pip3 install -r requirements.txt
else
    echo "[2/4] Dependencies already installed"
fi

echo "[3/4] Initializing database..."
python3 -c "from app.database.models import init_db; init_db()"

echo "[4/4] Starting server..."
echo ""
echo "========================================"
echo "  Server is starting..."
echo "  Backend API: http://localhost:8000"
echo "  Frontend: Open frontend/index.html"
echo "========================================"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# 启动服务器
python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 --app-dir backend
