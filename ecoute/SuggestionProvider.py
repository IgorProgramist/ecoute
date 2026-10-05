import difflib
import re
import threading
import time
import uuid
from datetime import datetime
from openai import OpenAI

import config

BASE_URL = "https://opencode.ai/zen/go/v1"

QUESTION_SILENCE_S = 3.0    # аудіо-тиша 3с = питання завершене (дихання/задуми посеред питання коротші) (порог <2с стріляє в "сліпій зоні", доки записується наступний шматок)
REFIRE_MIN_NEW_WORDS = 4   # повторний показ тільки якщо питання виросло на 4+ слів
# скільки чекати ПЕРШЕ слово стріму. Було 10с: повільний, але живий стрім
# рубали, а запасний запит починав генерацію з нуля -> 10+25+25с тиші і [none]
# (17 разів за 2 прогони). Виміряно: один запит = перше слово за 1.4с,
# п'ять одночасних = 20-39с
STREAM_FIRST_WORD_S = 25
QUEUE_MAX_REMARKS = 3      # скільки останніх реплік склеюється в одне питання в черзі

SYSTEM_PROMPT_TEMPLATE = (
    "You are helping a candidate during a live technical job interview (Unity / Technical Artist role). "
    "You receive the interviewer's latest spoken question, plus the candidate's background info "
    "and their own prepared answers for similar questions — "
    "reuse their facts, style and tone (confident, direct). "
    "Reply in the SAME language as the question (English or Ukrainian). "
    "The answer must be about {max_words} words — a complete, confident reply that "
    "fully answers ALL parts of the question. "
    "Use SIMPLE everyday words and short clear sentences — the candidate reads it aloud fast. "
    "Avoid difficult vocabulary and abbreviations you can't say. "
    "Facts about the candidate (companies, projects, dates, results) come ONLY from the background "
    "info and prepared answers given to you. NEVER invent numbers, percentages, FPS values, "
    "project names or stories that are not written there — describe what was done and how, "
    "without made-up figures. "
    "Answer only about Unity itself: what the thing is, how it works, how it is done. "
    "Unless the interviewer asks about the candidate's experience, say NOTHING about the candidate's "
    "own work, projects, games or experience — no 'at work', no 'in my project', no 'I used it', "
    "no 'it did not come up'. "
    "The question comes from speech recognition and may contain misheard words — "
    "answer about the closest real Unity term and never comment on the wording. "
    "Sound like a person talking, not like a textbook: never use words like utilize, leverage, "
    "furthermore, moreover, additionally, crucial, robust, seamless, ensure, essentially, "
    "'it is worth noting', 'in order to'. "
    "Do not say numbers or exact values unless the interviewer asks for a number. "
    "Do not say names of functions or properties from code (like GetComponent or shortNameHash) — "
    "describe in plain words what is done. Only SetTrigger, SetBool and SetFloat may be named. "
    "Start straight with the answer: never open with Sure, Good question, Of course, Certainly "
    "or 'To continue'. "
    "{style} "
    "Output ONLY the answer text, nothing else."
)
STYLE_PLAIN = "Do not use lists, headings or markdown — plain sentences only."
# "як це зробити": людина перелічує кроки словами, а не цифрами зі списку
STYLE_STEPS = (
    "The interviewer asks HOW to do it: answer as a few short spoken steps, each a plain sentence "
    "that starts with First, Second, Third, Then or Finally. No digits, no bullet points, no markdown."
)
# "чи працював ти з X": питають, щоб кандидат РОЗПОВІВ, а не сказав "так"
STYLE_EXPERIENCE = (
    "The interviewer asks whether the candidate worked with something — they ask so that the candidate "
    "talks about the topic. The candidate has already answered yes or no himself: do NOT say yes or no, "
    "and say nothing about the candidate, his work or his experience. Tell about the thing itself, "
    "moving through the related parts one after another (for example the Animator, then the Animator "
    "Controller, then states and transitions), one or two simple sentences for each part. "
    "Every part must be a different topic, never repeat one. Plain sentences, no lists, no markdown."
)
# питання про досвід, для якого немає теми кукбукса: AI бачить ABOUT ME
RULE_HONEST = (
    "If the interviewer asks whether the candidate has used a tool or feature: say yes ONLY if the "
    "background info says so, otherwise say plainly that the candidate has not worked with it. "
    "Keep it to one short sentence about the candidate, with no story about a project."
)
# Ігор 2026-10-04: відповідь AI - лише про Unity, без "I". Не стосується питань
# про досвід без теми кукбукса (там діє RULE_HONEST і мова якраз про кандидата)
RULE_NO_I = (
    "Talk about Unity, not about a person: never use the words I, my, me or we. "
    "Say what is done in imperative or neutral form: 'First, select the panel', "
    "'The anchors are set to stretch' - not 'First, I select the panel'. "
    "Never mention the home assignment, the test task or its island unless the interviewer asks about it."
)
EXPERIENCE_WORDS = 120
# так чи ні каже КОД за рядками ABOUT ME, а не AI: модель дописувала "a lot at
# all my jobs, mainly for UI, popups and character animations"
EXPERIENCE_YES = "Yes, I worked with it."
EXPERIENCE_NO = "No, I have not worked with it, but I know how it works."
# рядок "Only in demos and my own projects: ..." з ABOUT ME (Ігор 2026-10-05)
EXPERIENCE_DEMO = "I have not used it in real projects, only in demos and my own projects."
ACTION_NOTE = (
    "Reference notes about this Unity topic. They describe how Unity works, NOT what the candidate "
    "did — never turn them into a personal story. Take only the facts the question needs and say "
    "them in your own simple spoken words. Never quote the notes and never mention notes, lessons "
    "or videos:\n"
)


def load_api_key():
    try:
        import keys
        return getattr(keys, "OPENCODE_API_KEY", None)
    except ImportError:
        return None


def _normalize(text):
    # whisper чує "mesh renderer", у файлі "MeshRenderer": ріжемо camelCase і
    # межу літера-цифра, щоб обидва записи давали ті самі слова
    text = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", text)
    text = re.sub(r"(?<=[A-Za-z])(?=\d)", " ", text)
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text, flags=re.UNICODE)
    return re.sub(r"\s+", " ", text).strip()


# слова без змісту: шаблон питання, а не його тема
_FILLER = {
    "what", "is", "are", "was", "a", "an", "the", "of", "in", "on", "to", "for",
    "do", "does", "did", "you", "your", "me", "we", "it", "its", "so", "and", "or",
    "can", "could", "would", "tell", "explain", "about", "between", "how", "that",
    "this", "with", "from", "at", "by", "be", "as", "us", "please", "mean", "means",
    "why", "when", "where", "which", "use", "used", "using", "there", "have", "has",
    # розмовні вставки інтерв'юера перед питанням
    "okay", "ok", "next", "question", "alright", "well", "let", "lets", "move", "now",
    "um", "uh", "yeah", "yes", "great", "thanks", "thank", "cool", "another", "just",
    "quick", "quickly", "actually", "basically", "know", "sure",
    # прохання розповісти більше: саме по собі не тема
    "more", "detail", "details", "detailed", "elaborate", "deeper", "bit", "little",
    "go", "into", "give",
    # обгортка питання "що таке X": "how do you understand what X is",
    # "describe X", "X in your own words", "X in simple words", "as you see it"
    "describe", "understand", "understanding", "understood", "own", "word", "words",
    "simple", "simply", "see", "say", "think", "opinion",
}

# репліки-підтвердження: інтерв'юер не питає, а реагує на відповідь
_ACK = {
    "good", "nice", "perfect", "fine", "see", "got", "understood", "interesting",
    "make", "sense", "right", "thank", "clear", "awesome", "correct", "exactly",
    "hmm", "mhm", "mm", "hm", "oh", "ah", "wow", "true", "agree", "agreed",
    "mmhmm", "mhmm", "mmm", "uhhuh", "uh", "huh", "yep", "yup", "aha", "noted",
    "helpful", "useful", "very", "really", "much", "lot", "appreciate", "answer",
}
_MORE_RE = re.compile(
    r"\b(more|detail|details|elaborate|deeper|example|examples|why|expand|go on|continue|"
    r"go into|explain|how so|what else|anything else|specifically|such as)\b")


_BACK_RE = re.compile(
    r"^(?:(?:and|so|but|okay|ok)[\s,]+)*(?:(?:how|why|when|where)\s+)?"
    r"(?:does|do|did|is|are|was|can|could|will|would|should)\s+"
    r"(?:you\s+\w+\s+)?(?:it|they|them|that|this|one|those|these)\b")


# "Tell me more about its parameters and how to use it": продовження попередньої теми,
# хоч у репліці й є власні слова
_MORE_ABOUT_RE = re.compile(r"\bmore about (it|its|their|them|that|this|these|those)\b")


_PERSONAL_RE = re.compile(
    r"\b(your (own )?experience|experience (with|in)|have you (ever )?\w+|did you (ever )?\w+|"
    r"in your (work|projects?|last job|previous job|career)|at your (last|previous) job|"
    r"tell me about a time|what \w+ have you (made|done|built|used|written|shipped))\b")


# питають про тестове завдання: лише тоді AI бачить його деталі. На загальні
# питання він переказував "seven direct variants", "a hammer sprite swings"
_HOME_RE = re.compile(
    r"\b(home (assignment|test|task|work)|homework|test (task|assignment)|take[- ]home|"
    r"your (island|assignment|submission|test)|tea house)\b")

_TEST_LINE_RE = re.compile(r"\bin (the|my) test\b", re.I)

# питають про ЧАСТИНУ компонента ("the Emission module of a Particle System",
# "parameters of an Image"): визначення цілого - не відповідь
_PIECE_RE = re.compile(
    r"\b(modules?|parameters?|settings?|propert(?:y|ies)|fields?|options?|types?|kinds?|any state)\b")
# ці слова є в кожному розділі: "parameters of a Particle System" тягло ANIMATION
_PIECE_WORDS = {"module", "modules", "parameter", "parameters", "setting", "settings",
                "property", "properties", "field", "fields", "option", "options"}

# слова заголовка розділу знань, які не називають тему
_TITLE_IGNORE = {"component", "assets", "asset", "project", "settings", "module", "modules",
                 "main", "used", "didn", "questions", "about", "what", "most", "matters",
                 "interview", "senior", "with", "every", "part"}


def _singular(w):
    """canvases -> canvas, atlases -> atlas, shaders -> shader; canvas і atlas не чіпає."""
    if w.endswith("ses"):
        return w[:-2]
    if w.endswith("s") and not w.endswith(("ss", "as", "us", "is")):
        return w[:-1]
    return w


def _root(w):
    """Корінь слова для назв розділів: batching, batcher, batches -> batch.
    Питання про "SRP Batcher" не знаходило розділ "DRAW CALLS AND BATCHING",
    і факт про GPU Instancing до AI не доходив."""
    w = _singular(w)
    for tail in ("ing", "er"):
        if len(w) > len(tail) + 3 and w.endswith(tail):
            return w[:-len(tail)]
    return w


def _title_words(title):
    """Змістові слова заголовка розділу (до дужки), зведені до кореня."""
    head = _normalize(title.split("(")[0])
    return set(_root(w) for w in head.split() if len(w) >= 4 and w not in _TITLE_IGNORE)


# про гроші кандидат відповідає сам: AI вигадав "senior level market rate"
_MONEY_RE = re.compile(
    r"\b(salary|salaries|compensation|pay (range|expectations?)|expected pay|rate expectations?|"
    r"how much (do|would|did) you (want|expect|earn|make|charge))\b")


def _is_money_question(text):
    return bool(_MONEY_RE.search(text.lower()))


def _utterance_kind(text):
    """'ack'  = "Okay, great, thank you" — нічого не показуємо;
    'more' = "Tell me more" / "Why?" без власної теми — продовження попередньої відповіді;
    'question' = усе інше."""
    # "Does it reduce draw calls?", "When would you use one?": питання про ТЕ,
    # про що щойно говорили. Без попередньої теми prepared-збіг тут хибний
    # (після SRP Batcher показало "How do you reduce draw calls?")
    if _BACK_RE.match(text.lower().strip()) or _MORE_ABOUT_RE.search(text.lower()):
        return "more"
    topic = [w for w in _ordered_tokens(text) if w not in _ACK]
    if _MORE_RE.search(text.lower()) and not [w for w in topic if not _MORE_RE.fullmatch(w)]:
        return "more"
    return "ack" if not topic else "question"


def _ordered_tokens(text):
    """Змістові слова питання по порядку: без шаблонних, множина -> однина."""
    out = []
    for w in _normalize(text).split():
        if w in _FILLER or len(w) < 2:   # одна літера = уламок whisper ("U.S.")
            continue
        if len(w) > 3 and w.endswith("s") and not w.endswith("ss"):
            w = w[:-1]
        out.append(w)
    return out


def _tokens(text):
    return set(_ordered_tokens(text))


def _stem(w):
    """whisper чує "GPU Instance" замість "Instancing", "slice" замість "slicing":
    для ЗБІГУ з prepared-питаннями зводимо форми слова до спільної основи."""
    if len(w) > 5 and w.endswith("ing"):
        w = w[:-3]
        if len(w) > 2 and w[-1] == w[-2]:
            w = w[:-1]          # clipping -> clip, not clipp
    elif len(w) > 4 and w.endswith("e"):
        w = w[:-1]              # instance -> instanc, slice -> slic
    return w


_DIFF = _stem("difference")


def _match_words(text):
    return [_stem(w) for w in _ordered_tokens(text)]


_PART_RE = re.compile(
    r"(?:^|[?,.;\-]\s*(?:and\s+|or\s+)?)"
    r"(?:what|how|why|when|which|where|who|can|could|does|do|did|is|are|should|would|will)\b")


def _question_parts(text):
    """Скільки окремих питань в одній репліці: "What is X, what is Y, and how...?" = 3."""
    return max(1, len(_PART_RE.findall(text.lower().strip())))


def _split_parts(text):
    """"What is X, what is Y, and how...?" -> ["What is X", "what is Y", "how...?"]."""
    starts = [m.start() for m in _PART_RE.finditer(text.lower())]
    if len(starts) < 2:
        return [text.strip()]
    starts[0] = 0
    out = []
    for a, b in zip(starts, starts[1:] + [len(text)]):
        part = re.sub(r"^[\s?,.;\-]+(?:and\s+|or\s+)?", "", text[a:b], flags=re.I).strip()
        if part:
            out.append(part)
    return out


def _split_lead_in(text):
    """"Let's talk about UI, what is a Canvas?" -> "what is a Canvas?"; "" якщо вступу немає."""
    m = _PART_RE.search(text.lower())
    if not m or m.start() == 0:
        return ""
    return re.sub(r"^[\s?,.;\-]+(?:and\s+|or\s+)?", "", text[m.start():], flags=re.I).strip()


def _max_words(question):
    """Ліміт слів AI-відповіді росте з питанням: 40 слів на три частини
    обрізали відповідь до однієї-двох частин."""
    return config.AI_MAX_WORDS + 20 * (min(_question_parts(question), 3) - 1)


_STEPS_RE = re.compile(
    r"\b(how (do|would|can|could|should|did) (you|i|we)\b|how to\b|what are the steps|"
    r"step by step|walk me through|show me how)")


# "how would you describe X", "how do you understand what X is" = це "що таке X"
# іншими словами, а не "як це зробити"
_DESCRIBE_RE = re.compile(
    r"\bhow (do|would|can|could|should|did) (you|i|we) "
    r"(describe|explain|define|understand|see|think|say|put)\b")


def _wants_steps(question):
    """"How do you set up a blend tree?" = просять кроки; "How does it work?" = ні."""
    low = question.lower()
    return bool(_STEPS_RE.search(low)) and not _DESCRIBE_RE.search(low)


# "чи працював ти з X": так чи ні каже код, AI розповідає лише про X. Раніше це
# діяло тільки для тем із кукбукса; без нього AI сам писав "Yes... I use it for
# shine, glow or water" (Particle System, Addressables, Shader Graph)
_WORKED_RE = re.compile(
    r"\b(have|did) you (ever )?(worked with|work with|used|use|tried|try|baked|bake) ")


def _asks_if_worked(question, has_topic):
    low = question.lower()
    return bool(_PERSONAL_RE.search(low)) and (has_topic or bool(_WORKED_RE.search(low)))


def _answer_words(question, has_topic):
    """Довжина AI-відповіді: коротко за замовчуванням, довше на "розкажи детальніше",
    найдовше на "як це зробити" (кроки), якщо для теми є кукбукс."""
    words = _max_words(question)
    if _asks_if_worked(question, has_topic):
        return EXPERIENCE_WORDS
    if has_topic and _wants_steps(question):
        return words + 30
    if _utterance_kind(question) == "more":
        # "tell me more about its parameters and how to use it": на 69 словах
        # відповідь устигала назвати параметри й не доходила до "як користуватися"
        return EXPERIENCE_WORDS
    return words


def _style_for(question, has_topic):
    """Як AI має будувати відповідь: розповідь по суміжних темах на "чи працював
    ти з X", кроки на "як зробити", інакше звичайні речення."""
    if _asks_if_worked(question, has_topic):
        return STYLE_EXPERIENCE
    if has_topic and _wants_steps(question):
        return STYLE_STEPS
    return STYLE_PLAIN


_BOOKISH_RE = re.compile(
    r"\b(utili[sz]e\w*|leverag\w+|furthermore|moreover|additionally|crucial\w*|robust\w*|"
    r"seamless\w*|ensur\w+|essentially|delve\w*|comprehensive\w*|facilitat\w+|plethora|"
    r"it is worth noting|it is important to note|in order to|in conclusion)\b")
# цифра в назві терміна - не число у відповіді
_NAME_DIGITS_RE = re.compile(r"\b(?:[a-z]*[123]d|9[- ]slic\w+|unity \d+|etc2|astc)\b", re.I)
_EXPERIENCE_RE = re.compile(
    r"\b(?:in|on|at) my (?:last |previous |current |own )?(?:project|job|work|game|team|company|studio)s?\b|"
    r"\bwhen i (?:was|worked)\b|\bi (?:once|recently|previously|personally)\b|"
    r"\bi (?:did|built|made|shipped|profiled|optimized|baked|reduced|fixed|worked|used|"
    r"implemented|created|wrote|set up|cut)\b|"
    r"\bi(?:'ve| have) (?:used|worked|built|made|done|shipped|profiled|optimized|baked)\b")
# так починає відповідь чат-бот, а не людина на співбесіді
_OPENER_RE = re.compile(
    r"^\W*(sure|good question|great question|of course|certainly|absolutely|to continue)\b")


def _strip_opener(text):
    """"Sure, let me go deeper..." -> "Let me go deeper...". Промпт це забороняє,
    але модель усе одно так починала 2 відповіді з 33."""
    m = re.match(r"\W*(?:sure|good question|great question|of course|certainly|absolutely)\b[\s,.!:;—–-]*",
                 text, flags=re.I)
    if not m:
        return text
    rest = text[m.end():]
    return rest[:1].upper() + rest[1:]


_PROJECT_RE = re.compile(
    r"\b(?:in|on|at|from|for) my (?:\w+ ){0,3}(?:work|projects?|games?|job|team)\b|"
    r"\bat work\b|\bin my experience\b|\bcome up in\b", re.I)
_SPINE_RE = re.compile(r"\bspine\b", re.I)


def _strip_projects(text, personal):
    """Викидає речення про власний досвід кандидата, якщо про досвід не питали
    (personal=False), і речення зі словом Spine - завжди. Ігор 2026-10-04:
    "коли не просять - не казати, відповіді тільки по Unity; про свій досвід я
    сам напишу". Кроки в теперішньому часі ("First, I select...") - не досвід.
    Якщо від відповіді нічого не лишається - повертає її як є."""
    kept = [s for s in re.split(r"(?<=[.!?]) +", text)
            if not _SPINE_RE.search(s)
            and (personal or not (_PROJECT_RE.search(s) or _EXPERIENCE_RE.search(s.lower())))]
    return " ".join(kept) if kept else text


def answer_tells(text):
    """Що у відповіді видає машину: 'opener' ("Sure.", "Good question."),
    'bookish' (книжкові слова), 'number' (цифри),
    'experience' (розповідь про власний досвід - звірити з ABOUT ME)."""
    low = text.lower()
    out = []
    if _OPENER_RE.search(low):
        out.append("opener")
    if _BOOKISH_RE.search(low):
        out.append("bookish")
    if re.search(r"\d", _NAME_DIGITS_RE.sub("", text)):
        out.append("number")
    if _EXPERIENCE_RE.search(low):
        out.append("experience")
    return out


def _split_sections(text):
    """Ріже текст на підтеми: заголовок = рядок (не список з '-'), закінчений
    на ':', до 80 символів. -> [(заголовок, текст)]"""
    sections, title, lines = [], None, []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.endswith(":") and len(stripped) <= 80 and not stripped.startswith("-"):
            if title is not None:
                sections.append((title, "\n".join(lines).strip()))
            title, lines = stripped, []
        else:
            lines.append(line)
    if title is not None:
        sections.append((title, "\n".join(lines).strip()))
    return sections


def load_actions():
    try:
        with open(config.ACTIONS_FILE, encoding="utf-8") as f:
            sections = _split_sections(f.read())
    except FileNotFoundError:
        print(f"[INFO] No cookbook file ({config.ACTIONS_FILE})")
        return []
    print(f"[INFO] Loaded {len(sections)} cookbook topics from {config.ACTIONS_FILE}")
    return sections


# питання про ТЕ, про що щойно говорили
_REFERS_RE = re.compile(r"\b(it|that|this|they|them|one|there|those|these)\b")

# слова питання про досвід, які не є назвою того, про що питають
_EXPERIENCE_WORDS = set(_stem(w) for w in (
    "work", "worked", "working", "built", "build", "made", "make", "done", "tried", "try",
    "experience", "real", "project", "production", "ever", "job", "before", "any", "baked"))

# слова, що є майже в кожній темі: самі по собі тему не вибирають
# ("set": до нього зводиться і "Settings", яке стоїть у кожному SUMMARY)
_ACTION_IGNORE = {"unity", "ui", "set", "up",
                  # дієслова питання, а не назва теми: "How do anchors WORK?"
                  "work", "make", "take", "add", "find", "get",
                  # "rect" є і в Full Rect, і в RectMask: саме по собі не Scroll Rect
                  "rect",
                  # слова назви "COMMON RULES FOR ALL UI ELEMENTS", які тему не називають
                  "all", "common", "rule", "rules", "element", "elements"}
_WEAK_NAMES = {"animation"}
# те саме слово, інше значення: шар сортування - не шар аніматора,
# змішування прозорості - не Blend Tree
_OTHER_MEANING_RE = re.compile(
    r"\b(sorting layers?|order in layer|(alpha|additive|multiply) blend\w*|blend modes?)\b", re.I)


def _action_words(text):
    """Слова для вибору теми кукбукса. whisper чує "Unity Profile" замість
    "Profiler" - для тем це одне слово."""
    out = []
    for w in _match_words(text):
        if w == "profiler":
            w = _stem("profile")
        elif len(w) > 4 and w.endswith("ed"):
            # "bake the lighting" має знайти тему "BAKED LIGHTING"
            w = _stem(w[:-1] if w.endswith(("ked", "ced", "led", "ped", "ted")) else w[:-2])
        out.append(w)
    return out


def _merge_pairs(words, vocab):
    """whisper пише "mip maps" / "sprite sheet", у файлі "Mipmap" / "spritesheet":
    сусідню пару зливаємо, якщо злите слово є серед слів prepared-питань."""
    out, i = [], 0
    while i < len(words):
        if i + 1 < len(words) and words[i] + words[i + 1] in vocab:
            out.append(words[i] + words[i + 1])
            i += 2
        else:
            out.append(words[i])
            i += 1
    return out


def _no_unity(words):
    """"What is the Unity Profiler?" і "What is the Profiler?" - одне питання: слово
    "Unity" вголос не кажуть. Лишається, лише коли питання саме про Unity."""
    rest = [w for w in words if w != "unity"]
    return rest or words


# готові питання з розділу про тестове завдання (заповнює load_prepared_answers)
HOME_QUESTIONS = set()


def load_prepared_answers():
    pairs = []
    info_text = ""
    try:
        with open(config.ANSWERS_FILE, encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"[INFO] No prepared answers file ({config.ANSWERS_FILE})")
        return pairs, ""
    # блок знань: ВСЕ до першого "Q: " (старий формат мав маркер "INFO:",
    # новий — просто розділи знань на початку файлу)
    m = re.search(r"\A(.*?)(?=^Q: )", content, flags=re.M | re.S)
    info_text = m.group(1).strip() if m else ""
    blocks = re.findall(r"Q:\s*(.*?)\nA:\s*(.*?)(?=\nQ:|\Z)", content, flags=re.S)
    HOME_QUESTIONS.clear()
    group = ""
    for q, a in blocks:
        # рядок "--- НАЗВА РОЗДІЛУ ---" стоїть після відповіді й потрапляв у її
        # текст (18 відповідей їхали на стрічку з назвою наступного розділу)
        marker = re.search(r"^--- (.*?) ---\s*$", a, flags=re.M)
        if marker:
            a = a[:marker.start()]
        if q.strip() and a.strip():
            pairs.append((q.strip(), a.strip()))
            if "HOME ASSIGNMENT" in group.upper():
                HOME_QUESTIONS.add(q.strip())
        if marker:
            group = marker.group(1)
    print(f"[INFO] Loaded {len(pairs)} prepared answers from {config.ANSWERS_FILE}"
          + (f" (+ INFO block {len(info_text)} chars)" if info_text else ""))
    return pairs, info_text


class SuggestionProvider:
    def __init__(self, api_key, transcriber=None):
        self.transcriber = transcriber
        self.enabled = bool(api_key)
        self.last_question = None
        self.last_ts = None
        self._gen = 0            # покоління питання: +1 на кожне нове питання
        self._busy_gen = None    # яке покоління зараз в роботі в AI
        self.last_shown_answer = None  # щоб та сама відповідь не перезапускала стрічку
        self._q_changed_at = 0.0
        self._fired_for_q = False
        self._last_fired_text = None
        self._prev_fired_q = None
        self._last_epoch = None
        self._retried = False
        self._main_gen = None        # покоління відповіді, що на стрічці або пишеться для неї
        self._main_inflight = False  # ця відповідь ще пишеться (стрічка може бути порожня)
        self._queued_parts = []      # [(epoch, текст)] сказане, поки стрічка зайнята
        self._queued_gens = set()    # покоління, чиї відповіді йдуть у чергу
        self._queued_text = None     # текст відповіді, що чекає в черзі
        self.prepared, self.info_text = load_prepared_answers()
        self._vocab = set(w for q, _ in self.prepared for w in _match_words(q))
        self.prepared_norm = [
            (q, a, _normalize(q), set(_no_unity(_merge_pairs(_match_words(q), self._vocab))),
             _normalize(q).replace(" ", ""))
            for q, a in self.prepared
        ]
        self._parse_info_sections()
        self._load_actions()
        self._personal = False
        self._basis_q = None
        if self.enabled:
            self.client = OpenAI(
                api_key=api_key,
                base_url=BASE_URL,
                default_headers={
                    "x-opencode-session": str(uuid.uuid4()),
                    "User-Agent": "ecoute-assistant/1.0",
                },
            )
            print(f"[INFO] AI suggestions enabled via {BASE_URL} ({config.AI_MODEL})")
        else:
            self.client = None
            print("[INFO] AI suggestions disabled (no API key)")

    def _parse_info_sections(self):
        """Ріже INFO на підтеми ОДИН раз при старті: заголовок = рядок
        (не список з '-'), закінчений на ':', до 80 символів."""
        self.info_about = ""
        self.info_sections = _split_sections(self.info_text or "")
        if not self.info_text:
            return
        # ABOUT ME — окремо: він летить у промпт завжди (ідентичність кандидата)
        kept = []
        for t, x in self.info_sections:
            if "ABOUT ME" in t.upper() and not self.info_about:
                self.info_about = x
            else:
                kept.append((t, x))
        self.info_sections = kept
        # окремі рядки знань для _fact_lines: (корені слів, рядок, чи це про тестове)
        self._fact_index = []
        seen = {}
        for title, text in kept:
            for line in text.splitlines():
                line = line.strip()
                if not line.startswith("- "):
                    continue
                roots = set(_root(w) for w in _normalize(line).split() if len(w) >= 5)
                is_home = "HOME ASSIGNMENT" in title.upper() or bool(
                    _TEST_LINE_RE.search(line) or re.search(r"\bin my (assignment|scene)\b", line, re.I))
                self._fact_index.append((roots, line, is_home))
                for r in roots:
                    seen[r] = seen.get(r, 0) + 1
        # слова, що є в багатьох рядках ("unity", "sprite"), рядок не визначають
        self._fact_common = set(r for r, n in seen.items() if n > 40) | {
            "module", "system", "component", "object", "thing", "unity", "about", "which", "would"}

    def _load_actions(self):
        """Кукбукс: для кожної теми слова назви (вага 3), слова з дужок заголовка
        (вага 2) і слова з SUMMARY (вага 1). Текст уроку в рахунок не йде:
        у 900 словах уроку є майже будь-яке слово."""
        self.actions = load_actions()
        self._last_action = None
        keys = []
        for title, body in self.actions:
            name, _, rest = title.partition("(")
            summary = body.split("LESSON", 1)[0]
            keys.append((_action_words(name), _action_words(rest), _action_words(summary)))
        self._action_vocab = set(w for k in keys for part in k for w in part)
        self._action_keys = [
            tuple(set(_merge_pairs(part, self._action_vocab)) for part in k) for k in keys]
        self._action_names = [k[0] - _ACTION_IGNORE for k in self._action_keys]

    def _action_pick(self, text, prefer=-1):
        """-> індекс теми кукбукса для тексту або -1. Тему вибирає лише слово із
        ЗАГОЛОВКА: два слова з SUMMARY ("turn", "off") тягнули чужу тему.
        При рівному рахунку виграє тема, про яку вже говорили (prefer):
        "transition" є і в аніматорі, і в UI."""
        # складене питання: тему називає ПЕРША частина, далі йдуть побіжні слова
        # ("for a 9-sliced button" -> кнопки, "uses more memory" -> Memory Profiler)
        compound = _question_parts(text) >= 2
        if compound:
            text = _split_parts(text)[0]
        text = _OTHER_MEANING_RE.sub(" ", text)
        words = set(_merge_pairs(_action_words(text), self._action_vocab)) - _ACTION_IGNORE
        best_key, best = None, -1
        for i, (name, rest, summary) in enumerate(self._action_keys):
            title = 3 * len(words & name) + 2 * len(words & (rest - name))
            # тему називає слово з її НАЗВИ або щонайменше два слова з дужок:
            # одне слово з дужок - випадковість ("Timeline" є у темі Profiler,
            # "root" - у темі Animator, "content" - у Scroll Rect)
            if not (words & name) and len(words & rest) < 2:
                continue
            # "animation" є в назвах трьох тем: саме по собі тему не називає
            # ("Texture Sheet Animation", "a building animation" -> Animation Window)
            if words & name <= _WEAK_NAMES and len(words & (rest - name)) < 2:
                continue
            key = (title, i == prefer, len(words & (summary - name - rest)))
            if best_key is None or key > best_key:
                best_key, best = key, i
        # коротка назва з 2-3 слів має збігтися більше ніж наполовину: "Sorting
        # Layer" - не шари аніматора, "Content Size Fitter" - не RectTransform
        if best >= 0 and len(words) <= 3 and not compound:
            name, rest, summary = self._action_keys[best]
            if 2 * len(words & (name | rest | summary)) <= len(words):
                return -1
        return best

    def _experience_opener(self, question):
        """"Have you worked with X?" -> EXPERIENCE_NO, якщо X є в рядку "Not used at
        work" з ABOUT ME; EXPERIENCE_YES, якщо всі слова X є в решті ABOUT ME;
        "" якщо ABOUT ME про X мовчить (тоді відповідь одразу про Unity)."""
        # однина і множина - одне слово: "Sprite Atlases" є в ABOUT ME як "Sprite Atlas"
        def words(text):
            return set(_singular(w) for w in _match_words(text))
        subject = words(question) - set(_singular(w) for w in _EXPERIENCE_WORDS)
        if not subject or not self.info_about:
            return ""
        used = []
        for line in self.info_about.splitlines():
            low = line.lower()
            listed = "not used at work" in low or "only in demos" in low
            if listed and ":" in line:
                items = line.split(":", 1)[1].split(".", 1)[0].split(",")
                if any(words(item) <= subject for item in items if item.strip()):
                    return EXPERIENCE_NO if "not used at work" in low else EXPERIENCE_DEMO
            else:
                used.append(line)
        return EXPERIENCE_YES if subject <= words(" ".join(used)) else ""

    def _raw_words(self, prepared_question):
        """Слова готового питання без зведення до кореня (рахуються один раз)."""
        cache = self.__dict__.setdefault("_raw_cache", {})
        if prepared_question not in cache:
            cache[prepared_question] = set(_ordered_tokens(prepared_question))
        return cache[prepared_question]

    def _tail_prepared(self, question):
        """"Let's talk about UI, what is a Canvas?" -> готова відповідь на саме питання
        без вступу. Відповідь про тестове завдання так не береться: хвіст "what do
        you check?" після "A sprite looks blurry on the device" влучав у "How did
        you check it?" і показував розміри екранів із тестового."""
        tail = _split_lead_in(question)
        hit = self._best_prepared(tail) if tail else None
        if hit and hit[0] in HOME_QUESTIONS and not _HOME_RE.search(question.lower()):
            return None
        return hit

    def _with_opener(self, question, prepared):
        """"Have you used the Frame Debugger?" влучає в готову відповідь "What is
        the Frame Debugger?": спершу так чи ні, далі сама відповідь. Якщо готове
        питання саме про досвід - у ньому вже все сказано."""
        if not _PERSONAL_RE.search(question.lower()) or _PERSONAL_RE.search(prepared[0].lower()):
            return prepared[1]
        opener = self._experience_opener(question)
        return (opener + " " + prepared[1]) if opener else prepared[1]

    def _related_summaries(self, action, limit=3):
        """SUMMARY сусідніх тем кукбукса (спільне слово в назві: Animator ->
        Animator Controller, Animator Layers...). Лише SUMMARY, без уроку:
        AI має про що розповісти далі, а промпт лишається малим."""
        i = self.actions.index(action)
        mine, out = self._action_names[i], []
        for j, (title, body) in enumerate(self.actions):
            if j != i and mine & self._action_names[j]:
                out.append(title + "\n" + body.split("LESSON", 1)[0].replace("SUMMARY", "").strip())
            if len(out) == limit:
                break
        return "\n\n".join(out)

    def _topic_basis(self, question, context=None):
        """Текст, за яким підбираються розділ знань з answers.md і приклади відповідей.
        Для уточнення це питання, якого воно стосується: за словами самого уточнення
        ("its parameters and how to use it") після питання про Prefab Variant
        витягувався розділ про шейдери, і AI відповів про dot product."""
        prev = context[0] if context else None
        if _utterance_kind(question) != "more":
            # коротке уточнення з "it" ("What can go wrong with it?") без власної теми:
            # знання беремо за попереднім питанням разом із цим
            if (prev and len(question.split()) <= 8 and _REFERS_RE.search(question.lower())
                    and self._action_pick(question) < 0 and self._best_prepared(question) is None):
                self._basis_q = prev
                return prev + " " + question
            self._basis_q = question
            return question
        if prev and _utterance_kind(prev) != "more":
            self._basis_q = prev
        return self._basis_q or question

    def _how_to_plan(self, question, prepared):
        """Питають "як зробити", а готова відповідь - лише визначення ("What is X?").
        'glue' = показати визначення одразу, AI дописує кроки з кукбукса;
        'drop' = визначення про ІНШУ тему ("profile a build" -> "What is a Build
        Profile?") - не показувати, відповідає AI; None = нічого не міняти."""
        if prepared is None or not _wants_steps(question) or prepared[0].lower().startswith("how"):
            return None
        # ті самі слова в іншому порядку - інший зміст: "profile a build" не є "Build Profile"
        heard, known = _match_words(question), _match_words(prepared[0])
        common = [w for w in known if w in heard]
        if len(common) >= 2 and [w for w in heard if w in common] != common:
            return "drop"
        topic = self._action_pick(question)
        # теми кукбукса немає - визначення все одно лише початок відповіді на "як зробити"
        if topic < 0:
            return "glue"
        return "glue" if self._action_pick(prepared[0]) == topic else "drop"

    def _relevant_action(self, question, context=None):
        """Тема кукбукса для питання -> (заголовок, текст) або None.
        Уточнення без власної теми ("tell me more", "how do you set it up",
        "what can go wrong with it") бере тему, про яку говорили щойно."""
        if not self.actions:
            return None
        prev = self._action_pick(context[0]) if context and context[0] else -1
        if prev < 0 and self._last_action in self.actions:
            prev = self.actions.index(self._last_action)
        i = self._action_pick(question, prefer=prev)
        low = question.lower()
        if _utterance_kind(question) == "more":
            # "Tell me more about its parameters": тема - попередня. Власну бере лише
            # коли НАЗВАНО тему ("more about the Animator layers"); слово з дужок
            # заголовка ("parameters" у темі про кнопки) тему не міняє
            words = set(_merge_pairs(_action_words(question), self._action_vocab))
            if i < 0 or not (words & self._action_keys[i][0]):
                i = prev
        elif i < 0 and (_REFERS_RE.search(low) or _wants_steps(low)):
            # "How do you make a character wave while walking?" одразу після питання
            # про шари аніматора: своєї теми немає, але це питання "як зробити" по ній
            i = prev
        return self.actions[i] if i >= 0 else None

    def _relevant_info(self, question, max_sections=2):
        """ABOUT ME завжди + 1-2 підтеми, найближчі до теми питання.
        Промпт ~3-5KB замість 198KB → швидкий prefill."""
        if not self.info_text:
            return ""
        qn = _normalize(question)
        qwords = set(w for w in qn.split() if len(w) >= 4)
        qnames = set(_root(w) for w in qwords)
        home = bool(_HOME_RE.search(question.lower()))
        scored = []
        for title, text in self.info_sections:
            if "HOME ASSIGNMENT" in title.upper() and not home:
                continue
            # питання НАЗИВАЄ розділ ("parameters of an Image" -> COMPONENT: IMAGE):
            # це важить більше за будь-які спільні слова в тексті. Тоді текст
            # розділу рахуємо весь - він розводить розділи з однаковою назвою
            # (три розділи PARTICLE SYSTEM: в якому з них Emission)
            named = len(qnames & _title_words(title))
            tn = _normalize(title + " " + (text if named else text[:800]))
            twords = set(w for w in tn.split() if len(w) >= 4)
            overlap = len(qwords & twords - _PIECE_WORDS) + 10 * named
            if overlap == 0:
                overlap = difflib.SequenceMatcher(None, qn, _normalize(title)).ratio()
            scored.append((overlap, text))
        scored.sort(key=lambda x: x[0], reverse=True)
        out = ""
        # ABOUT ME бачить AI лише коли питають про досвід: модель не може
        # переказати роботу кандидата, якщо її не бачить
        if self.info_about and self._personal:
            out += f"Candidate background (ABOUT ME):\n{self.info_about}\n\n"
        for _, text in scored[:max_sections]:
            if text and not home:
                # рядки "In the test: ... seven direct variants" стоять і в загальних розділах
                text = "\n".join(l for l in text.splitlines() if not _TEST_LINE_RE.search(l))
            if text:
                out += text.strip() + "\n\n"
        facts = [l for l in self._fact_lines(question) if l not in out]
        if facts:
            out += "Facts that match the question:\n" + "\n".join(facts) + "\n\n"
        return out

    def _fact_lines(self, question, limit=4):
        """Окремі рядки знань, що збігаються з питанням двома і більше змістовими
        словами. Розділ вибирається за першими 800 символами, тож факт у глибині
        довгого розділу до AI не доходив: про Resources він домислив "loads into
        memory at launch", хоча правильний рядок у файлі був."""
        home = bool(_HOME_RE.search(question.lower()))
        words = set(_root(w) for w in _normalize(question).split() if len(w) >= 5) - self._fact_common
        if len(words) < 2:
            return []
        scored = []
        for i, (roots, line, is_home) in enumerate(self._fact_index):
            hits = len(words & roots)
            if hits >= 2 and (home or not is_home):
                scored.append((-hits, i, line))
        scored.sort()
        return [line for _, _, line in scored[:limit]]

    def _best_prepared(self, question, part=False):
        """Рахунок = F1 по змістових словах: скільки слів prepared-питання
        прозвучало (recall) І яку частку почутого воно покриває (precision).
        Сам recall стріляв хибно: 3 спільні слова з 6 давали 0.5 навіть коли
        почуте питання було про інше (Q095 lags -> blurry, Q109 mesh)."""
        qn = _normalize(question)
        heard = _no_unity(_merge_pairs(_match_words(question), self._vocab))
        qt = set(heard)
        qsq = qn.replace(" ", "")
        # позиція слова в почутому: при рівному рахунку виграє prepared про те,
        # що названо ПЕРШИМ ("pivot on a sprite" -> Pivot, не Sprite)
        order = {}
        for i, w in enumerate(heard):
            order.setdefault(w, i)
        # "how would you describe X" - теж прохання про визначення, хоч "what" і немає
        what_asked = "what" in qn.split() or bool(_DESCRIBE_RE.search(question.lower()))
        raw = set(_ordered_tokens(question))
        best_key, best, best_ov, best_ptok = (0.0, 0.0, False, 0, 0.0), None, 0, set()
        for qorig, aorig, qnorm, ptok, psq in self.prepared_norm:
            ov = len(qt & ptok)
            f1 = 0.0
            # коротке prepared-питання має прозвучати ПОВНІСТЮ: "built-in render
            # pipeline" має 2 слова з 3 від "universal render pipeline", але це
            # інша тема (заміна головного слова = інше питання)
            # prepared-питання з ОДНИМ змістовим словом збігається, лише коли це
            # слово названо першим: "component in Unity" -> Component, але
            # "has exit time" -/-> "What would you do with more time?"
            lone_tail = len(ptok) == 1 and len(qt) > 1 and ov and order[next(iter(qt & ptok))] != 0
            # питають про РІЗНИЦЮ, а prepared — це визначення одного з двох:
            # "difference between a Sprite Atlas and a spritesheet" -/-> Sprite Atlas
            wants_diff = _DIFF in qt and _DIFF not in ptok
            if ov and not lone_tail and not wants_diff and not (len(ptok) <= 3 and ov < len(ptok)):
                recall, precision = ov / len(ptok), ov / len(qt)
                f1 = 2 * precision * recall / (precision + recall)
            # майже дослівний повтор, стійкий до злитих/розбитих слів
            # ("sprite sheet" = "spritesheet", "mip map" = "mipmap")
            ratio = difflib.SequenceMatcher(None, qsq, psq).ratio()
            score = max(f1, ratio if ratio >= 0.9 else 0.0)
            first = min((order[w] for w in qt & ptok), default=99)
            # рівний рахунок: питали "what ... is" - виграє визначення ("What is a
            # ScriptableObject?"), а не "When do you use ScriptableObjects?"
            same_kind = what_asked and qnorm.startswith("what")
            # "Batching" і "Batches" мають один корінь: виграє питання, де слово
            # сказано буква в букву
            exact = len(raw & self._raw_words(qorig)) if score else 0
            key = (round(score, 3), -first, same_kind, exact, ratio)
            if key > best_key:
                best_key, best, best_ov, best_ptok = key, (qorig, aorig), ov, ptok
        if best_key[0] < config.MATCH_THRESHOLD:
            return None
        # почуте повністю називає тему кукбукса, а prepared-питання покриває лише
        # її частину: "What are Animator layers?" показувало "What is an Animator?".
        # Таке йде в AI з кукбуксом
        if best_key[0] < 0.9:
            names = set(_merge_pairs(heard, self._action_vocab))
            if any(n and n <= names and n - best_ptok for n in self._action_names):
                return None
        # питають про частину ("the Emission module of a Particle System"), а
        # prepared - визначення цілого ("What is a Particle System?")
        if best_key[0] < 0.9 and _PIECE_RE.search(qn) and not _PIECE_RE.search(_normalize(best[0])):
            return None
        # питають про ДОСВІД кандидата, а не про термін: "What shaders have you
        # made?" показувало визначення "What is a Shader?". Таке йде в AI з
        # фактами про кандидата, якщо немає готової відповіді саме на це питання
        if best_key[0] < 0.9 and _PERSONAL_RE.search(question.lower()):
            return None
        # частина складного питання: одного спільного слова мало, якщо частина
        # не складається лише з нього ("what do you check first" -> "How did
        # you check it?" - хибно; "what is overdraw" -> Overdraw - вірно)
        if part and best_ov < 2 and len(qt) != 1 and best_key[4] < 0.9:
            return None
        # питання з 2-3 частин: одна prepared-відповідь закриває лише одну з них
        # (Prefab + Variant + "коли" -> показано тільки Variant). Таке йде в AI,
        # якщо тільки prepared-питання саме не є цим складним питанням
        if best_key[0] < 0.9 and _question_parts(question) >= 2:
            return None
        return best

    def _clean(self, text):
        """Що з тексту AI йде на стрічку: без зірочок, без вступу чат-бота, без
        речень про проєкти і Spine. Те саме для стріму і для фінального тексту -
        інакше речення з'явилось би у стрімі й зникло наприкінці."""
        return _strip_projects(_strip_opener(text.replace("*", "")), self._personal)

    def _similar_prepared(self, question, k=3):
        """ТОП-k найближчих prepared-відповідей — контекст для AI."""
        qn = _normalize(question)
        home = bool(_HOME_RE.search(question.lower()))
        scored = [
            (difflib.SequenceMatcher(None, qn, qnorm).ratio(), qorig, aorig)
            for qorig, aorig, qnorm, _, _ in self.prepared_norm
            if home or qorig not in HOME_QUESTIONS
        ]
        scored.sort(key=lambda x: x[0], reverse=True)
        return [(q, a) for _, q, a in scored[:k]]

    def _extract_speaker_text(self, transcript):
        for line in transcript.splitlines():
            if line.startswith("Speaker:"):
                return line[len("Speaker:"):].strip().strip("[]").strip()
        return None

    def maybe_update(self, question, display, phrase_epoch=None, speaker_last_ts=None):
        question = (question or "").strip()
        if not question:
            return

        if phrase_epoch is not None and phrase_epoch != self._last_epoch:
            # нове питання (нова фраза) — дозволяємо показ заново
            self._last_epoch = phrase_epoch
            self._last_fired_text = None
            # нове питання: старий AI-запит (якщо висить) — застарілий,
            # нове покоління дозволяє запустити новий запит не чекаючи старий
            self._gen += 1
            # діагностика: стан на момент початку нової фрази
            sil = "?"
            if speaker_last_ts is not None:
                sil = f"{(datetime.utcnow() - speaker_last_ts).total_seconds():.1f}s"
            print(f"[MATCH] new phrase epoch={phrase_epoch}, silence={sil}, q={question[:60]!r}")

        # сигнал завершеності = АУДІО-тиша 3с: дихання/задуми посеред питання
        # коротші за 3с, тому часткові фрази не стріляють
        if speaker_last_ts is not None:
            silence_s = (datetime.utcnow() - speaker_last_ts).total_seconds()
            if silence_s < QUESTION_SILENCE_S:
                return  # спікер ще говорить (недавно був аудіо) — чекати

        # повторний показ тільки коли питання РЕАЛЬНО виросло
        # (дрібні шматки/повтори від whisper не рестартують стрічку)
        if self._last_fired_text is not None:
            old_n = len(self._last_fired_text.split())
            new_n = len(question.split())
            if new_n - old_n < REFIRE_MIN_NEW_WORDS:
                return
        self._last_fired_text = question
        print(f"[MATCH] question complete: {question[:250]}")
        # буфер питання: після відстрілу далі з чистого
        if self.transcriber is not None:
            self.transcriber.clear_speaker_buffer()

        kind = _utterance_kind(question)
        if kind == "ack":
            # "Okay, great, thank you": раніше це йшло в AI і збивало стрічку
            print("[MATCH] acknowledgement ignored")
            return
        if _is_money_question(question) and self._best_prepared(question) is None:
            # початок рядка той самий, що в підтвердження: тест-ранер читає його як "ignored"
            print("[MATCH] acknowledgement ignored (money question - the candidate answers himself)")
            return
        # черга (config.RIBBON_QUEUE): стрічка зайнята або перша відповідь ще
        # пишеться - нове питання не перериває, а стає в чергу. Усе сказане за цей
        # час склеюється в одне питання
        if self._queue_on(display):
            if display.busy() or self._main_inflight:
                question = self._merge_queued(question, phrase_epoch)
                kind = _utterance_kind(question)
                self._queued_gens.add(self._gen)
                display.reserve(self._gen)
                print(f"[QUEUE] ribbon is busy, queued: {question[:200]}")
            else:
                self._queued_parts = []
                self._main_gen = self._gen
        # що було сказано до цього: AI потрібне для "tell me more" / "why?"
        context = (self._prev_fired_q, self.last_shown_answer)
        prev_q, self._prev_fired_q = self._prev_fired_q, question
        prepared = None if kind == "more" else self._best_prepared(question)
        if prepared is None and kind == "question" and _question_parts(question) == 1:
            # вступ перед питанням: "Let's talk about UI, what is a Canvas?" —
            # слова вступу заважають збігу, тому пробуємо саме питання без нього
            prepared = self._tail_prepared(question)
        if prepared is not None and prepared[1] == self.last_shown_answer:
            same_q = difflib.SequenceMatcher(
                None, _normalize(prev_q or ""), _normalize(question)).ratio() >= 0.85
            if same_q:
                return  # те саме питання ще раз — не рестартуємо стрічку
            # ІНШЕ питання влучило в щойно показану відповідь ("addressable
            # screw" після "What are Addressables?") — це сусідня тема, а не
            # повтор: раніше тут була тиша, тепер відповідає AI
            print("[MATCH] same answer for a different question -> AI")
            prepared = None
        how_to = self._how_to_plan(question, prepared)
        definition = prepared[1] if how_to == "glue" else ""
        if how_to:
            prepared = None
        if prepared is not None:
            shown = self._with_opener(question, prepared) if kind == "question" else prepared[1]
            print(f"[MATCH] fired prepared answer: {shown}")
            # тема для наступних уточнень = тема ЦЬОГО питання (або жодної):
            # інакше "tell me more" після overdraw тягнуло б кукбукс про Canvas
            self._last_action = self._relevant_action(question)
            self._set_text(display, shown, restart=True, gen=self._gen)
            return

        # питання з кількох частин: готові відповіді на частини показуємо
        # одразу підряд, у AI йде лише те, на що готової немає
        if (not definition and kind == "question"
                and _asks_if_worked(question, self._relevant_action(question, context) is not None)):
            # "Have you worked with the Animator?": так чи ні одразу на стрічку,
            # AI дописує лише про саму тему
            definition = self._experience_opener(question)
        if definition:
            glued, rest = definition, [question]
        else:
            glued, rest = ("", []) if kind == "more" else self._glue_prepared(question)
        if glued:
            print(f"[MATCH] glued prepared answers; parts left for AI: {len(rest)}")
            print(f"[MATCH] fired prepared answer: {glued}")
            self._set_text(display, glued, restart=True, gen=self._gen)
            if not rest:
                return

        if not self.enabled:
            return  # збігу немає, AI вимкнений — нічого не показуємо

        if self._busy_gen == self._gen:
            return  # це ж питання вже в роботі
        self._busy_gen = self._gen
        # НЕ показуємо "generating answer..." — стрічка мовчить, поки
        # відповідь реально не готова (без миготіння)
        if self._gen == self._main_gen:
            self._main_inflight = True
        threading.Thread(target=self._run_fetch, args=(question, display, self._gen),
                         kwargs={"prefix": glued, "only": rest, "context": context}, daemon=True).start()

    def _run_fetch(self, question, display, gen, **kwargs):
        try:
            self._fetch(question, display, gen, **kwargs)
        finally:
            if gen == self._main_gen:
                self._main_inflight = False

    # ---------- черга відповідей (AnswerDeck) ----------
    def _queue_on(self, display):
        return getattr(config, "RIBBON_QUEUE", False) and hasattr(display, "reserve")

    def _stale(self, gen):
        """Відповідь уже нікому не потрібна: прийшло нове питання. З чергою головна
        відповідь (та, що на стрічці або пишеться для неї) живе далі - нове питання
        її не вбиває, застаріває лише попередня відповідь у черзі."""
        return gen != self._gen and gen != self._main_gen

    def promoted(self, gen):
        """Черга показала відповідь: тепер головна вона, наступне питання - з чистого."""
        self._main_gen = gen
        self._queued_parts = []
        if self._queued_text:
            self.last_shown_answer = self._queued_text
        self._queued_text = None

    def _merge_queued(self, question, epoch):
        """Усе, що інтерв'юер сказав під час стрічки, - одне питання. Та сама фраза,
        що виросла (той самий epoch), замінює свою попередню версію."""
        if self._queued_parts and epoch is not None and self._queued_parts[-1][0] == epoch:
            self._queued_parts[-1] = (epoch, question)
        else:
            self._queued_parts.append((epoch, question))
        # не більше трьох останніх реплік: черга, що застрягла, не роздує питання
        self._queued_parts = self._queued_parts[-QUEUE_MAX_REMARKS:]
        return " ".join(q for _, q in self._queued_parts)

    def _glue_prepared(self, question):
        """-> (готові відповіді на частини підряд, частини без готової відповіді)."""
        parts = _split_parts(question)
        if len(parts) < 2:
            return "", []
        answers, rest = [], []
        for i, part in enumerate(parts):
            # "does IT reduce draw calls", "which ONE is cheaper": без першої
            # частини незрозуміло про що мова — таке вирішує AI з повним питанням
            refers_back = i > 0 and re.search(r"\b(it|its|they|them|both|one|each)\b", part.lower())
            hit = None if refers_back else self._best_prepared(part, part=True)
            # "tell me more about the Animator, what parameters...": відповідь
            # про Animator щойно була на стрічці — не показуємо її вдруге
            if hit is not None and hit[1] in (self.last_shown_answer or ""):
                hit = None
            if hit is None:
                rest.append(part)
            elif hit[1] not in answers:
                answers.append(hit[1])
        return " ".join(answers), (rest if answers else [])

    def _call_api(self, messages, max_tokens, timeout_s=25):
        """Жорсткий дедлайн: SDK timeout проксі ігнорує (keep-alive), тому
        тримаємо запит у daemon-потоку і просто чекаємо рівно timeout_s.
        25с = повільна відповідь сервера (13-20с) все одно показується,
        як і було до дедлайнів."""
        result = {}

        def _run():
            try:
                result["r"] = self.client.chat.completions.create(
                    model=config.AI_MODEL,
                    messages=messages,
                    max_tokens=max_tokens,
                    extra_body={"reasoning_effort": "low"},
                )
            except Exception as e:
                result["e"] = e

        th = threading.Thread(target=_run, daemon=True)
        t0 = time.time()
        th.start()
        th.join(timeout=timeout_s)
        if th.is_alive():
            raise TimeoutError(f"AI call exceeded {timeout_s}s (latency {time.time() - t0:.1f}s)")
        if "e" in result:
            raise result["e"]
        return result["r"]

    def _stream_answer(self, messages, display, gen, prefix=""):
        """Стрімінг: відповідь показується у стрічці ПО МІРІ генерації.
        Повертає повний текст або None (якщо стрім не дав контенту)."""
        box = {}

        def _worker():
            try:
                t0 = time.time()
                stream = self.client.chat.completions.create(
                    model=config.AI_MODEL,
                    messages=messages,
                    max_tokens=config.AI_MAX_TOKENS,
                    extra_body={"reasoning_effort": "low"},
                    stream=True,
                )
                box["stream"] = stream
                acc = ""
                got_first = False
                last_push = 0.0
                first_push_done = [False]
                for chunk in stream:
                    if self._stale(gen):
                        # прийшло нове питання — стрім застарів, не показуємо
                        return
                    now = time.time()
                    if not got_first and now - t0 > STREAM_FIRST_WORD_S:
                        # так довго без жодного слова — сервер завис, марно чекати
                        print(f"[AI] stream: no content in {STREAM_FIRST_WORD_S}s, falling back")
                        return
                    piece = ""
                    if chunk.choices:
                        delta = chunk.choices[0].delta
                        piece = (delta.content or "") if delta else ""
                    if piece:
                        got_first = True
                        acc += piece
                        if now - last_push >= 0.25:
                            last_push = now
                            # перший пуш = нова відповідь -> рестарт стрічки
                            r = not first_push_done[0]
                            first_push_done[0] = True
                            # prefix уже на стрічці: дописуємо, а не рестартуємо
                            self._set_text(display, prefix + self._clean(acc), restart=r and not prefix, gen=gen)
                if acc.strip():
                    box["a"] = acc.strip()
            except Exception as e:
                print(f"[AI] stream error: {e!r}")
            finally:
                _close(box.get("stream"))

        def _close(stream):
            # кинутий стрім треба ЗАКРИТИ: інакше сервер генерує далі, запити
            # накопичуються, а під 5 одночасними перше слово йде 20-39с замість 1.4с
            try:
                if stream is not None:
                    stream.close()
            except Exception:
                pass

        th = threading.Thread(target=_worker, daemon=True)
        th.start()
        th.join(timeout=35)
        if th.is_alive():
            print("[AI] stream stalled, abandoned")
            _close(box.get("stream"))
            return None
        return box.get("a") or None

    def _fetch(self, question, display, gen, prefix="", only=None, context=None):
        """prefix = уже показані готові відповіді; only = частини питання,
        на які ще треба відповісти (AI дописує їх після prefix);
        context = (попереднє питання, попередня відповідь на стрічці)."""
        prefix = (prefix + " ") if prefix else ""
        # про досвід питали прямо - тоді проєкти кандидата у відповіді доречні
        self._personal = bool(_PERSONAL_RE.search(question.lower()))
        earlier = ""
        if context and context[0] and context[1]:
            earlier = (
                "Earlier in this interview the interviewer asked: \"" + context[0] + "\"\n"
                "and the candidate answered: \"" + context[1] + "\"\n"
                "If the new question refers back to that (tell me more, in more detail, why, an example, "
                "it, that), continue from there with NEW details and do not repeat what was already said. "
                "Otherwise ignore it.\n\n")
        try:
            # контекст: схожі prepared-відповіді кандидата (уже завантажені
            # при старті — читання файлу не витрачає час під час інтерв'ю)
            # уточнення бере знання і приклади за питанням, якого воно стосується
            basis = self._topic_basis(question, context)
            examples = self._similar_prepared(basis)
            examples_text = "\n\n".join(f"Q: {q}\nA: {a}" for q, a in examples)
            info_block = ""
            if self.info_text:
                info_block = (
                    f"Candidate background info (facts you may use):\n"
                    f"{self.info_text}\n\n"
                )
            # кукбукс: тема самого питання, далі тема попереднього питання, далі
            # (друге-третє "tell me more" підряд) тема, з якої вже відповідали
            action = self._relevant_action(question, context)
            self._last_action = action
            style = _style_for(question, action is not None)
            if style == STYLE_EXPERIENCE:
                # про тему є кукбукс: AI розповідає лише про Unity, ABOUT ME не бачить,
                # речення про роботу кандидата викидаються
                self._personal = False
            max_words = _answer_words(" ".join(only) if only else question, action is not None)
            action_block = ""
            if action is not None:
                print(f"[AI] cookbook topic: {action[0]}")
                action_block = ACTION_NOTE + action[0] + "\n" + action[1] + "\n\n"
                if style == STYLE_EXPERIENCE:
                    related = self._related_summaries(action)
                    if related:
                        action_block += "Related topics, in short:\n" + related + "\n\n"
            if only:
                # AI має бачити вже сказане: без цього він дописав "Yes, Bloom is a
                # renderer feature" одразу після готової відповіді, де сказано навпаки
                question += ("\n\nThe candidate has ALREADY said this, word for word: \"" + prefix.strip() + "\"\n"
                             "Treat it as true and never contradict it. Do not repeat it. "
                             "Continue the answer with ONLY this remaining part: " + " ".join(only))
            if self._personal:
                style += " " + RULE_HONEST
            elif not _HOME_RE.search(basis.lower()):
                style += " " + RULE_NO_I
            system = SYSTEM_PROMPT_TEMPLATE.format(max_words=max_words, style=style)
            # з кукбуксом промпт уже великий: з answers.md досить однієї підтеми
            info_block = self._relevant_info(basis, max_sections=1 if action else 2)
            messages = [
                {"role": "system", "content": system},
                {
                    "role": "user",
                    "content": (
                        f"{info_block}"
                        f"{action_block}"
                        f"Candidate's prepared answers for similar questions:\n"
                        f"{examples_text}\n\n"
                        f"{earlier}"
                        f"Interviewer's question: {question}"
                    ),
                },
            ]
            t0 = time.time()
            answer = self._stream_answer(messages, display, gen, prefix)
            # стрім уже ВИВІВ початок цієї відповіді на стрічку
            streamed = bool(answer)
            if not answer:
                # стрім не дав контенту — повний запит як раніше
                try:
                    resp = self._call_api(messages, config.AI_MAX_TOKENS)
                except TimeoutError:
                    # сервер нестабільний (upstream timeout) — один ретрай,
                    # 50с тиші краще ніж нічого
                    print("[AI] timeout, retrying once...")
                    resp = self._call_api(messages, config.AI_MAX_TOKENS)
                msg = resp.choices[0].message
                answer = (msg.content or "").strip()
                n_words = len(answer.split())
                # ретрай ТОЛЬКИ коли відповідь реально неповна: пуста або значно
                # коротша за ліміт. finish=length з 40 слів = нормальна відповідь,
                # ретрай тут лише подвоював час (33с замість 3с)
                if n_words < max(12, config.AI_MAX_WORDS - 5) and not self._retried:
                    print(f"[AI] answer too short ({n_words} words), retrying with bigger budget...")
                    self._retried = True
                    try:
                        resp = self._call_api(messages, 900)
                        msg = resp.choices[0].message
                        answer = (msg.content or "").strip() or answer
                    finally:
                        self._retried = False
                if not answer:
                    # reasoning з'їв усі токени — НЕ ліпимо відповідь зі сміття,
                    # стрічка мовчить краще ніж покаже обірване слово
                    print("[AI] empty content (reasoning ate the token budget), skipping")
                    return
            # відповідь НЕ обрізається (Ігор 2026-10-04): кількість слів - побажання для
            # AI, а не правило. Обрізання по реченню з'їло четвертий тип Image
            answer = self._clean(answer)
            print(f"[AI] latency {time.time() - t0:.1f}s, words {len(answer.split())}")
            if answer:
                print(f"[AI] dynamic answer: {answer}")
        except Exception as e:
            print(f"[AI] error: {e!r}")
            # таймаут не блокує ретрай: питання може вирости — дозволити новий запит
            if self._busy_gen == gen:
                self._busy_gen = None
            return

        # поки генерували — прийшло нове питання: відповідь застаріла
        if self._stale(gen):
            print("[AI] stale answer dropped (new question arrived)")
            return

        # після стріму повний текст лише ДОПОВНЮЄ стрічку. Раніше він ішов як нова
        # відповідь: стрім пушить раз на 0.25с, останні слова в пуш не потрапляли,
        # повний текст відрізнявся від показаного - і стрічка їхала з початку
        self._set_text(display, prefix + answer, restart=not prefix and not streamed, gen=gen)

    def _set_text(self, display, text, restart=False, gen=None):
        if self._queue_on(display) and gen in self._queued_gens and gen != self._main_gen:
            # відповідь у черзі ще не показана: "щойно було на стрічці" - не про неї
            self._queued_text = text
        else:
            self.last_shown_answer = text
        text = text.replace("\n", "   ")
        if self._queue_on(display):
            try:
                display.after(0, display.write, gen, text, restart, gen in self._queued_gens)
            except Exception:
                pass
            return
        try:
            # restart=True (нова відповідь) = рестарт стрічки зі свіжого заїзду;
            # стрімінг-пуши того ж розрахунку = оновлення тексту на лету
            fn = display.start if restart else display.update_text
            display.after(0, fn, text)
        except Exception:
            pass
