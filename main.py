import threading
import queue
import time
import sys
import subprocess
import customtkinter as ctk

import config
import AudioRecorder
from AudioRecorder import DefaultMicRecorder, DefaultSpeakerRecorder
from AudioTranscriber import AudioTranscriber
import TranscriberModels
from Teleprompter import Teleprompter
from SuggestionProvider import SuggestionProvider, load_api_key

CHROMA = config.TRANSPARENT_COLOR


def update_transcript_UI(transcriber, display, suggestion_provider):
    # суфлер: стрічка залежить тільки від питань спікера, не від твоїх слів
    display.sync("")
    suggestion_provider.maybe_update(
        transcriber.get_transcript(), display, transcriber.get_latest_speaker_ts()
    )
    display.after(100, update_transcript_UI, transcriber, display, suggestion_provider)


def main():
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except FileNotFoundError:
        print("ERROR: ffmpeg is not installed. Install it and try again.")
        return

    root = ctk.CTk()
    root.title("Ecoute Teleprompter")
    root.geometry(config.WINDOW_SIZE)
    try:
        root.configure(fg_color=CHROMA, bg=CHROMA)
    except Exception:
        root.configure(bg=CHROMA)
    root.attributes("-transparentcolor", CHROMA)
    if config.ALWAYS_ON_TOP:
        root.attributes("-topmost", True)
    root.overrideredirect(True)
    root.bind("<Escape>", lambda e: root.destroy())
    root.bind("<Double-Button-1>", lambda e: root.destroy())

    def start_move(e):
        root._dx, root._dy = e.x, e.y
    def do_move(e):
        root.geometry(f"+{root.winfo_x() + e.x - root._dx}+{root.winfo_y() + e.y - root._dy}")
    root.bind("<ButtonPress-3>", start_move)
    root.bind("<B3-Motion>", do_move)

    root.update_idletasks()
    sw = root.winfo_screenwidth()
    root.geometry(f"+{max(sw // 2 - 500, 0)}+20")

    speaker_queue = queue.Queue()
    mic_queue = queue.Queue()

    # СУФЛЕР-РЕЖИМ: слухаємо ТІЛЬКИ спікера (інтерв'юера).
    # Твій мікрофон не потрібен — стрічка показує відповідь з answers.md
    # або AI-підказку, поки ти читаєш її вголос.
    user_audio_recorder = DefaultMicRecorder(calibrate=False)
    speaker_audio_recorder = DefaultSpeakerRecorder()

    speaker_audio_recorder.record_into_queue(speaker_queue)

    model = TranscriberModels.get_model('--api' in sys.argv)

    transcriber = AudioTranscriber(user_audio_recorder.source, speaker_audio_recorder.source, model)
    transcribe = threading.Thread(target=transcriber.transcribe_audio_queue, args=(speaker_queue, mic_queue))
    transcribe.daemon = True
    transcribe.start()

    suggestion_provider = SuggestionProvider(load_api_key())

    display = Teleprompter(root, height=160)
    display.pack(fill="both", expand=True)
    display.start("ready — speak and your answer will appear here (click = next words, ESC = exit)")

    print("READY")

    update_transcript_UI(transcriber, display, suggestion_provider)

    root.mainloop()


if __name__ == "__main__":
    main()
