"""Prepared-answer matcher: the wrong fires recorded on 2026-10-03 must not come back.

Run from the ecoute folder:  python -m pytest TESTING/test_matcher.py -q
"""
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

import SuggestionProvider as SP  # noqa: E402


@pytest.fixture(scope="module")
def sp():
    return SP.SuggestionProvider(None)


def title(sp, heard):
    hit = sp._best_prepared(heard)
    return hit[0] if hit else None


@pytest.mark.parametrize("heard, want", [
    # whisper splits the words the file writes as one
    ("What is the difference between mesh renderer and skinned mesh renderer?",
     "What is the difference between MeshRenderer and SkinnedMeshRenderer?"),
    ("What is a game object?", "What is a GameObject?"),
    ("What is the difference between transform and rect transform?",
     "What is the difference between Transform and RectTransform?"),
    ("What are MIP maps?", "What is a Mipmap?"),
    # spoken lead-ins and rephrasings
    ("Can you tell me what a game object is?", "What is a GameObject?"),
    ("So what is a component in unity?", "What is a Component?"),
    ("What is a prefab and why do we use it?", "What is a Prefab?"),
    ("What is a pivot on a sprite?", "What is a Pivot?"),
    ("Why does a scene need an event system?", "What is an EventSystem?"),
    ("What is URP?", "What is URP?"),
])
def test_finds_the_right_prepared_answer(sp, heard, want):
    assert title(sp, heard) == want


@pytest.mark.parametrize("heard", [
    # three shared words with an unrelated prepared Q used to be enough to fire it
    "The game runs fine in the editor but lags on a weak phone, where do you start, "
    "which tools do you use, and what do you check first?",
    "What does the SRP batcher do? Does it reduce draw calls? And how is it different from normal batching?",
    "What is your salary expectation?",
    # one word swapped in a short question = another topic (was answered as URP)
    "What is the built-in render pipeline?",
    # 2-3 questions in one: a single prepared answer covered only one part
    "What is a prefab? What is a prefab variant? And when would you use a variant instead of a new prefab?",
    "What is an animator state, what is a transition, and why can a transition feel late?",
])
def test_unsure_question_goes_to_ai(sp, heard):
    assert title(sp, heard) is None


@pytest.mark.parametrize("heard, parts, words", [
    ("What is a draw call?", 1, 40),
    ("What is a prefab and why do we use it?", 1, 40),
    ("What is post processing, and is it expensive on mobile?", 2, 60),
    ("What is overdraw, what is fill rate, and how exactly do you reduce overdraw?", 3, 80),
    ("What is transparency? What is alpha clipping? And does additive blending reduce overdraw?", 3, 80),
    ("The game lags, where do you start, which tools do you use, what do you check, and how do you fix it?", 4, 80),
])
def test_ai_word_limit_grows_with_the_question(heard, parts, words):
    assert SP._question_parts(heard) == parts
    assert SP._max_words(heard) == words


class _Display:
    def __init__(self):
        self.shown = []

    def after(self, _ms, _fn, text):
        self.shown.append(text)

    start = update_text = None


def _ask(sp, heard, display):
    sp._last_fired_text = None
    sp.maybe_update(heard, display)


def test_same_answer_for_a_different_question_is_not_silent(sp, monkeypatch):
    """Recorded: "What are addressables?" then "What is an addressable screw?"
    (whisper for "Addressables Group") hit the answer just shown -> nothing at all."""
    asked_ai = []
    monkeypatch.setattr(sp, "enabled", True)
    monkeypatch.setattr(sp, "_fetch", lambda q, d, g: asked_ai.append(q))
    monkeypatch.setattr(SP.threading, "Thread", lambda target, args, daemon: type(
        "T", (), {"start": lambda self: target(*args)})())
    d = _Display()
    _ask(sp, "What are addressables?", d)
    assert len(d.shown) == 1 and not asked_ai
    _ask(sp, "What are addressables?", d)          # the same question again
    assert len(d.shown) == 1 and not asked_ai      # ribbon is not restarted
    sp._gen += 1
    _ask(sp, "What is an addressable screw?", d)   # a different question
    assert asked_ai == ["What is an addressable screw?"]


def test_every_prepared_question_finds_itself(sp):
    for lead in ("", "Can you tell me ", "Okay, next question. "):
        bad = [q for q, a in sp.prepared if (sp._best_prepared(lead + q) or ("", ""))[1] != a]
        assert not bad, (lead, bad[:5])
