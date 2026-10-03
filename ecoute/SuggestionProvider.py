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

SYSTEM_PROMPT_TEMPLATE = (
    "You are helping a candidate during a live technical job interview (Unity / Technical Artist role). "
    "You receive the interviewer's latest spoken question, plus the candidate's background info "
    "and their own prepared answers for similar questions — "
    "reuse their facts, style and tone (first person, confident, direct). "
    "Reply in the SAME language as the question (English or Ukrainian). "
    "The answer must be about {max_words} words — a complete, confident reply that "
    "fully answers ALL parts of the question. "
    "Use SIMPLE everyday words and short clear sentences — the candidate reads it aloud fast. "
    "Avoid difficult vocabulary and abbreviations you can't say. "
    "The question comes from speech recognition and may contain misheard words — "
    "answer about the closest real Unity term and never comment on the wording. "
    "Do not use lists, headings or markdown — plain sentences only. "
    "Output ONLY the answer text, nothing else."
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
}

# репліки-підтвердження: інтерв'юер не питає, а реагує на відповідь
_ACK = {
    "good", "nice", "perfect", "fine", "see", "got", "understood", "interesting",
    "make", "sense", "right", "thank", "clear", "awesome", "correct", "exactly",
    "hmm", "mhm", "mm", "hm", "oh", "ah", "wow", "true", "agree", "agreed",
    "mmhmm", "mhmm", "mmm", "uhhuh", "uh", "huh", "yep", "yup", "aha", "noted",
}
_MORE_RE = re.compile(
    r"\b(more|detail|details|elaborate|deeper|example|examples|why|expand|go on|continue|"
    r"go into|explain|how so|what else|anything else|specifically|such as)\b")


_BACK_RE = re.compile(
    r"^(?:(?:and|so|but|okay|ok)[\s,]+)*(?:(?:how|why|when|where)\s+)?"
    r"(?:does|do|did|is|are|was|can|could|will|would|should)\s+"
    r"(?:you\s+\w+\s+)?(?:it|they|them|that|this|one|those|these)\b")


def _utterance_kind(text):
    """'ack'  = "Okay, great, thank you" — нічого не показуємо;
    'more' = "Tell me more" / "Why?" без власної теми — продовження попередньої відповіді;
    'question' = усе інше."""
    # "Does it reduce draw calls?", "When would you use one?": питання про ТЕ,
    # про що щойно говорили. Без попередньої теми prepared-збіг тут хибний
    # (після SRP Batcher показало "How do you reduce draw calls?")
    if _BACK_RE.match(text.lower().strip()):
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
    for q, a in blocks:
        if q.strip() and a.strip():
            pairs.append((q.strip(), a.strip()))
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
        self.prepared, self.info_text = load_prepared_answers()
        self._vocab = set(w for q, _ in self.prepared for w in _ordered_tokens(q))
        self.prepared_norm = [
            (q, a, _normalize(q), set(_merge_pairs(_ordered_tokens(q), self._vocab)),
             _normalize(q).replace(" ", ""))
            for q, a in self.prepared
        ]
        self._parse_info_sections()
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
        self.info_sections = []
        if not self.info_text:
            return
        current_title, current_lines = None, []
        for line in self.info_text.splitlines():
            stripped = line.strip()
            is_header = (stripped.endswith(":") and len(stripped) <= 80
                         and not stripped.startswith("-"))
            if is_header:
                if current_title is not None:
                    self.info_sections.append((current_title, "\n".join(current_lines).strip()))
                current_title, current_lines = stripped, []
            else:
                current_lines.append(line)
        if current_title is not None:
            self.info_sections.append((current_title, "\n".join(current_lines).strip()))
        # ABOUT ME — окремо: він летить у промпт завжди (ідентичність кандидата)
        kept = []
        for t, x in self.info_sections:
            if "ABOUT ME" in t.upper() and not self.info_about:
                self.info_about = x
            else:
                kept.append((t, x))
        self.info_sections = kept

    def _relevant_info(self, question, max_sections=2):
        """ABOUT ME завжди + 1-2 підтеми, найближчі до теми питання.
        Промпт ~3-5KB замість 198KB → швидкий prefill."""
        if not self.info_text:
            return ""
        qn = _normalize(question)
        qwords = set(w for w in qn.split() if len(w) >= 4)
        scored = []
        for title, text in self.info_sections:
            tn = _normalize(title + " " + text[:800])
            twords = set(w for w in tn.split() if len(w) >= 4)
            overlap = len(qwords & twords)
            if overlap == 0:
                overlap = difflib.SequenceMatcher(None, qn, _normalize(title)).ratio()
            scored.append((overlap, text))
        scored.sort(key=lambda x: x[0], reverse=True)
        out = ""
        if self.info_about:
            out += f"Candidate background (ABOUT ME):\n{self.info_about}\n\n"
        for _, text in scored[:max_sections]:
            if text:
                out += text.strip() + "\n\n"
        return out

    def _best_prepared(self, question, part=False):
        """Рахунок = F1 по змістових словах: скільки слів prepared-питання
        прозвучало (recall) І яку частку почутого воно покриває (precision).
        Сам recall стріляв хибно: 3 спільні слова з 6 давали 0.5 навіть коли
        почуте питання було про інше (Q095 lags -> blurry, Q109 mesh)."""
        qn = _normalize(question)
        heard = _merge_pairs(_ordered_tokens(question), self._vocab)
        qt = set(heard)
        qsq = qn.replace(" ", "")
        # позиція слова в почутому: при рівному рахунку виграє prepared про те,
        # що названо ПЕРШИМ ("pivot on a sprite" -> Pivot, не Sprite)
        order = {}
        for i, w in enumerate(heard):
            order.setdefault(w, i)
        best_key, best, best_ov = (0.0, 0.0, 0.0), None, 0
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
            if ov and not lone_tail and not (len(ptok) <= 3 and ov < len(ptok)):
                recall, precision = ov / len(ptok), ov / len(qt)
                f1 = 2 * precision * recall / (precision + recall)
            # майже дослівний повтор, стійкий до злитих/розбитих слів
            # ("sprite sheet" = "spritesheet", "mip map" = "mipmap")
            ratio = difflib.SequenceMatcher(None, qsq, psq).ratio()
            score = max(f1, ratio if ratio >= 0.9 else 0.0)
            first = min((order[w] for w in qt & ptok), default=99)
            key = (round(score, 3), -first, ratio)
            if key > best_key:
                best_key, best, best_ov = key, (qorig, aorig), ov
        if best_key[0] < config.MATCH_THRESHOLD:
            return None
        # частина складного питання: одного спільного слова мало, якщо частина
        # не складається лише з нього ("what do you check first" -> "How did
        # you check it?" - хибно; "what is overdraw" -> Overdraw - вірно)
        if part and best_ov < 2 and len(qt) != 1 and best_key[2] < 0.9:
            return None
        # питання з 2-3 частин: одна prepared-відповідь закриває лише одну з них
        # (Prefab + Variant + "коли" -> показано тільки Variant). Таке йде в AI,
        # якщо тільки prepared-питання саме не є цим складним питанням
        if best_key[0] < 0.9 and _question_parts(question) >= 2:
            return None
        return best

    def _similar_prepared(self, question, k=3):
        """ТОП-k найближчих prepared-відповідей — контекст для AI."""
        qn = _normalize(question)
        scored = [
            (difflib.SequenceMatcher(None, qn, qnorm).ratio(), qorig, aorig)
            for qorig, aorig, qnorm, _, _ in self.prepared_norm
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
        # що було сказано до цього: AI потрібне для "tell me more" / "why?"
        context = (self._prev_fired_q, self.last_shown_answer)
        prev_q, self._prev_fired_q = self._prev_fired_q, question
        prepared = None if kind == "more" else self._best_prepared(question)
        if prepared is None and kind == "question" and _question_parts(question) == 1:
            # вступ перед питанням: "Let's talk about UI, what is a Canvas?" —
            # слова вступу заважають збігу, тому пробуємо саме питання без нього
            tail = _split_lead_in(question)
            if tail:
                prepared = self._best_prepared(tail)
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
        if prepared is not None:
            print(f"[MATCH] fired prepared answer: {prepared[1]}")
            self._set_text(display, prepared[1], restart=True)
            return

        # питання з кількох частин: готові відповіді на частини показуємо
        # одразу підряд, у AI йде лише те, на що готової немає
        glued, rest = ("", []) if kind == "more" else self._glue_prepared(question)
        if glued:
            print(f"[MATCH] glued prepared answers; parts left for AI: {len(rest)}")
            print(f"[MATCH] fired prepared answer: {glued}")
            self._set_text(display, glued, restart=True)
            if not rest:
                return

        if not self.enabled:
            return  # збігу немає, AI вимкнений — нічого не показуємо

        if self._busy_gen == self._gen:
            return  # це ж питання вже в роботі
        self._busy_gen = self._gen
        # НЕ показуємо "generating answer..." — стрічка мовчить, поки
        # відповідь реально не готова (без миготіння)
        threading.Thread(target=self._fetch, args=(question, display, self._gen),
                         kwargs={"prefix": glued, "only": rest, "context": context}, daemon=True).start()

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
                    if gen != self._gen:
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
                            self._set_text(display, prefix + acc.replace("*", ""), restart=r and not prefix)
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
            examples = self._similar_prepared(question)
            examples_text = "\n\n".join(f"Q: {q}\nA: {a}" for q, a in examples)
            info_block = ""
            if self.info_text:
                info_block = (
                    f"Candidate background info (facts you may use):\n"
                    f"{self.info_text}\n\n"
                )
            max_words = _max_words(" ".join(only) if only else question)
            if _utterance_kind(question) == "more":
                max_words += 20   # "tell me more" чекає на розгорнуту відповідь
            if only:
                # AI має бачити вже сказане: без цього він дописав "Yes, Bloom is a
                # renderer feature" одразу після готової відповіді, де сказано навпаки
                question += ("\n\nThe candidate has ALREADY said this, word for word: \"" + prefix.strip() + "\"\n"
                             "Treat it as true and never contradict it. Do not repeat it. "
                             "Continue the answer with ONLY this remaining part: " + " ".join(only))
            system = SYSTEM_PROMPT_TEMPLATE.format(max_words=max_words)
            info_block = self._relevant_info(question)
            messages = [
                {"role": "system", "content": system},
                {
                    "role": "user",
                    "content": (
                        f"{info_block}"
                        f"Candidate's prepared answers for similar questions:\n"
                        f"{examples_text}\n\n"
                        f"{earlier}"
                        f"Interviewer's question: {question}"
                    ),
                },
            ]
            t0 = time.time()
            answer = self._stream_answer(messages, display, gen, prefix)
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
            answer = answer.replace("*", "")
            if len(answer.split()) > max_words + 10:
                # обрізаємо по ОСТАННЬОМУ ЗАВЕРШЕНОМУ реченню, не по слову
                # (рубання по слову лишає "so it" замість відповіді)
                out = ""
                for part in re.split(r"(?<=[.!?]) +", answer):
                    if len((out + " " + part).split()) > max_words + 10:
                        break
                    out = (out + " " + part).strip()
                if out:
                    answer = out
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
        if gen != self._gen:
            print("[AI] stale answer dropped (new question arrived)")
            return

        self._set_text(display, prefix + answer, restart=not prefix)

    def _set_text(self, display, text, restart=False):
        self.last_shown_answer = text
        text = text.replace("\n", "   ")
        try:
            # restart=True (нова відповідь) = рестарт стрічки зі свіжого заїзду;
            # стрімінг-пуши того ж розрахунку = оновлення тексту на лету
            fn = display.start if restart else display.update_text
            display.after(0, fn, text)
        except Exception:
            pass
