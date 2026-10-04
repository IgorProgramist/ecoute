"""Безкоштовна перевірка: що отримає кожне питання, БЕЗ звуку і БЕЗ запиту до AI.

    py -3.14 TESTING\\dry_check.py TESTING\\test_questions.md
    py -3.14 TESTING\\dry_check.py "What is the Emission module of a Particle System?"

Для кожного питання показує:
    ГОТОВА   - яка готова відповідь з answers.md вийде на стрічку (або "-" = піде в AI)
    КУКБУКС  - яку тему з actions.md отримає AI (або "-")
    РОЗДІЛИ  - які розділи знань з answers.md отримає AI

Чого НЕ бачить: як whisper розчує голос, що саме напише AI, швидкість.
Це перевіряє лише голосовий прогін (qa_runner2.ps1).
"""
import io
import os
import sys
from contextlib import redirect_stdout

ECOUTE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ECOUTE)
sys.path.insert(0, ECOUTE)
with redirect_stdout(io.StringIO()):
    import SuggestionProvider as SP
    sp = SP.SuggestionProvider(None)


def read_questions(args):
    for arg in args:
        if not os.path.isfile(arg):
            yield arg
            continue
        with open(arg, encoding="utf-8-sig") as f:
            for line in f:
                line = line.strip()
                if line.startswith("- "):
                    yield line[2:].strip()
                elif line[:1].isdigit() and ". " in line[:5]:
                    yield line.split(". ", 1)[1].strip()


def sections(question):
    sent = sp._relevant_info(question)
    return [t.rstrip(":")[:38] for t, x in sp.info_sections if x and x.strip()[:60] in sent]


def main():
    questions = list(read_questions(sys.argv[1:]))
    if not questions:
        print(__doc__)
        return 1
    to_ai = 0
    for q in questions:
        sp._last_action = None
        hit = sp._best_prepared(q) or sp._tail_prepared(q)
        plan = sp._how_to_plan(q, hit)
        topic = sp._relevant_action(q)
        if hit and plan == "glue":
            ready = hit[0] + "  + AI дописує кроки"
        elif hit and plan != "drop":
            ready = hit[0]
        else:
            ready = "-"
            to_ai += 1
        print(q)
        print("   ГОТОВА :", ready)
        print("   КУКБУКС:", topic[0].split(" (")[0] if topic else "-")
        if ready == "-" or "AI" in ready:
            print("   РОЗДІЛИ:", "; ".join(sections(q)) or "-")
    print()
    print(f"питань {len(questions)}: готова відповідь {len(questions) - to_ai}, в AI {to_ai}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
