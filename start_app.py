import subprocess
import sys
import time
import configparser
from pathlib import Path
import platform
import os

os.environ["APP_ENV"] = "default"

config_path = Path(__file__).resolve().parent / "backend" / "app" / "config.ini"
config = configparser.ConfigParser()
config.read(config_path)


host = config.get("server", "host", fallback="127.0.0.1")
port = config.get("server", "port_backend", fallback="8000")
log_level = config.get("server", "log_level", fallback="info")

backend_dir = Path(__file__).resolve().parent / "backend"
frontend_dir = Path(__file__).resolve().parent / "frontend"

npm_command = "npm.cmd" if platform.system() == "Windows" else "npm"

print("Start Frontend (npm run dev)...")
frontend_process = subprocess.Popen([npm_command, "run", "dev"], cwd=frontend_dir)

time.sleep(3)

print("Start Backend (uvicorn)...")
backend_process = subprocess.Popen([
    sys.executable, "-m", "uvicorn",
    "app.main:app",
    "--host", host,
    "--port", port,
    "--reload", True,
    "--log-level", log_level,
    "--reload_delay", 5,
 #   "--reload_dirs", ['myapp', 'frontend/dist'],
], cwd=backend_dir)

try:
    frontend_process.wait()
    backend_process.wait()
except KeyboardInterrupt:
    print("Beende Prozesse…")
    frontend_process.terminate()
    backend_process.terminate()
