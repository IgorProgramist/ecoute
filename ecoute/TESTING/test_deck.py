"""Черга відповідей (AnswerDeck): стрічка не переривається, нове чекає в черзі.
Рішення Ігоря 2026-10-04:
  - нове питання НІКОЛИ не перериває стрічку;
  - усе, що накопичилось за час стрічки, склеюється в одне питання, AI думає на фоні;
  - накопичене виходить саме: стрічка доїхала + 3 с тиші інтерв'юера;
  - стрілка вліво/вправо = історія; вгору = прибрати поточне і одразу показати
    накопичене; вниз = прибрати стрічку І чергу;
  - поки дивишся стару відповідь, черга чекає.
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config  # noqa: E402
import SuggestionProvider as SP  # noqa: E402
from AnswerDeck import AnswerDeck  # noqa: E402


class FakeRibbon:
    def __init__(self):
        self.calls = []
        self.playing = False
        self.badge = ""
        self.on_done = None

    def start(self, text):
        self.calls.append(("start", text))
        self.playing = True

    def update_text(self, text):
        self.calls.append(("update", text))

    def hide(self):
        self.calls.append(("hide", ""))
        self.playing = False

    def is_busy(self):
        return self.playing

    def set_badge(self, text):
        self.badge = text

    def sync(self, _text):
        pass

    def after(self, ms, fn, *args):
        if ms == 0:
            fn(*args)       # виклики з потоку AI виконуємо одразу; таймер черги - ні

    def finish(self):
        """Стрічка доїхала до кінця."""
        self.playing = False
        if self.on_done:
            self.on_done()

    def shown(self):
        return [text for kind, text in self.calls if kind == "start"]


class Silence:
    def __init__(self, seconds=0.0):
        self.seconds = seconds

    def __call__(self):
        return self.seconds


@pytest.fixture
def deck():
    ribbon = FakeRibbon()
    silence = Silence(0.0)
    d = AnswerDeck(ribbon, silence_fn=silence, wait_s=3.0)
    d.test_ribbon, d.test_silence = ribbon, silence
    return d


def test_first_answer_goes_straight_to_the_ribbon(deck):
    deck.write(1, "Answer A", restart=True, queued=False)
    assert deck.test_ribbon.calls == [("start", "Answer A")]
    assert not deck.has_pending()


def test_answer_for_a_new_question_does_not_interrupt_the_ribbon(deck):
    deck.write(1, "Answer A", restart=True, queued=False)
    deck.reserve(2)
    deck.write(2, "Answer B", restart=True, queued=True)
    assert deck.test_ribbon.shown() == ["Answer A"]
    assert deck.has_pending() and deck.test_ribbon.badge == "+1"


def test_queued_answer_waits_for_the_end_of_the_ribbon_and_three_seconds_of_silence(deck):
    promoted = []
    deck.on_promote = promoted.append
    deck.write(1, "Answer A", restart=True, queued=False)
    deck.reserve(2)
    deck.write(2, "Answer B", restart=True, queued=True)
    deck.test_silence.seconds = 10.0
    deck.tick()                                   # ribbon still running
    assert deck.test_ribbon.shown() == ["Answer A"]
    deck.test_silence.seconds = 1.0               # interviewer has just spoken
    deck.test_ribbon.finish()
    deck.tick()
    assert deck.test_ribbon.shown() == ["Answer A"]
    deck.test_silence.seconds = 3.5
    deck.tick()
    assert deck.test_ribbon.shown() == ["Answer A", "Answer B"]
    assert not deck.has_pending() and deck.test_ribbon.badge == "" and promoted == [2]


def test_stream_of_a_promoted_answer_keeps_feeding_the_ribbon(deck):
    deck.write(1, "Answer A", restart=True, queued=False)
    deck.reserve(2)
    deck.write(2, "Answer B", restart=True, queued=True)
    deck.test_ribbon.finish()
    deck.test_silence.seconds = 5.0
    deck.tick()
    deck.write(2, "Answer B and more", restart=False, queued=True)
    assert deck.test_ribbon.calls[-1] == ("update", "Answer B and more")


def test_newer_queued_question_replaces_the_older_one(deck):
    # everything said while the ribbon runs is glued into ONE question: the answer to the
    # glued question replaces the answer to its first part
    deck.write(1, "Answer A", restart=True, queued=False)
    deck.reserve(2)
    deck.write(2, "Answer B", restart=True, queued=True)
    deck.reserve(3)
    assert deck.test_ribbon.badge == "+2" and deck.pending_text() == ""
    deck.write(2, "Answer B, late words", restart=False, queued=True)   # a stale stream
    assert deck.pending_text() == ""
    deck.write(3, "Answer B and C", restart=True, queued=True)
    assert deck.pending_text() == "Answer B and C"
    assert deck.test_ribbon.shown() == ["Answer A"]


def test_reserved_place_without_text_is_not_shown_until_the_text_comes(deck):
    deck.write(1, "Answer A", restart=True, queued=False)
    deck.reserve(2)                               # the AI is still thinking
    deck.test_ribbon.finish()
    deck.test_silence.seconds = 9.0
    deck.tick()
    assert deck.test_ribbon.shown() == ["Answer A"] and deck.has_pending()
    deck.write(2, "Answer B", restart=True, queued=True)
    deck.tick()
    assert deck.test_ribbon.shown() == ["Answer A", "Answer B"]


def test_left_and_right_walk_through_the_history(deck):
    deck.write(1, "Answer A", restart=True, queued=False)
    deck.test_ribbon.finish()
    deck.write(2, "Answer B", restart=True, queued=False)
    deck.left()                                   # B is running: one back
    assert deck.test_ribbon.shown()[-1] == "Answer A"
    deck.right()
    assert deck.test_ribbon.shown()[-1] == "Answer B"
    deck.test_ribbon.finish()
    deck.left()                                   # nothing is running: the last one again
    assert deck.test_ribbon.shown()[-1] == "Answer B"


def test_queue_waits_while_an_old_answer_is_on_the_ribbon(deck):
    deck.write(1, "Answer A", restart=True, queued=False)
    deck.test_ribbon.finish()
    deck.write(2, "Answer B", restart=True, queued=False)
    deck.reserve(3)
    deck.write(3, "Answer C", restart=True, queued=True)
    deck.left()                                   # reading A again
    deck.test_ribbon.finish()
    deck.test_silence.seconds = 9.0
    deck.tick()
    assert deck.test_ribbon.shown()[-1] == "Answer A"      # C did not push in
    deck.right()                                  # back to B
    deck.right()                                  # nothing newer in history: the queue
    assert deck.test_ribbon.shown()[-1] == "Answer C" and not deck.has_pending()


def test_up_drops_the_current_answer_and_shows_the_queued_one_at_once(deck):
    deck.write(1, "Answer A", restart=True, queued=False)
    deck.reserve(2)
    deck.write(2, "Answer B", restart=True, queued=True)
    deck.up()                                     # silence is 0 s: no waiting
    assert deck.test_ribbon.shown() == ["Answer A", "Answer B"]


def test_up_with_an_empty_queue_only_hides_the_ribbon(deck):
    deck.write(1, "Answer A", restart=True, queued=False)
    deck.up()
    assert deck.test_ribbon.calls[-1][0] == "hide" and not deck.test_ribbon.playing


def test_down_clears_the_ribbon_and_the_queue(deck):
    deck.write(1, "Answer A", restart=True, queued=False)
    deck.reserve(2)
    deck.write(2, "Answer B", restart=True, queued=True)
    deck.down()
    assert not deck.test_ribbon.playing and not deck.has_pending() and deck.test_ribbon.badge == ""
    deck.write(2, "Answer B, late words", restart=False, queued=True)   # its stream is still alive
    deck.test_silence.seconds = 9.0
    deck.tick()
    assert deck.test_ribbon.shown() == ["Answer A"]


def test_stream_of_the_main_answer_updates_the_ribbon(deck):
    deck.write(1, "Root motion is", restart=True, queued=False)
    deck.write(1, "Root motion is when the clip moves the character.", restart=False, queued=False)
    assert deck.test_ribbon.calls == [("start", "Root motion is"),
                                      ("update", "Root motion is when the clip moves the character.")]


# ---------- SuggestionProvider + deck ----------

@pytest.fixture
def talk(monkeypatch):
    monkeypatch.setattr(config, "RIBBON_QUEUE", True)
    provider = SP.SuggestionProvider(None)          # AI off: prepared answers only
    ribbon = FakeRibbon()
    deck = AnswerDeck(ribbon, silence_fn=Silence(0.0), wait_s=3.0)
    deck.on_promote = provider.promoted
    return provider, deck, ribbon


def test_second_question_during_the_ribbon_is_queued_not_shown(talk):
    provider, deck, ribbon = talk
    provider.maybe_update("What is a Canvas?", deck, phrase_epoch=1)
    provider.maybe_update("What is a Prefab?", deck, phrase_epoch=2)
    assert len(ribbon.shown()) == 1 and ribbon.shown()[0].startswith("A Canvas is")
    assert deck.pending_text().startswith("A Prefab is")


def test_everything_said_during_the_ribbon_becomes_one_question(talk):
    provider, deck, ribbon = talk
    provider.maybe_update("What is a Canvas?", deck, phrase_epoch=1)
    provider.maybe_update("What is a Prefab?", deck, phrase_epoch=2)
    provider.maybe_update("What is overdraw?", deck, phrase_epoch=3)
    text = deck.pending_text()
    assert "A Prefab is" in text and "Overdraw happens" in text
    assert len(ribbon.shown()) == 1 and ribbon.badge == "+2"


def test_after_the_queue_is_shown_the_next_question_starts_clean(talk):
    provider, deck, ribbon = talk
    provider.maybe_update("What is a Canvas?", deck, phrase_epoch=1)
    provider.maybe_update("What is a Prefab?", deck, phrase_epoch=2)
    ribbon.finish()
    deck.silence_fn.seconds = 5.0
    deck.tick()                                    # the Prefab answer is on the ribbon now
    ribbon.finish()
    provider.maybe_update("What is overdraw?", deck, phrase_epoch=3)
    assert ribbon.shown()[-1].startswith("Overdraw happens")
    assert "Prefab" not in ribbon.shown()[-1]


def test_switch_off_keeps_the_old_behaviour(monkeypatch):
    monkeypatch.setattr(config, "RIBBON_QUEUE", False)
    provider = SP.SuggestionProvider(None)
    ribbon = FakeRibbon()
    provider.maybe_update("What is a Canvas?", ribbon, phrase_epoch=1)
    provider.maybe_update("What is a Prefab?", ribbon, phrase_epoch=2)
    assert [t[:10] for t in ribbon.shown()] == ["A Canvas i", "A Prefab i"]


def test_new_phrase_does_not_kill_the_answer_that_is_being_written(talk):
    # "while the AI is thinking the interviewer adds something": the first answer must come out
    provider, deck, ribbon = talk
    provider._gen = 5
    provider._main_gen = 5
    provider._gen = 6                               # a new phrase arrived
    assert not provider._stale(5) and not provider._stale(6)
    assert provider._stale(4)
