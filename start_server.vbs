Set objShell = CreateObject("WScript.Shell")
objShell.CurrentDirectory = "D:\New project\backend"
objShell.Environment("PROCESS")("PYTHONPATH") = "C:\Users\ASUS\AppData\Roaming\Python\Python310\site-packages"
objShell.Run """C:\Users\ASUS\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"" -m uvicorn app.main:app --host 127.0.0.1 --port 8000", 0, False
