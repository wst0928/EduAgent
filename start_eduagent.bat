@echo off
cd /d D:\New project\backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --log-level info
pause
