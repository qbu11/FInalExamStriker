@echo off
cd /d E:\11Projects\FInalExamReviewer\backend
echo Testing main.py import...
python -c "import main; print('Routes:', [r.path for r in main.app.routes])"
pause
