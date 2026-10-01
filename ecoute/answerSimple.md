UNITY FOR A TECHNICAL ARTIST - PLAYTIKA INTERVIEW PREPARATION
Short version: only the essentials of every topic. Details and all questions - answers.md.

Topic order = how often it is asked in TA interviews for mobile Unity games (top = most often).
Source of the order and questions: ГУГЛ/ПИТАННЯ_11 and ПИТАННЯ_12 (Glassdoor, interview guides, Unity docs).

What matters most for a Senior TA at Playtika (ПИТАННЯ_11):
1) owning a feature from start to release (ownership),
2) performance and optimization on weak phones,
3) pipeline and tools for artists,
4) clear communication with artists, programmers and product.
Most common live tests: a shader, optimizing a scene, a pipeline on a whiteboard.
No need to go deep: Timeline, ECS, networking, 3D character rigging, old Unity features.


=====================================================================
1. PERFORMANCE ON MOBILE (asked most often)
=====================================================================

What it is:
The game must hold a stable frame rate on a weak phone. Every frame has a time budget:
16.6 ms for 60 fps, 33.3 ms for 30 fps. Studios aim lower (~11 ms and ~22 ms), because a phone heats up
and slows down (thermal throttling).
Either the processor (CPU) or the graphics card (GPU) can be the limit - and they are fixed differently.

Why:
A mobile live game runs on thousands of different phones. If it lags on a weak one, the player leaves.

How to think:
1. Measure on a real weak phone (development build). The Editor on a PC lies.
2. Find out: is it CPU or GPU?
   - CPU: draw calls, Canvas rebuilds, particles, garbage (GC), scripts.
   - GPU: overdraw (transparent on transparent), heavy shaders, big screen size, post-processing.
3. Change ONE thing and measure again. Give numbers: "14.2 ms -> 10.8 ms".

They ask: "How would you find and fix a frame-rate drop on a low-end Android?"
Answer: a development build on the phone and the Profiler - CPU or GPU. Then the biggest marker:
Canvas - split the Canvas; particles - fewer and smaller; GPU - cut overdraw and heavy shaders. Measure again.


=====================================================================
2. SHADERS (Shader Graph, math, cost on mobile)
=====================================================================

What it is:
A shader is a small program on the graphics card that calculates the colour of every pixel.
Material = shader + values (texture, colour, speed).
- Vertex shader - runs once per vertex (triangle corner): positions, UV, vertex colour.
- Fragment (pixel) shader - runs once per pixel: the final colour.
  There are many more pixels than vertices, so heavy math in the fragment shader = expensive.
- Shader Graph - shaders from nodes, no code. For 2D: Sprite Unlit / Sprite Lit.

Why a TA cares:
A shader gives motion and effects almost for free: wind, glow, shine, water, dissolve, scrolling.
One shared material on many objects = batching does not break.

When to use what:
- A motion repeated on many objects (wind on trees) - a shader.
- A one-time unique motion - an Animator clip.
- Shader Graph - almost always. HLSL (code) - when you need exact performance control,
  custom lighting or a port of an old shader. A TA must be able to READ simple HLSL.

They ask: "How do you reduce shader cost on mobile without killing the look?"
Answer: fewer nodes and texture samples, Unlit instead of Lit, half instead of float where possible,
smooth math in the vertex shader, few keywords (variants). And measure on the phone.


=====================================================================
3. RENDER PIPELINE: BUILT-IN, URP, HDRP
=====================================================================

What it is:
The pipeline is Unity's "drawing engine": how the camera draws a frame, how light is calculated, which shaders work.
- Built-in - old, Unity marks it "deprecated", no new features.
- URP - the light modern pipeline for phones, PC, consoles. Has the 2D Renderer, Shader Graph, SRP Batcher.
- HDRP - heavy 3D for PC and consoles, does not run on phones.

Why:
Shaders do not move between pipelines (a Built-in shader in URP = pink). 2D lights and axis sorting
exist only in the URP 2D Renderer. Post-processing is its own (Volume).

When to use what:
Mobile game - URP. Old Built-in project - keep it until moving pays off. AAA 3D - HDRP.

They ask: "Which pipeline and why?"
Answer: URP with the 2D Renderer - light for phones, gives 2D lights, sorting, Shader Graph and the SRP Batcher.
Built-in is deprecated, HDRP is not for phones.


=====================================================================
4. DRAW CALLS AND BATCHING
=====================================================================

What it is:
- Draw call - a command from the processor to the graphics card "draw this with this material". Each costs CPU time.
- SetPass call - a change of material/shader between commands. Even more expensive.
- Batching - gluing objects into one command. Works only if material and texture are the same.
- Atlas (Sprite Atlas) - one big texture with many sprites, so they share ONE texture.

Why:
A phone processor is weak. Keep ~100-200 draw calls on weak phones; 300+ is usually trouble.

When to use what (4 kinds of batching):
- SRP Batcher (on by default in URP) - does NOT reduce the number of draw calls, but makes each one cheap.
  Works for objects with the same shader, even with different materials. The main one for sprites.
- Static batching - merges non-moving meshes into one at build time. More memory. Not for sprites and UI.
- Dynamic batching - merges small meshes every frame. In URP usually not worth it (CPU cost beats the gain).
- GPU Instancing - many copies of one mesh with one material in one command (grass, trees).
- uGUI has its own batching inside a Canvas: one atlas and material = one batch.

They ask: "How do you reduce draw calls?"
Answer: atlases per screen, shared materials, a draw order without texture switches,
the SRP Batcher. I check in the Frame Debugger why a batch broke.


=====================================================================
5. TEXTURES AND COMPRESSION
=====================================================================

What it is:
Every picture has import settings: Max Size, compression, mipmaps, Read/Write, PPU.

Why:
Textures are the biggest part of memory and build size in a 2D game. A 2048×2048 texture uncompressed ~16 MB,
with ASTC ~1-4 MB.

When to use what:
- ASTC - the standard for modern iOS and Android. 4x4 - sharp UI and small text, 6x6 - items,
  8x8 - soft shadows and gradients. Bigger block = less memory, worse quality.
- ETC2 - fallback format for old Android without ASTC.
- Max Size - by the real size on screen, not by the PSD size.
- Mipmaps - off for UI and 2D (+33% memory for nothing). Read/Write - off (a copy in memory).

They ask: "Which compression format for iOS/Android and why?"
Answer: ASTC - the best quality-to-size ratio; block size by asset importance (4x4 UI, 6x6 items,
8x8 shadows). ETC2 as a fallback for old Android. I compare on a real phone.


=====================================================================
6. PARTICLES AND VFX
=====================================================================

What it is:
- Particle System (Shuriken) - particles on the processor. Works everywhere, phones too.
- VFX Graph - millions of particles on the graphics card, needs compute shaders, limited on phones.
- Modules: Emission (how many), Shape (from where), Color/Size over Lifetime (how they change),
  Texture Sheet Animation (flipbook).

Why:
Effects give "juice", but they are the easiest way to kill the frame rate through overdraw.

When to use what:
- Mobile 2D - Particle System. VFX Graph - only if all target devices can run it.
- Alpha blend - smoke and clouds that must cover the background. Additive - light, fire, sparks
  (only brightens, disappears on a light background).

They ask: "A big explosion lags on weak phones. First three steps?"
Answer: fewer particles and a shorter life, a smaller particle size (less overdraw),
one shared material. Then crop the texture tighter and measure again.


=====================================================================
7. UI (Canvas, uGUI, TextMeshPro)
=====================================================================

What it is:
- Canvas - the root of the interface; inside are Image, Button, TextMeshPro.
- Canvas Scaler - scales UI to any screen (Scale With Screen Size, reference 1080x2400).
- Anchors - which edge an element is pinned to. Safe Area - the zone without the camera notch.
- TextMeshPro - text from an SDF atlas, sharp at any size.

Why:
UI is most of a casual mobile game's screen, and the most common source of CPU problems.

The main trap - the Canvas rebuild:
any change (colour, text, sprite, on/off, size in a layout) - Unity rebuilds the WHOLE Canvas.
A timer on a big Canvas rebuilds the whole screen every second.
The cure: static UI and often-changing UI on separate Canvases.

They ask: "How do you optimize a complex UI screen on mobile?"
Answer: split the Canvas into static and dynamic, shared atlases, Raycast Target off on decoration,
fewer full-screen transparent panels, no heavy Layout Groups. I check Canvas.SendWillRenderCanvases in the Profiler.


=====================================================================
8. 2D WORKFLOW: SPRITES, IMPORT, SORTING
=====================================================================

What it is:
- Sprite import: Sprite Mode (Single/Multiple), PPU (pixels per 1 unit), pivot, Mesh Type.
- 2D sorting (who is in front): 1) Sorting Layer, 2) Order in Layer, 3) the sort axis.
- Sorting Group - an object made of many sprites sorts as one.

Why:
Wrong import = blurry sprites or sprites of different sizes. Wrong sorting = items jump in front of
each other, shadows end up on top.

When to use what:
- One PPU for the whole art set, so sizes match.
- Pivot at the bottom for everything that stands on the ground.
- Sort by Y without a script: Renderer 2D Data -> Transparency Sort Mode = Custom Axis (0, 1, 0),
  Sprite Sort Point = Pivot. Lower on screen = in front.

They ask: "How do you configure sprite import for a 2D mobile game?"
Answer: Sprite, one PPU per set, pivot by purpose, Max Size by size on screen,
no mipmaps and Read/Write, compression through the atlas.


=====================================================================
9. ANIMATION (Animator, tweens, 2D skeletons)
=====================================================================

What it is:
- Animation Clip - a recording of values changing over time. Animator - a state machine (which clips play when).
- Parameters: Trigger (one-time signal), Bool (lasting state).
- Tween (DOTween, PrimeTween) - a small move from code.
- Timeline - one fixed sequence with many objects (a cutscene). Asked rarely.

Why:
The artist tunes the timing alone. But animation only SHOWS the game state, it does not decide it.

When to use what:
- States that switch (button: idle/pressed/disabled; item: Available/Build/Built) - Animator.
- Many small UI moves (pop, scale, fade) - a tween: runs only when needed, lighter.
- One sequence of UI, particles and sound together - Timeline.

They ask: "When do you NOT use the Animator for UI?"
Answer: for many small moves. An active Animator dirties the Canvas every frame and costs CPU, even
when idle. There I use a tween or turn the Animator off after the clip.


=====================================================================
10. ADDRESSABLES AND REMOTE CONTENT
=====================================================================

What it is:
Addressables loads assets by address when needed. Assets are in groups, each group = a bundle.
A bundle can live in the app (local) or on a server (remote). The catalog - the list of where everything is.

Why:
A new island or event comes from a server without a store update. A smaller build, a faster start.

When to use what:
- Local: the first screen, main UI, fonts, shared shaders, the first island - the game starts without internet.
- Remote: later islands, events, seasonal art.
- Shared assets (atlas, effect materials) - their own group, otherwise they are copied into every bundle.

They ask: "How would you build Addressables for a live game with many events?"
Answer: a stable core - local, events and islands - remote groups, one group per event or island,
shared things separate. A remote catalog so new content arrives without a release. Every load - with a Release.


=====================================================================
11. PROFILER AND FRAME DEBUGGER (often a live test)
=====================================================================

What it is:
- Profiler - frame time per thread. Main Thread - logic, UI, particles. Render Thread - sending to the graphics card.
- Frame Debugger - every draw call one by one and the reason a batch broke.
- Memory Profiler - memory snapshots, comparing "before" and "after".

Why:
In interviews they often show a Profiler screenshot and ask "where is the bottleneck?".

How to read it:
- Main Thread busy (more than ~11-12 ms for 60 fps) - CPU. Look for the biggest marker:
  Canvas.SendWillRenderCanvases - UI rebuilds; ParticleSystem.Update - particles; GC.Alloc - garbage.
- Main Thread waits, and the Render Thread is busy in Gfx.PresentFrame / Gfx.WaitForPresent - GPU (or VSync).
- Gfx.WaitForCommands on the Render Thread - it waits for the Main Thread, so the CPU is to blame.

They ask: "Here is a Profiler - where is the bottleneck?"
Answer: first CPU or GPU by threads, then the biggest marker. For example: "The main thread is the bottleneck,
most of the time is in Canvas.SendWillRenderCanvases, so I split the Canvas".


=====================================================================
12. PREFABS AND VARIANTS FOR LIVE EVENTS
=====================================================================

What it is:
- Prefab - a template. Variant - a "child" of a prefab that keeps only its differences.
- Nested prefab - a prefab inside another one. Override - a change on a copy (bold).
- ScriptableObject - a data asset (prices, rewards, event config).

Why:
The job post: "reuse content for new variants so the project stays manageable".
Hundreds of items: one base - one fix reaches all. Copies - every fix repeated hundreds of times.

How to do it right:
- Base: a stable structure, same child names, one shared Animator.
- Variants change only looks and data (sprite, colour, text, effect reference).
- Chain no deeper than base + one level. Event config - in a ScriptableObject or a table, not in the prefab.
- A tool check: forbidden overrides, required children present.

They ask: "How do you avoid a memory explosion with hundreds of event variants?"
Answer: shared sprites and materials instead of copies, each event - its own remote Addressables group,
unloading after the event ends, recolouring with a material instead of new big textures.


=====================================================================
13. ART PIPELINE AND TOOLS (asked especially of a Senior)
=====================================================================

What it is:
The path of art from the artist to the game: sources (Photoshop, Spine) -> import -> checks -> atlases -> Addressables.
A TA builds this path and the tools, so artists do not make mistakes.

Why:
A senior is asked "design a pipeline" and "which tool did you make". The job post bonus - editor tools.

How:
- Import rules per folder (AssetPostprocessor / Presets): drop into UI/ - the settings are right at once.
- Validators: texture size, compression, names, budgets, required prefab parts.
- Gates before the main branch: an automatic check + review.
- A rules document and owners: who approves new shaders, effects, UI patterns.

They ask: "Design on a whiteboard a pipeline for islands, UI, particles and Addressables."
Answer: sources -> import with presets -> validators (size, compression, names, budgets) -> atlases ->
Addressables groups (core local, events remote) -> review -> build. Plus owners and budgets per device tier.


=====================================================================
14. 2D LIGHTS AND POST-PROCESSING ON MOBILE
=====================================================================

What it is:
- Light 2D - lights for sprites in the URP 2D Renderer (only for Sprite-Lit).
- Post-processing - full-frame effects (Bloom, Vignette, Color Grading) through a Volume.

Why:
Both look good, but every light and every full-screen effect costs GPU.

When to use what:
- The most expensive in 2D lights: many overlapping lights, shadows, normal maps (Accurate), a high resolution
  of the light texture. Guide: 3-8 lights in view, shadows on 1-2 main ones, Render Scale 0.5-0.75.
- Post-processing on mobile: cheaper - Bloom (without High Quality Filtering), Vignette, Color Grading.
  Expensive - Motion Blur, high-quality Depth of Field. On weak phones - off, or colour only.
- Things that glow by themselves - an unlit sprite + Bloom, not a real light on every particle.

They ask: "Which post-processing effects do you limit on weak phones?"
Answer: Motion Blur and high-quality Depth of Field - off; Bloom - fast mode or off;
I keep Color Grading. Every effect is a full-screen pass.


=====================================================================
15. MEMORY AND ASSET BUDGETS
=====================================================================

What it is:
- Build size - what the player downloads. Memory - what is loaded now. Loading - how long it takes.
  Linked, but different.
- A budget - a limit per screen or device tier: MB of textures, draw calls, particles, ms per frame.

Why:
Go over memory on a weak phone - the game crashes (OOM). A senior is asked "how do you set budgets".

Guides for 2D on weak phones:
- Texture memory ~50-150 MB for the whole game (depends on scope).
- Draw calls ~100-200. Frame: target ~22 ms for 30 fps, ~11 ms for 60 fps.

They ask: "How do you control memory in a live game?"
Answer: budgets per device tier, Memory Profiler snapshots before and after, a Release for every
Addressables load, unloading event content. Validators keep heavy assets out.


=====================================================================
16. QUALITY TIERS AND DEVICES
=====================================================================

What it is:
Thousands of different phones are split into tiers: low / mid / high. Each tier has its own settings.

How the tier is chosen:
A device list + rules: GPU, memory (≤3 GB - low, 4-6 - mid, ≥8 - high), processor.
On first launch the game reads SystemInfo and picks a tier. Plus data from the live game and QA tests.

What changes between tiers:
- Texture size (HD/SD), particle counts, post-processing (low - off), Render Scale (0.5-0.75 on low),
  frame target (low - 30 fps, high - 60).

How in Unity:
Quality Settings - tiers; a separate URP asset per tier; Addressables variants HD/SD;
a startup script calls QualitySettings.SetQualityLevel.

They ask: "How do you define and test quality tiers?"
Answer: tiers by GPU and memory from a device list, a separate URP asset per tier, its own budgets.
I test first on the weakest Android and an old iPhone, plus long sessions for heat.


=====================================================================
17. BUILD AND PLAYER SETTINGS
=====================================================================

What it is:
- IL2CPP - C# is turned into C++ and machine code in advance. Mono - compiling during the game (JIT).
  Mobile - IL2CPP: faster, and iOS does not allow JIT at all.
- Stripping - Unity throws away unused code and engine modules, so the build is smaller.
- Player Settings for mobile: texture compression (ASTC, fallback ETC2), graphics API (Vulkan/GLES on Android,
  Metal on iOS), ARM64 only, AAB for Google Play.

Why a TA cares:
Build size and "works in the Editor, not on the phone" often come from here.

They ask: "What do you change in Player Settings for size and performance?"
Answer: IL2CPP, ARM64, ASTC, Vulkan with a GLES fallback, AAB, stripping. Plus I remove extra shader variants.


=====================================================================
18. GIT AND WORKING TOGETHER
=====================================================================

What it is:
Git and pull requests: every change recorded and reviewed. Scenes and prefabs are saved as text (Force Text),
so they can be merged.

Why:
The job post directly asks for Git/PR. Unity files break easily on merge.

How:
- Small prefabs instead of one big scene, owners for the parts.
- Always commit the .meta with its asset (otherwise a new GUID and every link broken).
- Big binary files (PSD) - Git LFS.
- Reviewing a prefab - open it in Unity, not only the text diff.

They ask: "How do you build prefabs and scenes to avoid conflicts?"
Answer: small prefabs with owners, the scene only assembles them, Force Text and UnityYAMLMerge. Small changes,
I check my own diff before the PR.


=====================================================================
19. 2D CAMERA
=====================================================================

What it is:
An orthographic camera (no perspective). Orthographic Size - half the height of the visible area in units.

How:
- Pick the size so the main content fits the narrowest phone; wider screens show more.
- Pixel Perfect Camera - only for pixel art. Not needed for smooth 2D.
- Parallax: 3-5 layers, move the layers at different speeds instead of adding cameras.
- Cinemachine: following, bounds (Confiner), shake. Small cost - it is C# logic. Not needed for a static screen.

They ask: "How would you set up the camera for an island on different screens?"
Answer: a fixed orthographic size for the narrowest phone, wider ones show more sky.
I test a 9:20 phone and a 3:4 tablet.


=====================================================================
BEHAVIOURAL QUESTIONS (STAR)
=====================================================================

What it is:
Playtika asks about ownership, conflicts, deadlines, failures. Answer with STAR:
Situation -> Task -> Action (what I did) -> Result (with a number).
Situation + task ~25% of the time, actions ~60%, result ~15%.

Mistakes:
- too much context, "we" instead of "I", no number in the result, vague actions ("optimized shaders"),
  no effect on the future (a rule, a tool, a document).

Which stories to prepare:
1. Art vs performance conflict - show: I translate the artist's wish into limits and decide with numbers.
2. A tool that saved time - show: found the pain, measured it, made it safe, counted the gain.
3. A bug on a phone before release - show: I test on hardware, find the cause, coordinate the fix.
4. A deadline - cut scope - show: priority by impact, said it early and honestly, kept the core.
5. A failure - show: admitted it, fixed it, changed the process so it does not repeat.

A failure without hurting yourself: admit it without blame -> what you did to fix it -> what you changed in the process
(a validator, a checklist) -> a number "after".

Questions to ask them at the end (sound senior):
- How do you balance art ambition and budgets on the weakest devices? An example of a hard trade-off?
- What does the content pipeline for live events look like and where is the biggest bottleneck for artists?
- How do you measure the impact of Tech Art (fps, time saved, fewer bugs)?
- What device quality tiers and test plan do you have?
- Which Tech Art problem on the project would you like someone to solve in the next 6-12 months?


=====================================================================
QUESTIONS ABOUT MY HOME ASSIGNMENT (they discuss it in the interview)
=====================================================================

What will happen:
After the assignment - a review: "why this way", "what else did you consider", "how does it scale to events",
"how did you check it", "what would you improve", "how would you make it data-driven for designers".

What I did (short):
- The island from sprites under an orthographic camera; bar and navigation - a Canvas with Canvas Scaler 1080x2400 and Safe Area.
- The PSD brought in with my PSD to Scene tool.
- Base BuildableItem_Base with three states + seven direct variants.
- Animator: Available -> trigger Build -> one BuildSequence clip -> Built. The item pops at 1.1 s
  (0.85 -> 1.06 -> 1.0), all by ~1.4 s; the next action is available in under 2 s.
- The cloud - one particle, a 4x4 flipbook, alpha blend. Hammers - sprites with the pivot near the handle.
- Atlases UI_Core and Island (items together with their shadows). Addressables: Local_Core, Shared_FX, Remote_Island_TeaHouse.


=====================================================================
HOW I WORK (job post: mockup -> feature, ownership, communication)
=====================================================================

Short: break down the mockup (states, data, taps) -> ask what is missing -> prototype -> base prefab and Canvas ->
animation and FX -> connect to game state -> two screens, performance, memory, loading -> variants and Addressables.


=====================================================================
QUESTIONS AND ANSWERS (by the topics of block 1)
=====================================================================

--- QUESTIONS ABOUT MY HOME ASSIGNMENT (they discuss it in the interview) ---

Q: Why did you structure the variants this way?
A: One base with the same structure and a shared Animator, and variants change only sprites, anchors and data. A change in the base reaches all seven, and the chain is short, so it is clear where every change comes from.

Q: What else did you consider?
A: A separate prefab per item - rejected, because every fix would be repeated seven times. Timeline for the build - rejected, because an Animator with one clip is simpler and shows the whole timing.

Q: How does this scale to events and new islands?
A: The same Animator and base, new variants with data, and each island - its own remote Addressables group with its own atlas. A new island comes from a server without an app update.

Q: How would you make it data-driven for designers?
A: Prices, rewards and sprite references in a ScriptableObject or a table, and a tool generates variants from the rows. A designer changes data without opening the prefab.

Q: How did you check it?
A: Two screen formats (1080x2400 and 2048x2732) plus the Device Simulator, EditMode tests on structure and flow, and pixels by eye. I wrote down honestly what was measured and what was not.

Q: Why is the island made of sprites and not UI?
A: Sprites sort together with particles, and the camera frames the island for the screen. UI stayed only for what is pinned to the screen.

Q: Why are a shadow and its item in one atlas?
A: They are drawn one after another. In different atlases the texture would switch on every item and break the batch.

Q: What did you leave outside atlases?
A: The island base 2241 px (it would eat the atlas), the sky gradient, the cloud flipbook and sprites whose shaders read UV.

Q: Why is the island remote?
A: The player reaches islands later, and new ones come out after release. The main UI must work offline, so it stayed local.

Q: What would you do with more time?
A: Real remote loading with a progress bar, profiling on a weak Android and checking ASTC quality on real devices.

Q: Did you use AI and how?
A: Yes, for drafts of tools, searching the docs and routine checks. I compiled, tested and checked every piece's API against the Unity 6 docs.

Q: What was the hardest?
A: Tuning the build timing to the reference video, so the next action is ready in under 2 seconds.
