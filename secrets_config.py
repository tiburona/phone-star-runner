import os
from dotenv import load_dotenv

load_dotenv()

def get_env_var(name):
    val = os.getenv(name)
    if not val:
        raise RuntimeError(f"Missing required env variable: {name}")
    return val

SSN = get_env_var("SSN")
ACCOUNT_SID = get_env_var("ACCOUNT_SID")
AUTH_TOKEN = get_env_var("AUTH_TOKEN")
TWILIO_NUMBER = get_env_var("TWILIO_NUMBER")
TARGET_NUMBER = get_env_var("TARGET_NUMBER")
ALERT_NUMBER = get_env_var("ALERT_NUMBER")
WEB_HOST = get_env_var("WEB_HOST")

