import time
import yaml
import threading
import requests
import sys
from pathlib import Path
from twilio.rest import Client
import asyncio
from secrets_config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_NUMBER, TARGET_NUMBER
from app import app
from start_ngrok import get_ngrok_url
from stream_server import streaming_server


client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

call_config_path = Path(__file__).parent / "call_config.yaml"

with open(call_config_path, "r") as f:
    call_config = yaml.safe_load(f)


def place_call(ngrok_url):
    call = client.calls.create(
        to=TARGET_NUMBER,
        from_=TWILIO_NUMBER,
        url=f"{ngrok_url}/voice/menu.xml"
    )
    print(f"Placed call: {call.sid}")

def run_loop(ngrok_url):
    with open(call_config_path, "r") as f:
        while True:
            place_call(ngrok_url)
            time.sleep(call_config.get("retry_interval", 300))  


def wait_for_flask(timeout=5):
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = requests.get("http://127.0.0.1:5050/health")
            if r.status_code == 200:
                return True
        except Exception:
            time.sleep(0.3)
    print("❌ Flask server not ready")
    return False

def wait_for_streaming(port=8765, timeout=5):
    import socket
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=1):
                return True
        except OSError:
            time.sleep(0.3)
    print("❌ Streaming server not ready")
    return False

def start_flask():
    threading.Thread(target=lambda:app.run(host="0.0.0.0", port=5050), daemon=True).start()

def start_streaming_server():
    threading.Thread(target=lambda: asyncio.run(streaming_server()), daemon=True).start()

if __name__ == "__main__":
    start_flask()
    start_streaming_server()

    if not wait_for_flask():
        sys.exit(1)
    if not wait_for_streaming():
        sys.exit(1)

    ngrok_url = get_ngrok_url()  
    run_loop(ngrok_url) 


