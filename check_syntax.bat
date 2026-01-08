@echo off
cd /d E:\11Projects\FInalExamReviewer\backend
python -m py_compile app\routes\chat_routes.py
if %errorlevel% equ 0 (
    echo SYNTAX OK
) else (
    echo SYNTAX ERROR
)
pause
