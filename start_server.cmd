@echo off
cd /d D:\New project\backend
set PYTHONPATH=C:\Users\ASUS\AppData\Roaming\Python\Python310\site-packages
start /b "" "C:\Users\ASUS\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --log-level info > D:\New project\backend\server.log 2>&1
