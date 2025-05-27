import asyncio
import base64
import websockets
import pyaudio

CHANNELS = 1
SAMPLE_WIDTH = 1
FRAME_RATE = 8000
FORMAT = pyaudio.paInt16

p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=FRAME_RATE,
                output=True)

async def handle_stream(websocket):
    print("WebSocket connection established.")
    try:
        async for message in websocket:
            if not message:
                continue

            if isinstance(message, bytes):
                continue

            import json
            data = json.loads(message)

            if data.get("event") == "media":
                payload = data["media"]["payload"]
                raw_audio = base64.b64decode(payload)
                stream.write(raw_audio)
            elif data.get("event") == "stop":
                print("Stream ended.")
                break

    finally:
        print("Closing audio stream.")
        stream.stop_stream()
        stream.close()
        p.terminate()


async def streaming_server():
    print("Listening on ws://0.0.0.0:8765")
    async with websockets.serve(handle_stream, "0.0.0.0", 8765):
        await asyncio.Future()  

if __name__ == "__main__":
    asyncio.run(streaming_server())