import os
import sys
import time
import socket
import subprocess
import webbrowser

try:
    import webview
except ImportError:
    webview = None
    print("Note: Install pywebview for a desktop window: pip install pywebview")

STREAMLIT_PORT = int(os.environ.get("SFO_PORT", 8501))
HOST = "127.0.0.1"

def start_streamlit(app_path, port=STREAMLIT_PORT):
    cmd = [
        sys.executable, "-m", "streamlit", "run", app_path,
        "--server.port", str(port),
        "--server.headless", "true",
        "--browser.gatherUsageStats", "false",
        "--server.address", HOST
    ]
    return subprocess.Popen(cmd)

def wait_for_port(port, timeout=25.0):
    """Waits until the Streamlit server is listening on the port."""
    deadline = time.time() + float(timeout)
    while time.time() < deadline:
        try:
            with socket.create_connection((HOST, int(port)), timeout=0.5):
                return True
        except Exception:
            time.sleep(0.25)
    return False

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.join(base_dir, "app.py")

    if not os.path.exists(app_path):
        print(f"CRITICAL ERROR: app.py not found at {app_path}")
        print("Please make sure app.py is in the same folder as run.py")
        input("Press Enter to exit...")
        sys.exit(1)

    print("--- Smart File Organizer Pro ---")
    print("1. Starting Streamlit server...")
    proc = start_streamlit(app_path, STREAMLIT_PORT)

    print(f"2. Waiting for server on port {STREAMLIT_PORT}...")
    if not wait_for_port(STREAMLIT_PORT, timeout=30):
        print("ERROR: Streamlit failed to start. Check your Python installation.")
        proc.terminate()
        sys.exit(1)

    url = f"http://{HOST}:{STREAMLIT_PORT}"
    print(f"3. Server ready at: {url}")

    try:
        if webview:
            print("4. Launching Desktop Window...")
            webview.create_window("Smart File Organizer Pro", url, width=1280, height=800, resizable=True)
            webview.start(debug=False)
        else:
            print("4. Opening in Default Browser...")
            webbrowser.open(url)
            while True:
                time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping server...")
    finally:
        proc.terminate()
        print("Server stopped.")