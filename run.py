"""Entry point: `python run.py` starts the development server."""
import os
import subprocess
import sys
from pathlib import Path

from app import create_app

app = create_app(os.environ.get("FLASK_CONFIG", "development"))


def _bash_executable() -> str:
    if os.name == "nt":
        git_bash = Path(os.environ.get("ProgramFiles", "C:\\Program Files")) / "Git" / "bin" / "bash.exe"
        if git_bash.exists():
            return str(git_bash)
    return "bash"


def run_startup_check() -> None:
    """Run the Python and Bash smoke tests before starting the server."""
    subprocess.run(
        [sys.executable, str(Path(__file__).with_name("helloworld.py"))],
        check=True,
    )
    subprocess.run(
        [_bash_executable(), str(Path(__file__).parent / "app" / "data" / "thebash.sh")],
        check=True,
    )

if __name__ == "__main__":
    run_startup_check()
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", 5000)))
