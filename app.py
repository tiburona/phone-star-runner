from flask import Flask, Response, request
import yaml
import os
from pathlib import Path
import xml.etree.ElementTree as ET
from step_key import secrets, audio_recordings
from start_ngrok import get_ngrok_url

app = Flask(__name__)

CONFIG_PATH = Path(__file__).parent / "call_config.yaml"
STEP_CONFIG_PATH = Path(__file__).parent / "generated_call_config.yaml"



with open(CONFIG_PATH, "r") as f:
    call_config = yaml.safe_load(f)

@app.before_request
def log_request():
    print(f"Incoming request: {request.method} {request.url}")

@app.route("/")
def index():
    return "Phone Star Runner is live!"

@app.route("/health")
def health():
    return "OK", 200

# @app.route("/voice/menu.xml")
# def menu():
#     wss_url = get_ngrok_url('wss')
#     with open(STEP_CONFIG_PATH, "r") as f:
#         steps_config = yaml.safe_load(f)

#     steps = steps_config.get("steps", [])

#     response_el = ET.Element("Response")

#     start_el = ET.SubElement(response_el, "Start")

#     print(f"Use this stream URL: {wss_url}")
#     ET.SubElement(start_el, "Stream", url=wss_url)

#     secret_counter = 0
#     audio_counter = 0

#     for step in steps:
#         pause = str(step["pause"])

#         if "digits" in step:
#             secret_value = os.environ[secrets[secret_counter]]
#             secret_counter += 1
#             ET.SubElement(response_el, "Pause", length=pause)
#             ET.SubElement(response_el, "Play", digits=secret_value)

#         elif "digit" in step:
#             ET.SubElement(response_el, "Pause", length=pause)
#             ET.SubElement(response_el, "Play", digits=step["digit"])

#         elif "play_audio" in step:
#             audio_route = f"{call_config['web_host']}/audio/{audio_recordings[audio_counter]}"
#             audio_counter += 1
#             ET.SubElement(response_el, "Play").text = audio_route

#     # redirect_el = ET.SubElement(response_el, "Redirect")
#     # redirect_el.text = "/voice/connect.xml"

#     xml_str = ET.tostring(response_el, encoding="utf-8", method="xml")
#     return Response(xml_str, mimetype='text/xml')

@app.route("/voice/menu.xml", methods=["GET", "POST"])
def menu():
    print("🚨 /voice/menu.xml was hit!")
    response_el = ET.Element("Response")
    ET.SubElement(response_el, "Say").text = "Hello. Testing menu response."
    xml_str = ET.tostring(response_el, encoding="utf-8", method="xml")
    return Response(xml_str, mimetype='text/xml')

@app.route("/voice/connect.xml")
def connect():
    forwarding_number = os.get_env['FORWARDING_NUMBER']
    dial_timeout = call_config.get("dial_timeout", 30)

    response_el = ET.Element("Response")
    ET.SubElement(
        response_el, "Dial", timeout=str(dial_timeout)).text = forwarding_number
    return Response(ET.tostring(response_el), mimetype="text/xml")