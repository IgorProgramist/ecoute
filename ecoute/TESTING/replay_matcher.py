"""Offline replay of the prepared-answer matcher against the two recorded runs.

Run from the ecoute folder:  python TESTING/replay_matcher.py [-v]
No audio, no AI calls: it feeds the matcher three versions of every question
(as written, as HEARD in the recorded run, HEARD with the repeat-garbage removed)
and counts right / AI / WRONG prepared answers.
"""
import difflib
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
os.chdir(ROOT)
sys.path.insert(0, ROOT)

import SuggestionProvider as SP  # noqa: E402

VERBOSE = "-v" in sys.argv

# run 2, questions 1-50: the one prepared Q each should hit
EXPECT_2 = """What is a GameObject?|What is a Component?|What is a Transform?|What is a Prefab?|What is a Prefab Variant?
What is a ScriptableObject?|What is a MonoBehaviour?|What is a Scene?|What is a SpriteRenderer?|What is a Sprite Atlas?
What is a Sprite Mask?|What is a Sorting Layer?|What is a Sorting Group?|What is a Pivot?|What are Pixels Per Unit?
What is 9-slicing?|What is a spritesheet?|What is a Canvas?|What is Canvas Scaler?|What is a Graphic Raycaster?
What is an EventSystem?|What is a CanvasGroup?|What is a Text Mesh Pro?|What is a ScrollRect?|What is a Layout Group?
What are Anchors?|What is a Safe Area?|What is an Animator?|What is an Animator Controller?|What is an Animation Event?
What is a Blend Tree?|What is Tweening?|What is a Material?|What is Shader Graph?|What is URP?
What are Renderer Features?|What is a Render Texture?|What is a Particle System?|What is Overdraw?|What is Fill Rate?
What is a Draw Call?|What is Batching?|What is GPU Instancing?|What is the Unity Profiler?|What is the Frame Debugger?
What is a Mipmap?|What are Addressables?|What is an AssetBundle?|What is Object Pooling?|What is a Development Build?"""
EXPECT_2 = [t for line in EXPECT_2.splitlines() for t in line.split("|")]

# run 2, questions 51-100 (multi-part): a prepared answer is acceptable only if
# its Q contains one of these words; anything else is a WRONG fire
ACCEPT_2 = """prefab|transform,anchor|texture,sprite|atlas,batch|sorting|tight,full rect,slic|pivot,pixels|canvas|canvas
raycaster,eventsystem,button|mask,stencil|layout,content size|spriterenderer,image|canvasgroup,popup,fade
animator,animation clip|animator,transition|parameter,trigger|tween,animator|animation event,sync|material,shader
shader|render pipeline,urp,renderer|post,renderer features,bloom|meshrenderer,lod|particle,vfx|overdraw,fill rate
transparen,alpha,overdraw,additive|draw call,batching|batching|srp,batching|instancing,srp|bound|frame time,fps
garbage,pooling|profiler,frame debugger|texture,compression|mipmap,read/write|texture,4096|memory|addressables
catalog,label,content|addressables,resources|assetbundle,addressables|build|lag,weak,performance,profiler,slow
draw call,overdraw|memory leak,leak|integration,artist|assignment|tools,bug,visual"""
ACCEPT_2 = [t.split(",") for line in ACCEPT_2.splitlines() for t in line.split("|")]


def parse_run(path):
    out = []
    for m in re.finditer(r"^## Q(\d+) - (.*?)\n- HEARD: (.*?)\n", open(path, encoding="utf-8").read(), flags=re.M):
        out.append((int(m.group(1)), m.group(2).strip(), m.group(3).strip()))
    return out


def dedupe(heard):
    """What the buffer fix produces: only the LAST cumulative transcription."""
    words = heard.split()
    if len(words) < 6:
        return heard
    head = " ".join(words[:3]).lower()
    i = heard.lower().rfind(head)
    return heard[i:] if i > 0 else heard


def judge(n, question, title, run, norm_titles):
    """-> 'ok' | 'ai' | 'WRONG'"""
    if title is None:
        return "ai"
    if run == 2 and n <= 50:
        return "ok" if title == EXPECT_2[n - 1] else "WRONG"
    if run == 2:
        return "ok" if any(k in title.lower() for k in ACCEPT_2[n - 51]) else "WRONG"
    want = norm_titles.get(SP._normalize(question))
    if want is None:      # no prepared Q with this exact wording
        qw = set(SP._normalize(question).split()) - {"what", "is", "a", "an", "the", "are", "difference", "between", "and"}
        return "ok" if qw & set(SP._normalize(title).split()) else "WRONG"
    return "ok" if SP._normalize(title) == SP._normalize(want) else "WRONG"


def main():
    sp = SP.SuggestionProvider(None)
    norm_titles = {SP._normalize(q): q for q, _ in sp.prepared}
    missing = [t for t in EXPECT_2 if t not in dict(sp.prepared)]
    if missing:
        sys.exit("EXPECT_2 titles not in answers.md: %s" % missing)
    # every prepared Q must find ITSELF, bare and behind a spoken lead-in
    for lead in ("", "Can you tell me ", "Okay, next question. "):
        bad = [q for q, a in sp.prepared if (sp._best_prepared(lead + q) or ("", ""))[1] != a]
        print("self-match lead=%-22r %d/%d" % (lead, len(sp.prepared) - len(bad), len(sp.prepared)))
        for q in bad[:8] if VERBOSE else []:
            print("   miss:", q, "->", (sp._best_prepared(lead + q) or [None])[0])
    total = {}
    for run, fname in ((1, "QA_test.md"), (2, "QA_test_new.md")):
        rows = parse_run(os.path.join(HERE, fname))
        for kind in ("written", "heard", "clean"):
            cnt = {"ok": 0, "ai": 0, "WRONG": 0}
            for n, question, heard in rows:
                text = {"written": question, "heard": heard, "clean": dedupe(heard)}[kind]
                hit = sp._best_prepared(text)
                title = hit[0] if hit else None
                if kind != "written":
                    # the recorded runs log some HEARD lines against the neighbouring
                    # question, so judge a heard text against the question it really is
                    cn = SP._normalize(dedupe(heard))
                    n, question = max(((m, q) for m, q, _ in rows), key=lambda r: difflib.SequenceMatcher(
                        None, cn, SP._normalize(r[1])).ratio())
                v = judge(n, question, title, run, norm_titles)
                cnt[v] += 1
                if v == "WRONG" or (VERBOSE and v == "ai" and kind == "written"):
                    print("  run%d %-7s Q%03d %-5s %r -> %r" % (run, kind, n, v, text[:70], title))
            total[(run, kind)] = cnt
            print("run%d %-7s n=%d  ok=%d  ai=%d  WRONG=%d" % (run, kind, len(rows), cnt["ok"], cnt["ai"], cnt["WRONG"]))
    return total


if __name__ == "__main__":
    main()
