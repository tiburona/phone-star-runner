from flask import Flask, Response
import yaml
from pathlib import Path
import xml.etree.ElmentTree as ET

app = Flask(__name__)

CONFIG_PATH = Path(__file__).parent / "call_config.yaml"

@app.route("/voice/menu.xml")
def menu():
    
    with open(CONFIG_PATH, "r") as f:
        call_config = yaml.safe_load(f)
    
    steps = call_config.get("steps", [])

    response_el = ET.Element("Response")

    for step in steps:
        digit = step.get("digit")
        pause = step.get("pause", 2)

        if digit in step:
            ET.SubElement(response_el, "Pause", length=str(pause))
            ET.SubElement(response_el, "Play", digits=digit)
        if "play_audio" in step:
            ET.SubElement(response_el, "Play").text = f"https://yourdomain.com/audio/{step['play_audio']}"
   
        
    redirect_el = ET.SubElement(response_el, "Redirect")
    redirect_el.text = "/voice/connect.xml"

    xml_str = ET.tostring(response_el, encoding="utf-8", method="xml")
    return Response(xml_str, mimetype='text/xml')

@app.route("/voice/connect.xml")
def connect():
    with open(CONFIG_PATH) as f:
        call_config = yaml.safe_load(f)
    alert_number = call_config["alert_number"]
    dial_timeout = call_config.get("dial_timeout", 30)

    response_el = ET.Element("Response")
    ET.SubElement(
        response_el, "Dial", timeout=str(dial_timeout)).text = alert_number
    return Response(ET.tostring(response_el), mimetype="text/xml")

if __name__ == "__main__":
    app.run(debug=True)