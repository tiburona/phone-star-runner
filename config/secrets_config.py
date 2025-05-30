import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).with_name(".env"), override=True)


def get_env_var(name):
    val = os.getenv(name)
    if not val:
        raise RuntimeError(f"Missing required env variable: {name}")
    return val

ID_NUMBER = get_env_var("ID_NUMBER")
PIN = get_env_var("PIN")
TWILIO_ACCOUNT_SID = get_env_var("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = get_env_var("TWILIO_AUTH_TOKEN")
TWILIO_NUMBER = get_env_var("TWILIO_NUMBER")
TARGET_NUMBER = get_env_var("TARGET_NUMBER")
FORWARDING_NUMBER = get_env_var("FORWARDING_NUMBER")
NGROK_AUTH_TOKEN = get_env_var("NGROK_AUTH_TOKEN")

SECRETS_DICT = {
    'ID_NUMBER': ID_NUMBER,
    'PIN': PIN,
    'FORWARDING_NUMBER': FORWARDING_NUMBER
}

