@echo off
cd /d E:\11Projects\FInalExamReviewer\backend
echo Starting server...
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
pause
