@echo off
cd /d E:\11Projects\FInalExamReviewer\backend
echo Upgrading SQLAlchemy...
pip install --upgrade sqlalchemy
echo.
echo Done! Now starting server...
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
pause
