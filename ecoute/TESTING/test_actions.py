"""Cookbook (actions.md): the right topic reaches the AI, and only when the question is about it.

Run from the ecoute folder:  python -m pytest TESTING/test_actions.py -q
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


def topic(sp, question, context=None):
    hit = sp._relevant_action(question, context)
    return hit[0].split(" (")[0] if hit else None


def test_cookbook_is_loaded(sp):
    assert len(sp.actions) >= 20
    # every topic keeps its lesson: an empty body means the header rule cut it
    assert all(len(body.split()) > 50 for _, body in sp.actions)


@pytest.mark.parametrize("heard, want", [
    ("How do anchors work on a RectTransform?", "RECTTRANSFORM AND ANCHORS"),
    ("What does Has Exit Time do on a transition?", "ANIMATOR CONTROLLER, STATES AND TRANSITIONS"),
    ("How do you set up a blend tree?", "BLEND TREES"),
    ("What is the culling mode on the Animator?", "ANIMATOR COMPONENT"),
    ("How do you add an animation event?", "ANIMATION CURVES AND ANIMATION EVENTS"),
    ("What are the render modes of a Canvas?", "CANVAS AND RENDER MODES"),
    ("How do you make a sliced image?", "UI IMAGE COMPONENT"),
    ("How do you compare two captures in the Profile Analyzer?", "PROFILE ANALYZER"),
    ("How do you take a memory snapshot?", "MEMORY PROFILER"),
    ("How does occlusion culling work?", "URP CAMERA AND PIPELINE"),
    ("How do you use the Frame Debugger?", "URP CAMERA AND PIPELINE"),
    ("What are light probes for?", "BAKED LIGHTING, LIGHT PROBES AND REFLECTION PROBES"),
    ("How do you read the Timeline in the Profiler?", "UNITY PROFILER"),
])
def test_question_finds_its_topic(sp, heard, want):
    assert topic(sp, heard) == want


@pytest.mark.parametrize("heard", [
    "What is your salary expectation?",
    "Tell me about yourself.",
    "What is your experience with Unity?",
    "Why did you leave your last job?",
    "Okay, great, thank you.",
])
def test_unrelated_question_gets_no_cookbook(sp, heard):
    assert topic(sp, heard) is None


@pytest.mark.parametrize("heard, prev_q, want", [
    ("Can you tell me more?", "What is a Blend Tree?", "BLEND TREES"),
    ("Can you go into more detail?", "How do anchors work?", "RECTTRANSFORM AND ANCHORS"),
    ("And how do you set it up?", "What is a Scroll Rect?", "UI SCROLL RECT"),
    # the follow-up names its own topic: it wins over the previous question
    ("Tell me more about the Animator layers.", "What is a Canvas?", "ANIMATOR LAYERS"),
    # live probe 2026-10-04: "turn" + "off" from a SUMMARY pulled the URP topic
    ("Why would you turn it off?", "What does Has Exit Time do on a transition?",
     "ANIMATOR CONTROLLER, STATES AND TRANSITIONS"),
    # "transition" is in two titles: the topic already on the table wins the tie
    ("How do you debug a transition that does not fire?", "What does Has Exit Time do on a transition?",
     "ANIMATOR CONTROLLER, STATES AND TRANSITIONS"),
    ("What can go wrong with it?", "How do you add an animation event?",
     "ANIMATION CURVES AND ANIMATION EVENTS"),
    ("Tell me more.", "How do you use the Frame Debugger?", "URP CAMERA AND PIPELINE"),
])
def test_follow_up_takes_topic_from_previous_question(sp, heard, prev_q, want):
    assert topic(sp, heard, (prev_q, "some answer")) == want


@pytest.mark.parametrize("heard, want", [
    ("What is your salary expectation?", True),
    ("What are your salary expectations for this role?", True),
    ("How much do you want to earn?", True),
    ("What compensation are you looking for?", True),
    ("How much memory does a texture use?", False),
    ("What is a Blend Tree?", False),
])
def test_money_question_is_left_to_the_candidate(heard, want):
    assert SP._is_money_question(heard) is want


@pytest.mark.parametrize("heard, want", [
    # sound run 3: a "how do you" question got only the definition of the thing
    ("How do you set up a Scroll Rect?", "glue"),
    # ... or the definition of a DIFFERENT thing: same words, other order
    # ("What is a Build Profile?", "What is an Animator State?")
    ("How do you profile a build?", "drop"),
    ("How do you check which state the Animator is in?", "drop"),
    # not a how-to, or the prepared question is itself the how-to: leave it alone
    ("What is a Scroll Rect?", None),
    ("How do you profile a game on a real phone?", None),
    # the prepared answer says what the two mean; the AI adds how to tell them apart
    ("How do you know if it is CPU bound or GPU bound?", "glue"),
])
def test_how_to_question_does_not_stop_at_a_definition(sp, heard, want):
    assert sp._how_to_plan(heard, sp._best_prepared(heard)) == want


def test_whisper_profile_for_profiler_still_finds_the_profiler(sp):
    # heard "What is the Unity Profile?": the follow-up got the Profile Analyzer cookbook
    assert topic(sp, "Tell me more.", ("What is the Unity Profile?", "x")) == "UNITY PROFILER"
    assert topic(sp, "What is the Profile Analyzer?") == "PROFILE ANALYZER"
    assert topic(sp, "How do you profile a build?") == "UNITY PROFILER"


@pytest.mark.parametrize("text, personal, want", [
    # kimi-k3, 2026-10-04: the prompt forbids it, the model said it anyway
    ("Blend Trees mix clips by a parameter. In my slot game work, animations were simple tweens "
     "and Spine clips, so this was never needed.", False,
     "Blend Trees mix clips by a parameter."),
    ("Layers split the state machine. On my last project I used two layers.", False,
     "Layers split the state machine."),
    # the interviewer asked about experience: the candidate's work is the answer
    ("Yes, I used it at work. In my slot projects it showed why batching broke.", True,
     "Yes, I used it at work. In my slot projects it showed why batching broke."),
    # Spine is never mentioned, even in an experience answer
    ("Yes, I animated UI. I also used Spine for characters.", True, "Yes, I animated UI."),
    # nothing to cut
    ("Anchors pin the element to its parent.", False, "Anchors pin the element to its parent."),
    # the whole answer would vanish: better the model's words than an empty ribbon
    ("In my work I did this a lot.", False, "In my work I did this a lot."),
])
def test_project_and_spine_sentences_are_cut(text, personal, want):
    assert SP._strip_projects(text, personal) == want


def test_prompt_forbids_code_names():
    prompt = SP.SYSTEM_PROMPT_TEMPLATE
    assert "SetTrigger" in prompt and "function" in prompt.lower()


class FakeRibbon:
    def __init__(self):
        self.calls = []

    def start(self, text):
        self.calls.append(("start", text))

    def update_text(self, text):
        self.calls.append(("update", text))

    def after(self, _ms, fn, *args):
        fn(*args)


def test_streamed_answer_does_not_restart_the_ribbon_when_it_ends(sp, monkeypatch):
    # Igor 2026-10-04: the ribbon reached the middle of an answer and started the
    # same answer again. The stream showed the first words (START), then the final
    # full text was sent as a NEW answer and the ribbon went back to the beginning
    full = "Root motion is when the animation clip itself moves the character."
    ribbon = FakeRibbon()

    def fake_stream(messages, display, gen, prefix=""):
        sp._set_text(display, "Root motion is", restart=True)
        return full

    monkeypatch.setattr(sp, "_stream_answer", fake_stream)
    sp._gen += 1
    sp._fetch("What is root motion?", ribbon, sp._gen)
    assert [kind for kind, _ in ribbon.calls] == ["start", "update"]
    assert ribbon.calls[-1] == ("update", full)


def test_answer_without_a_stream_still_starts_the_ribbon(sp, monkeypatch):
    full = "Root motion is when the animation clip itself moves the character and nothing else does."

    class Msg:
        content = full

    class Choice:
        message = Msg()

    class Resp:
        choices = [Choice()]

    ribbon = FakeRibbon()
    monkeypatch.setattr(sp, "_stream_answer", lambda *a, **k: None)
    monkeypatch.setattr(sp, "_call_api", lambda *a, **k: Resp())
    sp._gen += 1
    sp._fetch("What is root motion?", ribbon, sp._gen)
    assert ribbon.calls == [("start", full)]


def test_how_to_right_after_a_topic_stays_on_it(sp):
    assert topic(sp, "How do you make a character wave while walking?",
                 ("What are Animator layers?", "x")) == "ANIMATOR LAYERS"


def test_tie_goes_to_the_topic_from_two_questions_back(sp):
    # Has Exit Time -> "Why would you turn it off?" -> this one: the previous
    # question has no topic of its own, the remembered one breaks the tie
    sp._last_action = sp._relevant_action("What does Has Exit Time do on a transition?")
    try:
        assert topic(sp, "How do you debug a transition that does not fire?",
                     ("Why would you turn it off?", "x")) == "ANIMATOR CONTROLLER, STATES AND TRANSITIONS"
    finally:
        sp._last_action = None


@pytest.mark.parametrize("text, want", [
    ("Sure, let me go deeper with how I spot it.", "Let me go deeper with how I spot it."),
    ("Sure — Frame Debugger shows draw calls.", "Frame Debugger shows draw calls."),
    ("Good question. First, I select the panel.", "First, I select the panel."),
    ("Surely the frame is done early.", "Surely the frame is done early."),
    ("First, I open the Profiler.", "First, I open the Profiler."),
])
def test_chatbot_opener_is_removed(text, want):
    assert SP._strip_opener(text) == want


def test_new_question_does_not_inherit_the_previous_topic(sp):
    assert topic(sp, "What is your salary expectation?", ("What is a Blend Tree?", "x")) is None


def test_third_follow_up_in_a_row_keeps_the_topic(sp):
    sp._last_action = sp._relevant_action("What is a Blend Tree?")
    try:
        assert topic(sp, "Can you go deeper?", ("Can you tell me more?", "x")) == "BLEND TREES"
    finally:
        sp._last_action = None


@pytest.mark.parametrize("heard", [
    # the heard question names a whole cookbook topic; the prepared answer is only
    # about one word of it ("What is an Animator?" was shown for Animator layers)
    "What are Animator layers?",
])
def test_cookbook_topic_beats_a_partial_prepared_answer(sp, heard):
    assert sp._best_prepared(heard) is None


@pytest.mark.parametrize("heard, want", [
    ("How do you set up a blend tree?", True),
    ("How would you bake the lighting?", True),
    ("What are the steps to profile a build?", True),
    ("Can you walk me through adding an animation event?", True),
    ("How do I create a slider?", True),
    ("What is a blend tree?", False),
    ("How does occlusion culling work?", False),
    ("Why do you use anchors?", False),
    ("Can you tell me more?", False),
])
def test_how_to_question_asks_for_steps(heard, want):
    assert SP._wants_steps(heard) is want


def test_answer_length_grows_with_the_kind_of_question():
    short = SP._answer_words("What is a blend tree?", False)
    more = SP._answer_words("Can you tell me more?", True)
    steps = SP._answer_words("How do you set up a blend tree?", True)
    assert short < more < steps


@pytest.mark.parametrize("text, want", [
    ("Furthermore, it is worth noting that anchors utilize the parent.", {"bookish"}),
    ("The frame takes 16 milliseconds.", {"number"}),
    ("In my last project I baked all the lighting.", {"experience"}),
    ("Yes, I've used it on a real build.", {"experience"}),
    ("Sure. A Blend Tree has a Blend Type.", {"opener"}),
    ("Good question. First, I select the panel.", {"opener"}),
    ("Anchors pin the element to its parent, so it stays in place when the screen changes.", set()),
    # an ordinal word is how a person lists steps; it is not a number
    ("First open the Lighting window, then press Generate Lighting.", set()),
])
def test_tells_are_detected(text, want):
    assert set(SP.answer_tells(text)) == want
