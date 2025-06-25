import tempfile
from pathlib import Path
from backend.app.generate_frontend_env import write_env_file

def test_write_env_file_creates_file_with_content():

    with tempfile.TemporaryDirectory() as tmpdirname:
        env_path = Path(tmpdirname) / ".env"

        write_env_file(env_path)

        assert env_path.exists()

        content = env_path.read_text()
        assert "VITE_BACKEND_URL=" in content
        assert "VITE_FRONTEND_PORT=" in content
        assert "VITE_HOST=" in content
