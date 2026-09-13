# 🎧 ECOUTE — ІНФО ПО НАЛАШТУВАННЮ (від А до Я)

Мета: live-помічник для співбесіди (SciPlay Technical Artist) — реальний транскрипт
мікрофона (You) + колонок (Speaker / інтерв'юер) у textbox.
Репо: https://github.com/SevaSk/ecoute
Шлях: `C:\Users\Eazy E\Desktop\Нова папка\work\ПІДКАЗКИ\ecoute`

---

## ✅ Що вже зроблено

| Крок | Статус |
|------|--------|
| Клонувати репо (`git clone`) | ✅ DONE (файли: main.py, AudioRecorder.py, AudioTranscriber.py, TranscriberModels.py, requirements.txt, tiny.en.pt) |
| Python | ✅ Python 3.13.1 |
| pip | ✅ pip 25.1.1 |
| git | ✅ git 2.48.1 |

## ⚙️ Що зроблено додатково (2026-09-13)

- FFmpeg 9.0.1 встановлено БЕЗ адмінки: `C:\Users\Eazy E\tools\ffmpeg\ffmpeg-9.0.1-essentials_build\bin` → додано в user PATH
- `Wave` з requirements.txt — НЕ встановлено (битий пакет, вимагає MySQL; стандартний `wave` уже вбудований у Python — він і використовується)
- `torch` — CPU-версія 2.14.0 (замість 2.5 GB CUDA-збірки; для tiny моделі вистачає)
- Python 3.13: додано `standard-aifc`, `audioop-lts` (ці модулі прибрали зі stdlib у 3.13, без них код не запускався)
- `keys.py` у поточній версії коду НЕ читається жодним файлом! Для `--api` режиму потрібно змінну середовища `OPENAI_API_KEY` (або пропатчити TranscriberModels.py)

## ❌ Що ще НЕ зроблено (наступні кроки)

| Крок | Статус | Як зробити |
|------|--------|-----------|
| 1. FFmpeg | ✅ DONE (standalone, у user PATH) | — |
| 2. pip-залежності | ✅ DONE | — |
| 3. OpenAI API key | ❌ (опційно) | потрібен ТІЛЬКИ для `--api`; ставиться як env-змінна OPENAI_API_KEY |
| 4. Тестовий запуск | 🔄 | `python main.py` (локально, EN) або `python main.py --api` |

## ⚠️ Ключові факти з README

- `python main.py` → локальна модель **tiny.en** (тільки англійська, безкоштовно, повільніше/менш точно).
- `python main.py --api` → **Whisper API** OpenAI: швидко, точно, будь-яка мова (українська теж), але платно (кредити OpenAI).
- Слухає **тільки дефолтні** мікрофон і колонки Windows → перед співбесідою переконатися, що потрібні пристрої = default.
- Прогрів ~кілька секунд перед стартом транскрипції.
- Обмеження локальної моделі: акценти, рідкісні слова — може помилятися.
- Ліцензія MIT.

## 🎯 Контекст використання (зв'язка з гугл.md / SciPlay)

- Співбесіда SciPlay → Technical Artist, мова спілкування ймовірно англійська
  (укр. teaching + EN technical terms) → локальна модель `tiny.en` може підійти, але `--api` значно краще.
- Кураторський план навчання: `STUDY_BLOCK_003 = Q031–Q055 A_CORE_ONLY`
  (2D, UI flows, troubleshooting, mobile perf) — ecoute це ЛАЙВ-інструмент, а куратор — ПІДГОТОВКА. Вони доповнюють одне одного.

## 📋 Прогрес налаштування

- [x] Скачано репо
- [ ] FFmpeg
- [ ] pip залежності
- [ ] keys.py (OpenAI)
- [ ] Тестовий запуск
- [ ] Перевірка мікрофона/колонок як default
- [ ] Фінальний прогін перед співбесідою
