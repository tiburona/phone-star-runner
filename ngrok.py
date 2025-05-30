import requests
import subprocess
import time
from pathlib import Path
import sys

from config.secrets_config import NGROK_AUTH_TOKEN


def write_config():
    config_path = Path("ngrok.yml")
    config_path.write_text(f"""version: 2
authtoken: {NGROK_AUTH_TOKEN}
tunnels:
  flask:
    proto: http
    addr: 5050
  stream:
    proto: http
    addr: 8765
""")

def start_ngrok():
    subprocess.Popen(["ngrok", "start", "--all", "--config=ngrok.yml"])
    time.sleep(3)
    return requests.get("http://localhost:4040/api/tunnels").json()['tunnels']

def needs_restart(tunnels):
    return not all(
        any(needed in str(t["config"]["addr"]) for t in tunnels)
        for needed in ("5050", "8765")
    )

def safe_restart():
    print("🚫 Ngrok is running, but not exposing both required ports (5000 and 8765).")
    choice = input("Kill ngrok and restart with correct config? (y/n): ").strip().lower()
    if choice == "y":
        subprocess.run(["pkill", "-f", "ngrok"])
        write_config()
        return start_ngrok()
    else:
        print("❌ Cannot continue without both tunnels — exiting.")
        sys.exit(1)

def get_ngrok_session():
    try:
        r = requests.get("http://localhost:4040/api/tunnels", timeout=1)
        tunnels = r.json().get("tunnels", {})
        return safe_restart() if needs_restart(tunnels) else tunnels
    except (requests.ConnectionError, requests.Timeout):
        write_config()
        return start_ngrok()

def get_ngrok_url(protocol='http'):
    tunnels = get_ngrok_session()
    port = "5050" if protocol == 'http' else "8765"
    for t in tunnels:
        if t["config"]["addr"].endswith(f":{port}"):
            return t["public_url"] if protocol == 'http' else t["public_url"].replace("https", "wss")
    raise RuntimeError(f"❌ Couldn't find HTTPS tunnel for(port {port})")
   