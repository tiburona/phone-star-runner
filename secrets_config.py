import os
from dotenv import load_dotenv

load_dotenv()

def get_env_var(name):
    val = os.getenv(name)
    if not val:
        raise RuntimeError(f"Missing required env variable: {name}")
    return val

ID_NUMBER = get_env_var("ID_NUMBER")
PIN = get_env_var("PIN")
TWILIO_ACCOUNT_SID = get_env_var("ACCOUNT_SID")
TWILIO_AUTH_TOKEN = get_env_var("AUTH_TOKEN")
TWILIO_NUMBER = get_env_var("TWILIO_NUMBER")
TARGET_NUMBER = get_env_var("TARGET_NUMBER")
FORWARDING_NUMBER = get_env_var("ALERT_NUMBER")

