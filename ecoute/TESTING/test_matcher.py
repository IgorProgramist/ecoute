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
    # a prepared Q with one content word must not catch a question that only ends with it
    "Tell me about Has Exit Time.",
    "What is Has Exit Time?",
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
    monkeypatch.setattr(sp, "_fetch", lambda q, d, g, **kw: asked_ai.append(q))
    monkeypatch.setattr(SP.threading, "Thread", lambda target, args, kwargs, daemon: type(
        "T", (), {"start": lambda self: target(*args, **kwargs)})())
    d = _Display()
    _ask(sp, "What are addressables?", d)
    assert len(d.shown) == 1 and not asked_ai
    _ask(sp, "What are addressables?", d)          # the same question again
    assert len(d.shown) == 1 and not asked_ai      # ribbon is not restarted
    sp._gen += 1
    _ask(sp, "What is an addressable screw?", d)   # a different question
    assert asked_ai == ["What is an addressable screw?"]


def _answer(sp, q):
    return dict(sp.prepared)[q]


def test_parts_with_prepared_answers_are_shown_together(sp):
    glued, rest = sp._glue_prepared("What is static batching, what is dynamic batching?")
    assert glued == _answer(sp, "What is Static Batching?") + " " + _answer(sp, "What is Dynamic Batching?")
    assert rest == []


def test_only_the_part_without_a_prepared_answer_goes_to_ai(sp, monkeypatch):
    sent = []
    monkeypatch.setattr(sp, "enabled", True)
    monkeypatch.setattr(sp, "_fetch", lambda q, d, g, **kw: sent.append(kw))
    monkeypatch.setattr(SP.threading, "Thread", lambda target, args, kwargs, daemon: type(
        "T", (), {"start": lambda self: target(*args, **kwargs)})())
    d = _Display()
    sp._gen += 1
    _ask(sp, "What is a pivot? What are pixels per unit? And why should all art use the same value?", d)
    shown = _answer(sp, "What is a Pivot?") + " " + _answer(sp, "What are Pixels Per Unit?")
    assert d.shown == [shown]                       # both prepared answers at once
    assert len(sent) == 1
    assert (sent[0]["prefix"], sent[0]["only"]) == (shown, ["why should all art use the same value?"])


@pytest.mark.parametrize("heard, kind", [
    ("Okay.", "ack"), ("Great, thank you.", "ack"), ("I see, that makes sense.", "ack"),
    ("Mm-hmm, good.", "ack"), ("Right, perfect.", "ack"),
    ("Tell me more.", "more"), ("Can you tell me more about that?", "more"),
    ("Can you elaborate?", "more"), ("Why?", "more"), ("Could you go into more detail?", "more"),
    ("Does it reduce draw calls?", "more"), ("When would you use one?", "more"),
    ("And how do you reduce it?", "more"), ("And how would you use them in a live game?", "more"),
    ("Is it expensive on mobile?", "more"),
    ("What is a prefab and why do we use it?", "question"), ("How do you reduce draw calls?", "question"),
    ("Does the SRP Batcher reduce draw calls?", "question"),
    ("Tell me more about the Animator.", "question"), ("What about Has Exit Time?", "question"),
    ("Okay, and what is a draw call?", "question"), ("Tell me about your home assignment.", "question"),
])
def test_what_kind_of_thing_the_interviewer_said(heard, kind):
    assert SP._utterance_kind(heard) == kind


def _spy(sp, monkeypatch):
    sent = []
    sp.last_shown_answer = sp._prev_fired_q = None   # a fresh interview
    monkeypatch.setattr(sp, "enabled", True)
    monkeypatch.setattr(sp, "_fetch", lambda q, d, g, **kw: sent.append((q, kw)))
    monkeypatch.setattr(SP.threading, "Thread", lambda target, args, kwargs, daemon: type(
        "T", (), {"start": lambda self: target(*args, **kwargs)})())
    return sent


@pytest.mark.parametrize("heard, want", [
    ("Let's talk about UI, what is a Canvas?", "What is a Canvas?"),
    ("Good. Now about rendering, what is a draw call?", "What is a Draw Call?"),
    ("Let's move on to animation. What is a Blend Tree?", "What is a Blend Tree?"),
])
def test_lead_in_before_the_question_does_not_hide_the_prepared_answer(sp, monkeypatch, heard, want):
    sent, d = _spy(sp, monkeypatch), _Display()
    sp._gen += 1
    _ask(sp, heard, d)
    assert d.shown == [_answer(sp, want)] and not sent


def test_thank_you_does_not_touch_the_ribbon(sp, monkeypatch):
    sent, d = _spy(sp, monkeypatch), _Display()
    sp._gen += 1
    _ask(sp, "What is a draw call?", d)
    _ask(sp, "Okay, great, thank you.", d)
    assert len(d.shown) == 1 and not sent


def test_tell_me_more_goes_to_ai_with_the_previous_question_and_answer(sp, monkeypatch):
    sent, d = _spy(sp, monkeypatch), _Display()
    sp._gen += 1
    _ask(sp, "What is an Animator?", d)
    shown = _answer(sp, "What is an Animator?")
    sp._gen += 1
    _ask(sp, "Tell me more.", d)
    assert [q for q, _ in sent] == ["Tell me more."]
    assert sent[0][1]["context"] == ("What is an Animator?", shown)


def test_more_about_the_topic_just_answered_is_not_the_same_answer_again(sp, monkeypatch):
    sent, d = _spy(sp, monkeypatch), _Display()
    sp._gen += 1
    _ask(sp, "What is an Animator?", d)
    sp._gen += 1
    _ask(sp, "Tell me more about the Animator.", d)
    assert len(d.shown) == 1                      # Animator answer is not replayed
    assert len(sent) == 1 and sent[0][1]["context"][0] == "What is an Animator?"


def test_follow_up_with_its_own_topic_gets_its_own_prepared_answer(sp, monkeypatch):
    sent, d = _spy(sp, monkeypatch), _Display()
    sp._gen += 1
    _ask(sp, "What is an Animator?", d)
    _ask(sp, "Tell me more about the Animator, what parameters are there?", d)
    assert d.shown[-1] == _answer(sp, "What is an Animator Parameter?") and not sent


def test_one_question_is_never_split(sp):
    assert sp._glue_prepared("What is the difference between a sprite renderer and a UI image?") == ("", [])


def test_every_prepared_question_finds_itself(sp):
    for lead in ("", "Can you tell me ", "Okay, next question. "):
        bad = [q for q, a in sp.prepared if (sp._best_prepared(lead + q) or ("", ""))[1] != a]
        assert not bad, (lead, bad[:5])
