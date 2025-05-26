from pathlib import Path
import time
import yaml
import threading
import simpleaudio as sa
from pynput import keyboard
import subprocess
import sys

audio_path = Path("/Users/katie/Downloads/DOL_call.m4a")

# for this to work you need ffmpeg installed
def convert_m4a_to_wav(m4a_path, wav_path):
   subprocess.run([
    "ffmpeg", "-y",
    "-i", str(m4a_path),
    "-f", "wav",                 
    "-acodec", "pcm_s16le",      
    "-ar", "44100",             
    "-ac", "1",                  
    str(wav_path)
], check=True)


if audio_path.suffix == '.m4a':
    wave_path = audio_path.with_suffix('.wav')
    convert_m4a_to_wav(audio_path, wave_path )
    audio_path = wave_path

keypress_log = []
done = threading.Event()

def on_press(key):
    if done.is_set():
        return False
    try: 
        if hasattr(key, 'char'):
            t = round(time.time() - start_time, 2)
            keypress_log.append((key.char, t))
            print(f"Logged: {key.char} at {t}s")
    except AttributeError:
        pass

def play_audio():
    try:
        wave_obj = sa.WaveObject.from_wave_file(str(audio_path))
        play_obj = wave_obj.play()
        play_obj.wait_done()
        done.set()
    except Exception as e:
        print(f"Audio playback failed: {e}")

def group_and_write_yaml(keypress_log):
    grouped_steps = []
    buffer = []
    buffer_start = None
    last_ts = None

    def append_grouped_chars():
        t = buffer_start if len(grouped_steps) == 0 else grouped_steps[-1]['time']
            
        pause = round(buffer_start - t)
        grouped_steps.append({
            'pause': pause,
            'chars': ''.join(buffer),
            'time': buffer_start
        })

    for char, ts in keypress_log:
        if last_ts is None or ts - last_ts <= 2:
            if buffer_start is None:
                buffer_start = ts
            buffer.append(char)
        else:
            append_grouped_chars()
            buffer = [char]
            buffer_start = ts
        last_ts = ts

    if buffer:
        append_grouped_chars()

    steps = []
    for step in grouped_steps:
        chars = step['chars']
        if len(chars) > 1:
            entry = {"pause": step["pause"], "digits": f"__SENSITIVE__{len(chars)}"}
        elif chars[0] == 'r':
            entry = {"pause": step["pause"], "play_audio": f"__AUDIO__"}
        else:
            entry = {"pause": step["pause"], "digit": chars}

        steps.append(entry)

    output_path = Path("generated_call_config.yaml")

    with open(output_path, "w") as f:
        yaml.dump({'steps': steps}, f)

    print(f"YAML written to {output_path.name}")
    
    return output_path, steps
    
start_time = time.time()
threading.Thread(target=play_audio).start()

listener = keyboard.Listener(on_press=on_press)
listener.start()

try:
    while not done.is_set():
        time.sleep(.1)
except KeyboardInterrupt:
    print("Ctrl+C detected — exiting.")
    listener.stop()
    listener.join()
    sys.exit(0)

group_and_write_yaml(keypress_log)






