"""The question buffer must hold each phrase ONCE.

Whisper re-transcribes the whole growing phrase on every audio chunk, so the
buffer has to replace the current phrase, not append to it. Recorded bug:
"Can you tell me what a game object... Can you tell me what a game object is?"

Run from the ecoute folder:  python -m pytest TESTING/test_speaker_buffer.py -q
"""
import os
import sys
from datetime import datetime, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

from AudioTranscriber import AudioTranscriber  # noqa: E402


class _Src:
    SAMPLE_RATE, SAMPLE_WIDTH, channels = 16000, 2, 1


def _feed(tr, t, text):
    """One audio chunk arrives at time t and whisper returns `text` for the phrase."""
    tr.update_last_sample_and_phrase_status("Speaker", b"\0\0", t)
    if text:
        tr.update_transcript("Speaker", text, t)


def _new():
    return AudioTranscriber(_Src(), _Src(), model=None), datetime(2026, 1, 1)


def test_growing_phrase_is_kept_once():
    tr, t0 = _new()
    _feed(tr, t0, "Can you tell me what a game object...")
    _feed(tr, t0 + timedelta(seconds=1.5), "Can you tell me what a game object is?")
    assert tr.get_current_speaker_phrase() == "Can you tell me what a game object is?"


def test_pause_inside_a_question_keeps_both_phrases():
    tr, t0 = _new()
    _feed(tr, t0, "What is a draw call?")
    _feed(tr, t0 + timedelta(seconds=4), "And how do you")
    _feed(tr, t0 + timedelta(seconds=5.5), "And how do you reduce them?")
    assert tr.get_current_speaker_phrase() == "What is a draw call? And how do you reduce them?"


def test_two_chunks_in_one_drain_still_start_a_new_phrase():
    tr, t0 = _new()
    _feed(tr, t0, "What is a Canvas?")
    # two chunks queued before the transcriber wakes up: only the first is "new"
    tr.update_last_sample_and_phrase_status("Speaker", b"\0\0", t0 + timedelta(seconds=5))
    tr.update_last_sample_and_phrase_status("Speaker", b"\0\0", t0 + timedelta(seconds=6))
    tr.update_transcript("Speaker", "What is a Mask?", t0 + timedelta(seconds=6))
    assert tr.get_current_speaker_phrase() == "What is a Canvas? What is a Mask?"


def test_question_is_not_finished_while_audio_is_still_being_processed():
    """Recorded on long questions: whisper needs seconds for a 9 s phrase, new
    chunks wait in the queue, and "3 s of silence" elapsed during transcription."""
    import queue
    tr, _ = _new()
    old = datetime.utcnow() - timedelta(seconds=10)
    tr.update_last_sample_and_phrase_status("Speaker", b"\0\0", old)
    assert tr.get_speaker_last_ts() == old                   # idle: real silence
    tr._speaker_busy = True                                   # whisper is working
    assert datetime.utcnow() - tr.get_speaker_last_ts() < timedelta(seconds=1)
    tr._speaker_busy = False
    tr._speaker_queue = queue.Queue()
    tr._speaker_queue.put((b"\0\0", datetime.utcnow()))      # audio not taken yet
    assert datetime.utcnow() - tr.get_speaker_last_ts() < timedelta(seconds=1)


def test_answered_question_does_not_leak_into_the_next():
    tr, t0 = _new()
    _feed(tr, t0, "What is a Prefab?")
    tr.clear_speaker_buffer()
    assert tr.get_current_speaker_phrase() == ""
    # next question starts inside the phrase timeout: old audio must be dropped
    _feed(tr, t0 + timedelta(seconds=1), "What is a Scene?")
    assert tr.get_current_speaker_phrase() == "What is a Scene?"
    assert tr.audio_sources["Speaker"]["last_sample"] == b"\0\0"
