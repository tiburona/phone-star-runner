from flask import Flask, Response, request, send_from_directory
import yaml
import os
from pathlib import Path
import xml.etree.ElementTree as ET
from ngrok import get_ngrok_url
from config.secrets_config import SECRETS_DICT
from config.public_config import SECRET_STEPS, AUDIO_RECORDINGS, DIAL_TIMEOUT, STEP_CONFIG_FNAME

app = Flask(__name__)

STEP_CONFIG_PATH = Path(__file__).parent / "config" / STEP_CONFIG_FNAME
AUDIO_DIR = Path(__file__).parent / "audio"


@app.before_request
def log_request():
    print(f"Incoming request: {request.method} {request.url}")

@app.route("/")
def index():
    return "Phone Star Runner is live!"

@app.route("/health")
def health():
    return "OK", 200

@app.route("/audio/<filename>")
def serve_audio(filename):
    return send_from_directory(AUDIO_DIR, filename)

@app.route("/voice/menu.xml", methods=["GET", "POST"])
def menu():
    wss_url = get_ngrok_url('wss')
    http_url = get_ngrok_url('http')
    with open(STEP_CONFIG_PATH, "r") as f:
        steps_config = yaml.safe_load(f)

    steps = steps_config.get("steps", [])

    response_el = ET.Element("Response")

    start_el = ET.SubElement(response_el, "Start")

    print(f"Use this stream URL: {wss_url}")
    ET.SubElement(start_el, "Stream", url=wss_url)

    secret_counter = 0
    audio_counter = 0

    for step in steps:
        pause = str(step["pause"])

        if "digits" in step:
            secret_value = SECRETS_DICT[SECRET_STEPS[secret_counter]]
            secret_counter += 1
            ET.SubElement(response_el, "Pause", length=pause)
            ET.SubElement(response_el, "Play", digits=secret_value)

        elif "digit" in step:
            ET.SubElement(response_el, "Pause", length=pause)
            ET.SubElement(response_el, "Play", digits=step["digit"])

        elif "play_audio" in step:
            audio_route = f"{http_url}/audio/{AUDIO_RECORDINGS[audio_counter]}"
            audio_counter += 1
            ET.SubElement(response_el, "Play").text = audio_route

    redirect_el = ET.SubElement(response_el, "Redirect")
    redirect_el.text = "/voice/connect.xml"

    xml_str = ET.tostring(response_el, encoding="utf-8", method="xml")
    return Response(xml_str, mimetype='text/xml')

@app.route("/voice/connect.xml")
def connect():
    forwarding_number = os.get_env['FORWARDING_NUMBER']

    response_el = ET.Element("Response")
    ET.SubElement(
        response_el, "Dial", timeout=str(DIAL_TIMEOUT)).text = forwarding_number
    return Response(ET.tostring(response_el), mimetype="text/xml")