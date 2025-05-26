import time
import yaml
from pathlib import Path
from twilio.rest import Client
from secrets_config import ACCOUNT_SID, AUTH_TOKEN, TWILIO_NUMBER, TARGET_NUMBER

client = Client(ACCOUNT_SID, AUTH_TOKEN)

call_config_path = Path(__file__).parent / "call_config.yaml"

with open(call_config_path, "r") as f:
    call_config = yaml.safe_load(f)


def place_call():
    call = client.calls.create(
        to=TARGET_NUMBER,
        from_=TWILIO_NUMBER,
        url=f"https://{call_config['base_url']}/voice/menu.xml"
    )
    print(f"Placed call: {call.sid}")

def run_loop():
    with open(call_config_path, "r") as f:
        while True:
            place_call()
            time.sleep(call_config.get("retry_interval", 300))  

if __name__ == "__main__":
    run_loop()
