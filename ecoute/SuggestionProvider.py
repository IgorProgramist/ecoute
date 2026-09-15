import difflib
import re
import threading
import time
import uuid
from datetime import datetime
from openai import OpenAI

import config

BASE_URL = "https://opencode.ai/zen/go/v1"

QUESTION_SILENCE_S = 2.5   # аудіо-тиша 2.5с = питання завершене (порог <2с стріляє в "сліпій зоні", доки записується наступний шматок)
REFIRE_MIN_NEW_WORDS = 4   # повторний показ тільки якщо питання виросло на 4+ слів

SYSTEM_PROMPT_TEMPLATE = (
    "You are helping a candidate during a live technical job interview (Unity / Technical Artist role). "
    "You receive the interviewer's latest spoken question. "
    "You are also given the candidate's own prepared answers for similar questions — "
    "reuse their facts, style and tone (first person, confident, direct). "
    "Reply in the SAME language as the question (English or Ukrainian). "
    "The answer must be at most {max_words} words: a direct, confident reply. "
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

        # сигнал завершеності = АУДІО-тиша: коли спікер реально замовк.
        # Текстова стабільність ненадійна — шматки тексту приходять
        # з cadence ~1.5-2с і стріляють посеред питання
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
        print(f"[MATCH] question complete: {question[:90]}")

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
            # контекст: схожі prepared-відповіді кандидата (уже завантажені
            # при старті — читання файлу не витрачає час під час інтерв'ю)
            examples = self._similar_prepared(question)
            examples_text = "\n\n".join(f"Q: {q}\nA: {a}" for q, a in examples)
            system = SYSTEM_PROMPT_TEMPLATE.format(max_words=config.AI_MAX_WORDS)
            resp = self.client.chat.completions.create(
                model=config.AI_MODEL,
                messages=[
                    {"role": "system", "content": system},
                    {
                        "role": "user",
                        "content": (
                            f"Candidate's prepared answers for similar questions:\n"
                            f"{examples_text}\n\n"
                            f"Interviewer's question: {question}"
                        ),
                    },
                ],
                max_tokens=config.AI_MAX_TOKENS,
            )
            msg = resp.choices[0].message
            answer = (msg.content or "").strip()
            if not answer:
                reasoning = getattr(msg, "reasoning_content", "") or getattr(msg, "reasoning", "") or ""
                sentences = [s.strip() for s in reasoning.replace("\n", ". ").split(".") if s.strip()]
                answer = sentences[-1][:config.AI_MAX_WORDS * 10] if sentences else ""
            answer = answer.replace("*", "")
            if answer:
                print(f"[AI] dynamic answer: {answer[:80]}")
        except Exception as e:
            print(f"[AI] error: {e!r}")
            return
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
