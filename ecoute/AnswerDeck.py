"""Черга відповідей між SuggestionProvider і стрічкою.

Нове питання НЕ перериває стрічку. Відповідь на нього готується на фоні й чекає
в одному місці черги; на стрічку виходить сама, коли стрічка доїхала і інтерв'юер
мовчить wait_s секунд. Усе показане лежить в історії.

Стрілки (глобально, працюють з будь-якого вікна):
    вліво  - попередня відповідь        вправо - наступна, далі те, що в черзі
    вгору  - прибрати поточну і одразу показати те, що в черзі
    вниз   - прибрати стрічку І чергу (нові питання не змішаються зі старими)

Вимикач: config.RIBBON_QUEUE = False повертає стару поведінку (main.py тоді
віддає в SuggestionProvider саму стрічку, і цей клас не бере участі).
"""
import time

TICK_MS = 200
# запас до wait_s: SuggestionProvider чекає такої ж тиші, щоб вистрілити нове питання.
# З запасом воно встигає зайняти місце в черзі раніше, ніж черга покаже старе
SILENCE_MARGIN_S = 0.5


class AnswerDeck:
    def __init__(self, ribbon, silence_fn=None, wait_s=3.0):
        self.ribbon = ribbon
        self.silence_fn = silence_fn or (lambda: 999.0)   # секунд від останнього звуку інтерв'юера
        self.wait_s = wait_s
        self.on_promote = None      # fn(gen): відповідь із черги стала головною
        self.history = []           # [[gen, text], ...] усе, що було на стрічці
        self.pos = -1               # що зараз (або востаннє) на стрічці
        self._viewing_old = False   # дивимось стару відповідь: черга чекає
        self._pending_gen = None    # місце в черзі зайняте відповіддю цього покоління
        self._pending_text = ""
        self._pending_n = 0         # скільки реплік накопичилось: цифра "+N" на стрічці
        self._last_key = 0.0
        ribbon.on_done = self._ribbon_done

    # ---------- те саме, що вміє стрічка (для main.py і SuggestionProvider) ----------
    def after(self, ms, fn, *args):
        return self.ribbon.after(ms, fn, *args)

    def sync(self, text):
        self.ribbon.sync(text)

    def hide(self):
        self.down()

    def busy(self):
        """Стрічка їде або стоїть на паузі, або в черзі щось чекає показу."""
        return self.ribbon.is_busy() or self._pending_gen is not None

    def has_pending(self):
        return self._pending_gen is not None

    def pending_text(self):
        return self._pending_text

    # ---------- запис від SuggestionProvider ----------
    def reserve(self, gen):
        """Нове питання прозвучало під час стрічки: займаємо місце в черзі одразу,
        ще до першого слова відповіді. Старіша відповідь у черзі відкидається -
        нове питання вже містить її питання (репліки склеюються в одне)."""
        if gen == self._pending_gen:
            return
        self._pending_gen = gen
        self._pending_text = ""
        self._pending_n += 1
        self._badge()

    def write(self, gen, text, restart=False, queued=False):
        """Текст відповіді покоління gen. queued=True - питання прозвучало, коли
        стрічка була зайнята."""
        entry = self._entry(gen)
        if queued and entry is None:
            if gen == self._pending_gen:
                self._pending_text = text
            return                      # інше покоління = застарілий стрім
        if entry is None or (restart and not queued):
            self.history.append([gen, text])
            self.pos = len(self.history) - 1
            self._viewing_old = False
            self.ribbon.start(text)
            return
        entry[1] = text
        if self.history[self.pos] is entry:
            self.ribbon.update_text(text)

    def _entry(self, gen):
        for entry in reversed(self.history):
            if entry[0] == gen:
                return entry
        return None

    # ---------- показ черги ----------
    def _ribbon_done(self):
        self.tick()

    def tick(self):
        """Чи час показати те, що в черзі. Викликається таймером і в кінці стрічки."""
        if (self._pending_text and not self.ribbon.is_busy() and not self._viewing_old
                and self.silence_fn() >= self.wait_s + SILENCE_MARGIN_S):
            self._promote()

    def run(self):
        """Таймер: перевіряти чергу кожні TICK_MS (запускає main.py)."""
        try:
            self.tick()
        finally:
            self.ribbon.after(TICK_MS, self.run)

    def _promote(self):
        gen, text = self._pending_gen, self._pending_text
        self._pending_gen, self._pending_text, self._pending_n = None, "", 0
        self._badge()
        self.history.append([gen, text])
        self.pos = len(self.history) - 1
        self._viewing_old = False
        print(f"[QUEUE] showing the queued answer: {text[:80]}")
        self.ribbon.start(text)
        if self.on_promote:
            self.on_promote(gen)

    def _badge(self):
        self.ribbon.set_badge(f"+{self._pending_n}" if self._pending_gen is not None else "")

    def _play(self, index):
        self.pos = index
        self._viewing_old = index < len(self.history) - 1
        self.ribbon.start(self.history[index][1])

    # ---------- стрілки ----------
    def left(self):
        """Попередня відповідь. Якщо стрічка стоїть - ще раз остання показана."""
        if not self.history:
            return
        index = self.pos - 1 if self.ribbon.is_busy() else self.pos
        print("[QUEUE] left: previous answer")
        self.ribbon.hide()
        self._play(max(0, index))

    def right(self):
        """Наступна відповідь з історії; якщо новіших немає - те, що в черзі."""
        if self.pos < len(self.history) - 1:
            print("[QUEUE] right: next answer")
            self.ribbon.hide()
            self._play(self.pos + 1)
        elif self._pending_text:
            print("[QUEUE] right: the queued answer")
            self.ribbon.hide()
            self._promote()

    def up(self):
        """Прибрати поточну стрічку; накопичене показати одразу."""
        print("[QUEUE] up: skip the current answer")
        self.ribbon.hide()
        self._viewing_old = False
        if self._pending_text:
            self._promote()

    def down(self):
        """Прибрати стрічку і чергу. Що було сказано - SuggestionProvider пам'ятає."""
        print("[QUEUE] down: ribbon and queue cleared")
        self.ribbon.hide()
        self._viewing_old = False
        self._pending_gen, self._pending_text, self._pending_n = None, "", 0
        self._badge()

    def arm_hotkeys(self):
        """Глобальні стрілки (як правий Ctrl): працюють, коли вікно суфлера не в фокусі."""
        actions = {"left": self.left, "right": self.right, "up": self.up, "down": self.down}

        def _cb(event):
            action = actions.get((event.name or "").lower())
            if action is None:
                return
            now = time.monotonic()
            if now - self._last_key < 0.25:      # затиснута клавіша не гортає пачкою
                return
            self._last_key = now
            try:
                self.ribbon.after(0, action)
            except Exception:
                pass
        try:
            import keyboard
            keyboard.on_press(_cb)
            print("[INFO] global arrows armed: left/right = history, up = skip, down = clear")
        except Exception as e:
            print(f"[WARN] global arrows unavailable ({e})")
