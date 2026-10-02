import threading
import queue
import time
import sys
import os
import subprocess
import customtkinter as ctk

import config
import AudioRecorder
from AudioRecorder import DefaultMicRecorder, DefaultSpeakerRecorder, start_keepalive
from AudioTranscriber import AudioTranscriber
import TranscriberModels
from Teleprompter import Teleprompter
from SuggestionProvider import SuggestionProvider, load_api_key

CHROMA = config.TRANSPARENT_COLOR


class _Tee:
    """Дублює консольний вивід у last_run.log — щоб логи завжди можна було прочитати."""
    def __init__(self, path):
        self.file = open(path, "a", encoding="utf-8", buffering=1)
        self.stdout = sys.stdout

    def write(self, s):
        self.stdout.write(s)
        self.file.write(s)

    def flush(self):
        self.stdout.flush()
        self.file.flush()


sys.stdout = _Tee(os.path.join(os.path.dirname(os.path.abspath(__file__)), "last_run.log"))
sys.stderr = _Tee(os.path.join(os.path.dirname(os.path.abspath(__file__)), "last_run.log"))


class IdleGate:
    """Суфлер спить, поки ти не натиснеш ENTER у консолі.

    Поки інтерв'ю українською — стрічка нічого не показує.
    ENTER = перейти в англійський режим (активувати суфлер).
    Другий ENTER = знову в очікування.
    При активації ВСЕ почуте раніше стирається — реагуємо
    тільки на те, що прозвучить ПІСЛЯ ENTER.
    """

    def __init__(self):
        self.active = False
        self.transcriber = None
        self.provider = None

    def _reset_history(self):
        if self.transcriber is not None:
            self.transcriber.transcript_data["Speaker"].clear()
            self.transcriber.clear_speaker_buffer()
            self.transcriber.audio_sources["Speaker"]["new_phrase"] = True
        if self.provider is not None:
            self.provider.last_question = None
            self.provider.last_ts = None
            self.provider.last_shown_answer = None
            self.provider._last_fired_text = None

    def start(self, display, transcriber, provider):
        self.transcriber = transcriber
        self.provider = provider

        def watch():
            # якщо консоль недоступна (stdin перенаправлений / планувальник)
            # — суфлер активується одразу, щоб не слухати "в нічку"
            try:
                interactive = sys.stdin is not None and sys.stdin.isatty()
            except Exception:
                interactive = False
            if not interactive:
                self.active = True
                print("[CONTROL] console not available -> суфлер АКТИВНИЙ одразу")
                return
            while True:
                try:
                    input()
                except (EOFError, OSError):
                    time.sleep(0.5)
                    continue
                self.active = not self.active
                if self.active:
                    # стираємо почуте ДО активації
                    self._reset_history()
                    print("[CONTROL] ENTER -> АНГЛІЙСЬКИЙ РЕЖИМ АКТИВНИЙ (слухаю тільки нове)")
                else:
                    print("[CONTROL] ENTER -> ОЧІКУВАННЯ (суфлер спить, нічого не показує)")
                    try:
                        display.after(0, display.hide)
                    except Exception:
                        pass
        threading.Thread(target=watch, daemon=True).start()


def update_transcript_UI(transcriber, display, suggestion_provider, gate):
    # суфлер: стрічка залежить тільки від питань спікера, не від твоїх слів
    display.sync("")
    if gate.active:
        suggestion_provider.maybe_update(
            transcriber.get_current_speaker_phrase(), display,
            transcriber.get_speaker_phrase_epoch(),
            transcriber.get_speaker_last_ts()
        )
    display.after(100, update_transcript_UI, transcriber, display, suggestion_provider, gate)


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
    user_audio_recorder = DefaultMicRecorder(calibrate=False, probe=False)
    speaker_audio_recorder = DefaultSpeakerRecorder()

    model = TranscriberModels.get_model('--api' in sys.argv)

    transcriber = AudioTranscriber(user_audio_recorder.source, speaker_audio_recorder.source, model)
    transcribe = threading.Thread(target=transcriber.transcribe_audio_queue, args=(speaker_queue, mic_queue))
    transcribe.daemon = True
    transcribe.start()

    # слухання стартує ПІСЛЯ транскрайбера — перше питання не втрачається
    if '--keepalive' in sys.argv:
        start_keepalive()
    speaker_audio_recorder.record_into_queue(speaker_queue)

    suggestion_provider = SuggestionProvider(load_api_key(), transcriber=transcriber)

    display = Teleprompter(root, height=160)
    display.pack(fill="both", expand=True)
    display.hide()

    gate = IdleGate()
    gate.start(display, transcriber, suggestion_provider)
    if '--active' in sys.argv:
        gate.active = True
        print("[CONTROL] --active: суфлер активований одразу (без ENTER)")
    print("[CONTROL] РЕЖИМ ОЧІКУВАННЯ: стрічка нічого не показує.")
    print("[CONTROL] Натисни ENTER у консолі, коли інтерв'ю перейде на англійську.")
    print("[CONTROL] Наступний ENTER поверне в очікування.")

    print("READY")

    update_transcript_UI(transcriber, display, suggestion_provider, gate)

    root.mainloop()


if __name__ == "__main__":
    main()
