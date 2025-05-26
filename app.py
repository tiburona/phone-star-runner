from flask import Flask, Response
import yaml
import os
from pathlib import Path
import xml.etree.ElementTree as ET
from step_key import secrets, audio_recordings

app = Flask(__name__)

CONFIG_PATH = Path(__file__).parent / "call_config.yaml"
GENERATED_CONFIG_PATH = Path(__file__).parent / "generated_call_config.yaml"


with open(CONFIG_PATH, "r") as f:
    call_config = yaml.safe_load(f)


@app.route("/")
def index():
    return "Phone Star Runner is live!"

@app.route("/voice/menu.xml")
def menu():
    
    with open(GENERATED_CONFIG_PATH, "r") as f:
        steps_config = yaml.safe_load(f)
    
    steps = steps_config.get("steps", [])

    response_el = ET.Element("Response")

    secret_counter = 0
    audio_counter = 0

    for step in steps:
        digit = step.get("digit")
        digits = step.get("digits")
        if digits:
            digit = os.get_env[secrets[secret_counter]]
            secret_counter += 1
        pause = step.get("pause", 2)

        if digit in step:
            ET.SubElement(response_el, "Pause", length=str(pause))
            ET.SubElement(response_el, "Play", digits=digit)

        if "play_audio" in step:
            audio_route = f"https://{call_config['web_host']}/audio/{audio_recordings[audio_counter]}"
            ET.SubElement(response_el, "Play").text = audio_route
            audio_counter == 1
     
    redirect_el = ET.SubElement(response_el, "Redirect")
    redirect_el.text = "/voice/connect.xml"

    xml_str = ET.tostring(response_el, encoding="utf-8", method="xml")
    return Response(xml_str, mimetype='text/xml')

@app.route("/voice/connect.xml")
def connect():
    alert_number = call_config["alert_number"]
    dial_timeout = call_config.get("dial_timeout", 30)

    response_el = ET.Element("Response")
    ET.SubElement(
        response_el, "Dial", timeout=str(dial_timeout)).text = alert_number
    return Response(ET.tostring(response_el), mimetype="text/xml")

if __name__ == "__main__":
    app.run(debug=True)