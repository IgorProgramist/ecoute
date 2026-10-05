"""Жива перевірка черги БЕЗ звуку: справжня стрічка, справжній AI, питання за розкладом.

    py -3.14 TESTING\\queue_demo.py

Сценарій (секунди від старту):
     1  "How do you set up anchors for different aspect ratios?"   -> AI, іде на стрічку
     7  "What is a Canvas?"            інтерв'юер перебив          -> у чергу
    10  "And what is overdraw?"        ще одна репліка             -> склеюється з попередньою
    далі стрічка доїжджає, 3 с тиші, і черга виходить сама
    +   стрілка вліво (попередня відповідь), стрілка вправо (назад до нової)
Усе видно у вікні стрічки і в рядках [QUEUE] / [PROMPT] / [AI] у консолі.
Коштує 1-2 запити до AI.
"""
import os
import sys
import time
import tkinter as tk

ECOUTE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ECOUTE)
sys.path.insert(0, ECOUTE)

import config  # noqa: E402
from AnswerDeck import AnswerDeck  # noqa: E402
from SuggestionProvider import SuggestionProvider, load_api_key  # noqa: E402
from Teleprompter import Teleprompter  # noqa: E402

T0 = time.monotonic()
last_spoken = [T0 - 100.0]


def stamp(msg):
    print(f"[DEMO {time.monotonic() - T0:5.1f}s] {msg}", flush=True)


def main():
    config.RIBBON_QUEUE = True
    # вікно таке саме, як у main.py: прозоре, поверх усіх вікон, без рамки.
    # Закрити: Esc або подвійний клік
    chroma = config.TRANSPARENT_COLOR
    root = tk.Tk()
    root.title("queue demo")
    root.geometry(config.WINDOW_SIZE)
    root.configure(bg=chroma)
    root.attributes("-transparentcolor", chroma)
    if config.ALWAYS_ON_TOP:
        root.attributes("-topmost", True)
    root.overrideredirect(True)
    root.bind("<Escape>", lambda e: root.destroy())
    root.bind("<Double-Button-1>", lambda e: root.destroy())
    root.update_idletasks()
    root.geometry(f"+{max(root.winfo_screenwidth() // 2 - 500, 0)}+20")
    ribbon = Teleprompter(root, height=160)
    ribbon.pack(fill="both", expand=True)
    provider = SuggestionProvider(load_api_key())
    deck = AnswerDeck(ribbon, silence_fn=lambda: time.monotonic() - last_spoken[0],
                      wait_s=config.QUEUE_SILENCE_S)
    deck.on_promote = provider.promoted
    deck.arm_hotkeys()          # справжні стрілки працюють і тут
    deck.run()

    def ask(epoch, question):
        last_spoken[0] = time.monotonic()
        stamp(f"INTERVIEWER: {question}")
        provider.maybe_update(question, deck, phrase_epoch=epoch)

    def key(name, action):
        stamp(f"KEY {name}")
        action()

    if "thinking" in sys.argv:
        # другий сценарій: інтерв'юер додає репліку, поки AI ще ДУМАЄ над першим питанням
        # (до першого слова 2-5 с). Перша відповідь має вийти, друга - стати в чергу
        root.after(1000, ask, 1, "What is the Emission module of a Particle System?")
        root.after(2200, ask, 2, "What is a Canvas?")
        root.after(45000, lambda: (stamp("END"), root.destroy()))
        root.mainloop()
        return
    root.after(1000, ask, 1, "How do you set up anchors for different aspect ratios?")
    root.after(7000, ask, 2, "What is a Canvas?")
    root.after(10000, ask, 3, "And what is overdraw?")
    # стрічка з відповіддю про anchors їде ~35-50 с; далі черга, далі стрілки
    root.after(70000, key, "left", deck.left)
    root.after(76000, key, "right", deck.right)
    root.after(84000, key, "down", deck.down)
    root.after(86000, lambda: (stamp("END"), root.destroy()))
    root.mainloop()


if __name__ == "__main__":
    main()
