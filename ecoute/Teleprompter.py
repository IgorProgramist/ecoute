import os
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
CHUNK_WORDS = 120         # скільки слів стрічки вантажиться за раз (довгі тексти
                          # цілим лейблом ламають tkinter)


def _is_pause_key(name):
    """Пауза стрічки = тільки правий Ctrl (бібліотека keyboard називає його 'right ctrl')."""
    return (name or "").lower() in ("right ctrl", "ctrl right", "right control")


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
        self._done_text = None   # текст, який стрічка щойно довезла до кінця
        self._full_words = []
        self._chunk_start = 0
        self._x = float(LEFT_MARGIN)
        self._scrolling = False
        self._paused = False
        self._after_id = None
        self._last_t = 0.0
        self._landed_at = 0.0
        self._last_toggle = 0.0
        self.on_done = None      # fn(): стрічка довезла текст до кінця (слухає AnswerDeck)
        self._badge = None       # "+N" у кутку: скільки реплік чекає в черзі
        self._start_global_pause()
        self._start_global_hotkeys()

    def show_cover_letter(self):
        """Кнопка '1' (глобально): показати текст CoverLetter.md у стрічці."""
        try:
            path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "CoverLetter.md")
            with open(path, encoding="utf-8") as f:
                text = f.read()
            # одна безперервна лінія: переноси рядків/абзаци ламають рендер
            # стрічки у кілька рядків
            text = " ".join(text.split())
            if text:
                self.start(text)
                print("[PROMPT] CoverLetter loaded into ribbon")
            else:
                print("[WARN] CoverLetter.md is empty")
        except Exception as e:
            print(f"[WARN] CoverLetter load failed: {e!r}")

    def _start_global_hotkeys(self):
        """Глобальна кнопка '1' — показати CoverLetter (працює з будь-якого вікна)."""
        def _cb(event):
            name = (event.name or "").lower()
            if name == "1":
                try:
                    self.after(0, self.show_cover_letter)
                except Exception:
                    pass
        try:
            import keyboard
            keyboard.on_press(_cb)
            print("[INFO] global hotkey armed: 1 = show CoverLetter")
        except Exception as e:
            print(f"[WARN] global '1' hotkey unavailable ({e})")
        # пауза тільки на ПРАВОМУ Ctrl (глобальний хук нижче ловить його з будь-якого
        # вікна). Alt прибрано: Alt+Tab на інтерв'ю зупиняв або запускав стрічку
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
        self._full_words = text.split()
        self._chunk_start = 0
        self._load_chunk()

    def _load_chunk(self):
        """Вантажить наступний кусок тексту (CHUNK_WORDS слів)."""
        self._cancel()
        chunk = self._full_words[self._chunk_start:self._chunk_start + CHUNK_WORDS]
        if not chunk:
            self.hide()
            return
        chunk_text = " ".join(chunk)
        self._label.config(text=chunk_text)
        print(f"[PROMPT] START ribbon: {chunk_text[:80]}")
        h = self._safe_height()
        if self._win is None:
            self._win = self.create_window(0, h // 2, window=self._label, anchor="w")
        # старт: текст за правим краєм вікна і ШВИДКО заїжджає до точки читання
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
            # стрічка вже доїхала, а AI дописав хвіст до ТОГО Ж тексту:
            # показуємо лише нове, а не всю відповідь з початку
            done = self._done_text
            if done and text.startswith(done) and text[len(done):].strip():
                text = text[len(done):]
            self.start(text)
            return
        self._current_text = text
        self._full_words = text.split()
        # текст росте на льоту: лейбл лишається на ПОТОЧНОМУ шматку. Раніше тут
        # ставився весь текст з нуля - на відповіді довшій за CHUNK_WORDS
        # останні слова їхали двічі, а на другому шматку стрічка стрибала назад
        chunk = self._full_words[self._chunk_start:self._chunk_start + CHUNK_WORDS]
        self._label.config(text=" ".join(chunk))

    def hide(self):
        """Приховати стрічку (порожньо = вікно прозоре і невидиме)."""
        self._cancel()
        self._paused = False
        self._current_text = None
        self._done_text = None
        self._full_words = []
        self._chunk_start = 0
        if self._win:
            self.coords(self._win, self.winfo_width() or 1000, self._safe_height() // 2)
        self._label.config(text="")

    def is_busy(self):
        """Стрічка їде або стоїть на паузі."""
        return self._scrolling or self._paused

    def set_badge(self, text):
        """Маленька позначка в правому верхньому куті ("+1" = у черзі чекає відповідь)."""
        if self._badge is None:
            self._badge = self.create_text(0, 4, text="", anchor="ne", fill="#FFD479",
                                           font=("Arial", 14, "bold"))
        self.coords(self._badge, (self.winfo_width() or 1000) - 8, 4)
        self.itemconfig(self._badge, text=text or "")

    def sync(self, you_text):
        # суфлер-режим: sync нічого не робить, стрічка їде сама
        pass

    def advance(self):
        # пропустити поточний текст
        self.hide()

    def _start_global_pause(self):
        """Глобальний хук: правий Ctrl працює навіть коли вікно суфлера не в фокусі."""
        def _cb(event):
            if _is_pause_key(event.name):
                try:
                    self.after(0, self.toggle_pause)
                except Exception:
                    pass
        try:
            import keyboard
            keyboard.on_press(_cb)
            print("[INFO] global pause hotkey armed: right Ctrl (works anywhere)")
        except Exception as e:
            print(f"[WARN] global right Ctrl pause unavailable ({e}); pause works only when window focused")

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
        # коли текст повністю виїхав за лівий край — наступний кусок або ховаємось
        if self._x + text_w < 0:
            self._chunk_start += CHUNK_WORDS
            if self._chunk_start < len(self._full_words):
                self._load_chunk()
            else:
                done = self._current_text
                self.hide()
                self._done_text = done
                print("[PROMPT] ribbon done")     # тест-ранер чекає цей рядок перед наступним питанням
                if self.on_done:
                    self.on_done()
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
