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
])
def test_unsure_question_goes_to_ai(sp, heard):
    assert title(sp, heard) is None


def test_every_prepared_question_finds_itself(sp):
    for lead in ("", "Can you tell me ", "Okay, next question. "):
        bad = [q for q, a in sp.prepared if (sp._best_prepared(lead + q) or ("", ""))[1] != a]
        assert not bad, (lead, bad[:5])
