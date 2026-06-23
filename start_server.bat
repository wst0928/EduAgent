@echo off
cd /d D:\New project\backend
set PYTHONPATH=C:\Users\ASUS\AppData\Roaming\Python\Python310\site-packages
start /min "" "C:\Users\ASUS\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level info
