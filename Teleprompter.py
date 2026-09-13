import difflib
import re
import time
import tkinter as tk
from tkinter import font as tkfont
import config

CHROMA = config.TRANSPARENT_COLOR
LEFT_MARGIN = 80
TAIL_EXTRA_WORDS = 8  # слова за правим краєм, які заїжджають при зсуві


def _norm(text):
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text, flags=re.UNICODE)
    return re.sub(r"\s+", " ", text).strip()


def _word_hit(wj, yn, heard):
    if f" {wj} " in yn:
        return True
    if len(wj) >= 6:
        pref = wj[:6]
        for h in heard:
            if h.startswith(pref):
                return True
    return False


class Teleprompter(tk.Canvas):
    def __init__(self, parent, height=140):
        super().__init__(parent, height=height, highlightthickness=0, bg=CHROMA)
        self._h = height
        self._label = tk.Label(
            self,
            text="",
            font=("Arial", config.TELEPROMPTER_FONT_SIZE, "bold"),
            fg="#A8FFB2",
            bg=CHROMA,
            anchor="w",
        )
        self._font = tkfont.Font(font=self._label.cget("font"))
        self._win = None
        self._words = []
        self._idx = 0
        self._phase = "idle"
        self._after_id = None
        self._shown_at = 0.0
        self._w0 = 0
        self._slide_start = 0.0
        self._last_debug_word = None
        self.bind("<Button-1>", self._on_click)

    def _on_click(self, e):
        self.focus_set()
        self.advance()

    def _safe_height(self):
        h = self.winfo_height()
        return h if h > 50 else self._h

    # ---------- public ----------
    def start(self, text):
        self._cancel()
        self._words = text.split()
        self._idx = 0
        self._show_at_margin()

    def sync(self, you_text):
        if self._phase != "idle" or not self._words:
            return
        # fallback: якщо довго мовчиш — рухаємось далі
        if config.TELEPROMPTER_WORD_TIMEOUT_MS and \
                time.monotonic() - self._shown_at > config.TELEPROMPTER_WORD_TIMEOUT_MS / 1000:
            self.advance()
            return
        yn = f" {_norm(you_text)} "
        heard = yn.split()
        # точний збіг або збіг за коренем слова (6 літер) — крапки/форми не заважають
        # перестриб максимум 3 (не даємо стрибати далеко на фальшивих збігах)
        for k in range(3):
            j = self._idx + k
            if j >= len(self._words):
                break
            wj = _norm(self._words[j])
            hit = wj and _word_hit(wj, yn, heard)
            if hit:
                total = sum(self._font.measure(self._words[self._idx + i] + " ") for i in range(k + 1))
                if k > 0:
                    print("[PROMPT] skipped 1 unrecognised word(s)")
                print(f"[PROMPT] heard '{self._words[j]}' -> advance {k + 1}")
                self._begin_slide(k + 1, total)
                break
            elif k == 0 and self._last_debug_word != self._words[j]:
                self._last_debug_word = self._words[j]
                print(f"[PROMPT] waiting for: '{self._words[j]}' | heard: ...{yn[-100:]}")

    # ---------- internal ----------
    def advance(self):
        if self._phase != "idle" or not self._words:
            return
        if self._idx >= len(self._words):
            self._finish()
            return
        self._begin_slide(1, self._font.measure(self._words[self._idx] + " "))

    def _begin_slide(self, k, total):
        self._pending_k = k
        self._w_total = total
        self._slide_start = time.monotonic()
        self._phase = "slide"
        self._slide_frame()

    def _slide_frame(self):
        if self._phase != "slide" or not self._win:
            return
        t = (time.monotonic() - self._slide_start) / max(config.SLIDE_DURATION_MS / 1000, 0.001)
        if t >= 1.0:
            self._idx += self._pending_k
            self._show_at_margin()
            return
        eased = t * t * (3 - 2 * t)
        x = LEFT_MARGIN - self._w_total * eased
        y = self._safe_height() // 2
        self.coords(self._win, x, y)
        self._after_id = self.after(15, self._slide_frame)

    def _show_at_margin(self):
        self._cancel()
        if self._idx >= len(self._words):
            self._finish()
            return
        text = " ".join(self._words[self._idx:self._idx + config.WORDS_PER_CHUNK + TAIL_EXTRA_WORDS])
        self._label.config(text=text)
        h = self._safe_height()
        if self._win:
            self.coords(self._win, LEFT_MARGIN, h // 2)
        else:
            self._win = self.create_window(LEFT_MARGIN, h // 2, window=self._label, anchor="w")
        self._phase = "idle"
        self._shown_at = time.monotonic()

    def _finish(self):
        self._words = []
        self._idx = 0
        self._phase = "idle"
        if self._win:
            self.delete(self._win)
            self._win = None

    def _cancel(self):
        if self._after_id:
            try:
                self.after_cancel(self._after_id)
            except Exception:
                pass
            self._after_id = None
