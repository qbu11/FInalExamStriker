@echo off
cd /d E:\11Projects\FInalExamReviewer\backend

echo Killing existing Python processes...
taskkill /F /IM python.exe 2>nul

echo Cleaning Python cache...
rd /s /q __pycache__ 2>nul
rd /s /q app\__pycache__ 2>nul
rd /s /q app\routes\__pycache__ 2>nul
rd /s /q app\services\__pycache__ 2>nul
rd /s /q app\database\__pycache__ 2>nul
rd /s /q app\models\__pycache__ 2>nul

echo.
echo Starting server...
python -m uvicorn main:app --host 0.0.0.0 --port 8000
pause
