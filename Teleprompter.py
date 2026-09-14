import time
import tkinter as tk
from tkinter import font as tkfont
import config

CHROMA = config.TRANSPARENT_COLOR
LEFT_MARGIN = 80

# --- СУФЛЕР-РЕЖИМ: стрічка їде справа-наліво ПОСТІЙНО ---
SCROLL_SPEED_PX_S = 160  # швидкість руху стрічки, пікселів/секунду


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
        self._current_text = None
        self._x = float(LEFT_MARGIN)
        self._scrolling = False
        self._paused = False
        self._after_id = None
        self._last_t = 0.0
        # пауза тільки на Ctrl (лівий/правий)
        self.bind_all("<Control_L>", lambda e: self.toggle_pause())
        self.bind_all("<Control_R>", lambda e: self.toggle_pause())

    def _safe_height(self):
        h = self.winfo_height()
        return h if h > 50 else self._h

    # ---------- public ----------
    def start(self, text):
        """Показати новий текст у стрічці і поїхати справа-наліво."""
        text = (text or "").strip()
        if not text:
            self.hide()
            return
        # той самий текст уже їде стрічкою — не перезапускаємо заново
        if text == self._current_text and (self._scrolling or self._paused):
            return
        self._cancel()
        self._paused = False
        self._current_text = text
        self._label.config(text=text)
        h = self._safe_height()
        if self._win is None:
            self._win = self.create_window(0, h // 2, window=self._label, anchor="w")
        # старт: текст за правим краєм вікна
        self._x = float(self.winfo_width() or 1000)
        self._scrolling = True
        self._last_t = time.monotonic()
        self._scroll_frame()

    def hide(self):
        """Приховати стрічку (порожньо = вікно прозоре і невидиме)."""
        self._cancel()
        self._paused = False
        self._current_text = None
        if self._win:
            self.coords(self._win, self.winfo_width() or 1000, self._safe_height() // 2)
        self._label.config(text="")

    def sync(self, you_text):
        # суфлер-режим: sync нічого не робить, стрічка їде сама
        pass

    def advance(self):
        # пропустити поточний текст
        self.hide()

    def toggle_pause(self):
        if not self._label.cget("text") or self._win is None:
            return
        if self._paused:
            self._paused = False
            self._scrolling = True
            self._last_t = time.monotonic()
            self._scroll_frame()
            print("[PROMPT] resumed")
        else:
            self._paused = True
            self._scrolling = False
            print("[PROMPT] paused")

    # ---------- internal ----------
    def _scroll_frame(self):
        if not self._scrolling or self._win is None:
            return
        now = time.monotonic()
        dt = min(now - self._last_t, 0.1)
        self._last_t = now
        self._x -= SCROLL_SPEED_PX_S * dt

        text_w = self._font.measure(self._label.cget("text"))
        # коли текст повністю виїхав за лівий край — ховаємо стрічку
        if self._x + text_w < 0:
            self.hide()
            return

        self.coords(self._win, self._x, self._safe_height() // 2)
        self._after_id = self.after(15, self._scroll_frame)

    def _cancel(self):
        self._scrolling = False
        if self._after_id:
            try:
                self.after_cancel(self._after_id)
            except Exception:
                pass
            self._after_id = None
