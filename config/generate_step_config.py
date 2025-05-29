from pathlib import Path
import time
import yaml
import threading
import simpleaudio as sa

from pynput import keyboard
import subprocess

from public_config import ORIG_AUDIO_PATH, STEP_CONFIG_FNAME

audio_path = Path(ORIG_AUDIO_PATH)

done = threading.Event()

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
# Will be set when the user presses Enter
start_time = None


def on_press(key):
    """
    First Enter press marks the start of the IVR; subsequent digit keys are logged
    relative to that moment.
    """
    global start_time
    if done.is_set():
        return False

    # 1) First Enter -> set the reference time
    if start_time is None:
        if key == keyboard.Key.enter or getattr(key, "char", None) in ("\r", "\n"):
            start_time = time.time()
            keypress_log.append(('Enter', start_time))
            print(">>> Enter received, logging started")
        # Ignore all other keys until the start marker
        return

    # 2) After start_time is set, record any printable character keys
    if hasattr(key, "char") and key.char is not None:
        t = round(time.time(), 2)
        keypress_log.append((key.char, t))
        print(f"Logged: {key.char} at {t}s")

def play_audio():
    try:
        wave_obj = sa.WaveObject.from_wave_file(str(audio_path))
        play_obj = wave_obj.play()
        play_obj.wait_done()
        print("\nAudio finished, setting done event")
        done.set()
        print("Audio thread completed")
    except Exception as e:
        print(f"Audio playback failed: {e}")

def group_and_write_yaml(keypress_log):
    grouped_steps = []
    buffer = []
    buffer_start = None

    last_ts = None

    def append_grouped_chars():
        t = start if len(grouped_steps) == 0 else grouped_steps[-1]['time']
            
        pause = round(buffer_start - t)
        grouped_steps.append({
            'pause': pause,
            'chars': ''.join(buffer),
            'time': buffer_start
        })

    start = keypress_log[0][1]

    for char, ts in keypress_log[1:]:       
            
        if buffer_start is None or ts - last_ts <= 2:
            if buffer_start is None:
                buffer_start = ts
            buffer.append(char)
        else:
            if buffer:
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

    script_dir = Path(__file__).resolve().parent   # folder that contains this script
    output_path = script_dir / STEP_CONFIG_FNAME    

    with open(output_path, "w") as f:
        yaml.dump({'steps': steps}, f)

    print(f"YAML written to {output_path.name}")
    
    return output_path, steps

print("The recording will start playing.")
print("Press Enter as soon as you hear sound on the recording; your key pressed will be logged after that.")

listener = keyboard.Listener(on_press=on_press)
listener.start()

threading.Thread(target=play_audio, daemon=True).start()

done.wait()                            
listener.stop()
listener.join(timeout=0.5)

group_and_write_yaml(keypress_log)
