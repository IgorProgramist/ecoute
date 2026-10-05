# ============================================
#  ВСІ НАЛАШТУВАННЯ ECUTE ПІД ТЕБЕ
#  Змінюй і перезапускай python main.py
# ============================================

# --- МОВА ТРАНСКРИПЦІЇ ---
# "en"   = тільки англійська (рекомендовано для англ. інтерв'ю)
# "uk"   = тільки українська
# "auto" = автоматичне визначення
TRANSCRIBE_LANGUAGE = "en"

# --- МОДЕЛЬ РОЗПІЗНАВАННЯ ---
# "tiny.en" = швидка, тільки англ
# "base"    = EN+UK (швидко)
# "small"   = точніша (EN+UK); на GPU працює швидко
WHISPER_MODEL = "small"
BEAM_SIZE = 1  # 1 = швидше (~0.6с проти 1.35с при 5), якість майже та сама
# Підказка whisper: терміни, які він інакше недочуває ("Addressables Group"
# чув як "addressable screw"). "" = без підказки.
WHISPER_PROMPT = (
    "A Unity technical artist job interview. Terms: GameObject, Prefab Variant, RectTransform, "
    "ScriptableObject, MonoBehaviour, SpriteRenderer, Sprite Atlas, Sprite Mask, Sorting Layer, "
    "Sorting Group, Pixels Per Unit, 9-slicing, Tight Mesh, Full Rect, Canvas Scaler, Graphic Raycaster, "
    "EventSystem, CanvasGroup, TextMeshPro, ScrollRect, RectMask2D, Layout Group, Content Size Fitter, "
    "Safe Area, RawImage, stencil buffer, Animator Controller, Blend Tree, tweening, Shader Graph, URP, "
    "Renderer Features, MeshRenderer, SkinnedMeshRenderer, Render Texture, VFX Graph, overdraw, fill rate, "
    "alpha clipping, draw call, SRP Batcher, GPU Instancing, CPU-bound, GPU-bound, Frame Debugger, mipmap, "
    "Read/Write Enabled, LOD, Addressables Group, Addressables Catalog, Addressables Label, AssetBundle, "
    "object pooling, Development Build, Build Profile, Bloom, Culling Mode, occlusion culling, "
    "Has Exit Time, Avatar Mask, Light Probes, Profile Analyzer, Memory Profiler."
)

# --- ТЕЛЕСУФЛЕР (безкінечна стрічка) ---
# Кажеш слово -> стрічка плавно з'їжджає вліво на одне слово,
# нове слово додається справа. Стоїть, поки ти мовчиш.
WORDS_PER_CHUNK = 5             # скільки слів видно у стрічці (5-6)
SLIDE_DURATION_MS = 500         # тривалість зсуву одного слова (більше = плавніше)
TELEPROMPTER_FONT_SIZE = 26     # розмір шрифту стрічки
TELEPROMPTER_WORD_TIMEOUT_MS = 0    # 0 = стрічка НЕ рухається сама ніколи (клік = зсув)

# --- МІКРОФОН ---
# Шматок назви твого мікрофона у Windows (дивись список у консолі при старті)
# "" = використовувати дефолтний пристрій Windows
MIC_DEVICE_NAME = "B15"
MIC_AUTO_PICK = True  # True = авто-проба кандидатів по гучності (обирає той, що реально чує)
MIC_GAIN = 1.0  # підсилення тихого мікрофона (1.0 = без змін)

# --- ВІКНО (невидиме крім тексту читання) ---
TRANSPARENT_COLOR = "#050505"   # колір-хромакей: все з цим кольором = прозоре
ALWAYS_ON_TOP = True
WINDOW_SIZE = "1000x240"

# --- AI ПІДКАЗКИ (opencode Go) ---
AI_MODEL = "kimi-k3"            # альтернатива: glm-5.2, glm-5.3-flash (було до 2026-10-04: 13.9с до першого слова, 3 відмови з 20)
AI_MAX_TOKENS = 900             # reasoning моделі з'їдає токени — 400 обриває відповідь на півреченні
AI_MAX_WORDS = 40               # ліміт слів у динамічній відповіді AI

# ЧЕРГА ВІДПОВІДЕЙ (AnswerDeck.py). True: нове питання НЕ перериває стрічку, відповідь
# на нього чекає в черзі і виходить сама, коли стрічка доїхала і інтерв'юер мовчить
# QUEUE_SILENCE_S секунд; стрілки вліво/вправо = історія, вгору = пропустити,
# вниз = очистити стрічку і чергу. False: стара поведінка - нове питання одразу
# замінює стрічку, стрілки не діють
RIBBON_QUEUE = True
QUEUE_SILENCE_S = 3.0

# --- ТВОЇ ПІДГОТОВЛЕНІ ВІДПОВІДІ ---
ANSWERS_FILE = "answers.md"
MATCH_THRESHOLD = 0.6           # 0.0..1.0: наскільки питання має бути схожим на Q

# --- КУКБУКС (детальні знання для уточнень "розкажи детальніше", "як саме") ---
# Теми з цього файлу йдуть тільки в AI як довідка, на стрічку напряму не потрапляють.
ACTIONS_FILE = "actions.md"
