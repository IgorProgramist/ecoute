"""The ribbon scrolls by itself and loads text in chunks of CHUNK_WORDS.
When AI adds a tail to prepared answers already on the ribbon, nothing may
be shown twice and the ribbon may not jump back.

Run from the ecoute folder:  python -m pytest TESTING/test_teleprompter.py -q
"""
import os
import sys
import types

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

import Teleprompter as TP  # noqa: E402


class _Label:
    def __init__(self):
        self.text = ""

    def config(self, text):
        self.text = text


def _ribbon(words_on_ribbon, chunk_start=0, scrolling=True):
    r = types.SimpleNamespace(
        _win=object(), _scrolling=scrolling, _paused=False, _label=_Label(), _done_text=None,
        _current_text=" ".join(words_on_ribbon), _full_words=list(words_on_ribbon), _chunk_start=chunk_start,
        started=[])
    r.start = lambda text: r.started.append(text)
    r._label.text = " ".join(words_on_ribbon[chunk_start:chunk_start + TP.CHUNK_WORDS])
    return r


def _words(n, tag="w"):
    return ["%s%d" % (tag, i) for i in range(n)]


def test_streaming_a_short_answer_just_grows_the_label():
    r = _ribbon(_words(5))
    TP.Teleprompter.update_text(r, " ".join(_words(9)))
    assert r._label.text == " ".join(_words(9)) and r._chunk_start == 0


def test_tail_added_to_a_long_answer_is_not_shown_twice():
    prepared = _words(130)
    r = _ribbon(prepared)
    full = prepared + _words(40, "ai")
    TP.Teleprompter.update_text(r, " ".join(full))
    assert r._label.text == " ".join(full[:TP.CHUNK_WORDS])      # still the first chunk only
    # the next chunks are loaded from _full_words: together they are the text once
    shown = full[:TP.CHUNK_WORDS] + r._full_words[TP.CHUNK_WORDS:]
    assert shown == full


def test_tail_arriving_during_the_second_chunk_does_not_jump_back():
    prepared = _words(130)
    r = _ribbon(prepared, chunk_start=TP.CHUNK_WORDS)
    full = prepared + _words(40, "ai")
    TP.Teleprompter.update_text(r, " ".join(full))
    assert r._chunk_start == TP.CHUNK_WORDS
    assert r._label.text == " ".join(full[TP.CHUNK_WORDS:])


def test_tail_arriving_after_the_ribbon_finished_shows_only_the_tail():
    prepared = " ".join(_words(30))
    r = _ribbon([], scrolling=False)
    r._done_text = prepared
    TP.Teleprompter.update_text(r, prepared + " " + " ".join(_words(10, "ai")))
    assert [t.strip() for t in r.started] == [" ".join(_words(10, "ai"))]
