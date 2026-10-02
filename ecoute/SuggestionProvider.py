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

# загальні слова, що не мають матчингової ваги — інакше overlap роздувається
# generic-словами і нерелевантні Q фолспозитивять ("salary" -> "mobile games")
_STOPWORDS = {
    "what", "when", "which", "would", "could", "should", "will", "your",
    "about", "that", "this", "these", "those", "there", "have", "has", "had",
    "does", "did", "was", "were", "been", "then", "than", "some", "many",
    "much", "most", "very", "also", "just", "into", "over", "every",
    "other", "each", "them", "they", "from",
}

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
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text, flags=re.UNICODE)
    return re.sub(r"\s+", " ", text).strip()


def load_prepared_answers():
    pairs = []
    info_text = ""
    try:
        with open(config.ANSWERS_FILE, encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"[INFO] No prepared answers file ({config.ANSWERS_FILE})")
        return pairs, ""
    # INFO-блок: довідка про кандидата/Unity — використовується як контекст для AI
    m = re.search(r"^INFO:\s*$(.*?)(?=^Q:|\Z)", content, flags=re.M | re.S)
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
        self._last_epoch = None
        self._retried = False
        self.prepared, self.info_text = load_prepared_answers()
        self.prepared_norm = [(q, a, _normalize(q)) for q, a in self.prepared]
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

    def _best_prepared(self, question):
        qn = _normalize(question)
        qcontent = set(w for w in qn.split() if len(w) >= 4 and w not in _STOPWORDS)
        best_score, best = 0.0, None
        for qorig, aorig, qnorm in self.prepared_norm:
            ratio = difflib.SequenceMatcher(None, qn, qnorm).ratio()
            # шлях 1: token-coverage по змістових словах (len>=4, без стоп-слів)
            # — стійкий до префіксів "Can you tell me about your experience with..."
            qw_content = set(w for w in qnorm.split() if len(w) >= 4 and w not in _STOPWORDS)
            overlap = qcontent & qw_content
            coverage = len(overlap) / len(qw_content) if qw_content else 0.0
            if len(overlap) >= 3 and coverage >= config.MATCH_THRESHOLD:
                score = coverage
            # шлях 2: ratio тільки для впевнених збігів + ЗМІСТОВИЙ гейт:
            # на шумних/коротких рядках 0.6 ratio ловило нерелевантні Q
            elif ratio >= 0.6 and len(overlap) >= 3:
                score = ratio
            # шлях 3: майже-точний повтор транскрипту. Дворівневий гейт:
            # ratio>=0.9 + 1 змістовне слово (точні визначення), або
            # ratio>=0.8 + 2 змістових слова (повтори з шумом). Без гейта
            # на "What is X?" ratio ~0.8 ловить ШАБЛОН, а не зміст
            # (texture -> Render Texture)
            elif ratio >= 0.95:
                # вербатим-повтор навіть зі стоп/короткими токенами
                # ("MIP map" -> "mipmap"): запас від FP (max 0.83) великий
                score = ratio
            elif ratio >= 0.9 and len(overlap) >= 1:
                score = ratio
            elif ratio >= 0.8 and len(overlap) >= 2:
                score = ratio
            else:
                score = 0.0
            if score > best_score:
                best_score, best = score, (qorig, aorig)
        if best_score >= config.MATCH_THRESHOLD:
            return best
        return None

    def _similar_prepared(self, question, k=3):
        """ТОП-k найближчих prepared-відповідей — контекст для AI."""
        qn = _normalize(question)
        scored = [
            (difflib.SequenceMatcher(None, qn, qnorm).ratio(), qorig, aorig)
            for qorig, aorig, qnorm in self.prepared_norm
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

        prepared = self._best_prepared(question)
        if prepared is not None:
            if prepared[1] == self.last_shown_answer:
                return  # та сама відповідь вже показувалась — не рестартуємо стрічку
            print(f"[MATCH] fired prepared answer: {prepared[1]}")
            self._set_text(display, prepared[1], restart=True)
            return

        if not self.enabled:
            return  # збігу немає, AI вимкнений — нічого не показуємо

        if self._busy_gen == self._gen:
            return  # це ж питання вже в роботі
        self._busy_gen = self._gen
        # НЕ показуємо "generating answer..." — стрічка мовчить, поки
        # відповідь реально не готова (без миготіння)
        threading.Thread(target=self._fetch, args=(question, display, self._gen), daemon=True).start()

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

    def _stream_answer(self, messages, display, gen):
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
                acc = ""
                got_first = False
                last_push = 0.0
                first_push_done = [False]
                for chunk in stream:
                    if gen != self._gen:
                        # прийшло нове питання — стрім застарів, не показуємо
                        return
                    now = time.time()
                    if not got_first and now - t0 > 10:
                        # 10с без жодного слова — сервер завис, марно чекати
                        print("[AI] stream: no content in 10s, falling back")
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
                            self._set_text(display, acc.replace("*", ""), restart=r)
                if acc.strip():
                    box["a"] = acc.strip()
            except Exception as e:
                print(f"[AI] stream error: {e!r}")

        th = threading.Thread(target=_worker, daemon=True)
        th.start()
        th.join(timeout=35)
        if th.is_alive():
            print("[AI] stream stalled, abandoned")
            return None
        return box.get("a") or None

    def _fetch(self, question, display, gen):
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
            system = SYSTEM_PROMPT_TEMPLATE.format(max_words=config.AI_MAX_WORDS)
            info_block = self._relevant_info(question)
            messages = [
                {"role": "system", "content": system},
                {
                    "role": "user",
                    "content": (
                        f"{info_block}"
                        f"Candidate's prepared answers for similar questions:\n"
                        f"{examples_text}\n\n"
                        f"Interviewer's question: {question}"
                    ),
                },
            ]
            t0 = time.time()
            answer = self._stream_answer(messages, display, gen)
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
            if len(answer.split()) > config.AI_MAX_WORDS + 10:
                # обрізаємо по ОСТАННЬОМУ ЗАВЕРШЕНОМУ реченню, не по слову
                # (рубання по слову лишає "so it" замість відповіді)
                out = ""
                for part in re.split(r"(?<=[.!?]) +", answer):
                    if len((out + " " + part).split()) > config.AI_MAX_WORDS + 10:
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

        self._set_text(display, answer, restart=True)

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
