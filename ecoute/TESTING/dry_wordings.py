"""Безкоштовний масовий тест: кожне готове питання "What is X?" з answers.md
ставиться різними словами, і має вийти ТА САМА готова відповідь.

    py -3.14 TESTING\\dry_wordings.py            # підсумок і перші 40 промахів
    py -3.14 TESTING\\dry_wordings.py all        # усі промахи

Без звуку, без AI, без грошей. Не бачить, як whisper розчує голос.
"""
import io
import os
import re
import sys
from collections import Counter
from contextlib import redirect_stdout

ECOUTE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ECOUTE)
sys.path.insert(0, ECOUTE)
with redirect_stdout(io.StringIO()):
    import SuggestionProvider as SP
    sp = SP.SuggestionProvider(None)

# {x} = те, про що питають, разом з артиклем: "a Prefab", "the Safe Area", "Addressables"
WORDINGS = [
    "What {be} {x}?",
    "Tell me how you understand what {x} {be}.",
    "What does {x} mean to you?",
    "In your own words, what {be} {x}?",
    "How would you describe {x}?",
    "Can you explain what {x} {be}?",
    "What do you understand by {x}?",
    "So, what {be} {x}, in simple words?",
    "Explain to me what {x} {be}.",
    "Okay, next question. What {be} {x}?",
    "Could you tell me what {x} {be}?",
    "What {be} {x}, as you see it?",
]
PART_WORDINGS = [
    "What parameters does {x} have?",
    "What settings does {x} have?",
    "What are the main properties of {x}?",
    "What types of {x} are there?",
]
WHAT_RE = re.compile(r"^What (is|are) (.+)\?$")


def main():
    show_all = "all" in sys.argv[1:]
    total, misses = 0, []
    per_wording = Counter()
    subjects = 0
    for question, _ in sp.prepared:
        m = WHAT_RE.match(question)
        # лише прості визначення: без "difference between", без складених питань
        if not m or "difference" in question.lower() or "," in question or " and " in question:
            continue
        subjects += 1
        be, x = m.group(1), m.group(2)
        for wording in WORDINGS:
            heard = wording.format(be=be, x=x)
            total += 1
            hit = sp._best_prepared(heard) or sp._tail_prepared(heard)
            plan = sp._how_to_plan(heard, hit)
            got = hit[0] if hit else "-"
            if plan:
                got += "  [+AI]" if plan == "glue" else "  [в AI]"
            if got != question:
                misses.append((heard, question, got))
                per_wording[wording] += 1
    # другий блок: питають про ЧАСТИНУ X - визначення самого X не має виходити
    part_total, part_misses = 0, []
    for question, _ in sp.prepared:
        m = WHAT_RE.match(question)
        if not m or "difference" in question.lower() or "," in question or " and " in question:
            continue
        if SP._PIECE_RE.search(question.lower()):
            continue    # готове питання саме про параметри ("What is an Animator Parameter?")
        x = m.group(2)
        if len(x.split()) > 4:
            continue    # не назва речі, а ціла фраза ("the first thing you check in ...")
        for wording in PART_WORDINGS:
            heard = wording.format(x=x)
            part_total += 1
            hit = sp._best_prepared(heard) or sp._tail_prepared(heard)
            if hit and hit[0] == question:
                part_misses.append((heard, "не визначення цілого", hit[0]))
    # третій блок: КОЖНЕ готове питання, як його скаже жива людина - зі вступом,
    # з хвостом, без розділових знаків (так його віддає whisper)
    talk_total, talk_misses = 0, []
    talk_per = Counter()
    for question, _ in sp.prepared:
        bare = re.sub(r"[?.,!]", "", question).lower()
        for name, heard in (
            ("без знаків і великих літер", bare),
            ("So, ...", "So, " + question),
            ("Alright. ...", "Alright. " + question),
            ("Um, ...", "Um, " + question[0].lower() + question[1:]),
            ("... Can you explain?", question + " Can you explain?"),
            ("Let's move on. ...", "Let's move on. " + question),
        ):
            talk_total += 1
            hit = sp._best_prepared(heard) or sp._tail_prepared(heard)
            got = hit[0] if hit else "-"
            if got != question:
                talk_misses.append((heard, question, got))
                talk_per[name] += 1
    print(f"усі готові питання в розмовній обгортці: {talk_total}, влучили: "
          f"{talk_total - len(talk_misses)}, промахів: {len(talk_misses)}")
    for name, n in talk_per.most_common():
        print(f"  {n:4d}  {name}")
    misses += talk_misses
    print(f"визначень у answers.md: {subjects}, формулювань на кожне: {len(WORDINGS)}")
    print(f"перевірок: {total}, влучили: {total - len(misses)}, промахів: {len(misses)}")
    print(f"питань про частину: {part_total}, правильно пішли в AI або в іншу відповідь: "
          f"{part_total - len(part_misses)}, показали визначення цілого: {len(part_misses)}")
    misses += part_misses
    if per_wording:
        print("\nпромахи за формулюванням:")
        for wording, n in per_wording.most_common():
            print(f"  {n:4d}  {wording}")
    if misses:
        print("\nпромахи (почуте -> мало бути -> вийшло):")
        for heard, want, got in misses if show_all else misses[:40]:
            print(f"  {heard}\n      мало: {want}\n      є:    {got}")
    return 1 if misses else 0


if __name__ == "__main__":
    sys.exit(main())
