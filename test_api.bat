@echo off
cd /d E:\11Projects\FInalExamReviewer\backend
curl -X POST "http://localhost:8000/api/formula/explain" -H "Content-Type: application/json" -d "{\"pdf_id\": 1, \"selected_text\": \"E=mc^2\"}"
pause
