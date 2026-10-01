UNITY KNOWLEDGE (facts, in simple words):

WHAT MATTERS MOST IN A SENIOR TA INTERVIEW:
- The topics below go from the most often asked to the least.
- Most important for a Senior TA at Playtika: owning a feature from start to release (ownership).
- Second: performance and optimization on weak phones.
- Third: pipeline and tools for artists.
- Fourth: clear communication with artists, programmers and product.
- Most common live tests: a shader, optimizing a scene, a pipeline on a whiteboard.
- No need to go deep: Timeline, ECS, networking, 3D character rigging, old Unity features.

PERFORMANCE ON MOBILE (asked most often):
- What it is: The game must hold a stable frame rate on a weak phone.
- Every frame has a time budget: 16.6 ms for 60 fps, 33.3 ms for 30 fps.
- Studios aim lower (~11 ms and ~22 ms), because a phone heats up and slows down (thermal throttling).
- Either the processor (CPU) or the graphics card (GPU) can be the limit - and they are fixed differently.
- Why: A mobile live game runs on thousands of different phones.
- If it lags on a weak one, the player leaves.
- How to think: Measure on a real weak phone (development build). The Editor on a PC lies.
- Find out: is it CPU or GPU?
- CPU: draw calls, Canvas rebuilds, particles, garbage (GC), scripts.
- GPU: overdraw (transparent on transparent), heavy shaders, big screen size, post-processing.
- Change ONE thing and measure again. Give numbers: "14.2 ms -> 10.8 ms".
- Overdraw - one pixel drawn many times (background + panels + particles). Phones are limited by fill rate (pixels per second), so big transparent layers cost a lot. See it: Scene view -> Overdraw.
- Garbage (GC.Alloc) - memory created in a frame that the garbage collector later cleans. Cleaning = a frame hitch. Goal - zero allocations per frame.
- Average FPS hides hitches. Look at the worst frames (frame time graph).
- Test long sessions: after 10-30 minutes the phone heats up and the frame rate drops.

SHADERS (Shader Graph, math, cost on mobile):
- What it is: A shader is a small program on the graphics card that calculates the colour of every pixel.
- Material = shader + values (texture, colour, speed).
- Vertex shader - runs once per vertex (triangle corner): positions, UV, vertex colour.
- Fragment (pixel) shader - runs once per pixel: the final colour. There are many more pixels than vertices, so heavy math in the fragment shader = expensive.
- Shader Graph - shaders from nodes, no code. For 2D: Sprite Unlit / Sprite Lit.
- Why a TA cares: A shader gives motion and effects almost for free: wind, glow, shine, water, dissolve, scrolling.
- One shared material on many objects = batching does not break.
- When to use what: A motion repeated on many objects (wind on trees) - a shader.
- A one-time unique motion - an Animator clip.
- Shader Graph - almost always. HLSL (code) - when you need exact performance control, custom lighting or a port of an old shader. A TA must be able to READ simple HLSL.
- Math they ask out loud:
- dot(A, B) - how much two directions agree: 1 same, 0 perpendicular, -1 opposite. Uses: lighting (normal · light direction), rim (normal · view), masks.
- UV - coordinates on the picture. Tiling = multiply (repeat), Offset = add (shift), scroll = offset + speed × time. Flipbook = pick a grid cell. Polar Coordinates - for circular effects.
- lerp(a, b, t) - blend a and b. step - hard 0/1 threshold. smoothstep - soft threshold. saturate - clamp to 0..1. frac - fractional part (repeat 0..1). sin(time) - a pulse.
- half (16 bit) - faster on phones, fine for colour and directions. float (32 bit) - for world positions, time, big UVs, otherwise things "shake".
- Shader variants: every keyword combination is a separately compiled shader. More variants = a bigger build, longer builds, broken batching. shader_feature removes unused variants, multi_compile does not.
- Magenta object = the shader does not work (missing, broken, Built-in in URP). Cyan = still compiling.
- Many sprites, one material, different motion: global time + a per-object phase in the vertex colour.
- MaterialPropertyBlock in URP takes the object out of the SRP Batcher.

RENDER PIPELINE: BUILT-IN, URP, HDRP:
- What it is: The pipeline is Unity's "drawing engine": how the camera draws a frame, how light is calculated, which shaders work.
- Built-in - old, Unity marks it "deprecated", no new features.
- URP - the light modern pipeline for phones, PC, consoles. Has the 2D Renderer, Shader Graph, SRP Batcher.
- HDRP - heavy 3D for PC and consoles, does not run on phones.
- Why: Shaders do not move between pipelines (a Built-in shader in URP = pink). 2D lights and axis sorting exist only in the URP 2D Renderer.
- Post-processing is its own (Volume).
- When to use what: Mobile game - URP.
- Old Built-in project - keep it until moving pays off.
- AAA 3D - HDRP.
- Rendering paths in URP:
- Forward - light is calculated per object, the number of lights per object is limited. Cheap. For mobile.
- Forward+ - like Forward, but with light culling - many lights possible. Only if you really need many.
- Deferred - first all objects into a G-buffer (several textures), then light per pixel. No light limit, but lots of memory and passes - expensive on phones.
- The 2D Renderer has its own Lighting Mode; for mobile - Forward.
- Where it is set: Graphics -> Default Render Pipeline = UniversalRP; Quality -> Render Pipeline Asset = UniversalRP (Quality overrides Graphics). Renderer2D lives INSIDE UniversalRP in the Renderer List - that is why you cannot drop it into Graphics or Quality.
- Moving from Built-in: the Render Pipeline Converter fixes pink materials.
- URP camera stack: a Base camera + Overlay cameras.

DRAW CALLS AND BATCHING:
- What it is: Draw call - a command from the processor to the graphics card "draw this with this material". Each costs CPU time.
- SetPass call - a change of material/shader between commands. Even more expensive.
- Batching - gluing objects into one command. Works only if material and texture are the same.
- Atlas (Sprite Atlas) - one big texture with many sprites, so they share ONE texture.
- Why: A phone processor is weak.
- Keep ~100-200 draw calls on weak phones; 300+ is usually trouble.
- When to use what (4 kinds of batching): SRP Batcher (on by default in URP) - does NOT reduce the number of draw calls, but makes each one cheap. Works for objects with the same shader, even with different materials. The main one for sprites.
- Static batching - merges non-moving meshes into one at build time. More memory. Not for sprites and UI.
- Dynamic batching - merges small meshes every frame. In URP usually not worth it (CPU cost beats the gain).
- GPU Instancing - many copies of one mesh with one material in one command (grass, trees).
- uGUI has its own batching inside a Canvas: one atlas and material = one batch.
- What breaks a batch: a sprite from another atlas between two sprites from the same atlas; different materials; masks; MaterialPropertyBlock in URP; different shader keywords.
- SRP Batcher and dynamic batching: when the SRP Batcher is on, it wins.
- Many IDENTICAL objects - GPU Instancing; many DIFFERENT ones with one shader - SRP Batcher.
- Stats shows fewer batches but the frame is not faster = the limit is the GPU (overdraw), not the CPU.

TEXTURES AND COMPRESSION:
- What it is: Every picture has import settings: Max Size, compression, mipmaps, Read/Write, PPU.
- Why: Textures are the biggest part of memory and build size in a 2D game.
- A 2048×2048 texture uncompressed ~16 MB, with ASTC ~1-4 MB.
- When to use what: ASTC - the standard for modern iOS and Android. 4x4 - sharp UI and small text, 6x6 - items, 8x8 - soft shadows and gradients. Bigger block = less memory, worse quality.
- ETC2 - fallback format for old Android without ASTC.
- Max Size - by the real size on screen, not by the PSD size.
- Mipmaps - off for UI and 2D (+33% memory for nothing). Read/Write - off (a copy in memory).
- Source sprites in an atlas - uncompressed: the atlas compresses, otherwise the picture is compressed twice.
- A thin line or halo at a sprite edge - atlas padding and Alpha Is Transparency.
- Find duplicates by content (hash), not by name: in my test 13 files were 6 unique pictures.
- Check pixels, not only logic: wrong filtering + compression blurred 59 of 90 UI sprites, while every test was green.
- In my test the atlases: 2048, ASTC 6x6, no mipmaps, no rotation, no tight packing, padding 4.

PARTICLES AND VFX:
- What it is: Particle System (Shuriken) - particles on the processor. Works everywhere, phones too.
- VFX Graph - millions of particles on the graphics card, needs compute shaders, limited on phones.
- Modules: Emission (how many), Shape (from where), Color/Size over Lifetime (how they change), Texture Sheet Animation (flipbook).
- Why: Effects give "juice", but they are the easiest way to kill the frame rate through overdraw.
- When to use what: Mobile 2D - Particle System. VFX Graph - only if all target devices can run it.
- Alpha blend - smoke and clouds that must cover the background. Additive - light, fire, sparks (only brightens, disappears on a light background).
- CPU or GPU: in the Profiler ParticleSystem.Update = processor (fewer particles, simpler modules); if the graphics card is the limit - it is overdraw (smaller particles, fewer layers, a smaller texture).
- Cheap: a few small systems, one shared unlit material, low Max Particles, no lights or collisions, Culling Mode = Pause for effects that are not visible.
- Guide: a local effect 20-100 live particles, a big screen burst 100-300.
- One-shot effects: Looping off, one Burst, Local simulation space.
- Props that must read clearly (hammers) - animated sprites, not particles.

UI (Canvas, uGUI, TextMeshPro):
- What it is: Canvas - the root of the interface; inside are Image, Button, TextMeshPro.
- Canvas Scaler - scales UI to any screen (Scale With Screen Size, reference 1080x2400).
- Anchors - which edge an element is pinned to. Safe Area - the zone without the camera notch.
- TextMeshPro - text from an SDF atlas, sharp at any size.
- Why: UI is most of a casual mobile game's screen, and the most common source of CPU problems.
- The main trap - the Canvas rebuild: any change (colour, text, sprite, on/off, size in a layout) - Unity rebuilds the WHOLE Canvas.
- A timer on a big Canvas rebuilds the whole screen every second.
- The cure: static UI and often-changing UI on separate Canvases.
- What breaks a UI batch: different atlases/materials side by side, masks, overlapping elements.
- Layout Groups and Content Size Fitter recalculate on every child change; nested ones multiply the cost. For static layouts - anchors. For long lists - reuse item views.
- Raycast Target on every Image = every tap checks every one.
- Safe Area: buttons inside, backgrounds full screen.
- TMP: Static font (letters in advance) or Dynamic (translations). Every Material Preset = a new material. No Auto Size on counters. Room for translations +30-50%.
- UI that reacts to game state: the game holds the data, the UI only shows it (listens to a "coins changed" event). An animation never decides logic. Change text only when the number changed.

2D WORKFLOW: SPRITES, IMPORT, SORTING:
- What it is: Sprite import: Sprite Mode (Single/Multiple), PPU (pixels per 1 unit), pivot, Mesh Type.
- 2D sorting (who is in front): 1) Sorting Layer, 2) Order in Layer, 3) the sort axis.
- Sorting Group - an object made of many sprites sorts as one.
- Why: Wrong import = blurry sprites or sprites of different sizes.
- Wrong sorting = items jump in front of each other, shadows end up on top.
- When to use what: One PPU for the whole art set, so sizes match.
- Pivot at the bottom for everything that stands on the ground.
- Sort by Y without a script: Renderer 2D Data -> Transparency Sort Mode = Custom Axis (0, 1, 0), Sprite Sort Point = Pivot. Lower on screen = in front.
- Mesh Type Tight - less transparent area (less overdraw), but a complex outline = many vertices.
- Custom Sorting Layers live in ProjectSettings/TagManager.asset and do not travel with the Assets folder. So in the test I used one layer + Order in Layer ranges (sky -3100, island -2000, items -71..628, FX 1000, markers 2000, UI 3000).
- A PSD with 200 layers: agree which layers move separately, merge the rest.

ANIMATION (Animator, tweens, 2D skeletons):
- What it is: Animation Clip - a recording of values changing over time. Animator - a state machine (which clips play when).
- Parameters: Trigger (one-time signal), Bool (lasting state).
- Tween (DOTween, PrimeTween) - a small move from code.
- Timeline - one fixed sequence with many objects (a cutscene). Asked rarely.
- Why: The artist tunes the timing alone.
- But animation only SHOWS the game state, it does not decide it.
- When to use what: States that switch (button: idle/pressed/disabled; item: Available/Build/Built) - Animator.
- Many small UI moves (pop, scale, fade) - a tween: runs only when needed, lighter.
- One sequence of UI, particles and sound together - Timeline.
- 2D characters:
- Spine - most common for characters and pets: many animations from one rig, little memory. Traps: premultiplied alpha (wrong = grey halo), every atlas page = a material = a draw call.
- Unity 2D Animation (bones + Sprite Skin) - built in, no licence; deformation on CPU or GPU.
- Frame-by-frame - no bone cost, but every frame is a whole picture, memory grows fast.
- Popup: Show 0.25-0.6 s with a small scale overshoot, Hide 0.15-0.3 s, CanvasGroup for the fade.
- An Animator and a script never write the same transform - one of them goes on an empty parent.

ADDRESSABLES AND REMOTE CONTENT:
- What it is: Addressables loads assets by address when needed.
- Assets are in groups, each group = a bundle.
- A bundle can live in the app (local) or on a server (remote).
- The catalog - the list of where everything is.
- Why: A new island or event comes from a server without a store update.
- A smaller build, a faster start.
- When to use what: Local: the first screen, main UI, fonts, shared shaders, the first island - the game starts without internet.
- Remote: later islands, events, seasonal art.
- Shared assets (atlas, effect materials) - their own group, otherwise they are copied into every bundle.
- Content update: keep addressables_content_state.bin from the release -> "Update a Previous Build" rebuilds only changed bundles. Check for Content Update Restrictions moves changes out of static groups.
- Cannot Change Post Release - for stable content; Can Change - the whole group is rebuilt and downloaded again.
- Memory: every LoadAssetAsync - Release, every InstantiateAsync - ReleaseInstance. Unload event content when the event ends.
- Analyze - finds duplicates between groups.
- Red flags: everything in the Default Local Group, the Resources folder, remote groups without remote paths, blocking loads, no Release.
- My groups in the test: Local_Core, Shared_FX, Remote_Island_TeaHouse.

PROFILER AND FRAME DEBUGGER (often a live test):
- What it is: Profiler - frame time per thread. Main Thread - logic, UI, particles. Render Thread - sending to the graphics card.
- Frame Debugger - every draw call one by one and the reason a batch broke.
- Memory Profiler - memory snapshots, comparing "before" and "after".
- Why: In interviews they often show a Profiler screenshot and ask "where is the bottleneck?".
- How to read it: Main Thread busy (more than ~11-12 ms for 60 fps) - CPU. Look for the biggest marker: Canvas.SendWillRenderCanvases - UI rebuilds; ParticleSystem.Update - particles; GC.Alloc - garbage.
- Main Thread waits, and the Render Thread is busy in Gfx.PresentFrame / Gfx.WaitForPresent - GPU (or VSync).
- Gfx.WaitForCommands on the Render Thread - it waits for the Main Thread, so the CPU is to blame.
- The Profiler in the Editor lies (its own overhead, a PC is faster). Only a development build on the phone.
- Sort by Self time to find the slowest function itself.
- A memory leak: two Memory Profiler snapshots before and after an action; look for textures and assets that should be gone.
- Live test "optimize to X ms": first CPU/GPU, then the biggest marker, each change separately, name the trade-off out loud.

PREFABS AND VARIANTS FOR LIVE EVENTS:
- What it is: Prefab - a template. Variant - a "child" of a prefab that keeps only its differences.
- Nested prefab - a prefab inside another one. Override - a change on a copy (bold).
- ScriptableObject - a data asset (prices, rewards, event config).
- Why: The job post: "reuse content for new variants so the project stays manageable".
- Hundreds of items: one base - one fix reaches all.
- Copies - every fix repeated hundreds of times.
- How to do it right: Base: a stable structure, same child names, one shared Animator.
- Variants change only looks and data (sprite, colour, text, effect reference).
- Chain no deeper than base + one level. Event config - in a ScriptableObject or a table, not in the prefab.
- A tool check: forbidden overrides, required children present.
- In the test: base BuildableItem_Base (ObjectVisual, ShadowVisual, anchors, three states), seven direct variants.
- Never "Apply All" from a variant - it changes the base and every other variant.
- Renamed an animated child - the clip silently loses it (the path is by name).

ART PIPELINE AND TOOLS (asked especially of a Senior):
- What it is: The path of art from the artist to the game: sources (Photoshop, Spine) -> import -> checks -> atlases -> Addressables.
- A TA builds this path and the tools, so artists do not make mistakes.
- Why: A senior is asked "design a pipeline" and "which tool did you make".
- The job post bonus - editor tools.
- How: Import rules per folder (AssetPostprocessor / Presets): drop into UI/ - the settings are right at once.
- Validators: texture size, compression, names, budgets, required prefab parts.
- Gates before the main branch: an automatic check + review.
- A rules document and owners: who approves new shaders, effects, UI patterns.
- A safe tool: Undo for every change, clear errors instead of silent defaults, a preview before applying.
- Build a tool when a task repeats and people make mistakes in it; one-time work by hand.
- A tool lives if it is simple, has a short guide, and I watch the first artists use it.
- My tool in the test: PSD to Scene - a PSD into a scene keeping layer positions.
- AI tools (job post bonus): drafts of tools, explaining code, routine work. I check: compile, tests, every API name in the docs for our Unity version.

2D LIGHTS AND POST-PROCESSING ON MOBILE:
- What it is: Light 2D - lights for sprites in the URP 2D Renderer (only for Sprite-Lit).
- Post-processing - full-frame effects (Bloom, Vignette, Color Grading) through a Volume.
- Why: Both look good, but every light and every full-screen effect costs GPU.
- When to use what: The most expensive in 2D lights: many overlapping lights, shadows, normal maps (Accurate), a high resolution of the light texture. Guide: 3-8 lights in view, shadows on 1-2 main ones, Render Scale 0.5-0.75.
- Post-processing on mobile: cheaper - Bloom (without High Quality Filtering), Vignette, Color Grading. Expensive - Motion Blur, high-quality Depth of Field. On weak phones - off, or colour only.
- Things that glow by themselves - an unlit sprite + Bloom, not a real light on every particle.
- Depth Texture and Opaque Texture in URP - full-screen textures: memory and extra passes. Turn them on only if something reads them (soft particles, "what is behind" effects).

MEMORY AND ASSET BUDGETS:
- What it is: Build size - what the player downloads. Memory - what is loaded now. Loading - how long it takes. Linked, but different.
- A budget - a limit per screen or device tier: MB of textures, draw calls, particles, ms per frame.
- Why: Go over memory on a weak phone - the game crashes (OOM).
- A senior is asked "how do you set budgets".
- Guides for 2D on weak phones: Texture memory ~50-150 MB for the whole game (depends on scope).
- Draw calls ~100-200. Frame: target ~22 ms for 30 fps, ~11 ms for 60 fps.
- Memory grows every time a screen opens = something is not unloaded: Addressables without Release, objects, subscriptions.
- Destroy does not free a texture at once - it lives while something references it.
- Build too big: Build Report, biggest first - textures, then audio and fonts. Resources always ships.

QUALITY TIERS AND DEVICES:
- What it is: Thousands of different phones are split into tiers: low / mid / high.
- Each tier has its own settings.
- How the tier is chosen: A device list + rules: GPU, memory (≤3 GB - low, 4-6 - mid, ≥8 - high), processor.
- On first launch the game reads SystemInfo and picks a tier.
- Plus data from the live game and QA tests.
- What changes between tiers: Texture size (HD/SD), particle counts, post-processing (low - off), Render Scale (0.5-0.75 on low), frame target (low - 30 fps, high - 60).
- How in Unity: Quality Settings - tiers; a separate URP asset per tier; Addressables variants HD/SD; a startup script calls QualitySettings.SetQualityLevel.
- Why weak ones first: memory, heat and driver problems show there. Runs there - runs everywhere.

BUILD AND PLAYER SETTINGS:
- What it is: IL2CPP - C# is turned into C++ and machine code in advance. Mono - compiling during the game (JIT). Mobile - IL2CPP: faster, and iOS does not allow JIT at all.
- Stripping - Unity throws away unused code and engine modules, so the build is smaller.
- Player Settings for mobile: texture compression (ASTC, fallback ETC2), graphics API (Vulkan/GLES on Android, Metal on iOS), ARM64 only, AAB for Google Play.
- Why a TA cares: Build size and "works in the Editor, not on the phone" often come from here.
- Stripping can throw away what is called through reflection - then link.xml or [Preserve].
- Shader variants: their count in Graphics settings and Editor.log ("Compiling shader"). Turn off URP features that multiply variants. A stripped needed variant = a pink object only on the phone.
- Upgrading Unity in a live project: a separate branch, read the URP/Addressables/2D/Shader Graph changes, build and test on key phones, compare with a reference build of the old version. Usually breaks: shaders, URP assets, atlases, Addressables (rebuild the content).

GIT AND WORKING TOGETHER:
- What it is: Git and pull requests: every change recorded and reviewed.
- Scenes and prefabs are saved as text (Force Text), so they can be merged.
- Why: The job post directly asks for Git/PR.
- Unity files break easily on merge.
- How: Small prefabs instead of one big scene, owners for the parts.
- Always commit the .meta with its asset (otherwise a new GUID and every link broken).
- Big binary files (PSD) - Git LFS.
- Reviewing a prefab - open it in Unity, not only the text diff.

2D CAMERA:
- What it is: An orthographic camera (no perspective).
- Orthographic Size - half the height of the visible area in units.
- How: Pick the size so the main content fits the narrowest phone; wider screens show more.
- Pixel Perfect Camera - only for pixel art. Not needed for smooth 2D.
- Parallax: 3-5 layers, move the layers at different speeds instead of adding cameras.
- Cinemachine: following, bounds (Confiner), shake. Small cost - it is C# logic. Not needed for a static screen.

BEHAVIOURAL QUESTIONS (STAR):
- What it is: Playtika asks about ownership, conflicts, deadlines, failures.
- Answer with STAR: Situation -> Task -> Action (what I did) -> Result (with a number).
- Situation + task ~25% of the time, actions ~60%, result ~15%.
- Mistakes: too much context, "we" instead of "I", no number in the result, vague actions ("optimized shaders"), no effect on the future (a rule, a tool, a document).
- Which stories to prepare: Art vs performance conflict - show: I translate the artist's wish into limits and decide with numbers.
- A tool that saved time - show: found the pain, measured it, made it safe, counted the gain.
- A bug on a phone before release - show: I test on hardware, find the cause, coordinate the fix.
- A deadline - cut scope - show: priority by impact, said it early and honestly, kept the core.
- A failure - show: admitted it, fixed it, changed the process so it does not repeat.
- A failure without hurting yourself: admit it without blame -> what you did to fix it -> what you changed in the process (a validator, a checklist) -> a number "after".
- Questions to ask them at the end (sound senior): How do you balance art ambition and budgets on the weakest devices? An example of a hard trade-off?
- What does the content pipeline for live events look like and where is the biggest bottleneck for artists?
- How do you measure the impact of Tech Art (fps, time saved, fewer bugs)?
- What device quality tiers and test plan do you have?
- Which Tech Art problem on the project would you like someone to solve in the next 6-12 months?

QUESTIONS ABOUT MY HOME ASSIGNMENT (they discuss it in the interview):
- What will happen: After the assignment - a review: "why this way", "what else did you consider", "how does it scale to events", "how did you check it", "what would you improve", "how would you make it data-driven for designers".
- What I did (short): The island from sprites under an orthographic camera; bar and navigation - a Canvas with Canvas Scaler 1080x2400 and Safe Area.
- The PSD brought in with my PSD to Scene tool.
- Base BuildableItem_Base with three states + seven direct variants.
- Animator: Available -> trigger Build -> one BuildSequence clip -> Built. The item pops at 1.1 s (0.85 -> 1.06 -> 1.0), all by ~1.4 s; the next action is available in under 2 s.
- The cloud - one particle, a 4x4 flipbook, alpha blend. Hammers - sprites with the pivot near the handle.
- Atlases UI_Core and Island (items together with their shadows). Addressables: Local_Core, Shared_FX, Remote_Island_TeaHouse.

HOW I WORK (job post: mockup -> feature, ownership, communication):
- Short: break down the mockup (states, data, taps) -> ask what is missing -> prototype -> base prefab and Canvas -> animation and FX -> connect to game state -> two screens, performance, memory, loading -> variants and Addressables.


QUESTIONS AND ANSWERS:

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

--- HOW I WORK (job post: mockup -> feature, ownership, communication) ---

Q: How do you work with artists and developers?
A: With artists I talk about the goal: how it should look and feel. With developers I talk about how it is built, the limits, speed and how easy it is to fix later. My job is to connect both sides, so the game looks good and still runs well.

Q: How do you work with designers and product?
A: First I ask why players need the feature, not only what to build. From a mockup or a Miro board I ask about all states, edge cases and what matters most. Then I build it in Unity and tell them early about any trade-offs.

Q: How would you turn a Miro board or mockup into a production-ready Unity feature?
A: I study the design first: states, taps, content, animations, data. I build a small test version in Unity, then the real reusable prefab and UI, then animation, effects and the link to game state. At the end I check speed, memory, loading and edge cases.

Q: What do you do when the brief is incomplete?
A: I ask clear questions early and write down what is known and what is not. Where it is safe, I make a guess or a small prototype and keep working. I do not make big risky decisions alone.

Q: How do you work when requirements change during production?
A: I ask what changed and what is most important now, then check which work I can keep. If the change touches prefab structure, animation states, Addressables or the release date, I tell the team early. The goal is to adapt without breaking what already works.

Q: What does end-to-end feature ownership mean to you?
A: I follow the feature from the first idea to the release, not just one step. I build it in Unity, add art and animation, check edge cases, watch speed and loading, and talk with the team. I do not do every type of work, but I own the Tech Art part until it ships.

Q: How do you know when a feature is ready to hand off?
A: The visual result matches the task, and the prefab and Unity setup are clean and easy to understand. All states and transitions work, and it follows the project rules. It also does not hurt performance or loading, so another person can pick it up and keep working.

Q: How do you design a prefab so it can be reused for variants?
A: I find the stable parts first: hierarchy, behaviour, shared links, animation, UI logic. Then I open only the parts that change: art, text, colours, data. One clear base plus controlled variants, not copies that drift apart.

Q: How do you avoid creating too many duplicated variants?
A: I check if the difference is real or only data and looks. If the behaviour is the same, I reuse the prefab and change its settings or data. A copy is fast today, but in a live game every fix then has to be repeated in every copy.

Q: How would you build UI that responds to real-time game state?
A: I keep the game state and the visuals separate: the game changes the data, the UI only shows it. I never hide game logic inside animations. The UI must always show the true state, even when taps come fast or events come out of order.

Q: How do you decide between Animator, Timeline, tweening and code-driven animation?
A: Animator for states that switch, Timeline for fixed sequences with many objects, tweens for small UI moves, and code when game logic drives the motion. I pick the simplest tool that stays clear and easy to change.

Q: How would you integrate a new 2D asset into Unity?
A: First I learn how it will be used: UI image, world sprite, panel, animation or particle. Then I set import settings: size, alpha, compression, atlas and platform settings. After that I check how it looks in the game and, if needed, its memory and loading cost.

Q: How do you use Photoshop in a Technical Artist workflow?
A: I use it between the source art and Unity. I check layers, fix and clean assets, check size and transparency, and prepare files for the engine. Art problems I fix in Photoshop, import and layout problems I fix in Unity.

Q: How do you approach optimization?
A: I do not guess. First I find the real problem with the Profiler: texture memory, UI batching, rendering, loading or animation. Then I make one focused change and measure again.

Q: How would you troubleshoot a UI screen that looks correct but performs badly?
A: I make the problem happen on the device and measure before changing anything. Then I check the causes one by one: Canvas rebuilds, batching, overdraw, layouts, animation. I change one thing at a time and keep it only if the numbers get better.

Q: What is important when working on mobile games?
A: Performance, memory, build size, loading time and differences between devices. I think about the cost while I add content, not after the game becomes slow. But I optimize only real, measured problems and keep the looks where they matter.

Q: How do you think about performance before a feature reaches production?
A: While I build, I watch for expensive things: big textures, copies of the same content, too many materials, heavy UI, extra effects, loading spikes. I do not optimize everything early, but I catch the big risks before the feature is locked.

Q: How do you think about memory, size and loading together?
A: They are linked but different: a small download does not mean low memory, and low memory does not mean fast loading. I ask what is loaded, when, for how long, how big it is, and whether it is needed all at once.

Q: How do you avoid memory problems with dynamically loaded content?
A: I decide who owns the content, how long it is needed and when it is released. Loading is only half the job: if a closed screen still holds its content, memory keeps growing. I check load, use and release, and confirm it in the Memory Profiler.

Q: How would you troubleshoot an Addressables content loading problem?
A: First I find the kind of problem: wrong address, bad build or catalog, missing remote files, loading or memory. I repeat it with the exact same settings and content version and check what the game asks for. For remote content I also test missing files and a slow network, not only the good case.

Q: What is remote content delivery with Addressables?
A: Some content does not need to be inside the app and is downloaded when needed. So new content can reach players without a full app update. I group assets well, check downloads and dependencies, and handle a slow network or missing files.

Q: How do you investigate a visual or technical issue on your own?
A: First I make the bug happen again. Then I check each layer: source art, import settings, prefab or Canvas, animation, material, runtime state, loading, code. I test one idea at a time and look for the real cause, not only a quick fix.

Q: What does root-cause analysis mean to you?
A: Not stopping at the first fix. If a prefab is wrong because someone changed one value by hand, I ask why it happened and whether other prefabs have the same problem. A good fix also stops the problem from coming back.

Q: How do you balance visual quality and performance?
A: I find what the player really sees and what really costs time. Then I pick the cheapest fix: a smaller texture, a different effect, better loading timing, reuse, or cutting what nobody notices. I decide with numbers, not guesses.

Q: How do you communicate technical trade-offs to non-technical teammates?
A: I do not start with technical words. I explain what changes for them: looks, loading, memory, risk, time. For example: "this looks better but is slow on weak phones; this looks a bit simpler but is safe".

Q: How do you handle a disagreement between an artist and a developer?
A: I find what the artist wants to keep and what the developer wants to protect, like memory or easy code. Then I look for a way to keep the look at a lower technical cost. A quick test or profiler numbers work better than arguing.

Q: How do you deliver on time when the feature is still changing?
A: I split the work into must-haves and extras and make the big risky decisions early. I keep the setup simple and modular and tell people fast when a change hurts the plan. If time is short, I ship a smaller stable version rather than miss the release.

Q: How do you prioritize when several things are urgent?
A: I look at the effect on the release, who is blocked, the risk, and the cost of waiting. If the priority is not clear, I ask. I do the biggest-impact work first and say early if two urgent things cannot both be done.

Q: How do you step into an existing pipeline and become productive?
A: I watch first, then change. I study how prefabs, folders, names, Addressables, UI, animation and Git are set up, and copy one or two good existing examples. I do not invent a new pipeline the team then has to maintain.

Q: How do you work in a shared project without breaking other people's work?
A: I learn the project rules first and keep my changes small and focused. I check my diff before I submit. If I must touch shared parts, I tell the team early, not during review.

Q: How comfortable are you with Git and a PR-based workflow?
A: I use Git and pull requests every day. I make small, clear changes with simple commit messages and check my work before review. In Unity I keep prefab and scene changes small, so others can review them.

Q: How comfortable are you with C#?
A: I am not a full-time programmer, but I can write and fix scripts when a Tech Art task needs it. My Flash and ActionScript background helps me read code and talk with developers. I use C# for small tools, checks and automation.

Q: When would you build an editor tool instead of doing the task by hand?
A: I look at how often the task repeats, how often people make mistakes in it, and how hard the tool is to keep working. A one-time task I do by hand. A weekly task with the same errors gets a small tool.

Q: How do you care about visual detail without slowing down production?
A: I separate real quality problems from my own perfectionism. If the player will notice it, I fix it; if not, I check whether it matters for this release. Good quality, but no endless polishing.

Q: What do you do when you do not know how to solve something?
A: I find out exactly what I do not know. Then I read the docs, look at examples in the project, or ask someone who knows, and make a small test if I can. Saying "I don't know yet" is fine; finding the right answer fast is what matters.

Q: How do you use AI tools in your work?
A: For research, comparing options, checklists, first drafts of small tools and repetitive work. I never trust it blindly: I compile, test and check the docs for our Unity version. It saves time, but I make the final decision.

--- PERFORMANCE ON MOBILE (asked most often) ---

Q: How would you find and fix a frame-rate drop on a low-end Android?
A: a development build on the phone and the Profiler - CPU or GPU. Then the biggest marker: Canvas - split the Canvas; particles - fewer and smaller; GPU - cut overdraw and heavy shaders. Measure again.

Q: What is a draw call and a batch?
A: A draw call is a request from the CPU to the GPU to draw something. A batch joins several compatible draw calls into one. Fewer calls mean less CPU time.

Q: Why does the Stats window show fewer batches but the frame is not faster?
A: Batches are CPU work. The limit can be the GPU instead, for example overdraw or heavy shaders. So I check both CPU and GPU time.

Q: What is overdraw and how do you reduce it?
A: Drawing the same pixel many times with transparent layers. I use tight meshes, fewer full-screen transparent images and smaller particles. The Overdraw view shows the hot spots.

Q: What is fill rate and why does it matter on mobile?
A: How many pixels the GPU can draw per second. Phones have little, so big transparent layers and big particles cost a lot.

Q: What frame budget do you target?
A: 16.6 ms per frame for 60 fps, 33.3 ms for 30 fps. I leave a margin, because phones heat up and slow down. I watch the worst frames, not only the average.

Q: How do you read the Profiler when the game is slow?
A: I profile a development build on the phone. If the render thread waits in Gfx.PresentFrame, the GPU is the limit; otherwise the CPU. Then I sort by Self time to find the slow function.

Q: Why is profiling in the Editor not enough?
A: The Editor adds its own work to the numbers, and a PC is much faster than a phone. I use the Editor only to iterate on problems I first found on the device. I also test a release build, because some problems show only there.

Q: What is GC.Alloc and why care?
A: Memory created in this frame that later becomes garbage. More garbage means more pauses when Unity cleans it. I keep it at zero per frame and use Call Stacks to find where it comes from.

Q: What creates garbage in UI code that people forget?
A: Formatting text every frame, GetComponent in Update, and new lists. I update text only when the value changes and use SetText. FindObjectOfType in gameplay is bad too: it searches the whole scene.

Q: The frame rate is fine but the game feels stuttery. Why?
A: Some frames are much slower than the rest: garbage collection, loading or shader compile. Average FPS hides them. I look at the frame time graph and the worst frames.

Q: How do you prove an optimization helped?
A: Same phone, same scene, same actions, before and after. I give numbers, like 14.2 ms to 10.8 ms. I also look at the worst frames.

Q: A popup opens with a visible hitch. What do you check?
A: The Profiler on that frame: creating objects, texture upload, shader compile, layout rebuild, garbage. Then I fix the biggest one: pool or preload the popup, or prewarm the shader.

Q: Why test on a low-end device?
A: Problems show there first. If it runs well on a weak phone, a strong one is usually fine. I also test long sessions, because phones slow down when they get hot.

Q: What is the difference between Update, FixedUpdate and LateUpdate?
A: Update runs every frame, FixedUpdate on the physics step, LateUpdate after animation. Camera follow goes in LateUpdate.

Q: Why use Time.deltaTime?
A: So movement is per second, not per frame. Without it, objects move slower when the frame rate drops.

Q: What three things do you check first when a mobile scene is too heavy?
A: Whether it is CPU or GPU (Profiler on the phone), then the biggest marker on the main thread (Canvas, particles, garbage), then overdraw in the Frame Debugger. I measure each change separately.

Q: How do you balance quality and performance in a live game on many devices?
A: Quality tiers (low/mid/high) with a budget for each. On weak phones fewer particles, lower resolution, no post-processing; on strong ones full beauty. I decide by numbers, not by eye.

--- SHADERS (Shader Graph, math, cost on mobile) ---

Q: How do you reduce shader cost on mobile without killing the look?
A: fewer nodes and texture samples, Unlit instead of Lit, half instead of float where possible, smooth math in the vertex shader, few keywords (variants). And measure on the phone.

Q: What is the SRP Batcher?
A: In URP it makes draw calls cheaper for objects that use the same shader variant, even with different materials. The shader must keep its material properties in the UnityPerMaterial buffer.

Q: What breaks SRP Batcher compatibility?
A: A shader without the UnityPerMaterial buffer, or a MaterialPropertyBlock on the renderer. The shader Inspector shows if it is compatible.

Q: How do keywords affect batching?
A: Every keyword combination is a different shader variant. Two materials with the same shader but different keywords do not batch together. Fewer keywords, more batching.

Q: shader_feature or multi_compile?
A: shader_feature when the option is set on the material; unused variants are removed from the build. multi_compile when code switches it at runtime; all combinations are built, so the build grows.

Q: What does a magenta or cyan object mean?
A: Magenta is the error shader: missing, broken, or a Built-in shader in URP. Cyan means the shader is still compiling. If it is pink only on the device, a variant was probably removed from the build.

Q: A shader variant freezes the game on first use. How do you avoid it?
A: I prewarm it during loading with ShaderVariantCollection.WarmUp. Then the first real use does not stall the frame.

Q: Sprite-Lit or Sprite-Unlit?
A: Sprite-Lit reacts to Light 2D, Sprite-Unlit ignores lights and is cheaper. Unlit is good for UI-like sprites and effects that glow by themselves.

Q: How do you animate a material without breaking batching?
A: I animate a shared value or use shader time, plus a small per-object difference in vertex colour. In URP a MaterialPropertyBlock takes the object out of the SRP Batcher, so I avoid it.

Q: How do you make a dissolve effect?
A: A noise texture is compared with a threshold; pixels below it disappear. A thin bright edge near the threshold looks like burning. Animating the threshold from 0 to 1 dissolves the object.

Q: How do you make a UV scroll for water or energy?
A: I move the UV by time multiplied by speed and repeat the texture. Two layers moving at different speeds look much richer.

Q: What is a Shader Graph Sub Graph for?
A: For reusing a group of nodes, like dissolve or UV scroll, in many graphs. One fix in the Sub Graph updates all of them.

Q: If a shader is slow on one phone only, what do you do?
A: I capture a frame on that phone and look for heavy math, many texture reads or discard. Then I simplify it, use half precision, or move work from pixels to vertices.

Q: Is alpha clipping cheaper than transparency?
A: Not always. On phone GPUs clipping (discard) turns off an early optimization and can cost more than blending. I measure on the device and choose per effect.

Q: How do you make light effects in URP 2D?
A: Light 2D components with the 2D Renderer, and normal maps for volume if needed. Things that glow by themselves use unlit sprites with Bloom. Real lights per particle are too expensive.

Q: What is the dot product and where do you use it?
A: A number that says how much two directions point the same way: 1 - the same, 0 - at a right angle, -1 - opposite. I use it for lighting (normal and light), for a rim around an object (normal and view) and for angle-based masks.

Q: What is the difference between a vertex and a fragment shader?
A: The vertex shader runs once per vertex, the fragment shader once per pixel. There are many more pixels, so smooth calculations that can be interpolated I move to the vertex shader.

Q: When half and when float?
A: half for colour, directions and small numbers: it is faster on phones. float for world positions, ever-growing time and big UVs, because half loses precision there and the picture shakes.

Q: When do you write HLSL instead of Shader Graph?
A: When I need exact cost control, custom lighting or a port of an existing shader. Otherwise Shader Graph, because others can edit it. But I must be able to read simple HLSL to find what is expensive.

Q: Make a dissolve in 5 minutes in the interview - how?
A: Noise -> compare with a Dissolve Amount slider through Step (or Smoothstep for a soft edge) -> that is the alpha. For a glowing edge - a narrow band near the threshold, multiplied by an edge colour and added to the colour. I expose parameters: threshold, edge width, colour.

--- RENDER PIPELINE: BUILT-IN, URP, HDRP ---

Q: Which pipeline and why?
A: URP with the 2D Renderer - light for phones, gives 2D lights, sorting, Shader Graph and the SRP Batcher. Built-in is deprecated, HDRP is not for phones.

Q: Forward or Deferred for a mobile 2D game?
A: Forward. Deferred keeps several full-screen textures and does extra passes, and phones are limited in memory and bandwidth. A 2D game rarely needs dozens of lights per pixel.

Q: Everything is pink after moving to URP. What do you do?
A: The materials still use Built-in shaders. I run the Render Pipeline Converter and remake custom shaders in Shader Graph.

Q: Why can you not drop the 2D Renderer into Graphics settings?
A: Graphics and Quality take a pipeline asset (UniversalRP), and the 2D Renderer is a renderer inside it. It goes into UniversalRP's Renderer List.

--- DRAW CALLS AND BATCHING ---

Q: How do you reduce draw calls?
A: atlases per screen, shared materials, a draw order without texture switches, the SRP Batcher. I check in the Frame Debugger why a batch broke.

Q: What is the difference between static batching, dynamic batching, GPU instancing and the SRP Batcher?
A: Static merges non-moving meshes at build time, dynamic merges small meshes every frame. Instancing draws many copies of one mesh in one command, and the SRP Batcher does not reduce commands but makes each cheap for the same shader. For 2D sprites in URP the main ones are the SRP Batcher and atlases.

Q: How do you set up atlases for UI and 2D, and what problems did you see?
A: One atlas per screen or feature, UI separate from world art, big backgrounds and flipbooks outside atlases. Problems: an atlas that grows forever, a sprite on a second atlas page, and broken batches because of draw order.

--- TEXTURES AND COMPRESSION ---

Q: Which compression format for iOS/Android and why?
A: ASTC - the best quality-to-size ratio; block size by asset importance (4x4 UI, 6x6 items, 8x8 shadows). ETC2 as a fallback for old Android. I compare on a real phone.

Q: What is Pixels Per Unit?
A: How many pixels of a sprite make one Unity unit. I keep one PPU for a whole art set, so sizes match. Double PPU makes the sprite half as big.

Q: What is a Sprite Atlas for?
A: It packs many sprites into one texture, so they draw in fewer draw calls. I group sprites that appear on the same screen.

Q: Why not one big atlas for the whole game?
A: The whole atlas stays in memory while any sprite from it is used. A screen that needs one icon would load everything. So I make one atlas per screen or feature.

Q: When does a sprite not batch even in the same atlas?
A: When it uses a different material, or when something else with another texture is drawn between them. Sorting order matters, not only the atlas.

Q: How do you plan atlases for a screen?
A: I group sprites shown together and keep UI apart from world art. Soft shadows and gradients go into their own atlas with a cheaper compression.

Q: How do you choose texture compression for mobile?
A: ASTC: 4x4 for sharp UI and small text, 6x6 for items, 8x8 for soft shadows and gradients. ETC2 as a fallback for old Android. I compare the result on a real phone.

Q: Why turn off Read/Write and mipmaps?
A: Read/Write keeps a second copy of the texture and doubles its memory. Mipmaps add a third more memory and are not needed for UI and 2D shown at a fixed size. World sprites that zoom far out may still need them.

Q: Why keep source art uncompressed when using an atlas?
A: The atlas decides the final format. If the source is compressed too, the picture is compressed twice and loses quality.

Q: Why set Mesh Type to Tight, and when is it worse?
A: Tight makes the mesh follow the sprite shape, so less empty transparent area is drawn. But a very complex outline makes many vertices. For small simple sprites Full Rect can be cheaper.

Q: How do you slice a sprite sheet?
A: Sprite Mode Multiple, then the Sprite Editor: automatic or by grid. When the image changes, I re-slice but keep the same sprite ids, so prefab links do not break.

Q: How do you set a sprite pivot and why does it matter?
A: In the Sprite Editor. The pivot is the point for position, rotation, scale, and sorting. For things standing on the ground I put it at the bottom.

Q: What does Sprite Atlas "Include in Build" do?
A: On: the atlas ships inside the game and loads with the sprites. Off: you must load it yourself, for example through Addressables.

Q: A sprite has a thin line or halo at its edge. How do you fix it?
A: Usually colour bleeds from neighbours in the atlas or from transparent pixels. I add atlas padding and turn on Alpha Is Transparency. I also check the edges in the source art.

Q: The artist gives you a PSD with 200 layers. What do you do?
A: We agree which layers must stay separate, because they move or change in the game. Everything else is merged into fewer sprites. Fewer sprites means less memory and fewer draw calls.

Q: The artist wants a 4096 texture for a small icon. What do you say?
A: I show it at real size on a phone next to a 512 version. If nobody sees a difference, we save the memory. If they do, we pick a middle size together.

Q: How do you decide texture resolution for different devices?
A: Max Size by the size on screen, and for weak devices smaller versions through quality tiers or Addressables variants (HD/SD). I check on a weak phone whether the difference is even visible.

--- PARTICLES AND VFX ---

Q: A big explosion lags on weak phones. First three steps?
A: fewer particles and a shorter life, a smaller particle size (less overdraw), one shared material. Then crop the texture tighter and measure again.

Q: How do you make a particle burst for a reward?
A: Emission with one Burst, short lifetime, Size and Color over Lifetime for the pop and fade. Stop Action turns it off or returns it to the pool when it ends.

Q: What does Simulation Space do?
A: Local moves the particles together with the parent. World leaves them behind in the world, which is right for smoke or trails from a moving object.

Q: How do you keep particle effects cheap on mobile?
A: Few systems, one shared unlit material, low Max Particles and little overdraw. No real lights and no collisions. Effects off screen are paused by culling.

Q: How do you decide how many particles is too many?
A: I measure the effect on the weakest target phone together with the rest of the screen. Usually overdraw (how much screen the particles cover) is the limit before the particle count.

Q: What if an effect must be very big for one moment?
A: I make it short and keep other effects quiet at that moment. Fewer but bigger particles look big too. Then I test that exact frame on a weak phone.

Q: Why use Prewarm?
A: A looping effect with Prewarm starts as if it already ran once. So it does not look empty for the first second, for example smoke from a chimney.

Q: How do you make an effect look the same every play?
A: I turn off Auto Random Seed and set a fixed seed. Then the particles move the same way every time. This is useful for reviews and tests.

Q: Additive or alpha blended particles?
A: Additive for light, fire and sparks: it only makes things brighter. Alpha blend for smoke and dust that must cover what is behind. A white cloud on a light sky needs alpha, with additive it disappears.

Q: What is a Sub Emitter?
A: A particle system started by another one, when a particle is born, hits something or dies. For example a spark that bursts into smaller sparks. The child system needs its own burst.

Q: How do you pool particle effects, and what goes wrong most often?
A: When the effect ends (Stop Action Callback) it goes back to the pool, and I reset it when I take it again. Typical bugs: reusing an effect that is still playing, returning it twice, or old colour and scale left over. If Stop Action is Destroy, the pooled effect is simply gone.

Q: What do you check if a particle effect does not appear?
A: Is it playing and on screen, sorting layer and order, material and shader, Max Particles and emission. I also check the camera culling mask and Simulation Space.

Q: How do you sort particles with sprites in 2D?
A: The particle Renderer has Sorting Layer and Order in Layer, like a sprite. Particles over UI need a Screen Space - Camera Canvas and a layer above it.

Q: Particle System or VFX Graph?
A: Particle System for most mobile effects: it runs on the CPU and works everywhere. VFX Graph is for very many particles on devices with compute shaders. On phones without them VFX Graph shows nothing.

Q: How do you keep VFX readable on a busy screen?
A: A clear shape and timing, and contrast with the background. Not too many effects at once. The effect should support the gameplay moment, not hide it.

Q: What are the most common VFX performance problems on mobile?
A: Overdraw from big transparent particles in layers, too many particles, a different material for every system and effects that are calculated off screen. I fix them with size, count, a shared material and Culling Mode.

--- UI (Canvas, uGUI, TextMeshPro) ---

Q: How do you optimize a complex UI screen on mobile?
A: split the Canvas into static and dynamic, shared atlases, Raycast Target off on decoration, fewer full-screen transparent panels, no heavy Layout Groups. I check Canvas.SendWillRenderCanvases in the Profiler.

Q: How do you set up a Canvas for a portrait mobile game?
A: Canvas Scaler set to Scale With Screen Size, reference resolution 1080x2400, Match about 0.5-0.7. Buttons go inside a Safe Area root. Then I test on a tall phone and on a tablet.

Q: How do anchors work in a RectTransform?
A: Anchors are points on the parent rectangle. Anchors together give a fixed size; anchors apart make the element stretch with the parent. I set anchors and pivot first, then the position.

Q: What is the difference between Content Size Fitter and a Layout Group?
A: Content Size Fitter changes the size of its own object, for example a label to fit its text. A Layout Group places and sizes its children, but not itself. Putting both on one object often makes them fight.

Q: Why can a big Canvas be slow?
A: When one element changes, the whole Canvas rebuilds its mesh. A timer on a big screen can rebuild the whole screen every second. So I put static UI and often-changing UI on separate Canvases.

Q: You split Canvases. How many is too many?
A: Each Canvas adds its own draw calls, so too many also cost. I split by how often things change: static background, timers and counters, and each popup. Only where it removes a real rebuild.

Q: What exactly causes a Canvas rebuild?
A: Changing a colour, sprite, text, turning something on or off, or changing size and position inside a layout. Moving an object without a layout is cheaper but still marks the Canvas dirty.

Q: What makes a UI button not react to clicks?
A: Usually a missing EventSystem, a missing Graphic Raycaster, Raycast Target turned off, or an invisible Image on top that catches the tap. With the new Input System the EventSystem also needs InputSystemUIInputModule.

Q: Why is Graphic Raycaster a cost?
A: On every tap it checks all raycast targets on that Canvas. I turn Raycast Target off on decoration and remove the Raycaster from Canvases that take no input. If the whole background must be clickable, I use one invisible target, not every image.

Q: How do you handle the notch on phones?
A: I put the top and bottom bars inside a Safe Area root that follows Screen.safeArea. Backgrounds can still go under the notch, edge to edge. I never shrink the whole Canvas.

Q: How do you fade a whole popup?
A: A CanvasGroup on the popup root gives one alpha for everything inside. While it is hidden I also turn off interactable and blocksRaycasts, so it cannot be tapped.

Q: How do you make a popup Show and Hide?
A: Show: scale and fade in with a small overshoot, about 0.3-0.5 s. Hide is a faster reverse, about 0.2 s, without overshoot. Input is blocked during the change.

Q: Mask or RectMask2D?
A: RectMask2D for rectangles: it is cheaper and supports soft edges. Mask can use any shape, but it uses the stencil buffer and breaks batching more.

Q: How do you make a scroll list with many items fast?
A: I reuse a few item views while scrolling instead of creating one object per item. I use RectMask2D and put the list on its own Canvas. This way a list of 500 items costs like a list of 10.

Q: How do you show a timer that updates every second without cost?
A: I change the text only when the number changes, not every frame. The timer sits on its own small Canvas, so it does not rebuild the whole screen.

Q: What if a Layout Group is slow?
A: Layout Groups recalculate when children change. For a static layout I let it calculate once and then turn it off, or I use anchors. For long lists I reuse views.

Q: How do you animate UI without breaking layouts?
A: I animate a child inside the layout element, not the element the Layout Group controls. Otherwise the Layout Group resets the position every rebuild and fights the animation.

Q: What is 9-slicing?
A: I set borders on the sprite in the Sprite Editor. The corners stay the same and the edges and middle stretch. One small sprite can make a panel or button of any size.

Q: Why should UI shaders use vertex color?
A: Image color and CanvasGroup fade reach the shader as vertex color. If the shader ignores it, tint and fade stop working. A UI shader must also support masks.

Q: How do you keep UI in sync with game data?
A: The UI listens to events or reads one data source; it never owns the data. When the data changes, the view updates. Every screen can be rebuilt from the data, for example after a reload.

Q: How do you make a reward flight: coins flying to the counter?
A: Pooled icons fly from the source to the counter on a curve, with small delays between them. The counter punches when each icon lands. The real number is updated in the data at once; the text rolls up at the end.

Q: What are the most common Canvas mistakes that kill performance?
A: One huge Canvas where something changes all the time, and Raycast Target on every image. Also nested Layout Groups, an Animator on every button and full-screen transparent panels.

--- 2D WORKFLOW: SPRITES, IMPORT, SORTING ---

Q: How do you configure sprite import for a 2D mobile game?
A: Sprite, one PPU per set, pivot by purpose, Max Size by size on screen, no mipmaps and Read/Write, compression through the atlas.

Q: How does 2D render order work?
A: Sorting Layer first, then Order in Layer, then distance to the camera. A Sorting Group makes an object made of many sprites sort as one.

Q: How do you sort sprites by Y?
A: In URP 2D: Transparency Sort Mode Custom Axis (0,1,0) on the Renderer 2D Data. The sprites share one layer and order, Sprite Sort Point is Pivot, and the pivot is at the bottom.

--- ANIMATION (Animator, tweens, 2D skeletons) ---

Q: When do you NOT use the Animator for UI?
A: for many small moves. An active Animator dirties the Canvas every frame and costs CPU, even when idle. There I use a tween or turn the Animator off after the clip.

Q: How do Animator parameters work?
A: There are Float, Int, Bool and Trigger. Code sets them with SetFloat, SetBool and SetTrigger. A Trigger resets itself when a transition uses it; a Bool stays until you change it.

Q: Trigger or Bool?
A: Bool for lasting states, like IsOpen. Trigger for one-time actions, like Show or Build. If two Triggers are set in one frame, one can stay and fire later by surprise, so I reset them or use Bools.

Q: Why do Animator transitions sometimes feel late?
A: Has Exit Time is on, so the transition waits for the clip, or the transition is long. For instant reaction to a tap I turn Exit Time off and use a short transition.

Q: How do you show a UI animation while the game is paused?
A: I set the Animator Update Mode to Unscaled Time, and particles to Unscaled Delta Time. At timeScale 0 normal time stops, so otherwise they freeze.

Q: Animator or tween for a simple button pop?
A: A tween or a short clip is fine. I avoid an Animator on every idle UI element, because an active Animator makes the Canvas rebuild every frame. After the clip I turn the Animator off.

Q: Animator or code for a counter that rolls up numbers?
A: Code or a tween, because the number comes from data. The Animator can do the fixed punch around it. Each tool does the part it is good at.

Q: How do you sync a sound or VFX with an animation?
A: With an Animation Event on the exact frame. I never check a value like "rotation equals 90", because Unity can skip that exact value between frames.

Q: What should an animation never decide?
A: Game logic, like whether a purchase worked or a reward was given. The animation only shows the result. For example, a reward given at the end of a clip is lost if the player closes the screen early.

Q: How do you handle an animation that must stop on the last frame?
A: Loop Time off on the clip, so the state stays at the end. For logic after it, I use an Animation Event on the last frame, not a timer.

Q: What are Animation Layers used for?
A: To play another animation on top of the base, for example only the upper body. Override replaces lower layers, Additive adds on top. An Avatar Mask limits a layer to some parts.

Q: Why override bone or object values in LateUpdate?
A: The Animator writes transforms after Update. If I change them in Update, the Animator overwrites my value. In LateUpdate my change comes last and stays.

Q: When do you use Timeline?
A: For one-time sequences with many objects and exact timing: an intro, a reward sequence, a level complete screen. For states that switch back and forth I use the Animator.

Q: What is root motion and do you need it for UI?
A: Root motion moves the object from the animation data itself, mostly for walking characters. For UI and most 2D effects I keep it off. Movement comes from the animated RectTransform or code.

Q: Spine, 2D Animation or frame-by-frame - when which?
A: Spine for characters with many animations, because one rig gives everything and uses little memory. 2D Animation is similar but built into Unity, without a licence. Frame-by-frame for short stylised moves, but every frame is a separate picture in memory.

--- ADDRESSABLES AND REMOTE CONTENT ---

Q: How would you build Addressables for a live game with many events?
A: a stable core - local, events and islands - remote groups, one group per event or island, shared things separate. A remote catalog so new content arrives without a release. Every load - with a Release.

Q: What usually takes the most build size?
A: Textures. First compression, then a smaller Max Size per texture until it starts to look worse. Everything in the Resources folder always ships, so I keep it small.

Q: The build is too big. Where do you start?
A: The Build Report shows which assets are biggest. Usually textures, then audio and fonts. Then compression, removing unused content, and moving optional content to remote Addressables.

Q: Memory grows every time a player opens a screen. What is it?
A: Something is loaded and never released: Addressables without Release, objects not destroyed, or events still subscribed. I compare two Memory Profiler snapshots, before and after.

Q: How do you use the Memory Profiler?
A: I take a snapshot, do the action, take another and compare. I look for things that should be gone and what still holds them. It also shows if the growth is textures (content) or managed memory (code).

Q: Why can Destroy not free memory right away?
A: Destroy removes the object, but the texture or mesh it used stays loaded while anything still uses it. It is freed later by Resources.UnloadUnusedAssets or by releasing Addressables.

Q: How do you load a scene without freezing?
A: LoadSceneAsync with a loading screen, and heavy content loaded in the background with Addressables. I avoid big loads that block the main thread.

Q: What is the difference between Resources and Addressables?
A: Everything in Resources always ships in the build and is hard to unload. Addressables load from local or remote storage, handle dependencies, and can be released.

Q: How would you split Addressables groups?
A: By when the content is needed and how it changes. A local group for the core UI, fonts and shaders; remote groups per feature or per island. A player then downloads only what he uses.

Q: What is a catalog in Addressables?
A: The list of all addresses and where each bundle lives. With a remote catalog the game can find new content without a new app build.

Q: How do you release memory from Addressables?
A: Every LoadAssetAsync needs a Release, every InstantiateAsync needs a ReleaseInstance. A bundle unloads only when nothing uses it anymore.

Q: Cannot Change or Can Change Post Release?
A: Cannot Change for static content: changed assets go into new small update bundles, and old bundles stay valid. Can Change rebuilds the whole bundle, so players download all of it again.

Q: How do you check Addressables duplicates?
A: With the Analyze tool. An asset used by two groups without its own group is copied into both bundles. The fix is to give the shared asset its own group.

Q: How do you ship a content update?
A: "Update a Previous Build" with the content state file from the released version. Only changed remote content is rebuilt. I keep that file for every release.

Q: How do you test remote content before release?
A: A local server or test profile, build the content, and run the game against it. I test updates and bad cases too: missing files, slow network, offline start.

Q: What if Addressables loading fails on a bad network?
A: I handle the failed operation: show a retry button, use local content if possible, and release the handle. The player never sees a frozen screen.

Q: What if a player has an old catalog and new code?
A: Remote content must work with the code that is already shipped. New code that needs new content comes with an app update, or checks the content version first.

Q: How do you check Addressables groups before a release?
A: Analyze for duplicates, build the content, run the game against a local test server. I also check the bad cases: no network, a slow network, a missing file, an offline start.

--- PROFILER AND FRAME DEBUGGER (often a live test) ---

Q: Here is a Profiler - where is the bottleneck?
A: first CPU or GPU by threads, then the biggest marker. For example: "The main thread is the bottleneck, most of the time is in Canvas.SendWillRenderCanvases, so I split the Canvas".

Q: How do you fit a 2D camera for different phones?
A: I choose the orthographic size from the content, so it fits the narrowest phone. Wider screens and tablets simply show more around it. I test the narrowest screen, not only the Game view.

Q: What if the game must support both short and very tall phones?
A: Safe area and anchors, and I test the extremes: 4:3 and 9:20. Backgrounds go past the safe area, buttons stay inside it.

Q: A screen looked fine in the Editor but is blurry on the phone. Why?
A: Usually the texture Max Size or compression for that platform, a wrong Canvas Scaler, or a sprite scaled up above its real size. I check the platform settings of the texture first.

Q: Text looks different on the device than in the Editor. What do you check?
A: The font asset, its fallback fonts, missing letters, and the Canvas Scaler. Fallback fonts can sit at a different height, so I check them with my eyes.

Q: What do you check first when a sprite looks wrong in the game?
A: I go step by step: source art, import settings (slicing, pivot, PPU, compression), prefab, animation, shader, runtime state, loading. Turning systems off one by one shows which one is guilty.

Q: How do you find where an error comes from in a build?
A: The Player.log file with stack traces turned on, or logcat on Android and the Xcode console on iOS. The Unity Console shows only the Editor.

--- PREFABS AND VARIANTS FOR LIVE EVENTS ---

Q: How do you avoid a memory explosion with hundreds of event variants?
A: shared sprites and materials instead of copies, each event - its own remote Addressables group, unloading after the event ends, recolouring with a material instead of new big textures.

Q: What is the difference between a prefab variant and a nested prefab?
A: A nested prefab is a prefab placed inside another prefab, like a marker inside an item. A variant is a copy of a base prefab that keeps only its differences. I keep the chain short: the base plus one level.

Q: How do you apply or revert prefab overrides safely?
A: I open the Overrides list first to see exactly what changed. Then I apply only what really belongs to the base and revert my local experiments. I never press "Apply All" from a variant, because it changes every other variant too.

Q: What happens if you rename a child that is animated?
A: The animation clip finds children by their path name, so it silently loses that child. Nothing shows an error, the object just stops moving. So I rename first and animate after.

Q: When do you use ScriptableObjects?
A: For shared data and settings: item lists, prices, rewards, tuning numbers. One asset can feed many prefabs. Designers change the values without touching code or scenes.

Q: What happens if you delete a .meta file?
A: Unity creates a new GUID for the asset, and every link to it breaks. Sprite slices stored in the .meta are lost too. That is why the .meta must always be committed with its asset.

Q: When do you use object pooling?
A: For things created often: coins, bullets, reward effects, list items. Reusing them avoids lag spikes from creating and destroying objects. Rare screens do not need a pool.

Q: What is the difference between Destroy and SetActive(false)?
A: SetActive(false) only hides the object; it stays in memory, ready to use again. Destroy removes it completely. Objects that come back often I hide or pool instead of destroying.

--- ART PIPELINE AND TOOLS (asked especially of a Senior) ---

Q: Design on a whiteboard a pipeline for islands, UI, particles and Addressables.
A: sources -> import with presets -> validators (size, compression, names, budgets) -> atlases -> Addressables groups (core local, events remote) -> review -> build. Plus owners and budgets per device tier.

Q: What is the difference between EditMode and PlayMode tests?
A: EditMode tests run in the Editor without Play, good for tools and data. PlayMode tests run real frames, good for gameplay and UI flow.

Q: Why does a test fail with "Unhandled log message"?
A: Any Debug.LogError during a test fails it. If the error is expected, I tell the test with LogAssert.Expect.

Q: How do you run Unity tests in CI?
A: Unity -batchmode -runTests with -testPlatform and -testResults. The results file shows passed and failed tests.

Q: What makes a good test in Unity?
A: It checks behaviour, not hierarchy names. It does not depend on the open scene, it cleans up after itself, and it fails with a clear message.

Q: What if a test is flaky?
A: I find the cause: timing, shared state or the open scene. I wait for a condition, not for a longer time.

Q: Why do you write tests for editor tools?
A: Tools change assets for the whole team. A test proves the tool does the right thing and keeps it working when Unity or the project changes.

Q: How do you make an editor tool safe for artists?
A: Undo for every change, clear error messages instead of silent defaults, and a preview before applying. It only touches the folders it should.

Q: How do you keep a tool from being abandoned?
A: It solves a real repeated task and is simple to use, with a short guide. I watch the first artists use it and fix what confuses them.

Q: How do you make an Inspector easier for artists?
A: Clear field names, sliders ([Range]), tooltips and headers. Fields they should not touch are hidden. For bigger tools, a custom editor window.

Q: When do you write an AssetPostprocessor?
A: To apply import rules automatically by folder, like compression and Max Size. Then nobody can import a texture with wrong settings by accident.

Q: How do you validate content before a build?
A: An editor check that finds missing links, wrong import settings and too many materials. It fails with a clear list, so the problem is fixed before release.

Q: Why do files written from outside Unity not appear?
A: Unity imports files when the window gets focus or on AssetDatabase.Refresh. A script that writes files must call Refresh before using them.

Q: How do you avoid merge conflicts in scenes and prefabs?
A: Small prefabs instead of one big scene, and clear owners for each part. Scenes are saved as text (Force Text), so Git can merge them, with UnityYAMLMerge as the merge tool.

Q: How do you handle a merge conflict in a scene?
A: I try UnityYAMLMerge first. If it fails, I take one side and redo the other change in the Editor, then check the scene works.

Q: What goes into .gitignore for Unity?
A: Library, Temp, Obj, Logs, Build and UserSettings folders, plus IDE files. Assets, Packages and ProjectSettings stay in Git.

Q: Why use Git LFS for art?
A: Big binary files like PSD and FBX make the Git history huge. LFS stores them outside the normal history.

Q: How do you review a prefab in a pull request?
A: I open it in Unity, not only the text diff. I check the hierarchy, links, overrides, and that it works in its scene.

Q: What do you do when a teammate's prefab change breaks your screen?
A: I find the exact change in Git history and talk to the owner. We agree on a fix together; I do not silently overwrite their work.

Q: What is the first thing you check in someone else's prefab?
A: Missing links, the hierarchy and names, and which components do the real work. Then overrides on instances in scenes that could break.

Q: How do you make the team follow import and naming rules?
A: I make the rules automatic: import presets per folder and a validator that blocks wrong things with a clear error. A document is needed, but alone it does not work, while a tool works every time.

--- 2D LIGHTS AND POST-PROCESSING ON MOBILE ---

Q: Which post-processing effects do you limit on weak phones?
A: Motion Blur and high-quality Depth of Field - off; Bloom - fast mode or off; I keep Color Grading. Every effect is a full-screen pass.

--- MEMORY AND ASSET BUDGETS ---

Q: How do you control memory in a live game?
A: budgets per device tier, Memory Profiler snapshots before and after, a Release for every Addressables load, unloading event content. Validators keep heavy assets out.

Q: Tell me how you would fix memory crashes on weak phones.
A: A Memory Profiler snapshot on that phone - which textures are biggest and what did not unload. I lower Max Size, set the right compression, add Releases and a validator on texture size, so the problem does not come back.

--- QUALITY TIERS AND DEVICES ---

Q: How do you define and test quality tiers?
A: tiers by GPU and memory from a device list, a separate URP asset per tier, its own budgets. I test first on the weakest Android and an old iPhone, plus long sessions for heat.

--- BUILD AND PLAYER SETTINGS ---

Q: What do you change in Player Settings for size and performance?
A: IL2CPP, ARM64, ASTC, Vulkan with a GLES fallback, AAB, stripping. Plus I remove extra shader variants.

--- GIT AND WORKING TOGETHER ---

Q: How do you build prefabs and scenes to avoid conflicts?
A: small prefabs with owners, the scene only assembles them, Force Text and UnityYAMLMerge. Small changes, I check my own diff before the PR.

--- 2D CAMERA ---

Q: How would you set up the camera for an island on different screens?
A: a fixed orthographic size for the narrowest phone, wider ones show more sky. I test a 9:20 phone and a 3:4 tablet.

--- BEHAVIOURAL QUESTIONS (STAR) ---

Q: How do you report a bug so it is easy to fix?
A: Steps to repeat it, the expected and the actual result, device and build version. Plus a screenshot or video and the log.

Q: How do you estimate a task you have not done before?
A: I split it into small parts and prototype the risky part first. I give a range, not one number, and update it when I learn more.

Q: What if you find a bug in someone else's system close to release?
A: I tell the owner right away, with steps and proof, and suggest a fix if I have one. I do not patch it silently.

Q: What if the deadline cannot be met?
A: I say it early: what can be done by the date and what must move. Less scope is better than a broken release.

Q: How would you convince an artist to change their workflow?
A: I show the problem on the phone and give a tool or preset that makes the new way easy. If the new way is more work for them, it will not stick.

Q: What would you improve first in a new project pipeline?
A: Nothing in the first weeks, before I understand why it works like this. Then the thing that wastes the most time for the team, with a small safe change that I measure.

Q: How do you hand over a feature?
A: A short note: what it does, how it is built, how to change it, and known limits. Plus the prefab and settings in a clean state in Git.

Q: When do you use a coroutine?
A: For simple steps over time: wait, then do something, like show a popup 0.5 s after a reward. For many timed UI sequences a Timeline or an Animator clip is easier to tune, because the timing is visible.

Q: What would you do in your first week on this project?
A: Build and run the project, read the pipeline docs, and look at how existing features are made. Then take a small real task. I ask questions early instead of guessing.

Q: What does "production-ready" mean for a feature?
A: It works on the target phones and fits the frame and memory budget. It handles all states and errors, it is tested and reviewed, and another person can work with it.

Q: How do you check AI-written Unity code?
A: I compile it, run the tests and look at the result in the Editor. I check every API name in the docs for our Unity version, because AI can invent APIs or use old ones. I treat AI output as a draft from a fast junior: useful, but I review every line.

Q: Where does AI help you most as a Technical Artist?
A: Small editor tools, batch scripts, first drafts of shaders, and explaining code I do not know. It saves time on routine work, but I still own the result.
