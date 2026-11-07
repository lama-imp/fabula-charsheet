"""Entry point for the packaged (click-to-run) version of the app.

Starts the Streamlit server for fabula_charsheet/main.py and opens the app
in the default browser. Keep the window (Windows/Linux) open while using the
app; closing it stops the app.
"""
import socket
import sys
import threading
import time
import webbrowser
from pathlib import Path


def app_directory() -> Path:
    # In a PyInstaller build, data files live in sys._MEIPASS.
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent.parent / "fabula_charsheet"


def free_port(start: int = 8501, attempts: int = 50) -> int:
    for port in range(start, start + attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.bind(("127.0.0.1", port))
            except OSError:
                continue
            return port
    raise RuntimeError("No free port found for the app")


def open_browser_when_ready(url: str, port: int, timeout: float = 60) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=1):
                webbrowser.open(url)
                return
        except OSError:
            time.sleep(0.3)


def main() -> None:
    app_dir = app_directory()
    if str(app_dir) not in sys.path:
        sys.path.insert(0, str(app_dir))

    from streamlit.web import cli as stcli

    port = free_port()
    url = f"http://localhost:{port}"
    print(f"Interactive Character Sheet is running at {url}")
    print("Keep this window open while using the app. Close it to quit.")
    # Headless mode skips Streamlit's first-run email prompt (which would
    # block without a terminal), so the browser is opened here instead.
    threading.Thread(
        target=open_browser_when_ready, args=(url, port), daemon=True
    ).start()

    sys.argv = [
        "streamlit",
        "run",
        str(app_dir / "main.py"),
        "--global.developmentMode=false",
        "--server.headless=true",
        f"--server.port={port}",
        "--server.address=localhost",
        "--server.fileWatcherType=none",
        "--browser.gatherUsageStats=false",
        "--theme.base=light",
        "--client.toolbarMode=viewer",
    ]
    sys.exit(stcli.main())


if __name__ == "__main__":
    main()
