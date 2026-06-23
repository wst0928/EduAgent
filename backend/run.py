"""启动脚本：一键启动 EduAgent 后端服务（日志写入文件）"""
import os
import sys
import subprocess

BUNDLED_PYTHON = r"C:\Users\ASUS\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "server.log")

backend_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(backend_dir)

python_exe = BUNDLED_PYTHON if os.path.exists(BUNDLED_PYTHON) else sys.executable

print("=" * 50)
print("EduAgent - 个性化学习多智能体系统")
print("=" * 50)
print(f"工作目录: {backend_dir}")
print(f"Python: {python_exe}")
print(f"日志: {LOG_FILE}")
print("正在启动后端服务...\n")

with open(LOG_FILE, "w", encoding="utf-8") as log:
    proc = subprocess.Popen(
        [python_exe, "-m", "uvicorn", "app.main:app",
         "--host", "0.0.0.0", "--port", "8000", "--log-level", "info"],
        cwd=backend_dir,
        stdout=log,
        stderr=subprocess.STDOUT,
    )

import time
time.sleep(3)
if proc.poll() is None:
    print(f"服务已启动 (PID: {proc.pid})")
    print(f"访问地址: http://localhost:8000")
    print(f"API文档: http://localhost:8000/docs")
    print("按 Ctrl+C 停止服务\n")

    # Tail the log
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as log:
            while True:
                line = log.readline()
                if line:
                    print(line.rstrip())
                elif proc.poll() is not None:
                    print(f"\n服务已停止 (exit code: {proc.returncode})")
                    break
                else:
                    time.sleep(0.1)
    except KeyboardInterrupt:
        proc.terminate()
        proc.wait()
        print("\n服务已停止")
else:
    print(f"启动失败 (exit code: {proc.returncode})")
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        print(f.read())
