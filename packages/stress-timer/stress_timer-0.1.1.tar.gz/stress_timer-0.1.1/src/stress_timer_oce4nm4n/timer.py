# timer.py

import os
import time
import simpleaudio as sa
import pandas as pd
from TTS.api import TTS
from pynput import keyboard

# Always use the directory where this script is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.path.join(BASE_DIR, "tts_cache")
CSV_FILE = os.path.join(BASE_DIR, "Question-Log.csv")

def generate_clip(text, filename):
    print(f"cached clip, number: {text}")
    path = os.path.join(CACHE_DIR, filename)
    if not os.path.exists(path):
        tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
        print(f"Generating clip for: {text}")
        tts.tts_to_file(
            text=text,
            speaker="Craig Gutsy",
            language="en",
            file_path=path
        )
    return path

def play_audio(filename):
    wave = sa.WaveObject.from_wave_file(os.path.join(CACHE_DIR, filename))
    wave.play().wait_done()

def announce_time(minutes: int, seconds: int):
    if minutes > 0:
        play_audio(f"{minutes}.wav")
        play_audio("minute.wav" if minutes == 1 else "minutes.wav")
    if seconds > 0 or minutes == 0:
        play_audio(f"{seconds}.wav")
        play_audio("second.wav" if seconds == 1 else "seconds.wav")
    play_audio("spent.wav")

def log_question(question_index, elapsed, correct):
    print(f"Logging question {question_index}: {elapsed} seconds, Correct: {correct}")
    df = pd.DataFrame([{"Question": question_index, "Time (seconds)": int(elapsed), "Correct": correct.title()}])
    df.to_csv(CSV_FILE, mode='a', index=False, header=False)

def main():
    print("Initializing TTS...")
    os.makedirs(CACHE_DIR, exist_ok=True)

    # CSV setup
    if not os.path.exists(CSV_FILE):
        pd.DataFrame(columns=["Question", "Time (seconds)", "Correct"]).to_csv(CSV_FILE, index=False)

    # Preload reusable words and numbers
    words = {
        "spent": "spent.wav",
        "minute": "minute.wav",
        "minutes": "minutes.wav",
        "second": "second.wav",
        "seconds": "seconds.wav",
    }
    for word, file in words.items():
        generate_clip(word, file)

    for i in range(61):
        generate_clip(str(i), f"{i}.wav")

    question_index = 1
    running = True
    question_start = None

    print("Press SPACE to start a question, again to end it. Press 'q' to quit.")

    def on_press(key):
        nonlocal question_start, question_index, running
        if key == keyboard.Key.space:
            print("Space key pressed.")
            if question_start is None:
                question_start = time.time()
                print(f"Question {question_index} started.")
            else:
                elapsed = time.time() - question_start
                mins, secs = divmod(int(elapsed), 60)
                print(f"Question {question_index} ended. Duration: {mins}m {secs}s")
                while True:
                    correct = input("Was the question correct? (yes / no / n/a): ").strip().lower()
                    if correct.lower() in ["yes", "no", "n/a"]:
                        break
                    print("Invalid input. Try again.")
                log_question(question_index, elapsed, correct)
                question_index += 1
                question_start = None
        elif hasattr(key, 'char') and key.char == 'q':
            print("\nSession ended.")
            running = False
            return False

    # Background listener
    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    # Main announcement loop (every 1s)
    announce_interval = 1  # seconds
    last_announcement = time.time()

    try:
        while running:
            if question_start:
                elapsed = time.time() - question_start
                if time.time() - last_announcement >= announce_interval:
                    mins, secs = divmod(int(elapsed), 60)
                    announce_time(mins, secs)
                    last_announcement = time.time()
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nSession interrupted. Any in-progress question not logged.")

if __name__ == "__main__":
    main()
