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
    # one shared word is not the topic: "Sorting LAYER" is not Animator layers,
    # "Content SIZE Fitter" is not RectTransform, "CANVAS Scaler" is not render modes
    "What is a Sorting Layer?",
    "What is a Content Size Fitter?",
    "What is a Canvas Scaler?",
    # dry check of the vacancy questions: ONE word from the brackets of a title is not a topic
    "What is Timeline?",                                                  # Profiler has a Timeline view
    "Which assets do you deliver remotely and which stay in the build?",  # Profiler: "profile a build"
    "How do you update content without an app update?",                   # Scroll Rect: "content"
    "How do you find the root cause of a visual bug?",                    # Animator: "Apply Root Motion"
    "What is the difference between Tight Mesh and Full Rect?",           # Scroll Rect: "Rect"
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
    # dry check 2026-10-04: "parameters" is a word in the title of the Button topic, so this
    # follow-up pulled the Button cookbook after 28 of 30 questions. "its" = the previous topic
    ("Tell me more about its parameters and how to use it.", "What is an Animator?", "ANIMATOR COMPONENT"),
    ("Tell me more about its parameters and how to use it.", "What is a Slider?", "UI SLIDER"),
    ("Tell me more about their parameters and how to use them.", "What are anchors?",
     "RECTTRANSFORM AND ANCHORS"),
    ("Tell me more about its parameters and how to use it.", "What is a Prefab?", None),
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
    # Igor 2026-10-04: when nobody asks about experience, nothing about his own work at all
    ("I baked lightmaps at work, so this is familiar. First, I set the lights to Baked mode.", False,
     "First, I set the lights to Baked mode."),
    ("First I capture the game. Honestly, I have not used the Profile Analyzer at work, but this is how it works.",
     False, "First I capture the game."),
    ("Layers and Blend Trees exist too, though those didn't come up in my work.", False,
     "Layers and Blend Trees exist too, though those didn't come up in my work."),   # only sentence: kept
    ("The Profiler shows the frame. I used both at work on a real phone.", False, "The Profiler shows the frame."),
    # steps in the present tense are how Unity is used, not a story about his job
    ("First, I select the panel. Second, I open the Anchor Presets.", False,
     "First, I select the panel. Second, I open the Anchor Presets."),
    # nothing to cut
    ("Anchors pin the element to its parent.", False, "Anchors pin the element to its parent."),
    # the whole answer would vanish: better the model's words than an empty ribbon
    ("In my work I did this a lot.", False, "In my work I did this a lot."),
])
def test_project_and_spine_sentences_are_cut(text, personal, want):
    assert SP._strip_projects(text, personal) == want


YES = "Yes, I worked with it."
NO = "No, I have not worked with it, but I know how it works."


@pytest.mark.parametrize("question, want", [
    # Igor 2026-10-04: just "yes, worked" - never "a lot", never where or what for.
    # The code says it, the AI never sees his background on these questions
    ("Have you worked with the Animator?", YES),
    ("Have you used the Frame Debugger at work?", YES),
    ("Have you baked lighting in a real project?", YES),
    ("What is your experience with the Profiler?", YES),
    # his own "Not used at work" line in ABOUT ME
    ("Have you used the Memory Profiler at work?", NO),
    ("Did you use the Profile Analyzer in your projects?", NO),
    ("Have you built Blend Trees at work?", NO),
    ("What is your experience with Animator layers?", NO),
    # ABOUT ME says nothing either way: no claim, the answer starts with Unity itself
    ("Have you used occlusion culling?", ""),
])
def test_yes_or_no_comes_from_about_me_not_from_the_ai(sp, question, want):
    assert sp._experience_opener(question) == want


def test_experience_style_tells_the_ai_to_stay_off_the_candidate(sp):
    style = SP.STYLE_EXPERIENCE.lower()
    assert "do not say yes or no" in style and "nothing about the candidate" in style


def test_have_you_worked_with_it_gets_a_long_answer_through_the_related_topics(sp):
    # Igor 2026-10-04: "Have you worked with the Animator?" is never just "yes". They ask
    # so that he talks: yes or no, then the Animator, then the Animator Controller, and so on
    q = "Have you worked with the Animator?"
    action = sp._relevant_action(q)
    assert action is not None and action[0].startswith("ANIMATOR")
    assert SP._answer_words(q, True) == 120
    assert SP._style_for(q, True) == SP.STYLE_EXPERIENCE
    related = sp._related_summaries(action)
    assert "Animator Controller" in related          # a neighbouring topic is offered
    assert action[1].split("LESSON")[0].strip() not in related   # the chosen one is not repeated
    assert "LESSON" not in related                   # summaries only: the prompt stays small


@pytest.mark.parametrize("question, has_topic, want", [
    ("How do you set up a blend tree?", True, "STYLE_STEPS"),
    ("What is a blend tree?", True, "STYLE_PLAIN"),
    ("Have you used the Memory Profiler at work?", True, "STYLE_EXPERIENCE"),
    # no cookbook topic: nothing to walk through, the plain rule answers
    ("Have you worked in a big team?", False, "STYLE_PLAIN"),
])
def test_answer_style_follows_the_kind_of_question(question, has_topic, want):
    assert SP._style_for(question, has_topic) == getattr(SP, want)


def test_follow_up_takes_its_knowledge_from_the_question_it_follows(sp):
    # voice run 2026-10-04: after "What is a Prefab Variant?" the follow-up "Tell me more about its
    # parameters and how to use it" was answered about the DOT PRODUCT - the knowledge section and the
    # example answers were picked by the words of the follow-up ("parameters", "use")
    more = "Tell me more about its parameters and how to use it."
    assert sp._topic_basis(more, ("What is a Prefab Variant?", "x")) == "What is a Prefab Variant?"
    # a second follow-up in a row still belongs to the same first question
    assert sp._topic_basis("Tell me more about that.", (more, "y")) == "What is a Prefab Variant?"
    # a new real question starts over
    q = "What is a draw call?"
    assert sp._topic_basis(q, (more, "y")) == q
    assert sp._topic_basis("Tell me more.", (q, "z")) == q


def test_how_to_without_a_cookbook_topic_still_gets_steps_after_the_definition(sp):
    # "How do you structure a base prefab and its variants?" showed only "A Prefab Variant is..."
    q = "How do you structure a base prefab and its variants?"
    assert sp._how_to_plan(q, sp._best_prepared(q)) == "glue"


@pytest.mark.parametrize("heard", [
    # Igor 2026-10-04: "they can ask about ANY parameter of the Animator or the Particle System".
    # The definition of the whole component is not the answer to a question about one part of it
    "What is the Emission module of a Particle System?",
    "What are the parameters of a Particle System?",
    "What settings does the Animator have?",
    "What is the Shape module in the Particle System?",
])
def test_question_about_a_part_does_not_get_the_definition_of_the_whole(sp, heard):
    assert sp._best_prepared(heard) is None


@pytest.mark.parametrize("heard, steps", [
    # voice run 2026-10-04: "how would you describe X" is "what is X", not "how to do it".
    # The word "how" added a 90-105 word AI tail of steps to a plain definition
    ("How would you describe anchors?", False),
    ("How do you understand what an Animator Controller is?", False),
    ("What is URP, how would you explain it?", False),
    ("How would you define a draw call?", False),
    ("How do you see the role of a Canvas?", False),
    # real how-to questions still ask for steps
    ("How do you set up anchors for different aspect ratios?", True),
    ("How would you split Addressables groups?", True),
    ("Walk me through setting up a Scroll Rect.", True),
])
def test_how_would_you_describe_is_not_a_how_to(heard, steps):
    assert SP._wants_steps(heard) is steps


@pytest.mark.parametrize("heard, want", [
    # Igor 2026-10-04: "what is X" comes in many wordings; the wrapper words are not the topic
    ("How would you describe anchors?", "What are Anchors?"),
    ("What do you understand by batching?", "What is Batching?"),
    ("What is a Material, in your own words?", "What is a Material?"),
    ("How do you understand what a Shader is?", "What is a Shader?"),
    ("What is 9-slicing, in simple words?", "What is 9-slicing?"),
    ("How do you understand what a ScriptableObject is?", "What is a ScriptableObject?"),
    ("Explain to me what the SRP Batcher is.", "What is the SRP Batcher?"),
    ("Describe what a Mask is in UI.", "What is a Mask?"),
    ("What is your understanding of GPU Instancing?", "What is GPU Instancing?"),
    ("What does a Canvas mean to you?", "What is a Canvas?"),
])
def test_what_is_x_in_any_wording_finds_the_prepared_answer(sp, heard, want):
    hit = sp._best_prepared(heard)
    assert hit is not None and hit[0] == want


@pytest.mark.parametrize("heard, want", [
    # the part rule must not eat ordinary questions
    ("What is a Particle System?", "What is a Particle System?"),
    ("What is a pivot on a sprite?", "What is a Pivot?"),
    ("So what is a component in unity?", "What is a Component?"),
    ("What is an Addressables Label?", "What is an Addressables Label?"),
    ("What is an Addressables group?", "What is an Addressables Group?"),
    ("What is an Animator Parameter?", "What is an Animator Parameter?"),
    ("How do Animator parameters work?", "How do Animator parameters work?"),
    ("What is a Prefab Variant?", "What is a Prefab Variant?"),
])
def test_ordinary_questions_keep_their_prepared_answer(sp, heard, want):
    hit = sp._best_prepared(heard)
    assert hit is not None and hit[0] == want


@pytest.mark.parametrize("heard, title", [
    # the question names the component: its own field-by-field section must reach the AI
    ("What is the Emission module of a Particle System?", "COMPONENT: PARTICLE SYSTEM"),
    ("What are the parameters of a Particle System?", "COMPONENT: PARTICLE SYSTEM"),
    ("What parameters does an Image have?", "COMPONENT: IMAGE:"),
    ("What parameters are in a material?", "ASSETS: MATERIALS AND SHADERS:"),
    ("What is Raycast Target on an Image?", "COMPONENT: IMAGE:"),
    ("What settings does a Canvas Scaler have?", "COMPONENT: CANVAS SCALER:"),
])
def test_question_naming_a_component_gets_its_own_section(sp, heard, title):
    sent = sp._relevant_info(heard)
    bodies = [x for t, x in sp.info_sections if t.startswith(title) and x]
    assert bodies and any(b.strip()[:80] in sent for b in bodies)


def test_emission_question_gets_the_section_that_talks_about_emission(sp):
    sent = sp._relevant_info("What is the Emission module of a Particle System?")
    assert "Emission" in sent


@pytest.mark.parametrize("heard, title", [
    # a passing word in a LATER part of a compound question is not the topic:
    # "for a 9-sliced button", "uses more memory", "all art"
    ("Can you explain Sorting Layer and Order in Layer, and where a Sorting Group fits in?", None),
    ("What is Tight Mesh, what is Full Rect, and which one would you use for a 9-sliced button?", None),
    ("What is a pivot, what are Pixels Per Unit, and why should all art use the same value?", None),
    ("What is transparency, what is alpha clipping, and does additive blending reduce overdraw?", None),
    ("What is static batching, what is dynamic batching, and which one uses more memory?", None),
    ("What is tweening, how is it different from the Animator, and which one would you use for a button press?", None),
    # the first part names the topic
    ("What is the Unity Profiler, what is the Frame Debugger, and when do you use each?", "UNITY PROFILER"),
    ("What kinds of Animator parameters are there, and when do you use a trigger?", "ANIMATOR CONTROLLER"),
    ("What does the SRP Batcher do, does it reduce draw calls, and how do you check it?", "URP CAMERA"),
    ("How do you fix a memory leak, how do you find it, and how do you prove it is gone?", "MEMORY PROFILER"),
    ("What are Animator layers?", "ANIMATOR LAYERS"),
    ("What is a Sorting Layer?", None),
])
def test_compound_question_takes_its_topic_from_the_first_part(sp, heard, title):
    sp._last_action = None
    hit = sp._relevant_action(heard)
    assert (hit[0] if hit else None) is None if title is None else hit and hit[0].startswith(title)


@pytest.mark.parametrize("heard", [
    "What is Any State in the Animator?",      # showed "What is an Animator State?"
    "What Image Types are there?",             # showed "What is an Image?"
])
def test_named_part_does_not_get_the_definition_of_the_whole(sp, heard):
    assert sp._best_prepared(heard) is None


@pytest.mark.parametrize("heard, title", [
    # the word "animation" alone names no cookbook topic: three topics carry it
    ("What is Texture Sheet Animation in the Particle System?", None),
    ("How do you make a dust effect for a building animation?", None),
    ("What is an Animation Event?", "ANIMATION CURVES"),
    ("How do you create a clip in the Animation window?", "ANIMATION WINDOW"),
])
def test_the_word_animation_alone_is_not_a_topic(sp, heard, title):
    sp._last_action = None
    hit = sp._relevant_action(heard)
    assert (hit[0] if hit else None) is None if title is None else hit and hit[0].startswith(title)


def test_plural_in_the_question_still_finds_the_component_section(sp):
    body = [x for t, x in sp.info_sections if t == "COMPONENT: CANVAS:"][0]
    assert body.strip()[:80] in sp._relevant_info("How do you split UI into Canvases?")


@pytest.mark.parametrize("heard, prepared_q, want", [
    # "have you used X" hits a prepared answer about X: yes or no still comes first
    ("Have you used the Frame Debugger?", "What is the Frame Debugger?", SP.EXPERIENCE_YES),
    ("Have you used the Memory Profiler?", "How do you use the Memory Profiler?", SP.EXPERIENCE_NO),
    # not a question about experience: nothing is added
    ("What is the Frame Debugger?", "What is the Frame Debugger?", ""),
    # the prepared answer is itself about his experience: nothing is added
    ("Have you ever missed a deadline?", "Have you ever missed a deadline?", ""),
])
def test_yes_or_no_goes_before_a_prepared_answer_too(sp, heard, prepared_q, want):
    shown = sp._with_opener(heard, (prepared_q, "BODY"))
    assert shown == (want + " BODY" if want else "BODY")


@pytest.mark.parametrize("heard", [
    # voice run 2026-10-04: both showed the home-assignment answer "I tested two screen
    # sizes (1080x2400...)" - the tail "what do you check" hit "How did you check it?"
    "A sprite looks blurry on the device, what do you check?",
    "An object is pink in the build, what do you check?",
])
def test_tail_of_a_question_does_not_pull_a_home_assignment_answer(sp, heard):
    assert sp._tail_prepared(heard) is None


def test_tail_of_a_question_still_finds_an_ordinary_answer(sp):
    assert sp._tail_prepared("Let's talk about UI, what is a Canvas?")[0] == "What is a Canvas?"


def test_short_follow_up_with_it_keeps_the_previous_question(sp):
    # "What can go wrong with it?" after anchors was answered about sprite import
    prev = "How do you set up anchors for different aspect ratios?"
    basis = sp._topic_basis("What can go wrong with it?", (prev, "First, decide..."))
    assert prev in basis
    # a long question with "it" inside is its own subject
    own = "What is a Prefab and why do we use it in a big project with many artists?"
    assert sp._topic_basis(own, (prev, "First, decide...")) == own


@pytest.mark.parametrize("heard, style", [
    # no cookbook about particles, Addressables or Shader Graph: the AI wrote the yes itself
    # and invented "I use it for shine, glow or water"
    ("Have you worked with the Particle System?", "experience"),
    ("Have you worked with Shader Graph?", "experience"),
    ("Have you used Addressables?", "experience"),
    # a question about what he did stays a question about him
    ("What shaders have you made?", "plain"),
    ("Tell me about a time you fixed a performance problem.", "plain"),
])
def test_have_you_worked_with_it_needs_no_cookbook(heard, style):
    want = SP.STYLE_EXPERIENCE if style == "experience" else SP.STYLE_PLAIN
    assert SP._style_for(heard, False) == want
    assert (SP._answer_words(heard, False) == SP.EXPERIENCE_WORDS) == (style == "experience")


def test_prepared_answers_do_not_carry_the_next_section_marker(sp):
    # 18 answers ended with "--- HOW I WORK (...) ---" and that line went to the ribbon
    assert [q for q, a in sp.prepared if "---" in a] == []


def test_home_assignment_reaches_the_ai_only_when_asked(sp):
    # voice run 2026-10-04: a general question about variants got "seven direct variants",
    # a general question about a build flow got "a hammer sprite swings"
    assert len(SP.HOME_QUESTIONS) >= 5
    for general in ("How do you structure a base prefab and its variants?",
                    "How do you make a buy, build and ready flow?"):
        assert "seven direct variants" not in sp._relevant_info(general)
        assert not any(q in SP.HOME_QUESTIONS for q, a in sp._similar_prepared(general))
    asked = "Why did you structure the variants this way in your home assignment?"
    assert "seven direct variants" in sp._relevant_info(asked)
    assert any(q in SP.HOME_QUESTIONS for q, a in sp._similar_prepared(asked))


def test_prompt_tells_the_ai_to_write_without_i():
    assert "first person" not in SP.SYSTEM_PROMPT_TEMPLATE
    assert "never use the words I" in SP.RULE_NO_I and "home assignment" in SP.RULE_NO_I


def test_about_me_reaches_the_ai_only_for_experience_questions(sp):
    # the model cannot retell his work if it never sees it
    sp._personal = False
    assert "ABOUT ME" not in sp._relevant_info("How do you bake the lighting?")
    sp._personal = True
    try:
        assert "ABOUT ME" in sp._relevant_info("Have you baked lighting in a real project?")
    finally:
        sp._personal = False


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


def test_long_answer_is_never_cut(sp, monkeypatch):
    # Igor 2026-10-04: "40 words is a wish, not a rule, answers must never be cut".
    # "What Image Types are there?" said "four image types" and showed three: the code
    # dropped the last sentence because the answer was longer than the limit plus ten
    full = " ".join("Sentence number %d has exactly seven words here." % i for i in range(12))
    assert len(full.split()) > SP._answer_words("What Image Types are there?", False) + 10
    ribbon = FakeRibbon()
    monkeypatch.setattr(sp, "_stream_answer", lambda messages, display, gen, prefix="": full)
    sp._gen += 1
    sp._fetch("What Image Types are there?", ribbon, sp._gen)
    assert ribbon.calls[-1][1] == full


def test_prompt_still_asks_for_a_short_answer():
    # Igor 2026-10-04: "I wrote not to cut, not to make the answers as big as possible".
    # Softening the prompt to "a wish, not a limit" gave 140-209 words; the prompt keeps
    # the firm word count, only the cutting in code is gone
    prompt = SP.SYSTEM_PROMPT_TEMPLATE
    assert "must be about {max_words} words" in prompt
    assert "wish" not in prompt


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


@pytest.mark.parametrize("heard", [
    "Tell me more about its parameters and how to use it.",
    "Tell me more about their parameters and how to use them.",
    "Can you say more about that?",
])
def test_more_about_it_is_a_follow_up_not_a_new_question(heard):
    # as a "question" it was matched against prepared answers by the word "parameters"
    assert SP._utterance_kind(heard) == "more"


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
    assert short < steps < more == 120


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
