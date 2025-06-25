import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.config import get_settings

def write_env_file(env_path: Path = None):
    settings = get_settings()

    if env_path is None:
        env_path = Path(__file__).resolve().parents[2] / "frontend" / ".env"

    env_path.parent.mkdir(parents=True, exist_ok=True)

    with env_path.open("w") as f:
        f.write(f"VITE_BACKEND_URL=http://{settings.public_ip}:{settings.port_backend}\n")
        f.write(f"VITE_FRONTEND_PORT={settings.port_frontend}\n")
        f.write(f"VITE_HOST={settings.host}\n")

    print(f".env file created in: {env_path}")

if __name__ == "__main__":
    write_env_file()
