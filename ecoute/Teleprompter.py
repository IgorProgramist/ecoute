import time
import tkinter as tk
from tkinter import font as tkfont
import config

CHROMA = config.TRANSPARENT_COLOR
LEFT_MARGIN = 80

# --- СУФЛЕР-РЕЖИМ: стрічка їде справа-наліво ---
SCROLL_SPEED_PX_S = 170   # швидкість читання, пікселів/секунду
ENTRY_SPEED_PX_S = 500    # швидкість заїзду тексту справа до точки читання
START_HOLD_S = 0.6        # скільки стрічка стоїть на точці читання перед рухом


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
        self._landed_at = 0.0
        self._last_toggle = 0.0
        self._start_global_pause()
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
        print(f"[PROMPT] START ribbon: {text[:70]}")
        h = self._safe_height()
        if self._win is None:
            self._win = self.create_window(0, h // 2, window=self._label, anchor="w")
        # старт: текст за правим краєм вікна і ШВИДКО заїжджає до точки
        # читання (лівий край), потім сідає на швидкість читання
        self._x = float(self.winfo_width() or 1000)
        self._scrolling = True
        self._last_t = time.monotonic()
        self._scroll_frame()

    def update_text(self, text):
        """Оновити текст стрічки НА ЛЕТУ (для стрімінгу AI) — без рестарту руху."""
        text = (text or "").strip()
        if not text:
            return
        if self._win is None or not (self._scrolling or self._paused):
            self.start(text)
            return
        self._current_text = text
        self._label.config(text=text)

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

    def _start_global_pause(self):
        """Глобальний хук: Ctrl працює навіть коли вікно суфлера не в фокусі."""
        def _cb(event):
            name = (event.name or "").lower()
            if "ctrl" in name:
                try:
                    self.after(0, self.toggle_pause)
                except Exception:
                    pass
        try:
            import keyboard
            keyboard.on_press(_cb)
            print("[INFO] global pause hotkey armed: Ctrl (works anywhere)")
        except Exception as e:
            print(f"[WARN] global Ctrl pause unavailable ({e}); pause works only when window focused")

    def toggle_pause(self):
        # захист від повторів при зажатому Ctrl
        now = time.monotonic()
        if now - self._last_toggle < 0.3:
            return
        self._last_toggle = now
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

        # точка читання = СЕРЕДИНА вікна: заїзд швидко до середини,
        # коротко стоїть, потім їде у темпі читання
        reading_x = (self.winfo_width() or 1000) / 2
        if self._x > reading_x:
            self._x -= ENTRY_SPEED_PX_S * dt
            if self._x <= reading_x:
                self._landed_at = now
        elif now - self._landed_at < START_HOLD_S:
            pass  # стоїть на точці читання
        else:
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
