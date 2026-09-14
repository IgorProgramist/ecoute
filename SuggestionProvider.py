import difflib
import re
import threading
import time
import uuid
from openai import OpenAI

import config

BASE_URL = "https://opencode.ai/zen/go/v1"

QUESTION_SETTLE_S = 2.2   # (не використовується)
QUESTION_STABLE_S = 2.0    # питання мовчить 2с → вважаємо завершеним
REFIRE_MIN_NEW_WORDS = 4   # повторний показ тільки якщо питання виросло на 4+ слів (Whisper ставить крапки всюди, крапка = ненадійний сигнал)

SYSTEM_PROMPT_TEMPLATE = (
    "You are helping a candidate during a live technical job interview (Unity / Technical Artist role). "
    "You receive the interviewer's latest spoken question from a transcript. "
    "Reply in the SAME language as the question (English or Ukrainian). "
    "The answer must be at most {max_words} words: a direct, confident reply. "
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
    try:
        with open(config.ANSWERS_FILE, encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"[INFO] No prepared answers file ({config.ANSWERS_FILE})")
        return pairs
    blocks = re.findall(r"Q:\s*(.*?)\nA:\s*(.*?)(?=\nQ:|\Z)", content, flags=re.S)
    for q, a in blocks:
        if q.strip() and a.strip():
            pairs.append((q.strip(), a.strip()))
    print(f"[INFO] Loaded {len(pairs)} prepared answers from {config.ANSWERS_FILE}")
    return pairs


class SuggestionProvider:
    def __init__(self, api_key):
        self.enabled = bool(api_key)
        self.last_question = None
        self.last_ts = None
        self.busy = False
        self.last_shown_answer = None  # щоб та сама відповідь не перезапускала стрічку
        self._q_changed_at = 0.0
        self._fired_for_q = False
        self._last_fired_text = None
        self._last_epoch = None
        self.prepared = load_prepared_answers()
        self.prepared_norm = [(q, a, _normalize(q)) for q, a in self.prepared]
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

    def _best_prepared(self, question):
        qn = _normalize(question)
        best_ratio, best = 0.0, None
        for qorig, aorig, qnorm in self.prepared_norm:
            ratio = difflib.SequenceMatcher(None, qn, qnorm).ratio()
            if ratio > best_ratio:
                best_ratio, best = ratio, (qorig, aorig)
        if best_ratio >= config.MATCH_THRESHOLD:
            return best
        return None

    def _extract_speaker_text(self, transcript):
        for line in transcript.splitlines():
            if line.startswith("Speaker:"):
                return line[len("Speaker:"):].strip().strip("[]").strip()
        return None

    def maybe_update(self, question, display, phrase_epoch=None):
        question = (question or "").strip()
        if not question:
            return
        now = time.time()

        if phrase_epoch is not None and phrase_epoch != self._last_epoch:
            # нове питання (нова фраза) — дозволяємо показ заново
            self._last_epoch = phrase_epoch
            self._last_fired_text = None

        if question != self.last_question:
            # питання ще договорюється — запам'ятати час останньої зміни
            self.last_question = question
            self._q_changed_at = now
            return

        stable_s = now - self._q_changed_at
        if stable_s < QUESTION_STABLE_S:
            return  # питання ще не дозріло — НЕ відповідаємо на частину

        # повторний показ тільки коли питання РЕАЛЬНО виросло
        # (дрібні шматки/повтори від whisper не рестартують стрічку)
        if self._last_fired_text is not None:
            old_n = len(self._last_fired_text.split())
            new_n = len(question.split())
            if new_n - old_n < REFIRE_MIN_NEW_WORDS:
                return
        self._last_fired_text = question
        print(f"[MATCH] question complete ({stable_s:.1f}s stable): {question[:90]}")

        prepared = self._best_prepared(question)
        if prepared is not None:
            if prepared[1] == self.last_shown_answer:
                return  # та сама відповідь вже показувалась — не рестартуємо стрічку
            self._set_text(display, prepared[1])
            return

        if not self.enabled:
            return  # збігу немає, AI вимкнений — нічого не показуємо

        if self.busy:
            return
        self.busy = True
        # НЕ показуємо "generating answer..." — стрічка мовчить, поки
        # відповідь реально не готова (без миготіння)
        threading.Thread(target=self._fetch, args=(question, display), daemon=True).start()

    def _fetch(self, question, display):
        try:
            resp = self.client.chat.completions.create(
                model=config.AI_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT_TEMPLATE.format(max_words=config.AI_MAX_WORDS)},
                    {"role": "user", "content": question},
                ],
                max_tokens=config.AI_MAX_TOKENS,
            )
            msg = resp.choices[0].message
            answer = (msg.content or "").strip()
            if not answer:
                reasoning = getattr(msg, "reasoning_content", "") or getattr(msg, "reasoning", "") or ""
                sentences = [s.strip() for s in reasoning.replace("\n", ". ").split(".") if s.strip()]
                answer = sentences[-1][:config.AI_MAX_WORDS * 10] if sentences else ""
        except Exception as e:
            answer = f"[AI error: {e}]"
        finally:
            self.busy = False

        self._set_text(display, answer)

    def _set_text(self, display, text):
        self.last_shown_answer = text
        text = text.replace("\n", "   ")
        try:
            display.after(0, display.start, text)
        except Exception:
            pass
