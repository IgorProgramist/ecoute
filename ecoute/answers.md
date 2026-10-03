ABOUT ME (facts about me, use them in answers):
- Unity Technical Artist with 7+ years in game development (since 2014), mostly mobile slot games for international studios.
- Strongest areas: UI implementation (uGUI, TextMeshPro), animation integration (Animator, tweens, Spine), atlas assembly, and performance optimization on weak phones.
- I work as the bridge between artists and developers: I integrate art so it looks right and runs fast.
- Before Unity I was a Flash/AS3 game developer - that gives me a solid programming foundation.
- I am comfortable on live projects: large content volume, frequent updates, release support.
- Past companies: Pur-Pur Games, Skywind Group, Sigma Software, GamePoint, Mad Brain Games, VOLMI, Custom Game Studio (Warsaw).
- Portfolio: slot game preview, GameChatUnity (Unity UI chat system), BotBusters (3D game), Player_Spine_to_Unity, Word Farm Adventure, Adventure 3Dgame.

UNITY KNOWLEDGE (facts, in simple words):

WHAT MATTERS MOST IN A SENIOR TA INTERVIEW:
- The topics below go from the most often asked to the least.
- Most important for a Senior TA at Playtika: owning a feature from start to release (ownership).
- Second: performance and optimization on weak phones.
- Third: pipeline and tools for artists.
- Fourth: clear communication with artists, programmers and product.
- Likely live-test areas: a shader, scene optimization, or a pipeline/tool design on a whiteboard.
- No need to go deep into advanced 3D character rigging, ECS, networking or old Unity features. But I should know the basics of 3D asset integration, materials, prefabs and scene setup.

PERFORMANCE ON MOBILE (asked most often):
- What it is: The game must hold a stable frame rate on a weak phone.
- Every frame has a time budget: 16.6 ms for 60 fps, 33.3 ms for 30 fps.
- In practice I aim a bit lower than 16.6/33.3 ms (for example ~11 ms and ~22 ms). That leaves room for spikes and for the phone getting hot (thermal throttling). The exact budget depends on the project and the phones.
- The limit can be the CPU or the GPU, and each needs a different fix.
- Why: A mobile live game runs on thousands of different phones.
- If it lags on a weak one, the player leaves.
- How to think: Measure on a real weak phone (development build). The Editor on a PC does not show the real phone timings.
- Find out: is it CPU or GPU?
- CPU: draw calls, Canvas rebuilds, particles, garbage (GC), scripts.
- GPU: overdraw (transparent on transparent), heavy shaders, big screen size, post-processing.
- Change ONE thing and measure again. Give numbers: "14.2 ms -> 10.8 ms".
- Overdraw - one pixel drawn many times (background + panels + particles). Phones are limited by fill rate (pixels per second), so big transparent layers cost a lot. See it: Scene view -> Overdraw.
- Garbage - memory the code creates in a frame. Later the garbage collector cleans it, and that can cause a frame-time spike, more so when there is a lot of it. Code that runs every frame should avoid creating garbage.
- Average FPS hides hitches. Look at the worst frames (frame time graph).
- Test long sessions: after 10-30 minutes the phone heats up and the frame rate drops.

SHADERS (Shader Graph, math, cost on mobile):
- What it is: A shader is a small program on the graphics card that calculates the colour of every pixel.
- Material = shader + values (texture, colour, speed).
- Vertex shader - runs once per vertex (triangle corner): positions, UV, vertex colour.
- Fragment (pixel) shader - runs roughly once per drawn pixel: the final colour. There are many more pixels than vertices, so heavy math in the fragment shader = expensive.
- Shader Graph - shaders from nodes, no code. For 2D: Sprite Unlit / Sprite Lit.
- Why a TA cares: A shader can give motion and effects (wind, glow, shine, water, dissolve, scrolling) much cheaper than animating every object. But it is not free - I still check the fragment cost, texture samples and overdraw.
- One shared material on many objects gives them a chance to batch. But draw order, textures, keywords and masks can still split it, so I check the Frame Debugger.
- When to use what: A motion repeated on many objects (wind on trees) - a shader.
- A one-time unique motion - an Animator clip.
- Shader Graph - usually my first choice. HLSL (code) - when I need exact control over performance, custom lighting, or to port an old shader. A TA must be able to READ simple HLSL.
- Math they ask out loud:
- dot(A, B) - how much two directions agree: 1 same, 0 perpendicular, -1 opposite. Uses: lighting (normal · light direction), rim (normal · view), masks.
- UV - coordinates on the picture. Tiling = multiply (repeat), Offset = add (shift), scroll = offset + speed × time. Flipbook = pick a grid cell. Polar Coordinates - for circular effects.
- lerp(a, b, t) - blend a and b. step - hard 0/1 threshold. smoothstep - soft threshold. saturate - clamp to 0..1. frac - fractional part (repeat 0..1). sin(time) - a pulse.
- half - a lower-precision number in a shader. On phones that support it, it can be 16-bit; on some platforms Unity treats it as float. When the precision is good enough (colour, directions), it can make the shader cheaper or save power. I check the result on the real phone. float (32 bit) - for values where half is not precise enough and you can see it, like big world positions or big growing coordinates, otherwise things "shake".
- Shader variants: each keyword combination creates a separate shader variant. More variants make builds slower and more complex, and can make the build bigger. Different variants can also split SRP Batcher batches, so I keep the number of variants as low as I can. shader_feature removes unused variants, multi_compile does not.
- Magenta object = the shader does not work (missing, broken, Built-in in URP). Cyan can mean the shader is still compiling in the Editor.
- Many sprites, one material, different motion: global time + a per-object phase in the vertex colour.
- A per-object property override in URP can take that renderer out of the SRP Batcher - I check it in the Frame Debugger.

RENDER PIPELINE: BUILT-IN, URP, HDRP:
- What it is: The pipeline is Unity's "drawing engine": how the camera draws a frame, how light is calculated, which shaders work.
- Built-in - the older pipeline. Unity 6 shows a deprecation warning for it in Project Settings -> Graphics. For a new mobile project I would normally pick URP. But I would not move an existing live project just to change pipelines - first I would check its Unity version, its rendering setup and how much the move costs.
- URP - the pipeline I would normally use for a mobile game (it also runs on PC and consoles). Has the 2D Renderer, Shader Graph, SRP Batcher.
- HDRP - for high-end 3D on PC and consoles; it is not meant for phones (mobile is not a supported target).
- Why: Shader compatibility depends on the render pipeline - a Built-in shader may not work in URP (pink), so after a migration I check the standard materials and rebuild custom shaders where needed. Transparency sorting and Custom Axis sorting are general 2D features; in a URP 2D project the 2D Renderer Data holds the sorting settings.
- Post-processing is its own (Volume).
- When to use what: Mobile game - URP.
- Old Built-in project - keep it until moving pays off.
- AAA 3D - HDRP.
- Rendering paths in URP:
- Forward - Unity draws each object and calculates the lights that touch it, with a limit of lights per object. It is the default path in URP and usually a good start for mobile.
- Forward+ - can handle more lights by splitting the screen into tiles. For a mobile 2D game I would use it only if the project really needs it and the target phones support it.
- Deferred - first draws all objects into a G-buffer (several textures), then calculates light per pixel. It handles many lights in a different way, but it needs extra memory and passes, and that is usually expensive on phones.
- The 2D Renderer has its own settings. Forward/Deferred is a choice in the Universal Renderer, not a 2D Renderer setting.
- Where it is set: Graphics -> Default Render Pipeline = UniversalRP; Quality -> Render Pipeline Asset = UniversalRP (Quality overrides Graphics). The URP asset points to its renderers (like the 2D Renderer) in its renderer list - that is why you don't drop the 2D Renderer into Graphics or Quality directly.
- Moving from Built-in: the Render Pipeline Converter can upgrade Built-in materials, but it does not convert custom shaders - I remake those by hand or in Shader Graph.
- URP camera stack: a Base camera + Overlay cameras.

DRAW CALLS AND BATCHING:
- What it is: Draw call - a command from the processor to the graphics card "draw this with this material". Each costs CPU time.
- SetPass call - a switch to the shader pass used for drawing. Many SetPass calls can add CPU cost, so I watch them together with draw calls.
- Batching - Unity groups objects that fit together, so it needs fewer draw calls or cheaper ones. It works only when they are drawn the same way: material, texture, shader pass and keywords, sorting and masks all matter.
- Atlas (Sprite Atlas) - one big texture with many sprites, so they CAN share one texture and batch. It does not cut draw calls by itself: draw order, materials, shaders and masks can still split the batches.
- Why: A phone processor is weak.
- I set a draw-call budget for each project from typical weak phones, and check it with the Profiler and Frame Debugger - there is no one number for everyone.
- When to use what (4 kinds of batching): SRP Batcher - does NOT cut the number of draw calls, but makes each one cheaper to set up. Works for objects with the same shader variant, even with different materials. For 2D sprites I mainly think about Sprite Atlases, shared materials and draw order; for uGUI I think about Canvas batching and rebuilds instead.
- Static batching - joins meshes that never move at build time. It can cut draw-call cost but uses more memory. For uGUI I look at Canvas batching and rebuilds; I don't just assume static batching is the answer without checking the real setup.
- Dynamic batching - joins some small meshes every frame. Unity today usually doesn't recommend it, especially when the SRP Batcher already does the work, so I don't count on it without profiling.
- GPU Instancing - can render many copies of the same mesh and material in one instanced draw call (grass, trees).
- uGUI has its own batching inside a Canvas: elements with the same material and texture, drawn next to each other, can batch together.
- What breaks a batch: a sprite from another atlas between two sprites from the same atlas; different materials; masks; per-object property overrides in URP; different shader keywords.
- SRP Batcher and dynamic batching: in URP the SRP Batcher and GPU Instancing usually come before Dynamic Batching. I don't count on Dynamic Batching and I measure the real scene.
- Many copies of the same mesh can use GPU Instancing. For other compatible objects, the SRP Batcher can make draw calls cheaper for the CPU.
- If fewer batches don't make the frame faster, batching probably wasn't the main problem - I profile CPU and GPU time to find what really slows the frame.

TEXTURES AND COMPRESSION:
- What it is: Every picture has import settings: Max Size, compression, mipmaps, Read/Write, PPU.
- Why: In a 2D game textures often take a big part of memory and build size. But audio, video, fonts and other assets can be big too, so I check the Build Report.
- A 2048×2048 texture uncompressed is about 16 MB; compressed it is several times smaller.
- When to use what: the compressed format that modern phones support well gives a good balance of quality and size. I keep higher quality for sharp UI and small text, and stronger compression for soft shadows and gradients, then check the quality on the target phones. Stronger compression = less memory, worse quality.
- Max Size - I pick it from how big the asset really is on screen and how good it must look, not from the original PSD size.
- Mipmaps - usually off for UI and 2D shown at a fixed size (the mip chain adds about a third more memory); world sprites that zoom far out may still need them. Read/Write - off (it keeps a copy in memory).
- Sprites in an atlas: the atlas platform and texture settings decide the final packed texture. So I don't count on the source sprites' compression, and I check the final atlas.
- A thin line or halo at a sprite edge - atlas padding and Alpha Is Transparency.
- Find duplicates by content (hash), not by name: in my test 13 files were 6 unique pictures.
- Check pixels, not only logic: wrong filtering + compression blurred 59 of 90 UI sprites, while every test was green.
- In my test the atlases: 2048, compressed, no mipmaps, no rotation, no tight packing, padding 4.

PARTICLES AND VFX:
- What it is: Particle System (Shuriken) is Unity's main built-in particle system, and the usual starting point for a typical mobile 2D project. VFX Graph is made for particles simulated on the GPU, but how well it works in URP on mobile depends on the Unity and package version and on the phone.
- VFX Graph - very many particles on the graphics card; only if the Unity version, the renderer and the phones support what it needs, so I check the target phones first.
- Modules: Emission (how many), Shape (from where), Color/Size over Lifetime (how they change), Texture Sheet Animation (flipbook).
- Why: Effects give "juice", but they are the easiest way to kill the frame rate through overdraw.
- When to use what: Mobile 2D - Particle System. VFX Graph - only if the Unity version, the renderer and the phones support what it needs.
- Alpha blend - smoke and clouds that must cover the background. Additive - light, fire, sparks (only brightens, disappears on a light background).
- CPU or GPU: if the Profiler shows particle simulation is heavy, it is the processor (fewer particles, simpler modules); if the graphics card is the limit, I check overdraw, shader cost, texture size and blending (smaller particles, fewer layers, a smaller texture).
- Cheap: a few small systems, one shared unlit material, low Max Particles, and no unnecessary lights or collisions. Use a culling mode that pauses off-screen effects when they don't need to keep simulating.
- I measure the effect on the weakest phone together with the rest of the screen. The real limit comes from the effect and the target device.
- One-shot effects: Looping off, one Burst. Simulation Space depends on the effect: Local if it should follow its emitter (a sparkle on an item), World if it should stay where it was born (smoke, trails).
- Props that must read clearly (hammers) - animated sprites, not particles.

UI (Canvas, uGUI, TextMeshPro):
- What it is: Canvas - the root of the interface; inside are Image, Button, TextMeshPro.
- Canvas Scaler - scales UI to any screen (Scale With Screen Size, reference 1080x2400).
- Anchors - which edge an element is pinned to. Safe Area - the zone without the camera notch.
- TextMeshPro - text from an SDF atlas. It stays sharp at most sizes (very small or very large sizes can still show artifacts).
- Why: UI can take a big part of CPU time in a casual mobile game, especially when big Canvases, layouts or often-changing elements trigger rebuilds.
- The main trap - Canvas rebuilds: when a UI element changes, Unity can mark parts of the UI as changed (dirty) and redo the geometry, layout or batches on that Canvas. On a big Canvas with many elements this can get expensive.
- A ticking timer on a big Canvas keeps causing that rebuild work - I check the UI rebuild time in the Profiler.
- A common fix: static UI and often-changing UI on separate Canvases, so one change doesn't rebuild a large unrelated Canvas.
- What can split UI batches: different materials or textures, draw order, and Masks that use the stencil (Mask adds extra drawing work; RectMask2D is usually cheaper for a simple rectangle clip).
- When a layout changes (children added, removed or resized), Layout Group and Content Size Fitter calculate again; layouts inside layouts multiply the cost. For static layouts - anchors. For long lists - reuse the item views.
- The Graphic Raycaster checks every Graphic that has Raycast Target on, so I turn it off on decoration to cut extra raycast work.
- Safe Area: buttons inside, backgrounds full screen.
- TMP: Static font asset = a fixed set of letters baked in advance; Dynamic = letters are added when needed (useful when the text can have letters you did not plan for). Every Material Preset = a new material. No Auto Size on counters. Leave room for longer translated text.
- UI that reacts to game state: the game holds the data, the UI only shows it (listens to a "coins changed" event). An animation never decides logic. Change text only when the number changed.

2D WORKFLOW: SPRITES, IMPORT, SORTING:
- What it is: Sprite import: Sprite Mode (Single/Multiple), PPU (pixels per 1 unit), pivot, Mesh Type.
- 2D sorting (who is in front): Sorting Layer and Order in Layer come first, then the render queue and the distance to the camera. In normal 2D work I mostly control it with Sorting Layer, Order in Layer, Sorting Group and, when needed, Custom Axis sorting.
- Sorting Group - an object made of many sprites sorts as one.
- Why: Wrong import = blurry sprites or sprites of different sizes.
- Wrong sorting = items jump in front of each other, shadows end up on top.
- When to use what: One PPU for the whole art set, so sizes match.
- Pivot at the bottom for everything that stands on the ground.
- Sort by Y without a script: Renderer 2D Data -> Transparency Sort Mode = Custom Axis (0, 1, 0), Sprite Sort Point = Pivot. Lower on screen = in front.
- Mesh Type Tight - less transparent area (less overdraw), but a complex outline = many vertices.
- Custom Sorting Layers live in the Project Settings and do not travel with the Assets folder. So in the test I used one layer + Order in Layer ranges (sky -3100, island -2000, items -71..628, FX 1000, markers 2000, UI 3000).
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
- Unity 2D Animation uses bones and Sprite Skin for skeletal animation. You choose CPU or GPU deformation depending on what you need.
- Frame-by-frame has no bone cost, but each frame is a whole picture - memory adds up quick.
- For popups (my design choice, not a Unity rule): Show 0.25-0.6 s with a small scale pop, Hide 0.15-0.3 s. I fade the UI elements with their color alpha. CanvasGroup also works if I need to fade the whole popup at once.
- I avoid letting an Animator and a script write to the same transform at the same time. If both need to control it, I put one of them on a separate parent object.

ADDRESSABLES AND REMOTE CONTENT:
- What it is: Addressables loads assets by address when needed.
- I put assets into Addressables groups. Each group's packing setting decides how it becomes bundles: Pack Together = one bundle for the group, Pack Separately = one bundle per entry, Pack Together By Label = bundles by shared label sets.
- A bundle can live in the app (local) or on a server (remote).
- The catalog tells the game where everything lives.
- Why: Compatible new islands or events can come from a server without a new app update.
- It keeps the app smaller and lets optional stuff download later instead of on day one.
- Local = first screen, UI, fonts, shaders, first island - the game must work without internet.
- Remote: later islands, events, seasonal art.
- For shared assets like atlases or materials, I run Analyze to find duplicates between bundles. If something is duplicated, I fix the grouping or give it its own group.
- For content updates: I keep the content state file from the release. "Update a Previous Build" creates an update that minimizes what players download. With the right restrictions and packing, unchanged bundles stay the same, and only changed content gets new bundles. "Check for Content Update Restrictions" moves changes out of static groups.
- Mark groups "Cannot Change Post Release" to move changed assets into a new update group. Or "Can Change Post Release" so a changed asset rebuilds its bundle - the download cost depends on packing.
- I keep the handle of each load and release it when I don't need the content anymore. I unload event content when the event ends.
- Analyze - finds duplicates between groups.
- Watch out for: everything in Default Local Group, anything in Resources folder, remote groups with no remote paths, blocking loads, and forgetting to Release.
- My groups in the test: Local_Core, Shared_FX, Remote_Island_TeaHouse.

PROFILER AND FRAME DEBUGGER (often a live test):
- The Profiler shows frame time per thread. Main Thread handles logic, UI, particles. Render Thread prepares and submits rendering commands for the GPU.
- Frame Debugger steps through every draw call and shows the render state. I compare them to see why batching stopped.
- Memory Profiler - memory snapshots, comparing "before" and "after".
- In interviews, they show a Profiler screenshot and ask where the bottleneck is.
- I compare Main Thread and Render Thread timing against the frame budget. Then I find what takes the most time - UI rebuilds, particles, scripts or garbage collection - and look deeper into that part.
- When the CPU waits for the GPU, it might mean the GPU is slow, but it could be VSync too. I check the render work and VSync before I say the GPU is the bottleneck.
- The Editor is good for trying things, but its timings are not the same as on a phone - the Editor does extra work of its own, and a PC is faster. For final decisions I test a development build on real phones.
- I sort by Self time to find which function is actually slow.
- I take two Memory Profiler snapshots before and after to see what grew. Growth is not always a leak - it could be caching or lazy loading. I look for unexpected memory and follow the references to see why it's still there.
- When I optimize to X milliseconds, I pick CPU or GPU first, then the biggest marker. I change one thing at a time and say what I'm trading off.

PREFABS AND VARIANTS FOR LIVE EVENTS:
- A Prefab is a template. A Variant is like a child prefab - it only stores its differences.
- Nested prefab - a prefab inside another one. Override - a change on a copy (bold).
- ScriptableObject - a data asset (prices, rewards, event config).
- The job says: reuse content with variants so the project doesn't get out of hand.
- Hundreds of items: one base - one fix reaches all.
- Copies - every fix repeated hundreds of times.
- The right way: a base with stable structure, the same child names, and one shared Animator.
- Variants change only looks and data - sprite, color, text, effect reference.
- Don't chain variants deeper than base + one level. Put event config in a ScriptableObject or a table, not in the prefab.
- My tool checks for forbidden overrides and checks that required children are there.
- In the test: base BuildableItem_Base (ObjectVisual, ShadowVisual, anchors, three states), seven direct variants.
- I'm careful with "Apply All" from a variant. If I apply an override to the base, it can change other variants that inherit from it.
- Animation bindings use the Transform path, so renaming or moving a child can break them. It might not be obvious, so after I change the hierarchy I check the clips.

ART PIPELINE AND TOOLS (asked especially of a Senior):
- Art goes from sources like Photoshop, through import, checks, atlases, and into Addressables.
- I would build this path and the tools so artists don't have to manage these settings by hand.
- In senior interviews they ask: design a pipeline and what tools did you build.
- The job post lists editor tools as a bonus.
- I would use import rules per folder with AssetPostprocessor or Presets. Drop something into UI/ and the settings are already right.
- I validate texture size, compression, names, budgets, and required prefab parts.
- Before content goes into the build, there's an automatic check and a review.
- There's a rules document saying who approves new shaders, effects, and UI patterns.
- A good tool has Undo, shows clear errors instead of silent defaults, and shows a preview before applying.
- I build a tool when a task happens over and over and people mess it up. One-time work, I do by hand.
- A tool survives if it's simple, has a short guide, and I watch the first person use it.

MEMORY AND ASSET BUDGETS:
- Build size is what players download. Memory is what's loaded right now. Loading is how long it takes. They're linked but separate.
- A budget - a limit per screen or device tier: MB of textures, draw calls, particles, ms per frame.
- Why: If memory gets too high on a weak phone, the app can run out of memory or be killed by the system.
- A senior is asked "how do you set budgets".
- I don't use one number for all textures. I define budgets per device tier and test on real phones.
- Draw calls: I set the budget from the weakest target device. For frame time, I might aim lower than 33.3/16.6 ms to leave room for spikes and heat throttling. The exact number depends on the project and device.
- Memory grows when a screen opens. Maybe something didn't unload - Addressables without Release, objects, subscriptions. Or it's a cache or lazy loading. I snapshot and follow the references before I call it a leak.
- Destroy removes the object, but the asset can stay loaded if something else still references it. With Addressables I release the handle, and Unity can unload the bundle once nothing needs it. Unloading unused assets is a separate step and heavy on the CPU.
- If the build is too big, I check the Build Report and start with the biggest things. Assets in Resources always ship, so that's not where optional content goes.

QUALITY TIERS AND DEVICES:
- I split thousands of different phones into tiers: low, mid, high.
- Each tier has its own settings.
- I pick a tier from a device list and rules. RAM is one input - these are just examples, my thresholds depend on the project. GPU, CPU, OS features, and QA data all matter.
- On first launch the game reads the device info and picks a tier.
- I also use data from live players and QA tests.
- Each tier changes texture size (HD or SD), particle count, post-processing (low is off), a lower render scale on low if profiling shows GPU or fill-rate pressure, and frame rate (low is 30 fps, high is 60).
- In Unity, I use Quality Settings for tiers, a separate URP asset per tier, Addressables variants for HD and SD, and a startup script that sets the quality level.
- I test the weakest phones first because memory, heat, and driver issues show up there. If it's stable on the weakest one, that's a safer baseline. But I still test the other tiers because GPUs, drivers, and OS versions are different.

BUILD AND PLAYER SETTINGS:
- For mobile, the C# code is usually built into native machine code ahead of time (iOS needs it). It changes runtime and build behaviour, but I don't assume it makes every piece of code faster; the build takes longer and the app might be bigger.
- Stripping removes unused code and engine modules so the build is smaller.
- Player Settings for mobile: I pick the right texture compression for the target phones, graphics APIs like Vulkan, Metal, or GLES depending on devices, ARM64 according to the platform and store requirements, and the package format Google Play needs.
- That's why it matters: these settings can strongly affect build size and how the game behaves on the device, but I measure the actual problem first instead of assuming the cause.
- Stripping can break code that is called only by name. If it does, I mark that code so it is kept.
- Shader variants: I check Graphics settings and the Editor log for the count. I turn off URP features that create too many variants. A missing variant can turn objects pink in the build even if the editor looks fine.
- When I upgrade Unity on a live project, I do it as a separate step and read the changes in URP, Addressables, 2D, and Shader Graph. I build and test on key phones. Shaders, URP assets, atlases, and Addressables are the usual trouble spots, so I compare against a build of the old version.

2D CAMERA:
- What it is: An orthographic camera (no perspective).
- Orthographic Size - half the height of the visible area in units.
- I pick the size so the content fits the narrowest phone. Wider screens just show more.
- Pixel Perfect Camera - only for pixel art. Not needed for smooth 2D.

BEHAVIOURAL QUESTIONS (STAR):
- What it is: Playtika asks about ownership, conflicts, deadlines, failures.
- Answer with STAR: Situation -> Task -> Action (what I did) -> Result (with a number).
- Keep Situation + Task short. Spend most of the answer on what I did and finish with the result.
- Watch out: too much setup, saying "we" instead of "I", no number in the result, vague actions like "optimized shaders", and forgetting to explain what changed going forward.
- Art versus performance: show how I translate the artist's idea into limits and decide with numbers.
- A tool that saved time: show you found the problem, measured it, made the tool safe, and counted how much time you saved.
- A bug on a phone before release: show how you test on real hardware, find the cause, and fix it.
- A deadline when you had to cut scope: show how you prioritized by impact, spoke up early and honestly, and kept what mattered.
- A failure: admit it, fix it, change the process so it doesn't happen again.
- For a failure: admit it without blame, say what you did to fix it, explain what process change you made (a validator, a checklist), and give a number showing it got better.
- Ask them: How do you balance art ambition and budgets on weak devices? Got an example of a hard trade-off?
- What's your content pipeline for live events and where does it bottleneck for artists?
- How do you measure Tech Art's impact? FPS, time saved, fewer bugs?
- What device tiers do you test and what's your test plan?
- What's one Tech Art problem on your project you'd want someone to fix in the next 6 to 12 months?

QUESTIONS ABOUT MY HOME ASSIGNMENT (they discuss it in the interview):
- They'll ask: why you did it this way, what else you considered, how it scales to events, how you tested it, what you'd improve, how you'd make it data-driven for designers.
- What I did (short): The island from sprites under an orthographic camera; bar and navigation - a Canvas with Canvas Scaler 1080x2400 and Safe Area.
- Base BuildableItem_Base with three states + seven direct variants.
- Animator goes Available -> trigger Build -> one BuildSequence clip -> Built. The item pops at 1.1 s (0.85 -> 1.06 -> 1.0), everything is done by ~1.4 s, and the next action is ready in under 2 s.
- One particle for clouds with a 4x4 flipbook and alpha blend. Hammers are sprites with their pivot near the handle.
- Atlases UI_Core and Island (items together with their shadows). Addressables: Local_Core, Shared_FX, Remote_Island_TeaHouse.

HOW I WORK (job post: mockup -> feature, ownership, communication):
- I break the mockup down into states, data and interactions, and first ask what's missing. Then I prototype, build the base prefab and Canvas, add animation and FX, connect it to game logic, and check performance and memory before moving to variants and Addressables.


SCENE COMPONENTS (every Unity component in my scene, field by field - what it is and what it changes):
- This is my Inspector-style lookup for the Unity component types I used, one entry per component type.
- Only Unity's own components and project assets are here, not our scripts.

COMPONENT: TRANSFORM:
- Position - where the object is, relative to its parent. I keep children at zero when I can, so moving the parent moves the whole group.
- Rotation - how the object is turned. Unity keeps it as a quaternion and shows it as angles. In 2D I rotate only on Z; turning a sprite on X or Y makes it flat and can break sorting.
- Scale - how big the object is. It multiplies down to all children. I keep art at 1 and scale the parent; a negative scale flips the sprite, but also flips colliders and particle directions.
- Constrain Proportions - an Editor lock that scales X, Y and Z together. It only changes how I edit in the Inspector, not the game.

COMPONENT: RECT TRANSFORM (every UI object):
- Anchor Min / Max - where the element is pinned inside its parent. If min and max are the same, the size is fixed. If they are different, the element stretches with the parent - that's how UI fits different phone shapes.
- Anchored Position - how far the pivot is from the anchor. This is what I animate to move UI, so the motion works on any resolution.
- Size Delta - the size of the element compared to its anchors. With stretched anchors it is the difference, so a negative number is normal.
- Pivot - the point the element turns and scales around. A top-right element uses a top-right pivot so it grows inward; a button that pops uses the center.
- A Screen Space - Camera canvas sits in world space in front of the camera, so its Rect Transform scale is small - that is normal.

COMPONENT: CAMERA:
- Projection - Orthographic or Perspective. Orthographic has no perspective, it is the normal choice for 2D. Perspective is for 3D or a parallax depth look.
- Orthographic Size - half of the height the camera sees, in world units. Bigger size = more of the world fits, everything looks smaller. I set it so the main content fits the narrowest phone; wider phones just see more on the sides.
- Clear Flags / Background - what the camera draws before the scene each frame. Solid Color clears the screen with one color; Skybox is mainly for 3D.
- Culling Mask - which layers this camera draws. With one camera I draw everything; with a separate UI camera I split the layers.
- Near / Far Clip - the depth range the camera draws. In a 2D setup I mainly make sure objects stay inside that range.
- Depth - the draw order between cameras in the old pipeline. In URP camera stacking (Base/Overlay) does this instead.
- Rendering Path - uses the pipeline setting by default. I don't change it per camera.
- HDR / MSAA / Dynamic Resolution - the camera allows them, but the URP asset decides if they really run. Dynamic Resolution can lower the render size to reduce GPU load when the project enables and controls it; a simple 2D scene usually doesn't need it.
- Occlusion Culling - skips objects hidden behind other objects. It needs baked occlusion data; in 2D there usually is none, so it does nothing.
- Target Texture - empty means the camera draws to the screen. A Render Texture is for minimaps or UI previews.
- Physical Camera fields (Iso, Aperture, Focal Length...) - only for a real-camera look in 3D; not used for an orthographic 2D camera.

COMPONENT: UNIVERSAL ADDITIONAL CAMERA DATA (the URP part of the camera):
- Render Type - Base is a normal camera; Overlay cameras draw on top of a Base camera. Every extra camera costs more, so I try to use one.
- Renderer - which renderer from the URP asset this camera uses; by default the first one (for us the 2D Renderer).
- Post Processing - turns Volume effects (Bloom, color grading) on for this camera. Effects can add extra passes and bandwidth cost, so on phones I keep it off unless the art needs it.
- Anti-aliasing - smooths jagged edges with a full-screen pass (FXAA/SMAA). Sprites already have soft edges, so I usually don't need it.
- Render Shadows / Depth Texture / Opaque Texture - 3D shadows and extra rendering data: depth values or a copy of the opaque colour. They cost memory and bandwidth, so I turn them on only if an effect uses them.
- Stop NaN / Dithering - fixes for broken HDR pixels and for color banding. I turn Dithering on only if a gradient shows bands on the phone.
- Volume Mask / Volume Trigger - which Volumes affect this camera. Only matters when post-processing is on.

COMPONENT: AUDIO LISTENER:
- The "ears" of the scene. Normally I keep one active AudioListener in the scene; several active listeners can cause a warning. It has no settings; I keep it on the main camera.

COMPONENT: CANVAS:
- Render Mode - Screen Space - Overlay renders UI directly in screen space without a camera. Screen Space - Camera draws UI through a camera, so it can sort together with sprites and particles. World Space puts UI in the game world, like a sign on a building.
- Render Camera - the camera used by a Screen Space - Camera Canvas. I set it explicitly for Camera mode.
- Plane Distance - where a Screen Space - Camera Canvas is placed in front of its render camera.
- Sorting Layer / Order in Layer - where the whole Canvas draws compared to sprites. Low for a background, high for the HUD. This works against sprites and particles only for Screen Space - Camera or World Space; a Screen Space - Overlay Canvas is drawn on top of the whole scene.
- Override Sorting - lets a nested Canvas use its own order instead of its parent's. I use it when one panel must draw in a different place.
- Pixel Perfect - snaps UI to whole pixels. For smooth, animated UI I keep it off; I turn it on only if the art style really needs it.
- Additional Shader Channels - extra vertex data that custom UI shaders may need. Each channel makes UI meshes bigger, so I add only what a shader reads.
- Vertex Color Always In Gamma Space - a compatibility option for UI shaders in a Linear project that expect vertex colors in gamma space. Off for TMP and URP UI shaders; with a custom UI shader I check which color space it expects.
- Receives Events - lets the Canvas get taps through its Graphic Raycaster.

COMPONENT: CANVAS SCALER:
- UI Scale Mode - how UI scales. Scale With Screen Size scales from a reference resolution and is the normal mobile choice. Constant Pixel Size keeps pixel sizes, so UI looks very different on different screens.
- Reference Resolution - the screen size the UI is designed for. The artist's mockup uses the same size.
- Screen Match Mode / Match - what the UI follows when the screen shape is different: width (0), height (1) or a mix. For a portrait game I usually start by matching the dominant dimension, then test different aspect ratios and tune the value for the project.
- Reference Pixels Per Unit - how sprite pixels turn into UI units. I keep it the same as the project's sprite scale, so UI sprites have the size I expect.

COMPONENT: GRAPHIC RAYCASTER:
- Finds which UI element is under a tap. It raycasts against the Graphics on its Canvas that have Raycast Target on, so I turn Raycast Target off on decoration.
- Ignore Reversed Graphics - ignores UI that faces away from the camera, like a flipped card. On is normal.
- Blocking Objects / Blocking Mask - whether 2D or 3D colliders in front can block UI taps. None when the world never covers the UI.

COMPONENT: CANVAS RENDERER (added with every UI Graphic):
- Cull Transparent Mesh - can skip rendering a Graphic when its vertex color alpha is zero. It doesn't look at the texture's individual pixels.

COMPONENT: CANVAS GROUP:
- Alpha - multiplies the alpha of every child. One value fades a whole popup.
- Interactable - when off, all buttons inside stop working. I turn it off while a popup animates out.
- Blocks Raycasts - when off, taps go through. A hidden popup must have it off, so it doesn't catch taps.
- Ignore Parent Groups - a child group ignores its parents' fade and lock. For something that must stay visible under a faded parent.

COMPONENT: IMAGE:
- Source Image - the sprite to draw. Images from the same atlas with the same material, drawn next to each other, can batch.
- Color - multiplied with the sprite. It is vertex color, so changing it is cheap and doesn't break batching.
- Material - empty means the default UI material. A custom material splits the batch, so I use one only where an effect needs it.
- Raycast Target - can this Image catch taps. Only buttons and blocking panels need it; on decoration it is extra work.
- Raycast Padding - makes the tap area bigger or smaller without changing the art. Good for small icons.
- Maskable - lets a Mask or RectMask2D clip this Image.
- Image Type - Simple draws the sprite as is. Sliced keeps the corners sharp and stretches the middle (panels, buttons). Tiled repeats the middle. Filled is for progress bars and round timers.
- Fill Center - for Sliced, whether the middle is drawn. Off gives just a frame and draws fewer pixels.
- Preserve Aspect - keeps the sprite's proportions inside its rect. I turn it on for icons that change size.
- Use Sprite Mesh - uses the sprite's tight shape instead of a square. Less empty area (less overdraw) on big odd-shaped art, but more vertices.
- Pixels Per Unit Multiplier - changes how the sprite's pixels map to UI units. For Sliced sprites I check it when the border thickness doesn't match the intended scale.

COMPONENT: TEXTMESHPRO - TEXT (UI):
- Font Asset - an SDF font atlas, so text stays sharp at many sizes from one texture. Using the same font asset and material where possible helps keep UI batching simpler.
- Material Preset - a material with outline or shadow settings. Every different preset is a different material and splits batches, so I keep only a few.
- Font Size / Auto Size - Auto Size tries sizes until the text fits. I avoid it when the text has a known size, because I don't need the extra fitting work; I use it when the text length can vary, like translations.
- Vertex Color / Color Gradient - text color without changing the material, so it doesn't break batches.
- Alignment - where the text sits in its box. Centering alone doesn't stop a counter from moving when its width changes, so for counters I give the text a fixed area and a font with stable digit widths, so 99 to 100 doesn't make the layout jump.
- Wrapping / Overflow - what happens when text is too long. Counters never wrap; long text wraps and uses Ellipsis or Truncate.
- Character / Word / Line / Paragraph Spacing - extra space between letters, words and lines. I change it only for the look.
- Rich Text - allows tags like <color> and other formatting. I turn it off when the text doesn't need markup, especially for simple counters.
- Raycast Target - text should not catch taps; the button under it does.
- Extra Padding - extra space in the text mesh for big outlines or shadows. On when a thick outline gets cut.
- Kerning - special spacing between specific letter pairs. It doesn't make digits equal width - for counters I want a font setup where digits have the same width.
- Parse Escape Characters - turns \n into a new line.
- Margins - inner padding of the text box.

COMPONENT: BUTTON:
- Interactable - when off, the button ignores taps and shows its Disabled look.
- Transition - how the button reacts to taps: Color Tint changes the color, Sprite Swap changes the sprite, Animation plays Animator states, None does nothing. I use None when my own clip animates the press, so two systems don't fight.
- Target Graphic - the Image the transition changes.
- Normal / Highlighted / Pressed / Selected / Disabled Color - the tint for each state. Highlighted is only for a mouse; on touch players see Pressed and Disabled.
- Color Multiplier / Fade Duration - how strong and how fast the tint changes.
- Navigation - moving between buttons with a gamepad or keyboard. Not needed for a touch-only game, so I set it to None when the project doesn't need keyboard or gamepad navigation.
- On Click - what runs when the button is tapped, set in the Inspector. The logic stays in code; the event just calls it.

COMPONENT: RECT MASK 2D:
- Cuts children to its rectangle without the stencil buffer. Cheaper than Mask, and it skips children that are fully cut, so I use it for scroll lists.
- Padding - makes the clipping area smaller or bigger.
- Softness - a soft fade at the edges. Nice for list edges; I keep it at zero when a hard edge is fine.

COMPONENT: HORIZONTAL LAYOUT GROUP (Vertical works the same way):
- Spacing / Padding - the gap between children and the space inside the edges.
- Child Alignment - where the children sit when they don't fill the group.
- Control Child Size - when on, the group also sets the children's size. Off means it only places them and each child keeps its own size - this avoids fights with Content Size Fitters.
- Child Force Expand - when on, extra space is shared between children. Off keeps them tight.
- Use Child Scale - when on, the child's scale counts in the layout. I keep it off, so a "punch" scale animation doesn't push the neighbours.
- Reverse Arrangement - right-to-left order without changing the hierarchy.
- A Layout Group recalculates when a child changes or appears. For UI that never changes, anchors can replace it.

COMPONENT: GRID LAYOUT GROUP:
- Cell Size / Spacing - every child gets the same cell size and the same gap. The Grid Layout Group controls the child sizes through its Cell Size.
- Constraint - Fixed Column Count or Fixed Row Count keeps the same number of columns or rows on any screen; Flexible does not fix the number of rows or columns; Unity tries to keep the grid roughly square when both dimensions are flexible.
- Start Corner / Start Axis / Child Alignment - where filling starts, in which direction, and where the whole block sits.

COMPONENT: CONTENT SIZE FITTER:
- Horizontal / Vertical Fit - Preferred Size makes the object grow with its content, like a list that gets taller with more items, so a ScrollRect knows how far to scroll. Unconstrained leaves that axis alone.
- It must not sit on an object whose parent layout already controls its size, or they fight and Unity warns.

COMPONENT: SCROLL RECT:
- Content / Viewport - the part that moves and the window that cuts it.
- Horizontal / Vertical - which directions can scroll.
- Movement Type - Clamped stops at the edges, Elastic bounces back (Elasticity is how strong), Unrestricted has no limits.
- Inertia / Deceleration Rate - the list keeps sliding after a flick and slows down; a lower rate stops it sooner.
- Scroll Sensitivity - speed for the mouse wheel and trackpad; finger drag ignores it.
- Scrollbars - optional; usually none on mobile.
- A normal ScrollRect keeps all active item objects in the content, so long lists can get expensive. For long lists I reuse item views (pooling).

COMPONENT: EVENT SYSTEM:
- Sends input to the UI; I normally keep one active EventSystem per scene.
- First Selected - which button is selected at start for a gamepad; empty on mobile.
- Send Navigation Events - lets gamepad and keyboard move between buttons.
- Drag Threshold - how far the pointer must move before Unity treats the gesture as a drag instead of a tap. I raise it if scroll lists eat taps.

COMPONENT: INPUT SYSTEM UI INPUT MODULE:
- Connects the new Input System to the UI (instead of the old StandaloneInputModule).
- Pointer Behavior - how mouse and touch pointers are represented. For multi-touch I make sure it matches how the UI should handle several fingers.
- Deselect On Background Click - tapping empty space clears the selected button.
- Move Repeat Delay / Rate - repeat speed for gamepad and keyboard; not used on touch.
- Scroll Delta Per Tick - how far one mouse wheel step scrolls.

COMPONENT: SPRITE RENDERER:
- Sprite - the picture to draw. Sprites from the same atlas with the same material can batch.
- Color - multiplied with the sprite. It is vertex color, so tint and fade are cheap and don't break batching; changing the material color would.
- Flip X / Y - mirrors the sprite without a negative scale, so children and colliders are not mirrored.
- Draw Mode - Simple draws the sprite as is and is the simplest; Sliced and Tiled stretch or repeat it using its borders (9-slice for world sprites).
- Size - only used by Sliced and Tiled; it is the drawn size in world units.
- Sorting Layer / Order in Layer - who is in front. The layer goes first, then the order inside the layer.
- Sprite Sort Point - Center or Pivot: the point used for distance and Y sorting. Pivot at the feet makes Y-sorting look right for things standing on the ground.
- Material - Sprite-Lit reacts to 2D lighting; Sprite-Unlit doesn't use 2D lighting, so it is a good choice when the sprite doesn't need lighting (I still check the actual cost on the target setup); custom materials add effects like shine or water. Every different material splits a batch, so I share one material per effect.
- Mask Interaction - shows the sprite only inside or outside a Sprite Mask, using the stencil. None means no mask and no extra cost.
- Shadows, Probes, Lightmap, Motion Vectors, Ray Tracing - 3D settings that every Renderer has. They do nothing for sprites in the 2D Renderer; I leave them.
- Rendering Layer Mask - used by URP features that filter renderers by rendering layer. In this 2D setup I left it at default.

COMPONENT: SORTING GROUP:
- Makes all sprites under it sort as one object against the rest of the scene, but keeps their order inside. Without it, parts of one item can slide between parts of another.
- Sorting Layer / Order in Layer - the order of the whole group.
- Sort At Root - a nested group sorts as if it were at the top level, not inside its parent group. For example, a marker that belongs to an item but needs to take part in sorting at the top level.

COMPONENT: ANIMATOR:
- Controller - the state machine asset. Many objects can share one controller.
- Avatar - only for humanoid or 3D rigs; UI and sprites animate by object path and don't need it.
- Apply Root Motion - moves the object from the clip's root movement. Off for UI and sprites; the clip just changes local values.
- Update Mode - Normal follows game time (pauses with timeScale 0). Unscaled Time keeps playing when the game is paused (pause menus). Animate Physics runs with physics.
- Culling Mode - what happens when the object is not visible. Always Animate keeps updating; Cull Update Transforms or Cull Completely save CPU for world objects off-screen. For UI I usually keep Animator culling simple and don't rely on renderer-based culling for important UI animation.
- Keep Animator State On Disable - off means an object that is turned off and on again starts from the default state. That's what I want for popups that replay Show.
- Write Default Values On Disable - whether animated values go back to their defaults when the Animator is turned off.

COMPONENT: MESH FILTER (not in my scene, here so the set is complete):
- Mesh - which 3D shape to draw. MeshFilter only says WHICH mesh; it has no drawing settings.
- Meshes that never move can be joined by static batching or drawn with GPU Instancing; a SpriteRenderer makes its own small mesh instead.

COMPONENT: MESH RENDERER (not in my scene, here so the set is complete):
- Draws the MeshFilter's mesh with its Materials list (one material per sub-mesh).
- Shadows, Light Probes, Reflection Probes, Lightmap - 3D lighting options; for flat 2D-style meshes I turn shadows off.
- Sorting Layer / Order in Layer exist on every Renderer, so a mesh can sort together with sprites.

COMPONENT: SKINNED MESH RENDERER (3D characters with bones):
- Mesh / Root Bone - the mesh that bends with bones, and the bone its bounds follow.
- Quality - how many bones can influence one vertex. Lower counts can reduce deformation cost, but I choose the setting based on the character and target devices.
- Update When Offscreen - when off, Unity skips bending the mesh while it is off-screen. On only if the animation moves the mesh far outside its box.
- Bounds - the box used to decide if the character is visible. If it is too small, the character disappears at the screen edge.
- Cast / Receive Shadows - 3D shadow work. In a 2D Renderer there are no shadow maps; I turn them off to be safe.
- Skinned Motion Vectors - only for motion blur or TAA; off if you don't use them.

COMPONENT: AUDIO SOURCE:
- Audio Resource - the sound clip. Play On Awake starts it with the scene; Loop repeats it.
- Volume / Pitch - how loud and how high the sound is.
- Spatial Blend - 0 is 2D sound (same in both ears, right for music and UI), 1 is 3D sound that gets quieter with distance (Min/Max Distance and Rolloff).
- Priority - when too many sounds play, the lower number wins. I give important music a low number (0 is the highest priority), so it is less likely to be cut when too many sounds play.
- Output - an Audio Mixer group. With a mixer the settings can control music and sound effects separately.
- Doppler, Spread, Reverb, Bypass Effects - 3D and effect settings; not used for 2D sound.

COMPONENT: PARTICLE SYSTEM - MAIN MODULE:
- Duration - the length of the emission cycle. For looping effects it repeats; for one-shots emission stops after the duration, but particles already born can live longer.
- Looping - repeats forever (ambience) or plays once (one-shot effects that can go back to a pool).
- Prewarm - a looping effect starts as if it already ran one cycle, so it looks full from the first frame.
- Start Delay - wait before emitting; good to stagger parts of one effect without code.
- Start Lifetime - how long each particle lives. Long life with a low rate means few particles on screen; lifetime drives the count as much as the rate.
- Start Speed - the starting speed along the shape direction.
- Start Size - the size of each particle. Large transparent particles can get expensive, because they cover more pixels and increase overdraw.
- Start Rotation - the starting angle; a random angle stops copies from looking cloned.
- Start Color - the starting color; random between two colors gives variety without new textures.
- Gravity Modifier - how much gravity pulls the particles.
- Simulation Space - Local: particles move with the object (a sparkle on a moving item). World: particles stay where they were born (smoke, trails).
- Simulation Speed - speeds up or slows down the whole effect without touching every curve.
- Scaling Mode - Hierarchy uses the parent's scale too, so a scaled prefab scales its effect.
- Play On Awake - starts when the object turns on. For pooled one-shots I still start it myself.
- Max Particles - a hard limit; no more particles are made. A cheap safety net for weak phones.
- Auto Random Seed - a different pattern every play. Off with a fixed seed makes it repeat the same way, good for tests.
- Stop Action - what happens when the system finishes: Disable, Destroy, or Callback (tells my pool code it finished, so it can take it back).
- Culling Mode - controls what happens when the system is outside the camera view. For effects that don't need to keep simulating, I can use Pause; for effects whose state should catch up when visible again, I use Pause And Catch-up.
- Ring Buffer Mode - keeps old particles alive until Max Particles is reached, then replaces the oldest; for footprints or marks.
- Emitter Velocity Mode - how the emitter's own speed is measured (Transform or Rigidbody); only matters when the emitter moves.

COMPONENT: PARTICLE SYSTEM - MODULES I USED:
- Emission - how many particles: Rate over Time for steady effects, Bursts for one-shots (all at once), Rate over Distance only while the emitter moves.
- Shape - where particles appear and which way they go: Box, Cone (fountains, sprays), Sphere/Circle (bursts). Randomize Direction adds spread.
- Color over Lifetime - changes color and alpha during life; I fade alpha in and out so particles don't pop.
- Size over Lifetime - changes size during life: grow for smoke, shrink for dying sparks.
- Rotation over Lifetime - spin speed during life (the Inspector shows degrees per second); it is a speed, not an angle.
- Texture Sheet Animation - plays a flipbook from one texture split into a grid. Cycles = how many times it plays in one life; Single Row picks one row per particle for variety; Sprites mode uses separate sprites.
- Velocity over Lifetime - adds movement during life, like a steady wind drift. Orbital and Radial make particles swirl around the center.
- Noise - adds a natural wobble. More octaves and higher quality cost more CPU per particle, so on mobile I keep it simple.
- Limit Velocity over Lifetime - slows particles down: they shoot out fast, then slow instead of flying away. Drag does the same based on size and speed.
- Sub Emitters - starts another system on a particle event (birth, collision, death): a rocket bursts into sparks where it dies, and Inherit Color keeps the color.
- Trails - ribbons behind particles. They add geometry and overdraw, so I keep them short and few.

COMPONENT: PARTICLE SYSTEM - MODULES I DIDN'T USE (one line each):
- Inherit Velocity - particles get the emitter's speed; for effects on fast-moving objects.
- Lifetime by Emitter Speed - life time depends on how fast the emitter moves.
- Force over Lifetime - a steady push like wind; Velocity over Lifetime can do a similar drift.
- Color by Speed / Size by Speed / Rotation by Speed - change particles by their speed, like sparks glowing while fast.
- External Forces - reacts to Wind Zones and Particle System Force Fields.
- Collision - particles hit colliders or planes; costs CPU per particle, so on mobile I avoid it or use Planes mode.
- Triggers - events when particles go in or out of colliders.
- Lights - real lights on particles; very expensive on mobile, so I fake glow with additive sprites.
- Custom Data - extra values per particle for custom shaders.

COMPONENT: PARTICLE SYSTEM RENDERER:
- Render Mode - Billboard: flat quads that face the camera (right for 2D). Stretched Billboard for sparks and rain. Mesh for 3D pieces.
- Material - an unlit particle material is cheap; one shared material per effect type batches better.
- Sort Mode - the order inside one system. Sorting by distance or age costs time; None avoids extra sorting when the particle order doesn't matter.
- Sorting Layer / Order in Layer - where the whole effect draws among sprites and Camera-mode UI.
- Min / Max Particle Size - limits particle size as a part of the screen, so one particle can't fill the screen near the camera.
- Render Alignment - View: particles face the camera. Local/World keep a fixed direction; Facing turns them to the camera position.
- Enable GPU Instancing - mostly for Mesh mode; for Billboard particles I don't count on it for speed.
- Shadows / Probes - 3D lighting; not used for 2D particles.
- Custom Vertex Streams - sends extra data to the shader (like flipbook blend); only when the shader uses it.

ASSETS: ADDRESSABLES SETTINGS:
- Profile - a set of build and load paths. I keep separate profiles for local testing, staging and the real server.
- Local Build / Load Path - local bundles are built into the app and load from the phone.
- Remote Build / Load Path - remote bundles are built to a folder that I upload; the load path is the server (CDN) address. A localhost address is only for testing and must change before release.
- Build Remote Catalog - also builds the catalog (address -> bundle list) for the server, so an already released app can find compatible remote content and updated bundles without a new app build.
- Check For Catalog Updates On Init - at start the game asks the server for a newer catalog. Off if I want to control updates myself.
- Unique Bundle IDs - helps when new bundles must load while old ones may still be loaded. I set it by the project's content-update strategy, not as a universal on/off rule.
- Contiguous Bundles - how assets are placed inside a bundle; I keep the project setting unless profiling shows a reason.
- Non-Recursive Dependency Calculation - an option for how the build finds dependencies; I keep the default unless the team has a reason.
- Max Concurrent Web Requests - how many downloads run at the same time. A higher value can improve throughput on some networks, but it adds concurrent work and competes with other requests, so I tune it from testing.
- Catalog Download Timeout - how long to wait for the catalog. On mobile I set one, so a bad network quickly shows a retry screen.

ASSETS: ADDRESSABLES GROUPS:
- In my assignment, a local group - content the game always needs: the UI atlas, shared effect materials and textures, shared shaders. It loads from the app, uses fast-loading compression and is Cannot Change Post Release - it ships with the app and doesn't change after release.
- In my assignment, one remote group per island - the island prefab, its item data and its atlas. It loads from the server, uses stronger compression for smaller downloads and is Can Change Post Release - each island downloads only when needed and can be updated on its own. Can Change / Cannot Change is a content-update strategy choice, not one right setting.
- Bundle Mode - Pack Together: one bundle per group. Pack Separately: one bundle per entry - it can reduce how much content is directly affected when one entry changes, but there are more bundles and more dependency and network overhead. Pack Together By Label: bundles by shared label sets.
- Compression - the fast option loads quickly with little CPU; the strong option makes downloads smaller, and Unity converts it to the fast one in the cache on the phone. I pick by what matters more: download size or loading speed.
- Include In Build - the group is part of the Addressables build (for remote groups that means built for the server, not put inside the app).
- Use Asset Bundle Cache - keeps downloaded bundles on the phone, so the next launch doesn't download again.
- Use Asset Bundle CRC - adds an integrity check when bundles load. It costs some CPU, so I use it where the extra check is worth it, like downloads.
- Bundle Naming - Append Hash changes the file name when the content changes, which helps avoid old bundles coming from the CDN or cache.
- Internal Asset Naming - how assets are named inside bundles. I keep the project's chosen naming mode and don't change it casually, because it affects the content build.
- Retry Count / Timeout - how many times to retry a failed download and how long to wait. I choose them by network conditions and how important the content is, so a short drop can recover without leaving the player waiting too long.
- Labels - tags on entries, so code can load a whole set at once, like every item of one island.

ASSETS: SPRITE ATLASES (Sprite Atlas V2):
- One atlas for the UI that is on screen together, so the HUD batches; one atlas per island, with items and their shadows together, living in that island's remote group.
- Include in Build - whether the atlas is part of the build. If it is off, I need another delivery path, such as Addressables or late binding.
- Allow Rotation / Tight Packing - Allow Rotation can turn sprites inside the atlas to pack them better; I may keep it off for UI if a predictable atlas layout makes debugging or tools easier. Tight Packing uses the sprite outline to save atlas space; whether the sprite uses a tight mesh is a separate setting. I turn them on only when the assets and setup support it.
- Padding - empty pixels between sprites, so filtering and compression don't bleed neighbours into each other.
- Alpha Dilation - fills empty padding with edge colors to hide bleeding; useful for soft edges with mipmaps.
- Read/Write - keeps an extra copy of the texture for the CPU. Off unless code reads pixels.
- Generate Mip Maps - smaller copies for far zoom; they add about a third more memory. Off for UI and fixed-size 2D.
- sRGB - on for color textures in a Linear project.
- Filter Mode - Bilinear is smooth; Point is for pixel art; Trilinear only makes sense with mipmaps.
- Platform override (Max Size, Format) - the atlas settings decide the final texture memory, not the source sprites. Stronger compression trades quality for memory (higher quality for sharp UI text, stronger compression for soft shadows - then I check on the phone).

ASSETS: TEXTURE IMPORT (sprites):
- Texture Type - Sprite for 2D and UI; Default for 3D textures.
- Sprite Mode - Single for one picture, Multiple for a sheet cut in the Sprite Editor. Changing Multiple to Single changes the sprite IDs that prefabs point to.
- Pixels Per Unit - how many pixels make one world unit. One value per art set keeps sizes matching.
- Mesh Type - Full Rect is a simple square. Tight follows the picture outline and cuts overdraw, but adds vertices.
- Alpha Is Transparency - helps Unity treat transparent edges correctly and can reduce coloured halos around sprites.
- Generate Mip Maps / Read/Write - off for fixed-size 2D with no pixel reading from code.
- Wrap Mode - Clamp stops edge pixels from repeating at the borders (sprites); Repeat is for tiling textures.
- Filter Mode - Bilinear for smooth art, Point for pixel art.
- Max Size - the largest size the texture is imported at. I match it to the size on screen; it is often one of the biggest ways to save texture memory.
- Compression / platform format - the compression strength per art type: soft art can take stronger compression. Sprites packed in an atlas get the atlas format instead.
- Non-Power-of-2 - None keeps the original size, which is usual for sprites; scaling to a power of 2 only when the target format or platform needs it.

ASSETS: MATERIALS AND SHADERS:
- Particles/Unlit - transparent, no lighting, cheap. Additive blend for light and sparks, Alpha blend for smoke and confetti.
- Sprite-Lit-Default - sprites react to 2D lighting. Sprite-Unlit-Default fits when sprites don't need 2D lighting, and I check the actual cost on the target setup.
- Custom Shader Graph sprite shaders (shine, water, wind, glow, lava, twinkle) - give items life without moving transforms. I share materials where possible, and I make sure the shader stays compatible with the SRP Batcher.
- A custom UI shader (like a liquid fill orb) - driven by a material property; it can split the UI batch around that element.
- TextMeshPro/Mobile/Distance Field - a TMP shader intended for mobile, with fewer features than the full shader; I use the features the project actually needs; outline and shadow presets are separate materials.
- URP Lit for 3D characters - full PBR lighting; Simple Lit or Unlit is cheaper on phones for small characters.
- Enable GPU Instancing (on a material) - helps many copies of one mesh. For sprites I count on the SRP Batcher and normal sprite batching instead.

ASSETS: ANIMATOR CONTROLLERS AND CLIPS:
- A simple chain without parameters (Fall -> Breath) - the Fall state moves to Breath through a transition with Exit Time; Breath loops. The transition is the logic, not the order of the clips.
- An item state machine (Available -> BuildSequence -> Built) with Trigger parameters. For trigger transitions that should react at once, I turn Has Exit Time off; Fixed Duration with 0 s blend, because sprite poses must not blend.
- Popups and cards (Show, Hide) - code plays the state by name.
- Write Defaults - with it on, a state writes default values for things it doesn't animate. I keep it the same inside one controller, because mixing makes values snap back.
- Character controllers - Float parameters drive a blend between idle and walk directions.
- Layers - let several animation tracks work independently. They add some evaluation work, so for simple UI and sprite animations I keep the controller simple and use only the layers I actually need.
- Clips - sample rate, Loop Time on only for idle loops, off for one-shots. Animation Events sync effects and sounds; they only show things, game logic stays in code.
- Curves animate values by object path. Renaming or moving an animated child can break the binding to that path.

PROJECT SETTINGS: URP ASSET:
- Renderer List - which renderers the pipeline can use; the 2D Renderer is the one that really draws a 2D game.
- Depth Texture / Opaque Texture - extra rendering data each frame: depth values or a copy of the opaque colour. Depth is used for effects like soft particles; the opaque copy is used for effects that read the scene colour behind them. Both cost memory and bandwidth, so I turn one on only for an effect that needs it.
- HDR - lets colors go above 1 (for bloom). It can add bandwidth and memory cost, so I keep it off when the project doesn't need HDR-dependent effects.
- MSAA - smooths edges but costs memory and bandwidth. For a 2D sprite-heavy project I only enable it if the visual result actually benefits, because it adds rendering cost.
- Render Scale - draws the game at a lower resolution and scales it up. A lower value can reduce fill-rate cost on GPU-bound phones, but the image gets softer, so I choose it from profiling and visual testing rather than a fixed number.
- Main Light / Additional Lights / Shadows / Cascades / Cookies / Reflection Probes - 3D lighting settings. The 2D Renderer ignores most of them.
- SRP Batcher - makes setting up each draw call cheaper on the CPU for compatible shaders.
- Dynamic Batching - joins some small meshes every frame. It's a separate mechanism from the SRP Batcher. I don't enable it just because it sounds faster: I check what the SRP Batcher and GPU Instancing already cover, then measure if Dynamic Batching helps this scene.
- Color Grading Mode / LUT Size - only used with post-processing.
- Volume Update Mode - Every Frame checks Volumes all the time; Via Scripting saves CPU if they never change.
- Store Actions Optimization - lets mobile GPUs skip saving data they won't need, which saves bandwidth.
- Adaptive Performance - gives the game thermal and performance feedback from the phone; my runtime logic can use it to lower quality when the device gets hot (if the package is installed).
- GPU Resident Drawer - a 3D feature for many meshes; I don't expect a useful benefit from it for this 2D sprite setup.
- Shader stripping options - remove shader variants for features I don't use, so builds are smaller and faster.

PROJECT SETTINGS: 2D RENDERER DATA:
- Transparency Sort Mode / Axis - Custom Axis (0, 1, 0) sorts by Y: lower on screen draws in front. That gives the isometric look without changing orders in code.
- Default Material Type - which material new sprites get (Lit or Unlit).
- Use Depth/Stencil Buffer - needed for Sprite Masks; off saves memory if no masks are used.
- Camera Sorting Layer Texture - copies layers into a texture for distortion effects; off saves a copy.
- Renderer Features - custom extra render passes.
- Post Process Data - used only when post-processing is on.

PROJECT SETTINGS: QUALITY:
- Levels - each level is one set of quality settings; the game can pick one per device.
- Render Pipeline Asset - each level can use its own URP asset, so different quality tiers can use different URP setups, for example a lighter configuration on weaker phones.
- VSync Count - waits for the screen refresh. On mobile the final frame rate is affected by the target frame rate the game sets, the platform and the device's display and OS behaviour.
- Anti Aliasing - in URP, MSAA comes from the URP asset, not from here.
- Global Mipmap Limit - lowers the resolution of every texture that has mipmaps; a quick memory lever for weak phones.
- Anisotropic Textures - helps textures seen at an angle; wasted in 2D.
- Soft Particles - softens particles where they touch geometry; needs the depth texture.
- Skin Weights - how many bones move one vertex. Lower counts reduce bone influence work, but I choose the value from the character and target-device needs.
- LOD Bias - when 3D LODs switch; does nothing in 2D.
- Async Upload Time Slice / Buffer Size - how much texture and mesh upload happens per frame while loading. More = faster loading, but bigger spikes.
- Texture Streaming - loads only the mip levels that are needed; useful for big 3D worlds.
- Per-platform default level - which level Android and iOS start with.

PROJECT SETTINGS: PLAYER:
- Color Space - Linear gives correct light and blending math; supported on modern phones.
- Scripting Backend - how Unity builds and runs the C# code on the device. iOS needs the code built into native code ahead of time, while Android can use either option depending on the project. The native option means longer builds.
- Target Architectures - for current Android releases I target ARM64, according to the platform and store requirements; ARMv7 only for very old phones.
- Minimum / Target API Level - the oldest Android the game supports, and the version it targets.
- Graphics APIs - Vulkan and OpenGLES3 on Android, Metal on iOS. I choose the order from the phones I support and test real devices.
- Managed Stripping Level - removes unused code to make the build smaller; higher levels can remove code that is called only by name, unless I mark it to be kept.
- Default Orientation - for a portrait-only game I lock Portrait, so the layout never meets landscape.
- Multithreaded Rendering - lets rendering work use a separate thread. I keep it matched to the renderer and check it on target devices, not just because it sounds faster.
- Api Compatibility Level - I use the level that the project and its packages support. I don't choose it only because it is smaller.
- Incremental GC - can spread garbage collection work over frames and reduce big spikes, depending on the game.
- Active Input Handling - which input system the project uses (the new Input System or the old Input Manager).

PROJECT SETTINGS: GRAPHICS:
- Default Render Pipeline - the URP asset; if it is empty, the project uses the old Built-in pipeline.
- Always Included Shaders - shaders that are always in the build; each adds variants, so the list stays short.
- Preloaded Shaders / Shader Variant Collection - prewarms selected shader variants during loading, which can reduce the hitch when a shader is used for the first time.
- Instancing / Lightmap / Fog Stripping - removes shader variants for features no scene uses.
- Sprites Default Material - only for Built-in; URP uses the 2D Renderer's material.
- Transparency Sort Mode here - ignored in URP; the 2D Renderer Data setting is used.

PROJECT SETTINGS: EDITOR:
- Sprite Packer Mode - Sprite Atlas V2 can pack atlases for Play Mode and builds, depending on the selected V2 mode. I don't disable it in a project that relies on Sprite Atlases.
- Asset Serialization - Force Text saves scenes and prefabs as readable text instead of binary, so changes can be compared.
- Enter Play Mode Options - can skip the domain reload so Play starts faster; then static fields keep their values, so code must reset them itself.
- Async Shader Compilation - in supported Editor configurations, the Editor shows a cyan placeholder while a shader compiles, instead of freezing.
- Asset Pipeline / Unity Accelerator - a shared import cache can make asset imports faster for a team.


QUESTIONS AND ANSWERS:

--- UNITY HANDS-ON FUNDAMENTALS ---

Q: What is a GameObject?
A: A GameObject is an empty container in Unity that holds components to create effects or any objects in the game. It is used as the base for everything in the scene and becomes visible when components like SpriteRenderer or ParticleSystem are added.

Q: What is a Component?
A: A Component is a piece of functionality attached to a GameObject that gives it specific abilities like displaying graphics, playing sounds, or physics. Components are configured in the Inspector and accessed through code to control object behavior.

Q: What is a Transform?
A: A Transform is a component on every GameObject that defines its position, rotation, and scale. It is used for placing objects in the scene and animating them by changing position or rotation values.

Q: What is a RectTransform?
A: A RectTransform is a special version of Transform used for UI elements inside a Canvas. RectTransform has anchors, pivot, and size. It is used for positioning elements so they adapt to different screen sizes.

Q: What is a Scene?
A: A Scene is a container holding GameObjects that form one level, area, or screen in the game like the main menu or gameplay island. Multiple scenes can be loaded to stream content without visible loading screens.

Q: What is a Prefab?
A: A Prefab is a reusable template of a GameObject saved as an asset that can be copied many times while keeping a link to the original for easy updates. It is used for buildings, characters, or effects that appear often in the game.

Q: What is a Prefab Variant?
A: A Prefab Variant is a version of a Prefab that inherits from a base Prefab but allows changing specific values like sprites or colors. It is used for creating different versions of the same object while keeping shared logic and structure.

Q: What is a MonoBehaviour?
A: A MonoBehaviour is the base class for all C# scripts attached to GameObjects, providing access to Unity methods like Start, Update, and event callbacks. It is used to add custom behavior, control animations, or manage visual effects through code.

Q: What is a ScriptableObject?
A: A ScriptableObject is a data container that stores configurations, stats, or settings without being attached to a GameObject. It is used for item stats, enemy settings, or game balance that designers can change in the Inspector without coding.

Q: What is a Texture?
A: A Texture is an image file imported into Unity that provides visual appearance for sprites, UI, materials, or 3D models.

Q: What is a Sprite?
A: A Sprite is a 2D image taken from a Texture that can be displayed in the game using a SpriteRenderer.

Q: What is a SpriteRenderer?
A: A SpriteRenderer is a component that displays a Sprite on a GameObject in the 2D game world. It controls properties like color, flip, and sorting order for rendering.

Q: What is a Sprite Atlas?
A: A Sprite Atlas is an asset that packs multiple Sprites into one large Texture to reduce draw calls and improve performance. It allows objects with different sprites to batch together when they share the same atlas.

Q: What is a Sprite Mask?
A: A Sprite Mask is a component that hides parts of Sprites based on a mask texture, creating cutout or reveal effects.

Q: What is a Sorting Layer?
A: A Sorting Layer is a named layer that controls the rendering order of 2D objects, with layers rendered from top to bottom in the list. Common layers include Background, Characters, Effects, and UI for organized depth.

Q: What is Order in Layer?
A: Order in Layer is a number that fine-tunes rendering order within one Sorting Layer, where higher values render on top of lower values. It allows precise control over which sprites appear in front when sharing the same layer.

Q: What is a Sorting Group?
A: A Sorting Group is a component that overrides sorting settings for all renderers on a GameObject and its children. For example, a Sorting Group is used for characters or buildings made of many sprites, so they sort as one object.

Q: What is a Pivot?
A: A Pivot is the anchor point of a Sprite that determines its position, scaling and rotation center. It can be set to Center, Top-Left, Bottom, or custom coordinates for alignment and animation.

Q: What are Pixels Per Unit?
A: Pixels Per Unit defines how many pixels in the sprite equal one Unity unit in the game world.

Q: What is 9-slicing?
A: 9-slicing divides a Sprite into nine sections so the center stretches while corners stay fixed, configured by setting borders in the Sprite Editor. It is used for UI panels and buttons that resize without distorting corners.

Q: What is a spritesheet?
A: A spritesheet is one Texture containing multiple Sprite frames in a grid, typically used for animations. Each frame is sliced as an individual Sprite and sequenced in animation clips.

Q: What is a Tight Mesh?
A: Tight Mesh creates vertices only around visible pixels. It is beneficial for irregular-shaped sprites where transparent areas would be rendered unnecessarily.

Q: What is Full Rect?
A: Full Rect creates a simple rectangular mesh covering the entire sprite bounds including transparent areas, using only 4 vertices. Full Rect is used for 9-slicing.

Q: What is a Canvas?
A: A Canvas is the root container for all UI elements in Unity that renders UI on the screen. All buttons, images, and text must be inside a Canvas to work properly.

Q: What is Canvas Scaler?
A: Canvas Scaler is a component that automatically scales UI based on screen size and resolution. It keeps UI looking consistent across different devices like phones and tablets.

Q: What is a Graphic Raycaster?
A: A Graphic Raycaster is a component on Canvas that allows UI elements to receive clicks and touches. It works with EventSystem to detect which UI element was interacted with.

Q: What is an EventSystem?
A: An EventSystem is a component that manages all input events like clicks, touches, and keyboard navigation. Every scene with UI needs one EventSystem to handle user input.

Q: What is a CanvasGroup?
A: A CanvasGroup is a component that controls alpha, interaction, and raycast for all child UI elements as one group. It is used for fading entire panels or disabling interaction with UI sections.

Q: What is an Image?
A: An Image is a basic UI component that displays a Sprite or solid color.

Q: What is a Button?
A: A Button is an interactive UI component that responds to clicks and triggers events. It provides visual states for Normal, Highlighted, Pressed, and Disabled conditions.

Q: What is a Text Mesh Pro?
A: TextMeshPro is an advanced text component for UI that provides high-quality typography with extensive formatting options. It supports rich text, custom fonts, outlines, shadows, and is the recommended text solution for all UI.

Q: What is a ScrollRect?
A: A ScrollRect is a component that creates scrollable areas for UI content that exceeds the visible area. It is used for inventory lists, dialogue boxes, settings menus, and any UI with large amounts of content.

Q: What is a Mask?
A: A Mask is a component that clips child UI elements to its shape, hiding content outside the mask area.

Q: What is a RectMask2D?
A: RectMask2D is a rectangular clipping component that masks child UI to a rectangle without using the stencil buffer. It is more performant than Mask.

Q: What is a Layout Group?
A: A Layout Group is a component that automatically organizes child UI elements in horizontal or vertical patterns. It handles positioning and spacing dynamically, reducing manual layout work.

Q: What is a Content Size Fitter?
A: A Content Size Fitter is a component that automatically resizes a RectTransform to fit its content precisely. It is used for dynamic UI panels that need to expand or contract based on text or item count.

Q: What are Anchors?
A: Anchors are reference points on a parent that determine how child UI elements are positioned and resized. They allow UI to maintain proportions when screen size changes, essential for responsive layouts.

Q: What is a Safe Area?
A: A Safe Area is the portion of the screen not covered by notches, status bars, or home indicators. It is used to position UI within visible bounds so content is not hidden on modern devices.

Q: What is an Animator?
A: An Animator is a component that controls animation playback on a GameObject based on an Animator Controller. It manages state transitions, parameters, and blending between animation clips during runtime.

Q: What is an Animator Controller?
A: An Animator Controller is an asset that defines animation logic for an Animator, containing states, transitions, parameters, and blend trees. It acts as a state machine that determines which animation plays based on conditions.

Q: What is an Animation Clip?
A: An Animation Clip is a reusable asset containing keyframe data that defines how properties change over time, such as position, rotation, or scale. It is the actual animation content like Idle, Run, or Jump.

Q: What is an Animator State?
A: An Animator State represents a single animation or blend tree within an Animator Controller that plays when the state is active. States are connected through transitions to create animation flow.

Q: What is an Animator Transition?
A: An Animator Transition defines the conditions and timing for moving from one Animator State to another. It specifies parameters, thresholds, and blend duration between states.

Q: What is an Animator Parameter?
A: An Animator Parameter is a variable defined in an Animator Controller that influences state transitions and animation behavior. Parameters can be Float, Int, Bool, or Trigger.

Q: What is an Animation Event?
A: An Animation Event is a marker on an Animation Clip that triggers a function call at a specific frame. It is used to synchronize actions with animation, such as spawning effects or playing sounds.

Q: What is a Blend Tree?
A: A Blend Tree is a special Animator State that blends between multiple Animation Clips based on a parameter value. It enables smooth transitions between similar animations like walk, jog, and run.

Q: What is a Material?
A: A Material is an asset that defines how an object looks when rendered, containing a Shader and values like color and textures.

Q: What is a Shader?
A: A Shader is a program that runs on the GPU and determines how pixels are calculated and displayed during rendering. It defines lighting, textures, transparency, and visual effects that create the final appearance.

Q: What is Shader Graph?
A: Shader Graph is a visual node-based editor for creating Shaders without writing code. It allows artists to build complex materials through node connections with real-time preview.

Q: What is the Universal Render Pipeline?
A: The Universal Render Pipeline is Unity's modern rendering solution that controls how scenes are rendered each frame. It allows customization through Renderer Features and includes built-in post-processing effects.

Q: What is URP?
A: The Universal Render Pipeline is Unity's modern rendering solution that controls how scenes are rendered each frame. It allows customization through Renderer Features and includes built-in post-processing effects.

Q: What are Renderer Features?
A: Renderer Features are built-in effects that can be added to URP to extend rendering. Common features include Render Objects, Decals, SSAO, and Screen Space Shadows. Custom features can be created for outlines, blur, or game-specific effects. Motion Blur and Bloom are post-processing effects, together with Vignette, Color Adjustments, Tonemapping, and Depth of Field.

Q: What is post-processing?
A: Post-processing is image effects applied to the whole picture after the camera renders the scene, like Bloom, Vignette, Color Adjustments, and Depth of Field. In URP it is set up with a Volume, not with Renderer Features. It is expensive on mobile because it processes the full screen, so it is used carefully and checked on a real phone.

Q: Is Bloom a Renderer Feature?
A: No, Bloom is a post-processing effect that is added through a Volume in URP. Renderer Features are a different thing, like Render Objects or Decals. Bloom makes bright parts glow and is expensive on mobile because it needs several full-screen passes.

Q: What is the 2D Renderer?
A: The 2D Renderer is a specialized renderer within URP designed for 2D games with features like 2D lights, shadows, and normal maps. It supports Sprite-Lit and Sprite-Unlit shaders for advanced 2D lighting.

Q: What is a Renderer?
A: A Renderer is a component that determines how a GameObject is drawn on screen, working with a Material to define visual appearance. Different types exist for different purposes like SpriteRenderer for 2D or MeshRenderer for 3D.

Q: What is a MeshRenderer?
A: A MeshRenderer is a component that renders 3D mesh geometry using a Material, commonly used for static or non-animated 3D objects. It works with a MeshFilter that provides the geometry data.

Q: What is a SkinnedMeshRenderer?
A: A SkinnedMeshRenderer is a specialized renderer for animated 3D characters and objects that use skeletal animation with bones. It deforms the mesh based on bone transformations and supports blend shapes.

Q: What is a Render Texture?
A: A Render Texture is a special texture that receives rendered image output from a Camera instead of displaying to screen.

Q: What is a Particle System?
A: A Particle System is a component that emits and simulates many small particles to create effects like fire, smoke, sparks, or magic. It is configured through modules controlling emission, shape, velocity, color, size, and lifetime. It is widely used for gameplay feedback, environment effects, and UI polish.

Q: What is VFX Graph?
A: VFX Graph is Unity's GPU-based visual effects system that creates complex particle simulations using compute shaders. It uses a node-based editor for designing effects visually without coding. It is best for high-end platforms and is less compatible with older mobile devices.

Q: What is Overdraw?
A: Overdraw happens when the same pixel is drawn multiple times in one frame, wasting GPU performance. It occurs with overlapping transparent objects like particles, UI panels, or sprites. Red areas in Overdraw mode indicate problem zones where performance is lost.

Q: What is Fixing Overdraw?
A: Fixing overdraw means reducing how many times pixels are drawn multiple times to improve performance. This is done by using fewer transparent particles or replacing transparency with Alpha Clipping for hard edges. Additive blend does not reduce overdraw - pixels are still drawn many times when transparent objects overlap. Overdraw is visible in Scene view Overdraw mode where red zones show problem areas that need optimization.

Q: What is Fill Rate?
A: Fill Rate is the number of pixels the GPU can render per second. It is a limiting factor for mobile performance, especially with large transparent effects or high-resolution UI. Fill Rate limitations cause frame drops when too many pixels need processing.

Q: What is Transparency?
A: This is one of the rendering modes in a material where we can choose the alpha parameter. It makes objects see-through with soft edges, like smoke or glass, but many transparent layers cause overdraw.

Q: What is Alpha Clipping?
A: Alpha clipping discards pixels with an alpha channel value below a certain threshold, creating sharp edges instead of a smooth transparency transition. Alpha clipping improves performance because the discarded pixels are not rendered.

Q: What is a Draw Call?
A: A draw call is a command from CPU to GPU telling it to draw objects. Too many draw calls slow down the game because CPU spends time sending commands instead of doing other work. Reducing draw calls by batching or instancing improves performance. Batching is used for optimization.

Q: What is Batching?
A: Batching combines multiple objects into one draw call so GPU draws them together instead of separately. This reduces CPU work and speeds up rendering. Unity has static batching, dynamic batching, and SRP Batcher as different batching methods.

Q: What is Static Batching?
A: Static batching combines objects that never move into one big mesh at build time or startup. This creates one draw call for many static objects like buildings or trees. Objects must be marked as Static in Inspector to use this feature.

Q: What is Dynamic Batching?
A: Dynamic batching combines small moving objects into one draw call each frame if they share the same material. Unity does this automatically for small meshes.

Q: What is the SRP Batcher?
A: SRP Batcher is a faster batching system for Universal Render Pipeline and High Definition Render Pipeline. It reduces CPU overhead by keeping render data in GPU memory instead of uploading it each frame. This works with both static and dynamic objects using compatible shaders.

Q: What is GPU Instancing?
A: GPU Instancing draws many copies of the same object with one draw call by sending position and scale data in arrays. This is perfect for forests, crowds, or repeated props. Objects must use the same mesh and material but can have different positions and colors.

Q: What is CPU-bound?
A: CPU-bound means the processor is the bottleneck limiting game performance. This happens when there are too many draw calls, physics calculations, or script updates. Fixing CPU-bound issues requires reducing script work, batching objects, or optimizing logic.

Q: What is GPU-bound?
A: GPU-bound means the graphics card is the bottleneck limiting game performance. This happens with high resolution, complex shaders, or too many pixels to render. Fixing GPU-bound issues requires lowering resolution, reducing overdraw, or simplifying materials.

Q: What is Frame Time?
A: Frame time is how long it takes to render one frame, measured in milliseconds. Lower frame time means smoother gameplay and higher FPS. Frame time is shown in Unity Profiler and helps identify performance bottlenecks.

Q: What is FPS?
A: Frames per second shows how many frames are rendered each second. Higher FPS means smoother gameplay, with 60 FPS as a common target and 30 FPS for weaker phones. FPS is calculated as 1000 divided by frame time in milliseconds.

Q: What is Garbage Collector?
A: Garbage collector is a system that cleans up memory that code no longer uses. When it runs, it can cause a short freeze. To avoid this, objects are reused instead of created every frame.

Q: What is the Unity Profiler?
A: Unity Profiler shows real-time performance data for CPU, GPU, memory, fps, meshes and other systems. It helps find what is slowing down the game by showing time spent in each function. The Profiler is opened from Window → Analysis → Profiler and used during play mode.

Q: What is the Frame Debugger?
A: Frame Debugger shows every draw call and render step for one frame in order. It helps understand what Unity renders and why objects appear in certain order. The Frame Debugger is opened from Window → Analysis → Frame Debugger and works with paused game.

Q: What is Texture Compression?
A: Texture compression reduces texture file size and memory usage by encoding image data in a smaller format. Compressed textures load faster and use less GPU memory but may lose some quality.

Q: What is a Mipmap?
A: Mipmaps are smaller versions of a texture used when objects are far from camera to save memory and improve quality. Unity generates mipmaps automatically and selects the right size based on distance. Enabling mipmaps uses more memory but prevents flickering and improves performance for 3D objects.

Q: What is Max Texture Size?
A: Max Texture Size limits the largest dimension of a texture to reduce memory usage.

Q: What is Read/Write Enabled?
A: Read/Write Enabled allows code to read or modify texture data from CPU but doubles memory usage. This is needed for scripts that change textures at runtime but should be disabled for static textures. Most textures do not need this option and it should be turned off to save memory.

Q: What is a Texture Format?
A: Texture format defines how texture data is stored in memory, affecting quality, size, and performance. Common formats include RGBA32 for quality, ASTC or ETC for mobile compression, and DXT for PC.

Q: What are Addressables?
A: Addressables is a Unity system for loading and managing assets by name instead of direct references. Assets can be loaded from disk or downloaded at runtime without rebuilding the game.

Q: What is an Addressables Group?
A: An Addressables Group is a collection of assets that are built and loaded together as one unit. Groups define how assets are packed into bundles and where they are stored locally or remotely. Groups are managed in the Addressables Groups window and each group has build settings like compression and location.

Q: What is an Addressables Catalog?
A: An Addressables Catalog is a file that contains information about all addressable assets and their locations. The catalog is downloaded at runtime so the game knows where to load assets from. Multiple catalogs can be used for different content updates or regions.

Q: What is an Addressables Label?
A: An Addressables Label is a tag that can be added to multiple assets for loading them as a group. Labels allow loading all assets with a certain tag without knowing their exact addresses. This is useful for loading all UI sprites or all levels in one call.

Q: What is an Addressable Asset?
A: An Addressable Asset is any asset that has been added to the Addressables system and can be loaded by address. These assets are marked with the Addressable checkbox in Inspector and appear in the Addressables Groups window.

Q: What is an AssetBundle?
A: An AssetBundle is a file containing compressed assets that can be loaded at runtime from disk or server. AssetBundles are the underlying technology used by Addressables to package and deliver content. They can be built for specific platforms and downloaded on demand to reduce initial game size.

Q: What is Object Pooling?
A: Object Pooling is a technique where objects are reused instead of destroyed and recreated to avoid garbage collection. Pooled objects are disabled when not needed and re-enabled when required, saving memory and CPU time.

Q: What is a Unity Build?
A: A Unity Build is the final game executable and data files created from a Unity project for a specific platform. Builds are created through the Build window and include all scenes, assets, and code. Different platforms like PC, Android, or iOS require separate builds with platform-specific settings.

Q: What is a Development Build?
A: A Development Build is a special build with extra debugging features like profiler connection and error logs enabled. These builds are larger and slower but allow testing and debugging during development. Development builds are created by checking "Development Build" in Build Settings before building.

Q: What is a Build Profile?
A: A Build Profile is a saved set of build settings that can be quickly switched between different configurations. Profiles store platform, scripting backend, architecture, and other options for consistent builds. Build profiles are managed in the Build Profiles window and allow one-click switching between development and release builds.

Q: What is technical integration of art content?
A: Technical integration of art content means importing artist work like models, textures, and animations into Unity with correct settings and performance. This includes setting texture compression, LOD levels, material properties, and ensuring assets work in the game. Technical Integration prevents visual issues and maintains target frame rate.

Q: What is identifying and addressing performance?
A: Identifying and addressing performance means finding what causes lag or stuttering using Profiler and Frame Debugger then fixing the root cause. Common fixes include reducing draw calls, optimizing textures, fixing overdraw, or reducing script allocations. Performance work is ongoing throughout development to maintain smooth gameplay.

Q: What is memory?
A: Memory is the RAM used by the game to store textures, meshes, audio, and code while running. High memory usage causes crashes on mobile devices with limited RAM. Memory is monitored in Profiler Memory module and reduced by compressing textures, unloading unused assets, and avoiding allocations.

Q: What does "Investigate visual and technical issues independently, identify their root cause, and implement effective solutions" mean?
A: This means finding problems like lags, visual glitches, or crashes by using Unity tools and logs to understand what causes them. Once the cause is known, appropriate fixes are applied like optimizing shaders, reducing overdraw, or fixing memory leaks. Independent problem solving requires understanding Unity rendering, memory, and CPU profiling.

Q: What does "Deliver within release timelines and coordinate your work with the wider production pipeline" mean?
A: This means completing tasks on schedule so the game can be released on time and working with other team members like artists and designers. Coordination includes using version control, following naming conventions, and communicating when assets are ready. Meeting deadlines requires planning work and prioritizing critical performance fixes.

Q: What is core tools in Unity?
A: Core tools in Unity include Profiler for performance, Frame Debugger for rendering, Memory Profiler for allocations, and Addressables for asset management. These tools are accessed through Window → Analysis menu and used for optimization work.

Q: What is addressables remote content delivery?
A: Addressables remote content delivery means hosting asset bundles on a server and downloading them to players devices when needed. This allows updating game content like new levels or events without releasing a new app version. Remote content requires a catalog URL and is loaded using Addressables with remote group settings.

Q: What is RawImage?
A: RawImage is a UI component that displays textures or render textures directly without using sprites or atlases. This is useful for dynamic content like downloaded images, video playback, or runtime-generated textures. RawImage is found under UI menu and accepts Texture or RenderTexture as source.

Q: What is stencil buffer?
A: Stencil buffer is a GPU feature that masks rendering to specific screen areas using values instead of alpha blending.

Q: How to optimize shaders?
A: Optimizing shaders means simplifying shader code to use fewer GPU instructions and texture samples for faster rendering. This is done by removing unnecessary calculations, using simpler math functions, and reducing texture fetches in fragment shaders. Shaders are optimized in Shader Graph by using fewer nodes or in hand-written shaders by simplifying HLSL code.

Q: What exactly needs to be done to reduce overdraw?
A: Reducing overdraw requires decreasing overlapping transparent objects by using fewer particles or making them smaller. Additive blend does not reduce overdraw - pixels are still drawn many times when transparent objects overlap. Another method is replacing Alpha Blend transparency with Alpha Clipping for hard-edge objects like foliage or grates to avoid blending calculations. Overdraw is identified in Scene view Overdraw mode and fixed by adjusting particle systems, UI panels, or transparent materials.

Q: How exactly to fix memory leaks?
A: Fixing memory leaks means finding code that keeps references to objects preventing garbage collector from freeing memory and removing those references.

Q: What is LOD levels?
A: LOD levels are multiple versions of the same 3D model with decreasing detail used at different distances from camera to save performance. High detail models are shown when close and lower detail models with fewer polygons are shown when far away. LOD Group component manages which level is active based on distance and is configured in Inspector with multiple mesh slots.

Q: What is the difference between a GameObject and a Component?
A: GameObject is an empty container in the scene that holds Components which add functionality like rendering, physics, or scripts. Components cannot exist alone and must be attached to a GameObject to work. GameObjects are created in Hierarchy while Components are added through Add Component button in Inspector.

Q: What is the difference between Transform and RectTransform?
A: Transform handles position, rotation, and scale in 3D space for regular GameObjects while RectTransform adds anchoring and pivoting for UI layout. RectTransform is used only for UI elements inside Canvas and controls how they resize with screen. Transform is for 3D objects and RectTransform is for 2D UI.

Q: What is the difference between a Prefab and a Prefab Variant?
A: Prefab is a reusable template of a GameObject while Prefab Variant is a modified version that inherits from another prefab. Variants allow creating different versions like enemy_fast or enemy_strong from one base enemy prefab without duplicating all data. Variants update when the base prefab changes but keep their own overrides.

Q: What is the difference between a Texture and a Sprite?
A: Texture is an image asset used for materials, UI, or rendering while Sprite is a Texture with additional settings for 2D rendering and slicing. Sprites have pivot points, borders for 9-slicing, and can be packed into atlases for UI efficiency. Textures are used for 3D materials and Sprites are used for 2D GameObjects.

Q: What is the difference between a Sprite and a SpriteRenderer?
A: Sprite is the image asset in Project folder while SpriteRenderer is the Component on a GameObject that displays the Sprite in scene. Multiple GameObjects can use the same Sprite asset through their SpriteRenderer components. Sprite is the data and SpriteRenderer is what renders it.

Q: What is the difference between a SpriteRenderer and a UI Image?
A: SpriteRenderer renders 2D sprites in world space for game objects while UI Image renders sprites in screen space inside Canvas for interface. SpriteRenderer uses Sorting Layers for depth while UI Image uses Canvas sorting order. SpriteRenderer is for 2D game world and UI Image is for menus and HUD.

Q: What is the difference between a Material and a Shader?
A: Shader is the code that defines how something is rendered with lighting, textures, and effects while Material is an instance of a shader with specific settings like colors and textures. Multiple materials can use the same shader but with different property values. Shaders are created once and materials are created from shaders for each object.

Q: What is the difference between an Animation Clip and an Animator Controller?
A: Animation Clip is a single animation like walk cycle or jump that stores keyframes for transforms over time. Animator Controller is a state machine that contains multiple Animation Clips and controls transitions between them using parameters. Clips are the animations and Controllers organize when each clip plays.

Q: What is the difference between Animator and Tweening?
A: Animator uses Animation Clips and state machines for complex character animation with blending and transitions. Tweening libraries like DOTween animate properties directly through code for simple UI or object animations without clips. Animator is for character animation and Tweening is for programmatic simple animations.

Q: What is the difference between Mask and RectMask2D?
A: Mask uses stencil buffer to cut content into any shape but adds extra draw calls and is slower on mobile. RectMask2D uses simple rectangle Mesh clipping without stencil buffer making it faster and better for UI and Canvases. RectMask2D is preferred for rectangular UI areas and for 9-slice while Mask is only for irregular shapes.

Q: What is the difference between Full Rect and Tight Mesh?
A: Full Rect creates a sprite mesh covering the entire rectangle while Tight Mesh creates a mesh that fits only the visible pixels reducing overdraw. Tight Mesh is better for irregular shapes like circles or characters to avoid rendering transparent areas. Full Rect is faster to generate but Tight Mesh saves GPU work.

Q: What is the difference between Sorting Layer and Order in Layer?
A: Sorting Layer is a named layer like Background, Characters, or UI that groups objects for rendering order. Order in Layer is a number within each Sorting Layer that determines which object renders on top within that layer. Sorting Layers are configured in Tags and Layers while Order in Layer is set on each SpriteRenderer.

Q: What is the difference between MeshRenderer and SkinnedMeshRenderer?
A: MeshRenderer renders static meshes that do not deform while SkinnedMeshRenderer renders meshes with bones for character animation. SkinnedMeshRenderer calculates vertex positions based on bone transforms each frame for animated characters. MeshRenderer is for props and buildings while SkinnedMeshRenderer is for characters.

Q: What is the difference between Particle System and VFX Graph?
A: Particle System is the built-in CPU-based particle system for simple effects like fire or smoke that works on all platforms. VFX Graph is a GPU-based system for complex high-count effects like magic or explosions that requires compute shader support. Particle System is for mobile and simple effects while VFX Graph is for high-end platforms.

Q: What is the difference between Transparency and Alpha Clipping?
A: Transparency blends pixels with background using alpha values creating semi-transparent effects but causes overdraw. Alpha Clipping discards pixels below a threshold creating hard edges without blending which is faster and has no overdraw. Transparency is for glass or ghosts while Alpha Clipping is for foliage or grates.

Q: What is the difference between Static Batching and Dynamic Batching?
A: Static Batching combines non-moving objects into one mesh at build time for zero runtime cost but objects cannot move. Dynamic Batching combines moving objects each frame automatically but has vertex limits and CPU overhead. Dynamic Batching objects must have the same material. Static is for buildings and terrain while Dynamic is for moving props.

Q: What is the difference between Batching and SRP Batcher?
A: Batching combines objects to reduce draw calls through static or dynamic methods that merge geometry. SRP Batcher keeps render data in GPU memory and reduces CPU overhead without merging geometry, working with compatible shaders. Batching reduces draw call count while SRP Batcher makes each draw call faster.

Q: What is the difference between CPU-bound and GPU-bound?
A: CPU-bound means processor is the bottleneck from too many draw calls, physics, or script calculations limiting performance. GPU-bound means graphics card is the bottleneck from high resolution, complex shaders, or overdraw limiting performance. CPU-bound is fixed by batching and script optimization while GPU-bound is fixed by lowering quality settings.

Q: What is the difference between Addressables and Resources?
A: Addressables loads assets by name, supporting local or remote delivery options and explicit unloading. Resources loads assets from Resources folder by path but includes all Resources assets in every build and cannot unload selectively. Addressables is the modern recommended system while Resources is legacy and discouraged.

Q: What is the difference between Addressables and AssetBundles?
A: Addressables is a high-level system that uses AssetBundles internally but adds features like labels, groups, and easy loading API. AssetBundles are the underlying bundle files that must be manually built, loaded, and managed with more complex code. Addressables wraps AssetBundles for easier use and better workflow.

Q: What is the difference between local and remote Addressables?
A: Local Addressables are built into the game and loaded from device storage without downloading. Remote Addressables are hosted on a server and downloaded at runtime for content updates or DLC without new builds. Local is for base game content while remote is for live ops and updates.

Q: What is the difference between Screen Space Overlay, Screen Space Camera and World Space Canvas?
A: Screen Space Overlay renders UI on top of everything ignoring camera and always facing screen for HUD elements. Screen Space Camera renders UI at a distance from camera allowing 3D perspective and camera effects. World Space renders UI as flat 3D objects in the scene that can be viewed from any angle like signs or terminals.

Q: What is Tweening?
A: Tweening smoothly moves a value from A to B over time - for example a button grows or a panel slides in. It is usually done in code, for small one-time moves.

Q: What is Resources?
A: Resources is an old Unity folder for content loaded by name. Everything in it always goes into the app, even if it is not used, so it makes the app bigger.

--- FUNDAMENTALS: BASIC DEFINITIONS AND DIFFERENCES ---

Q: What is Unity?
A: Unity is a game engine and editor for building games for phones, PC, consoles and other platforms. Scenes are built from GameObjects and components, and art, UI, animation, effects and C# code all come together in the editor. For a mobile 2D game the main parts are sprites, uGUI, the Animator, the Particle System, URP and Addressables.

Q: What is the difference between a prefab variant and a nested prefab?
A: A nested prefab is a prefab inside another prefab, like a marker inside an item. A variant is a prefab based on another prefab that keeps the link to its base and overrides only its differences. So a nested prefab is about composition - building one prefab from others - and a variant is about inheritance from a base prefab.

Q: How do you handle overrides on variants?
A: First I open the Overrides list to see exactly what changed. Then I apply only what really belongs to the base and revert my own experiments. I don't just press Apply All, because applying an override to the base can change the other variants that come from it.

Q: How do you decide between Animator, Timeline, tweening and code-driven animation?
A: The Animator is for objects with states that switch, like a popup with show, idle and hide. Timeline is for fixed sequences with many objects and exact timing, like an intro or a reward sequence. Tweens are for small one-time UI moves, and code is for motion driven by game logic. The best choice is the simplest tool that stays clear and easy to change.

Q: Additive or alpha blended particles?
A: Additive for light, fire and sparks - it only makes things brighter. Alpha blend for smoke and dust that must cover what's behind. A soft white cloud usually needs alpha blending, because additive blending becomes hard to see against a bright background.

Q: What are garbage collector allocations?
A: Garbage collector allocations are memory that the code allocates while the game runs, which the garbage collector later has to clean up. Repeated allocations create garbage and more collection work, which can make frames slower or cause spikes. Hot code that runs every frame should avoid unnecessary allocations, while an occasional allocation, like on a button press, is usually fine, and the Profiler shows where they come from.

Q: What is an AssetPostprocessor?
A: An AssetPostprocessor is an editor script that runs code before or after Unity imports an asset. It is used to apply the same import settings automatically - for example compression, Max Size and Read/Write per folder - instead of setting every asset by hand. It helps keep the art pipeline consistent.

Q: What is the difference between EditMode and PlayMode tests?
A: EditMode tests run in the Editor without Play - fast, and good for tools and data checks. PlayMode tests run real frames with the game systems working, which is needed for gameplay and UI animation.

--- QUESTIONS ABOUT MY HOME ASSIGNMENT (they discuss it in the interview) ---

Q: Why did you structure the variants this way?
A: I use one base prefab with a shared Animator. Each variant changes only the sprites, anchors and data. So a fix to the base reaches all seven items at once, unless a variant overrides that exact part - that's why I keep the overrides small. The chain stays short, and I always know where a change came from.

Q: What else did you consider?
A: I thought about a separate prefab for each item, but then every fix would have to be copied seven times. I also thought about Timeline for the animation, but one Animator clip is simpler and shows all the timing in one place.

Q: How does this scale to events and new islands?
A: Same base and Animator, new variants with their own data. Each island gets its own remote Addressables group with its own atlas. So a compatible new island can come from the server without an app update.

Q: How would you make it data-driven for designers?
A: I'd put prices, rewards and sprite references in a ScriptableObject or a table, and write a tool that generates the variants from the rows. Then a designer can change the numbers without ever opening the prefab.

Q: How did you check it?
A: I tested two screen sizes (1080x2400 and 2048x2732) plus the Device Simulator. I wrote EditMode tests for structure and checks, and I looked at the pixels myself. For behaviour while the game runs I would add PlayMode tests. And I wrote down honestly what I measured and what I didn't.

Q: Did you test on a real device?
A: Not for this assignment, but I would profile on a weak Android before release.

Q: Why is the island made of sprites and not UI?
A: The island lives in the world, not on the screen. World sprites give me the normal 2D renderer and sorting control, and I can put particles in the same sorting order when I need them between items. The camera shows the world so it fills the screen. I used UI only for things pinned to the screen, like buttons and text.

Q: Why are a shadow and its item in one atlas?
A: They are usually drawn next to each other, so putting them in one atlas gives them a chance to batch without a texture switch. If they were in different atlases, drawing them in an interleaved order could need extra texture switches and split the batch.

Q: What did you leave outside atlases?
A: The island base at 2241 pixels - it was too big for the 2048 atlas I used, so I kept it separate - plus the sky gradient and the cloud flipbook. I also kept out a few sprites whose custom shaders depend on the original 0-1 UVs, because atlas packing changes those UVs.

Q: Why is the island remote?
A: Players get to islands later in the game, and new islands come out after launch. The main UI must work without internet, so it stays local, but islands can be remote.

Q: What would you do with more time?
A: Real remote loading with a progress bar, and profiling on a weak Android to see where the time really goes. I would also check the texture compression quality on real phones.

Q: What is the SRP Batcher, and did you use it in the assignment?
A: Before every draw call the CPU prepares data for the GPU: the material and its values, the object position. The SRP Batcher keeps material data in GPU buffers, so the CPU doesn't have to set it all up again for every draw call. It does not cut the number of draw calls - it makes each one cheaper for the CPU. It works only with compatible shaders; standard URP shaders and compatible Shader Graph shaders can use it. Objects must use the same shader variant - materials can be different, but other keywords split the batch. A per-object property override can make a renderer incompatible with the SRP Batcher, so for per-object differences I prefer vertex color. I check it in the Frame Debugger, where I look at the draw sequence and the batch information, and in the shader Inspector, which shows if a shader is compatible. In the assignment, the SRP Batcher was enabled in the URP asset. I didn't tune it separately, but I kept it working: shared Shader Graph materials, no per-object property overrides, vertex color for variation. For the 2D part I mainly relied on Sprite Atlases, shared materials and controlled draw order - the SRP Batcher matters more for compatible mesh-based rendering. On a real project I would check it in the Frame Debugger and measure on the phone.

Q: What was the hardest?
A: Getting the animation timing to match the reference video, so the next action is ready in under 2 seconds. It has to feel quick.

--- HOW I WORK (job post: mockup -> feature, ownership, communication) ---

Q: How do you work with artists and developers?
A: With artists I talk about the goal - how it should look and feel. With developers I talk about how it's built, the limits, speed, and how easy it is to fix later. My job is to connect both sides, so the game looks great and still runs well.

Q: How do you work with designers and product?
A: First I ask why players need this feature, not only what to build. From a mockup or a Miro board I ask about all the states, the edge cases and what matters most. Then I build it in Unity and tell them early about any trade-offs.

Q: How would you turn a Miro board or mockup into a production-ready Unity feature?
A: First I study the design - all the states, taps, animations and data. Then I build a small test version in Unity. Then the real reusable prefab and UI, then animation and effects, and I connect it to the game state. At the end I check speed, memory, loading and edge cases.

Q: What if the design is broken?
A: I say so, and I show a fix with a quick prototype.

Q: What do you do when the brief is incomplete?
A: I ask clear questions early and write down what we know and what we don't. If it's safe, I make a guess or a small test and keep going. But I don't make big risky decisions alone.

Q: How do you work when requirements change during production?
A: I ask what changed and what matters most now. Then I check which work I can keep. If the change touches the prefab structure, animation states, Addressables or the release date, I tell the team early. The goal is to change without breaking what already works.

Q: What does end-to-end feature ownership mean to you?
A: I follow the feature from the first idea to the release, not just one step. I build it in Unity, add art and animation, check edge cases, watch speed and loading, and talk with the team. I don't do every kind of work, but I own the Tech Art part until it ships.

Q: How do you know when a feature is ready to hand off?
A: It looks like the task asked. The prefab and Unity setup are clean and easy to understand. All states and transitions work, it follows the project rules, and it doesn't slow down the game or loading. So another person can pick it up and keep working.

Q: How do you design a prefab so it can be reused for variants?
A: First I find the parts that stay the same - hierarchy, behaviour, shared links, animation, UI logic. Then I open only the parts that change - art, text, colours, data. One clear base plus a few controlled variants. Not copies that slowly drift apart.

Q: How do you avoid creating too many duplicated variants?
A: I check if the difference is real behaviour, or just data and looks. If the behaviour is the same, I reuse the prefab and change its settings or data. A copy is fast today, but in a live game every fix then has to go into every copy.

Q: How would you build UI that responds to real-time game state?
A: I keep the game state and the visuals apart. The game changes the data, the UI only shows it. I never hide game logic inside animations. The UI must always show the true state, even when taps come fast or events come in the wrong order.

Q: How would you integrate a new 2D asset into Unity?
A: First I find out how it will be used - UI image, world sprite, panel, animation or particle. Then I set the import settings: size, alpha, compression, atlas and platform. After that I check how it looks in the game and, if needed, how much memory and loading time it costs.

Q: How do you use Photoshop in a Technical Artist workflow?
A: I use it between the source art and Unity. I check layers, clean up assets, check size and transparency, and prepare files for the engine. Art problems I fix in Photoshop. Import and layout problems I fix in Unity.

Q: How do you approach optimization?
A: I don't guess. First I find the real problem with the Profiler — texture memory, UI batching, rendering, loading or animation. Then I make one focused change and measure again to see if it helped.

Q: How would you troubleshoot a UI screen that looks correct but performs badly?
A: I make the problem happen on the device and measure before changing anything. Then I check the causes one by one — Canvas rebuilds, batching, overdraw, layouts, animation. I change one thing at a time and keep it only if the numbers get better.

Q: What tool do you reach for first?
A: The Profiler on the device, not the Editor.

Q: What is important when working on mobile games?
A: Performance, memory, build size, loading time, and how it runs on different phones. I test on a weak device early, because a solution that looks fine on my PC can fail badly on a phone. I think about the cost while I add content, not after the game gets slow. But I only optimize real problems that I measured, and I keep the looks where they matter.

Q: How do you think about performance before a feature reaches production?
A: While I build, I watch for expensive things — big textures, copies of content, too many materials, heavy UI, extra effects, loading spikes. I don't optimize everything early, but I catch the big risks before the feature is locked in.

Q: How do you think about memory, size and loading together?
A: They are linked, but different. A small download doesn't mean low memory. And low memory doesn't mean fast loading. I ask what is loaded, when, for how long, how big it is, and if it really needs to be loaded all at once.

Q: How would you troubleshoot an Addressables content loading problem?
A: First I find out what kind of problem it is - wrong address, bad build or catalog, missing remote files, loading or memory. I repeat it with the same settings and the same content version and check what the game asks for. For remote content I also test missing files and a slow network, not only the good case.

Q: How do you investigate a visual or technical issue on your own?
A: I first make the bug happen consistently. Then I narrow it down layer by layer - source art, import settings, prefab or Canvas, animation, material, runtime state, loading and code. I change one thing at a time until I can explain the actual cause, not just make the symptom disappear.

Q: What does root-cause analysis mean to you?
A: I don't stop at the first fix. If a prefab is wrong because someone changed one value by hand, I ask why it happened and if other prefabs have the same problem. A good fix also stops it from coming back.

Q: How do you balance visual quality and performance?
A: I find what the player really sees and what really costs time. Then I pick the most practical low-cost fix - a smaller texture, a different effect, better loading timing, reuse, or cutting what nobody notices. I make the trade-off from profiling and visual comparison, not from guesses.

Q: How do you communicate technical trade-offs to non-technical teammates?
A: I don't start with technical words. I explain what changes for them — looks, loading, memory, risk, time. For example, "this looks better but is slow on weak phones; this looks a bit simpler but is safe". Then I give them the choice and explain the consequence of each option.

Q: How do you handle a disagreement between an artist and a developer?
A: I find what the artist wants to keep and what the developer wants to protect, like memory or easy code. Then I look for a way to keep the look at a lower technical cost. A quick test or profiler numbers work better than arguing.

Q: How do you deliver on time when the feature is still changing?
A: I split the work into must-haves and extras, and I make the big risky decisions early. I keep the setup simple and in small parts, and I tell people fast when a change hurts the plan. If time is short, I propose a smaller stable scope and agree on it with the team instead of silently cutting things.

Q: How do you prioritize when several things are urgent?
A: I first look at what can block the release or other people, then the user impact and the risk of waiting. If the priority isn't clear, I ask. I do the most important work first and say early if two urgent things can't both be done.

Q: How do you step into an existing pipeline and become productive?
A: I understand first, then change. I study how prefabs, folders, names, Addressables, UI and animation are set up, and I copy one or two good examples that already exist. I don't invent a new pipeline that the team then has to look after.

Q: How do you work in a shared project without breaking other people's work?
A: I learn the project rules first and keep my changes small and focused. I check my own changes before I hand them over. If I must touch shared parts, I tell the team early, not during review. Before handing it over, I run the affected scene or feature and check the files I touched.

Q: How comfortable are you with C#?
A: I'm not a full-time programmer, but I'm comfortable reading and writing C# when a Technical Art task needs it. My Flash and ActionScript background helps me understand code and communicate with developers. I mainly use C# for small tools, validation and automation.

Q: When would you build an editor tool instead of doing the task by hand?
A: I look at how often the task repeats, how often people make mistakes in it, and how hard the tool would be to keep working. A one-time task I do by hand. A weekly task with the same mistakes gets a small tool.

Q: How do you care about visual detail without slowing down production?
A: I separate visible quality problems from details that only I notice. If the player will notice it or it affects the feature, I fix it. Otherwise I check whether that polish is worth the time for this release. Good quality, but no endless polishing.

Q: What do you do when you do not know how to solve something?
A: I find out exactly what I don't know. Then I read the docs, look at examples in the project, or ask someone who knows. If I can, I make a small test. Saying "I don't know yet" is fine - finding the right answer fast is what matters.

--- PERFORMANCE ON MOBILE (asked most often) ---

Q: How would you find and fix a frame-rate drop on a low-end Android?
A: First a development build on the phone with the Profiler - I check if it's the CPU or the GPU. Then the biggest marker. If the Canvas is the spike, I look at what rebuilds and move the part that changes often to its own Canvas. If it's particles, I use fewer and smaller ones. If it's the GPU, I cut overdraw and heavy shaders. Then I measure again.

Q: How long does that usually take?
A: It depends on the problem. Finding the cause with the Profiler is usually the quick part. Fixing it properly and checking it on the phone takes longer.

Q: What frame budget do you target?
A: 16.6 milliseconds per frame for 60 fps, 33.3 milliseconds for 30 fps. I leave some room, because phones get hot and slow down. I look at the worst frames, not only the average.

Q: Why is profiling in the Editor not enough?
A: The Editor does its own extra work, and a PC is much faster than a phone. I use the Editor for iteration and debugging, but I don't treat its timings as final - for performance decisions I check on the target phone, especially a weak one. I also test a release build, because some problems show up only there.

Q: What creates garbage in UI code that people forget?
A: Building strings every frame, creating new lists, and some closures or LINQ in code that runs every frame. Looking up components or searching for objects every frame is a different problem - it is slow searching, not garbage - so I save the reference once. I update text only when the value changes.

Q: The frame rate is fine but the game feels stuttery. Why?
A: Some frames are much slower than the rest - garbage collection, loading or shader compile. The average FPS hides them. I look at the frame time graph to see the worst frames.

Q: How do you prove an optimization helped?
A: Same phone, same scene, same actions, before and after. I give numbers like 14.2 milliseconds down to 10.8 milliseconds. I also look at the worst frames.

Q: A popup opens with a visible hitch. What do you check?
A: I look at that frame in the Profiler to see what spiked - creating objects, texture upload, shader compile, layout rebuild, garbage. Then I fix the biggest one - pool or preload the popup, or prewarm the shader.

Q: Why test on a low-end device?
A: Problems show up there first. A typical weak phone gives me a safer starting point. But I still check the other device tiers, because the GPU, driver, OS and resolution can change the result. I also test long sessions, because phones slow down when they get hot.

Q: How do you balance quality and performance in a live game on many devices?
A: Quality tiers for low, mid and high. On weak phones: fewer particles, lower resolution, no post-processing. On strong phones: full beauty. I decide with numbers, not by eye.

--- SHADERS (Shader Graph, math, cost on mobile) ---

Q: How do you reduce shader cost on mobile without killing the look?
A: First I cut texture samples and heavy math. Then I switch from Lit to Unlit if the look allows it. The number of nodes is not the whole cost - what matters is what the graph turns into and how heavy that is on the phone's GPU. I use half where the precision is enough, because it can make the shader cheaper on mobile GPUs. If a calculation can move to the vertex shader without changing how it looks, I move it, so it isn't done again for every pixel. I keep keywords low, because each combination builds a separate variant. Then I measure on the real phone to see if it helped.

Q: What breaks SRP Batcher compatibility?
A: If the shader isn't written to be compatible, or if a per-object property override is put on the renderer, it falls out of the batcher. You can see in the shader Inspector if it is compatible.

Q: How do keywords affect batching?
A: Each keyword combination is a different shader variant. Two materials with the same shader but different keywords won't batch together. So fewer keywords means more chances to batch.

Q: shader_feature or multi_compile?
A: shader_feature when the option is set on the material - variants that no material uses are removed from the build. multi_compile when code switches it while the game runs - all combinations are built, so the build grows fast. The trap is a shader_feature keyword that I turn on from C# at runtime: if no material used it at build time, that variant can be stripped. So if I change a keyword at runtime, I make sure the needed variants are kept - with multi_compile or a variant collection. I think about what really needs to be compiled.

Q: What does a magenta or cyan object mean?
A: Magenta is the error shader - the shader is missing, broken, not supported on that platform, or it is a Built-in shader in URP where it doesn't work. In the Editor, a cyan placeholder can appear while a shader is still compiling. If it's pink only on the phone, a missing or stripped shader variant is one possible reason. I would also check if the shader is supported, look for compile errors, and read the player log, instead of just guessing it was stripped.

Q: A shader variant freezes the game on first use. How do you avoid it?
A: I prewarm the needed shader variants during loading, so the first use is less likely to freeze. I still profile on the phone, because DX12, Vulkan and Metal can need extra work from the driver.

Q: Sprite-Lit or Sprite-Unlit?
A: Sprite-Lit is for sprites that need the project's 2D lighting. Sprite-Unlit ignores lighting and is good for world sprites and effects that don't need 2D lighting. I choose by what the art needs and what it costs when I measure.

Q: How do you animate a material without breaking batching?
A: I animate one shared value or use shader time, maybe with a small difference per object in the vertex colour for variety. A per-object property override in URP can take the object out of the SRP Batcher, so I try to avoid it.

Q: What if I need per-object material animation?
A: I use vertex colour or the object's position instead of a per-object property override. If that doesn't work, I accept the lost batch and measure if it matters.

Q: How do you make a dissolve effect?
A: A noise texture is compared with a threshold - pixels below it disappear. A thin bright band right at the threshold looks like burning or a glowing edge. Moving the threshold from 0 to 1 dissolves the object.

Q: How do you make a UV scroll for water or energy?
A: I move the UVs by time multiplied by speed and repeat the texture. Two layers moving at different speeds look much richer than one.

Q: What is a Shader Graph Sub Graph for?
A: For reusing a group of nodes across many graphs, like dissolve or UV scroll. When I fix it once in the Sub Graph, it updates everywhere it's used.

Q: If a shader is slow on one phone only, what do you do?
A: I profile the GPU on that phone and capture a frame if needed. The Frame Debugger shows me the draw calls, the shader and the render state. For the real shader cost I use GPU timing or a GPU frame capture tool. Then I make the math simpler, use half, or move work from the fragment shader to the vertex shader, and measure again.

Q: How do you prioritize which optimization to try first?
A: I look at how many pixels are drawn. If the phone has a high resolution or particles overlap, overdraw comes first. If not, I look at the math per pixel.

Q: Is alpha clipping cheaper than transparency?
A: Not always. Throwing away pixels can block some GPU speed-ups and can cost more, depending on the GPU and the effect. So I measure both on the phone and pick the one that is really faster.

Q: What is the dot product and where do you use it?
A: It's a number that says how much two directions point the same way: 1 means the same direction, 0 means a right angle, -1 means opposite. I use it for lighting (normal and light direction), for a rim around an object (normal and view direction), and for masks based on angle.

Q: What is the difference between a vertex and a fragment shader?
A: The vertex shader runs once per vertex, the fragment shader roughly once per drawn pixel. There are many more pixels, so any smooth calculation that can be blended between vertices I move to the vertex shader.

Q: When half and when float?
A: half for colour, directions and small numbers when its precision is enough - on phones that support it, it can make the shader cheaper or save power. I don't assume it is faster; I check it on the target GPU. float for values where half is not precise enough and you can see it - big world positions or big growing coordinates - because then the image crawls or shakes.

Q: When do you write HLSL instead of Shader Graph?
A: When I need exact control over cost, custom lighting, or to port an old shader. Otherwise Shader Graph, so others can edit it. But I must be able to read simple HLSL to see what is expensive.

Q: Make a dissolve in 5 minutes in the interview - how?
A: A noise texture goes into Step or Smoothstep with a Dissolve Amount slider - that result becomes the alpha, with Alpha Clipping on so the pixels below the threshold are thrown away. For a glowing edge I add a thin band near the threshold, multiply it by an edge colour, and add it to the output colour. I expose the threshold, edge width and colour as parameters.

--- RENDER PIPELINE: BUILT-IN, URP, HDRP ---

Q: Which pipeline and why?
A: URP with the 2D Renderer. It's light for phones, has 2D sorting, Shader Graph and the SRP Batcher. Built-in is the older pipeline; for a new mobile project I would normally choose URP. HDRP is not made for phones. For a live project that already uses Built-in, I would first look at how much the move costs.

Q: Forward or Deferred for a mobile 2D game?
A: For a normal mobile 2D project I would start with Forward. Deferred needs a G-buffer, extra bandwidth and memory, so I would choose it only if the project really gains from its lighting. A 2D game rarely needs dozens of lights per pixel anyway.

Q: Everything is pink after moving to URP. What do you do?
A: First I check whether the materials still use Built-in shaders - that's the most common reason. Then I run the Render Pipeline Converter and remake custom shaders in Shader Graph. I also check that the URP asset is set in Graphics and Quality settings, and that the shaders are compatible.

Q: Why can you not drop the 2D Renderer into Graphics settings?
A: Graphics settings take a pipeline asset like UniversalRP. The 2D Renderer is a renderer inside that asset - it goes into UniversalRP's Renderer List, in the asset itself.

--- DRAW CALLS AND BATCHING ---

Q: How do you reduce draw calls?
A: Atlases per screen, shared materials, a draw order that avoids texture switches, and the SRP Batcher for world objects in URP. I step through the Frame Debugger and compare calls next to each other to see what changed.

Q: How do you find the biggest win?
A: I step through the Frame Debugger and look at what changes between calls - material, texture, shader pass or keyword, sorting, masking. If it's texture switches, I change the draw order or use atlases.

Q: What is the difference between static batching, dynamic batching, GPU instancing and the SRP Batcher?
A: Static batching joins meshes that don't move at build time. Dynamic batching can join some small meshes, but Unity today doesn't recommend counting on it. GPU Instancing draws many copies of the same mesh and material in one instanced draw call. The SRP Batcher makes each draw call cheaper for the CPU, but doesn't cut the number of calls, and it matters most for compatible mesh-based rendering. For 2D sprites the main tools are Sprite Atlases, shared materials and draw order.

--- TEXTURES AND COMPRESSION ---

Q: Which compression format for iOS/Android and why?
A: The modern compressed format that most phones support, because it usually gives a good balance of quality and size. I pick the compression strength by how important the asset is - higher quality for UI and text, stronger compression for soft shadows - and an older format as a backup for devices that don't support it. And I compare the result on a real phone.

Q: What if compression makes one asset look bad?
A: I lower the compression for that asset: it keeps more detail but uses more memory. I measure if less compression or a smaller texture is the better answer.

Q: Why not one big atlas for the whole game?
A: A sprite atlas packs sprites into one texture, so loading the atlas can bring sprites you don't need into memory with the rest of it. That's why I usually split atlases by screen or feature, especially for content that is not used at the same time.

Q: When does a sprite not batch even in the same atlas?
A: When it uses a different material, or when something else with another texture is drawn between them. Sorting order matters, not just being in the same atlas.

Q: How do you plan atlases for a screen?
A: I group sprites by usage - what is shown together on the same screen goes together, and I keep UI apart from world art. Then I think about loading and memory: when any sprite from an atlas is needed, the whole atlas texture is in memory, so I don't put a rarely used popup into the atlas of the main screen, and content that loads remotely, like one island, gets its own atlas. For batching, sprites that draw one after another should share an atlas, otherwise the texture switches between them. Compression is a separate decision: I choose it per atlas by how important the art is visually and by the platform, and I check the result on the phone.

Q: Why turn off Read/Write and mipmaps?
A: Read/Write keeps an additional CPU-accessible copy of the imported texture data, which increases memory use. So I turn it off when no code needs to read the pixels. A full mip chain adds about one third more texture memory, so I usually turn mipmaps off for fixed-size UI. World sprites that get much smaller on screen can still need them.

Q: Why keep source art uncompressed when using an atlas?
A: The source sprite is my master quality. For sprites packed into an atlas, the atlas controls the final packed texture and its compression, so I keep the source clean and let the atlas and platform settings control the final compression. That gives me one place to judge the final quality and avoids unnecessary quality loss before packing, and I check the final atlas on the phone.

Q: How do you slice a sprite sheet?
A: Sprite Mode Multiple, then the Sprite Editor with automatic or grid slicing. When the sheet changes, I recheck the slices after reimport and make sure prefabs and sprite links still point to the right sprites, instead of just hoping they do.

Q: How do you set a sprite pivot and why does it matter?
A: I set it in the Sprite Editor. The pivot is the point used for position, rotation and scale, and it can also be used as the Sprite Sort Point. For standing objects I usually put it at the bottom, so Y-sorting uses the character's feet.

Q: What does Sprite Atlas "Include in Build" do?
A: On: the atlas is part of the build. Off: it is not included through that setting, so if I want the atlas to arrive later, I need another delivery path, such as Addressables or late binding.

Q: A sprite has a thin line or halo at its edge. How do you fix it?
A: I first check for colour bleeding from neighbouring sprites or transparent pixels. Then I check atlas padding, Alpha Is Transparency and the source edges, and compare the result on the device.

Q: The artist gives you a PSD with 200 layers. What do you do?
A: We agree which layers must stay separate, because they move or change in the game. Everything else merges into fewer sprites. That can save some asset and draw-call cost, but texture memory mostly depends on the final packed textures - their size, pages, compression, mipmaps and Read/Write.

Q: The artist wants a 4096 texture for a small icon. What do you say?
A: I show it at real size on a phone next to a 512 version. If nobody sees a difference, we save the memory. If they do, we pick a size together.

Q: How do you decide texture resolution for different devices?
A: I choose Max Size from how big the asset really is on screen and how good it must look, not from the PSD size. For weak phones I can use smaller versions through quality tiers or separate Addressables variants, depending on the project's pipeline. Then I check on a weak phone if anyone can even see the difference.

--- PARTICLES AND VFX ---

Q: A big explosion lags on weak phones. First three steps?
A: Fewer particles and a shorter lifetime, smaller particles to cut overdraw, and one shared material. Then I crop the texture tighter and measure again.

Q: How do you make a particle burst for a reward?
A: Emission with one Burst, a short lifetime, and Size and Colour over Lifetime for the pop and the fade. When it ends, I decide what happens: Stop Action can disable or destroy the object, or a callback can return it to my pool if the reward plays often.

Q: What does Simulation Space do?
A: Local moves the particles with the parent, World leaves them in the world. World is useful for smoke or trails that should stay where they were created while the emitter moves.

Q: How do you keep particle effects cheap on mobile?
A: Few systems, one shared unlit material, low Max Particles, little overdraw, and no unnecessary lights or collisions. For effects that don't need to keep simulating off-screen, I use a culling mode that lets them pause when they're not visible.

Q: How do you decide how many particles is too many?
A: I measure the effect on the weakest phone together with the rest of the screen. For transparent particles overdraw is often the big limit, but I also check the particle simulation time and measure both CPU and GPU cost.

Q: What if an effect must be very big for one moment?
A: I make it short and keep other effects quiet at that moment. Sometimes fewer larger particles give the same impact, but bigger particles can mean more overdraw, so I check it. Then I test that exact frame on a weak phone.

Q: Why use Prewarm?
A: Prewarm starts a looping effect as if it has already been running for a while, so the first frame looks full, not empty - like smoke from a chimney. I use it when the effect must look like it was always there.

Q: How do you pool particle effects, and what goes wrong most often?
A: When the effect ends, Stop Action set to Callback tells my pool code, and it puts the effect back in the pool. I reset it when I take it out again. Common bugs: using an effect that is still playing, returning it twice, or old colour and scale left over. If Stop Action is Destroy, that effect is destroyed instead of being returned to the pool, so I use Callback for pooled effects.

Q: What do you check if a particle effect does not appear?
A: Is it playing and on screen? Sorting layer and order, material and shader, Max Particles and emission. I also check the camera's culling mask and the Simulation Space.

Q: How do you sort particles with sprites in 2D?
A: The particle renderer has Sorting Layer and Order in Layer, like a sprite. If particles must draw in a clear order with world or camera UI, I choose the Canvas render mode and the sorting on purpose. With a Screen Space - Camera Canvas, I can use sorting layers and camera settings to put particles in front of or behind the UI.

Q: Particle System or VFX Graph?
A: For a typical mobile 2D project I'd start with the built-in Particle System, because it's the simpler and more widely applicable choice. VFX Graph is made for particles simulated on the GPU. I check the Unity and package version, the renderer and the target devices first, because VFX Graph's mobile support and requirements depend on that setup.

Q: What are the most common VFX performance problems on mobile?
A: Overdraw from big transparent particles, too many particles, a different material for every system, and effects that keep running off screen. I fix them with size, count, one shared material, and Culling Mode.

Q: How do you determine whether a particle effect is CPU-bound or GPU-bound?
A: I compare the CPU and GPU frame time first. If the particle simulation is heavy on the CPU, I use fewer particles or fewer heavy modules. If the GPU is the problem, I look at particle size, overdraw, transparency, and how many effects overlap.

Q: Why can fewer particles still be slower than more particles?
A: The number of particles alone doesn't tell me the GPU cost. Big transparent particles can cover a lot of the screen and cause heavy overdraw. So I look at both the simulation cost and how much of the screen they cover.

Q: When would you use a Sub Emitter in a particle effect?
A: When a second effect must start at the exact place and moment of a particle event - birth, collision or death. For example a firework rocket that bursts into sparks where it dies, with Inherit Color so the sparks match. The timing stays inside one effect, and I don't need code to spawn and place another Particle System.

Q: Walk me through building a construction dust effect in the Particle System.
A: In Main I set a short Duration, Looping while the building is under construction, about one second of lifetime, low speed and a small random size. I keep Max Particles low. Then I use a small Emission rate, maybe with a Burst at the start, and a Box or Edge Shape along the building base, so the dust comes from the ground. Velocity over Lifetime pushes it up, Size over Lifetime grows it, and Color over Lifetime fades the alpha, so it disappears softly. In the Renderer I use one shared soft dust material and set the sorting between the ground and the building. Then I test it on the phone and reduce size or count if the overdraw is too high.

Q: How would you create a simple firework trail in the Particle System?
A: I turn on the Trails module, give it its own material, and keep the trail short with Lifetime and Width over Trail. Trails add extra geometry and cover more screen, so they add overdraw - I keep few of them and check the cost on the phone.

--- UI (Canvas, uGUI, TextMeshPro) ---

Q: How do you optimize a complex UI screen on mobile?
A: First I profile the screen on the device, to see if UI rebuilds are really the cost - for example if UI rebuilds take a large part of the frame. If a large Canvas rebuilds because of one element that changes often, like a timer, I move that dynamic part to its own Canvas, so the static part is left alone. I use shared atlases, and I turn Raycast Target off on decoration, because extra raycast targets mean extra work. Then I look for full-screen transparent panels and heavy Layout Groups - they are common problems.

Q: How do you set up a Canvas for a portrait mobile game?
A: First I use the Canvas Scaler with Scale With Screen Size and a reference resolution like 1080 by 2400. Then I choose the Match value for the portrait layout. I start with a balanced value and adjust it after testing different aspect ratios, rather than assuming one value works for every phone. I put the buttons inside a Safe Area root, so they don't hide under the notch. Then I test on the narrowest and the tallest phones I can find.

Q: What is the difference between Content Size Fitter and a Layout Group?
A: Content Size Fitter changes its own size to fit its content - for example a label that grows with its text. A Layout Group controls the position and size of its children. I avoid setups where both try to control the same size on the same axis, because then they fight over it.

Q: Why can a big Canvas be slow?
A: When a UI element changes its look, layout or material, Unity has to redo some UI work before drawing. On a big Canvas, changes that happen often can make that work expensive - especially a timer or a value that updates every frame or every second. So when the Profiler shows rebuild cost, I put the often-changing UI apart from the UI that doesn't change.

Q: You split Canvases. How many is too many?
A: Each Canvas batches and rebuilds on its own. Splitting can cut rebuild cost, but it can also add more batches and draw calls - so more Canvases is not free. I split by how often things change: the static background, the ticking timers and counters, and each popup - and only where the Profiler shows a real rebuild cost.

Q: What exactly causes a Canvas rebuild?
A: A UI change marks a part of the element as dirty - its vertices, its material or its layout - and Unity redoes only that kind of work. Changing text or size makes new geometry, swapping a sprite or material changes the material, and changing size inside a layout makes the layout run again. The Canvas then has to rebuild its batches. The expensive case is elements that change often and make a lot of geometry, layout or batching work on a big Canvas. Moving an object that is not in a layout is usually cheaper, but still not free.

Q: What makes a UI button not react to clicks?
A: First I check if there is an EventSystem in the scene - buttons need it. Then I look for a Graphic Raycaster on the Canvas. If Raycast Target is off on the button, taps go through it. An invisible Image on top can catch the tap instead. If the project uses the new Input System, I also check that the EventSystem has the InputSystemUIInputModule configured correctly.

Q: Why is Graphic Raycaster a cost?
A: The Graphic Raycaster raycasts against the Graphics on its Canvas that have Raycast Target on, so I turn it off on decoration to cut extra work. I also remove the Raycaster from Canvases that don't take input. If the whole background must be tappable, I use one invisible target instead of making every image tappable.

Q: How do you handle the notch on phones?
A: I use a Safe Area root that follows the safe area of the screen. The top and bottom bars sit inside it, so they stay away from the notch. Backgrounds can still stretch under the notch, edge to edge. I don't shrink the whole Canvas just to handle the notch, because that wastes screen space.

Q: How do you fade a whole popup?
A: For my UI animations I usually animate the color alpha of the Image or TextMeshProUGUI. If I need to fade and control the whole popup at once, CanvasGroup works too. While the popup is hidden I also turn off its input, so the player can't tap it by accident.

Q: How do you make a popup Show and Hide?
A: For Show I scale up from small and fade in at the same time, with a small overshoot, about 0.3 to 0.5 seconds. Hide is the reverse but faster, about 0.2 seconds, with no overshoot. These timings are a design choice from the reference, not a Unity rule. I block input while the animation plays.

Q: How do you make a scroll list with many items fast?
A: Instead of creating 500 item objects, I reuse a few item views and move them as I scroll. I use RectMask2D and put the list on its own Canvas. So only a few item views are active instead of 500 - the data and the scroll logic still cost something, but much less.

Q: How do you handle item pooling?
A: I keep a pool of, say, 10 item views. As I scroll, the views that leave the top get new data and come back at the bottom.

Q: How do you show a timer that updates every second without unnecessary UI cost?
A: I update the text only when the number really changes, not every frame. I put the timer on its own small Canvas, so its rebuild work stays isolated from the rest of the screen.

Q: What if the timer needs to show milliseconds?
A: Then it changes every frame, and I still put it on its own Canvas. The main idea is to keep what changes fast apart from what changes slowly.

Q: What if a Layout Group is slow?
A: Layout Groups recalculate when the layout changes - for example when children are added, removed or resized. For a layout that never changes, I let it calculate once and then turn it off, or I use anchors. For long lists I reuse item views.

Q: How do you animate UI without breaking layouts?
A: I animate something inside the layout element, not the element the Layout Group controls. For example, I animate a child Image inside the item instead of the RectTransform that the Layout Group positions. If I animate the element itself, the Layout Group resets it on every rebuild and fights the animation.

Q: Why should UI shaders use vertex color?
A: Image color and CanvasGroup alpha come to the shader as vertex color. If the shader doesn't read vertex color, normal UI tinting and alpha fades stop working. A good UI shader also supports masks.

Q: How do you keep UI in sync with game data?
A: The UI reads from one data source, or listens to events. It never owns the data. When the data changes, the view updates. So every screen can be built again from the data at any time, like after a reload or a tab switch.

Q: Why can many TextMeshPro material presets increase UI complexity?
A: Different material presets can split UI batches, because they are different materials. I try to reuse TMP materials and make a new preset only when the look really needs one.

Q: How do you build UI and TMP text so it survives localization?
A: I leave room for longer translations. Text boxes can grow, or I use Auto Size with sensible min and max, instead of fitting each label to the English text. I keep strings out of prefabs with the Localization package or our own string tables. For Arabic or Hebrew I check RTL and complex scripts early. I also watch the font atlases, because extra fallback fonts add memory and different materials can add batches.

Q: How would you implement a reward icon flying from a world object to a UI counter?
A: I take the world position of the object and turn it into a screen position with the world camera. Then I turn that screen point into the local space of the target RectTransform. That step depends on the Canvas Render Mode: for Screen Space - Overlay I pass no camera, and for Screen Space - Camera or World Space I pass the Canvas camera. The icon flies along a short curve to the counter, and when it lands the counter punches and updates its number. I make it one reusable effect that gets the start, the target and the icon, so stars, coins and energy all use the same code, and I pool the icons.

Q: How would you build a reusable UI component library?
A: I would start with a small set of stable components: buttons, panels, counters, popups and list items. Each one gets a clear API and predictable states - normal, pressed, disabled - and controlled variants instead of copies. Visual settings like colours, fonts and sprites stay reusable, so a screen is built from components instead of copying the same UI structure again. Then I would test the components on real screens and keep a short guide, so new screens use them the same way.

--- 2D WORKFLOW: SPRITES, IMPORT, SORTING ---

Q: How do you configure sprite import for a 2D mobile game?
A: I set the Texture Type to Sprite. One PPU value for the whole art set keeps sizes the same. I put the pivot where it needs to turn from - the center for most things, the bottom for characters. I pick Max Size from the real size on screen and how good it must look, not from the PSD size. I turn off mipmaps and Read/Write for most things. For sprites in an atlas, the atlas settings decide the final texture and its compression.

Q: How does 2D render order work?
A: For normal 2D work I first control the order with Sorting Layer and Order in Layer. When those are equal, Unity's other transparent-sorting rules, like the render queue, the distance and the Custom Axis, can decide the final order. In practice I control it with Sorting Layer, Order in Layer, Sorting Group and, when needed, Custom Axis sorting, and I check the real order in the Frame Debugger. A Sorting Group lets an object made of many sprites sort as one.

Q: How do you sort sprites by Y?
A: In URP 2D I set Transparency Sort Mode to Custom Axis (0, 1, 0) on the Renderer 2D Data. All the sprites use the same Sorting Layer and Order in Layer. Sprite Sort Point is set to Pivot, and the pivot is at the bottom of each sprite.

Q: When would you use Transparency Sort Mode instead of setting Order in Layer by hand?
A: If objects should sort by their position in the world, I let Unity's 2D sorting do it instead of changing Order in Layer every frame. Manual sorting is useful for special cases where the normal world-space sorting rule isn't enough. If I do it by hand, I avoid recalculating the order every frame unless I really need that custom behaviour.

Q: What problem does SortingGroup solve in a 2D game?
A: SortingGroup makes several SpriteRenderers sort as one object. I use it when a character or an object is made of many sprites that must keep their order inside, while the whole object sorts against other objects.

Q: What does Sort At Root do?
A: It lets a SortingGroup inside another SortingGroup sort at the top level, not only inside its parent. I would use it for something like a marker that belongs to an object but must draw above other objects.

--- 3D ASSETS (integration basics) ---

Q: How do you integrate a 3D model into Unity?
A: First I check the source scale, orientation and polygon complexity. Then I check the model import settings - scale factor, axes, normals, materials, textures and animations. After that I put it into a prefab, check its bounds and how it looks under the project's lighting, and profile it on the target device. I don't optimize the model blindly - I measure where the real cost is.

Q: What do you check when a 3D model looks wrong in Unity?
A: I check the import scale and axes first, then normals, materials, textures and shader compatibility. If the model is pink or too dark, I look at the material and shader. If the animation or the bounds are wrong, I check the rig, the root and the imported animation settings.

Q: How do you optimize a 3D asset for mobile?
A: I look at the polygon count, the number of materials, texture size, shader cost, and whether the object really needs shadows or expensive lighting. I try to cut the expensive parts without changing what the player actually sees - for example fewer materials through a shared texture, or a lower LOD when it's small on screen. Then I profile it on the target phone.

--- ANIMATION (Animator, tweens, 2D skeletons) ---

Q: How do you make an animation clip by hand, step by step?
A: I select the object, open the Animation window and create a new clip. If the object doesn't have an Animator setup yet, I set that up first. Then I press Record and set keys. For a pop I put scale 0 at the start, about 1.1 a little later, and 1 at the end, so it overshoots and settles. I animate only what the clip really needs - usually scale, position and colour alpha - because every animated property is extra work, and properties that change the layout can cause UI rebuilds. In the clip settings I turn Loop Time on only for idle loops, and off for one-time moves like show or hide. At the end I check the curves, so the motion eases in and out instead of moving at a flat speed.

Q: How do you set up the states for a building - available, under construction, built?
A: One base controller with one state per look: Available, Construction, Built, plus short clips for the moments between them, like the completion pop. The game code decides which state the building is in and sets a parameter - a Trigger like Build for a one-time event, or an Int or Bool setup for the lasting state, depending on how many stages the feature has. For a reaction to a tap I turn Has Exit Time off and keep the transition short, so it doesn't feel late. Where the next state should start only after a clip ends, like the pop going into the Built idle, I leave Exit Time on. I put this in the base prefab, so every variant gets the same states, and the animation only shows what the game already decided.

Q: When do you NOT use the Animator for UI?
A: For small one-time UI moves I usually prefer a tween, because it keeps the animation simple and I don't need a state machine for it. An Animator can also keep evaluating its state while the object is active, so if it changes UI values that affect layout or appearance, it can add unnecessary work. So for small one-time moves I use a tween, or I turn the Animator off when the clip ends. For UI with real states, like a popup with show, idle and hide, the Animator is fine.

Q: How do Animator parameters work?
A: There are four types: Float and Int for values, Bool for a lasting state, and Trigger for a one-time transition. Code changes them, for example with SetTrigger. A Trigger is consumed by a transition, while a Bool stays until I change it.

Q: Trigger or Bool?
A: Bool for states that last, like IsOpen or IsMoving. Trigger for one-time actions, like Show or Build. If several transitions can happen close together, I keep the state logic clear - often with Bools - instead of firing many triggers in the same frame.

Q: Why do Animator transitions sometimes feel late?
A: If Has Exit Time is on, the transition waits for the current clip to finish. Or the transition itself is slow. For an instant reaction to a tap, I turn Exit Time off and use a short transition, like 0.1 seconds.

Q: How do you show a UI animation while the game is paused?
A: When the game is paused, timeScale is 0, so normal animations stop. I set the Animator Update Mode to Unscaled Time, so it ignores timeScale. For particles, I also set their simulation to use unscaled time if I want the effect to continue during the pause. Then they keep playing while the game is frozen.

Q: Animator or code for a counter that rolls up numbers?
A: Code or a tween, because the number comes from data and I need to control when it changes. The Animator can do the punch or scale around it. Each tool does what it is best at.

Q: How do you sync a sound or VFX with an animation?
A: I put an Animation Event on the exact frame where the sound or effect should start. For precise sync I prefer an Animation Event or an explicit state change, instead of waiting for a value like "rotation equals 90" - Unity can skip that exact value between frames.

Q: What should an animation never decide?
A: An animation should never decide game logic. It should never check if a purchase worked or give a reward. The animation only shows what already happened. If important logic depends on an animation event, interrupting the animation can stop that event from firing.

Q: How do you handle an animation that must stop on the last frame?
A: I turn Loop Time off so the clip ends on its last frame, and I make sure no transition moves the object away if it must stay there. For something visual, like a sound or a sparkle, I can put an Animation Event on that frame - but important game logic stays in code and state. A reward or a purchase never waits for an animation to finish.

Q: When do you use Timeline?
A: I use Timeline for one-time sequences with many objects and exact timing - like an intro, a reward sequence, or a level complete screen. If something has states that switch back and forth, I use the Animator instead.

Q: Bones (2D Animation) or frame-by-frame - when which?
A: 2D Animation (bones) lets me rig a character, so one skeleton drives many animations. It comes from the 2D Animation package and uses bones and Sprite Skin; how the deformation runs can be set up for the project and target platform. Frame-by-frame is good for short stylized moves, but a large number of unique frames can increase texture memory and atlas size.

Q: What happens if an Animator and a script both modify the same Transform property?
A: They fight, because both try to control the same value. I want one clear owner for each animated value. For example, the Animator moves the object's local position, while a parent object does the big movement.

Q: When would you use AnimatorOverrideController instead of one shared Animator Controller?
A: When several objects use the same state machine - the same states, transitions and parameters - but need different clips. The override controller keeps the logic in one place and only swaps the clips, so I don't copy the controller for every item. If the variants only differ in sprites and the clips animate the same paths, one shared controller is enough.

Q: What is Write Defaults in the Animator, and why can it cause unexpected behaviour?
A: With Write Defaults on, a state writes default values for things it doesn't animate itself. So when I switch states, a value that another state animated can jump back to its default - for example a UI element that suddenly resets its alpha or scale. I keep the setting the same across one controller, and I check it when values jump between states.

--- ADDRESSABLES AND REMOTE CONTENT ---

Q: How would you build Addressables for a live game with many events?
A: The core game stays inside the app. Events and islands go into remote groups when they work with the released app. I would usually start with a separate remote group per event or island, then adjust the grouping based on dependencies, update frequency and download size. Shared things like fonts or UI sprites get their own group. I use a remote catalog, so compatible new content can arrive without a new app build. I keep the handle of every load and release it when that content is not needed anymore.

Q: How do you handle a bad update?
A: If new remote content breaks the game, I would roll back the remote catalog and content to the last good version, if our hosting and versioning allow it, and stop giving out the bad content. Then I fix it.

Q: The build is too big. Where do you start?
A: I use the Build Report to find what takes the most space first. Textures are often big, but I don't guess before I measure. Then I fix the biggest contributors: if it's textures, compression and max size; if it's unused or duplicated content, I remove it; and optional content can move to remote Addressables. Then I build again and compare.

Q: Memory grows every time a player opens a screen. What is it?
A: It can be a leak, but not always - it can also be a cache or lazy loading. Common leaks are Addressables without Release, GameObjects not destroyed, or event listeners not removed. I take a Memory Profiler snapshot before opening the screen and one after, and compare them to find memory that should be gone - then I follow the references to see why it stays.

Q: How do you use the Memory Profiler?
A: I take a snapshot, do the action, like opening a screen, take another one and compare. I look for objects or assets that should have disappeared and inspect what still references them. I also separate real leaks from expected caches or assets that are intentionally kept loaded. The Profiler also shows if the growth is textures or script memory.

Q: How do you find what is holding a reference?
A: In the Memory Profiler I select the object and look at what still references it in the snapshot, to see what keeps it alive. Then I check that owner in the code.

Q: Why can Destroy not free memory right away?
A: Destroy removes the object, but an asset can stay loaded if something else still uses it. With Addressables I release the handle, and Unity can unload the bundle once nothing needs it. For Resources and other assets, unloading unused assets is a separate step - and heavy on the CPU, so I call it at safe moments, like a loading screen.

Q: How do you load a scene without freezing?
A: I load the scene asynchronously, and with Addressables where it fits, so the loading doesn't block the game, and I show a loading screen. I still profile the scene start, asset loading and any spikes on the main thread, because async loading doesn't make every part of loading free.

Q: How would you split Addressables groups?
A: I split by when the content is needed and how often it changes. I start with the core content that the first session needs locally. Features and optional islands can go into remote groups. Shared assets get their own group when that reduces duplication. That way a player only downloads what they use.

Q: How do you release memory from Addressables?
A: I keep the load or instance handle and release it with the matching Addressables release method when the content is not needed anymore. A bundle unloads only when nothing uses it, so I keep track of the handles.

Q: What is the difference between Cannot Change Post Release and Can Change Post Release?
A: Cannot Change for content that should stay the same - if an asset changes, it can move into a new small update group, and the old bundles stay valid. Can Change - a changed asset can make its whole bundle rebuild, and how much players download depends on how the group is packed.

Q: How do you check Addressables duplicates?
A: I run the Analyze tool and look for assets duplicated across bundles. Shared dependencies can be pulled into several bundles depending on the group structure, so I give truly shared content a clear owner group where that reduces duplication.

Q: How do you ship a content update?
A: I use "Update a Previous Build" with the content state file from the old release. It builds an update that tries to keep what players download small, and bundles that didn't change can stay as they were - the real size depends on how the groups are packed and on the update settings. I save that state file with every release, so I can update from it.

Q: How do you test remote content before release?
A: I set up a local server or a test profile, build the content, and run the game against it. I test the normal case, updates, and the bad cases - missing files, slow network, starting offline.

Q: What if Addressables loading fails on a bad network?
A: I catch the failed load and show a retry button. If local content exists, I use that instead. I don't leave the player on a frozen screen: I show a loading or retry state, handle the error, and release the failed handle when it makes sense.

Q: What if a player has an old catalog and new code?
A: The important rule is that remote content must stay compatible with the code already installed on the phone. If new code needs new content, it comes with an app update, or the code checks the content version first and refuses it if it is too old.

Q: What happens if a scene directly references an asset that is also placed in a remote Addressables group?
A: The scene reference can pull the asset into the build through the scene, and the Addressables build can also put it into the remote bundle. Then the content is there twice, or there are dependencies nobody expected. I use Addressables Analyze to find duplicates and make sure every asset has one clear owner.

--- PROFILER AND FRAME DEBUGGER (often a live test) ---

Q: Here is a Profiler - where is the bottleneck?
A: I don't decide the bottleneck from one marker. I look at the Main Thread and the Render Thread together, at the wait markers, and at the GPU timing and the frame time. A wait for the GPU can mean the GPU is slow, but it can also be VSync, so I check it together with the rest. Then I find what takes the most time. For example: "The main thread is slow, UI rebuilds take the most time, so I would look at what is rebuilding and move the part that changes often to its own Canvas."

Q: What if the GPU is the bottleneck?
A: I look for heavy shaders, overdraw, or too many particles. I may use fewer particles, smaller textures, or make the shader simpler.

Q: A screen looked fine in the Editor but is blurry on the phone. Why?
A: Usually it's the texture Max Size or the compression for that platform. A wrong Canvas Scaler can also make it blurry. Or a sprite is scaled up bigger than its real size. I check the platform texture settings first.

Q: Text looks different on the device than in the Editor. What do you check?
A: I check the font asset first, and its fallback fonts - they can have a different height. I check for missing letters. The Canvas Scaler can also change how text looks. Then I check it with my own eyes on a real phone.

Q: What do you check first when a sprite looks wrong in the game?
A: I go step by step. Source art first. Then the import settings: slicing, pivot, PPU, compression. Then the prefab, animation, shader, and the state while the game runs. Turning systems off one by one shows which one is the problem.

Q: How do you find where an error comes from in a build?
A: I check the device logs and stack traces with the Android and iOS developer tools. The Editor Console is not the main place to inspect logs from a device build.

--- PREFABS AND VARIANTS FOR LIVE EVENTS ---

Q: How do you avoid a memory explosion with hundreds of event variants?
A: First I check what takes the most memory: textures, atlas pages or copied content. Where I can, I reuse shared sprites and materials instead of making copies. Each event gets its own remote Addressables group, and I unload it as soon as the event ends. If the shader has a colour parameter, I reuse the same texture and change only the material data - and I still check what that does to batching and memory.

Q: What happens if you rename a child that is animated?
A: Animation is linked to objects by their path in the hierarchy, so renaming or moving an animated child can break that link. You may not notice it right away, so after I change the hierarchy, I check the clips. That's why I rename first and animate after.

Q: When do you use ScriptableObjects?
A: For shared data that many prefabs need: item lists, prices, rewards, tuning numbers. One ScriptableObject can feed dozens of prefabs. Designers can change values without touching code or scenes, and there's one place to look.

Q: What happens if you delete a .meta file?
A: Unity creates a new GUID for the asset, which means every link breaks. Sprite slices stored in the .meta are also lost. That's why I always keep the .meta together with its asset.

Q: When do you use object pooling?
A: For things I create all the time: coins, bullets, reward effects, items in big lists. Reusing them avoids lag spikes from creating and destroying objects. A menu that shows up once or twice doesn't need a pool.

Q: How do you reset a pooled object when it's reused?
A: I reset its state myself, and I unsubscribe from events when it goes back to the pool. The moments when the object is turned on and off are good places for that cleanup, but they don't reset the object by themselves.

Q: What is the difference between Destroy and SetActive(false)?
A: SetActive(false) only hides the object - it stays in memory, ready to use again. Destroy removes the GameObject from the scene, but the assets it used can stay loaded. Objects that come back often I hide or pool instead of destroying.

Q: What should stay in the base prefab and what should be overridden in a prefab variant?
A: The base holds what all items share: the hierarchy, components, animation controller, common logic and standard effects. A variant changes only what is special for that item: sprites, offsets, collider size or data. I keep overrides few, because a variant with dozens of unexplained overrides is hard to keep working.

--- ART PIPELINE AND TOOLS (asked especially of a Senior) ---

Q: Design on a whiteboard a pipeline for islands, UI, particles and Addressables.
A: I start with the source files and import them with presets, so everyone gets the same settings. Then a validator checks size, compression, names and budgets. It reports problems, and for the rules that are critical for a release it can fail the build. Then atlases, then Addressables groups: core content local, events remote. Then review, then build. I also name an owner for each part and set budgets per device tier, because weak phones need different settings than tablets.

Q: What makes a good test in Unity?
A: A good test checks behaviour, not object names in the hierarchy. It doesn't depend on which scene is open, it cleans up after itself, and its error message is clear enough that I don't have to read the code to know what failed.

Q: Why do you write tests for editor tools?
A: Because tools change assets for the whole team, and if a tool is broken, everyone is stuck. A test shows the tool does the right thing, and that it still works after a Unity update or when someone changes the asset structure.

Q: How do you make an editor tool safe for artists?
A: Undo for every change, so artists can try things without fear. Clear error messages instead of silent defaults. A preview before applying. And the tool only touches the folders it should, nothing else.

Q: How do you keep a tool from being abandoned?
A: It solves a real task that happens again and again, and it is simple to use. A guide helps, but the real test is watching artists use it. I see where they get confused and improve the tool itself, instead of expecting the guide to solve everything.

Q: How do you make an Inspector easier for artists?
A: Clear field names, sliders with [Range], and tooltips, so they know what each value does. Headers group fields that belong together. For risky settings I can hide or restrict them. For bigger tools I make a custom editor window, so it's not just a long list of fields.

Q: When do you write an AssetPostprocessor?
A: I would write one when there are import rules that must always apply: compression, Max Size, Read/Write per folder. With an AssetPostprocessor these rules apply by themselves, so nobody can import a texture with wrong settings by mistake.

Q: How would you make a PSD-to-Unity pipeline safe to reimport?
A: I would make the import deterministic: the same PSD and the same metadata should give the same result every time. I would keep stable names or IDs for layers, separate generated data from what artists changed by hand, and avoid overwriting manual changes on reimport. After reimport I would check that the prefab hierarchy, sprite references and animations still point to the right objects.

Q: How do you validate content before a build?
A: I would write an editor check that runs before the build and looks for missing links, wrong import settings, too many materials per object. If something is wrong, it reports a clear list of problems, and for critical rules the build can fail, so they get fixed before release.

Q: Why do files written from outside Unity not appear?
A: With Auto Refresh on, Unity normally finds external changes by itself, for example when the Editor gets focus again. If my tool writes files and I need them imported right away, I don't rely on that - I tell Unity from code to refresh or import them. Otherwise Unity may not import the new files until the next refresh.

Q: What do you do when a teammate's prefab change breaks your screen?
A: I find the exact change that broke it, then talk to them. We agree on how to fix it together - I don't silently overwrite their change.

Q: What is the first thing you check in someone else's prefab?
A: Missing links first, because they will fail when the game runs. Then the hierarchy - are the names clean, is it organized well. I find which components do the real work. Then I check for risky overrides on instances that could break in production.

Q: How do you make the team follow import and naming rules?
A: I make the rules automatic instead of hoping people read a document. Import presets per folder, so textures import right by default. I add a check that catches invalid assets and reports a clear error before they reach release. Documents help, but tools work every time.

Q: What can go wrong when opening a Unity project in another editor version?
A: Opening a project in an older Unity version is usually not safe. I would check scenes and prefabs, package versions, URP assets, Addressables and other package data. If I must go back to an older version, I start from that version and move the content over carefully, instead of hoping the newer project opens fine in the older Editor.

Q: What makes a useful Technical Art test?
A: I like tests that check our own project rules, not Unity itself: asset links, scene structure, animation data, Addressables setup, or what an editor tool produces. The goal is to catch production mistakes automatically - not to test if Unity's Animator works.

--- BEHAVIOURAL QUESTIONS (STAR) ---

Q: How do you report a bug so it is easy to fix?
A: I give clear reproduction steps, the expected and actual result, the device and build version, and a screenshot or video. If there is a useful log or stack trace, I include that too.

Q: How do you estimate a task you have not done before?
A: I break it into small parts and first prototype the riskiest part. Then I give a range, not one number - the low end if everything goes smoothly, the high end if it gets complicated. I update the estimate when I learn more.

Q: What if you find a bug in someone else's system close to release?
A: I tell the owner right away, with steps to repeat it and proof. I suggest a fix if I have one. I don't quietly overwrite their work - we agree on the fix, and if I'm the right person to do it, I help.

Q: What if the deadline cannot be met?
A: I say it as soon as I know, not on the day of release. I tell the team what can be done by the date and what has to move. I'd rather agree on a smaller scope than knowingly ship a broken release.

Q: How would you convince an artist to change their workflow?
A: I show the problem on a real phone, so it's real to them. Then I give them a tool or a preset that makes the new way easy. I also let them try it on a real asset, so they can see whether it actually makes their work easier. If it's more work for them, they won't use it, so I make it simpler.

Q: What would you improve first in a new project pipeline?
A: I wouldn't redesign anything in the first weeks - first I need to understand why the pipeline works the way it does. Then I pick the thing that wastes the most time for the team. I make a small safe change and measure if it really helps.

Q: How do you hand over a feature?
A: I write a short note: what the feature does, how it's built, how to change it, and what it doesn't do. I also leave the prefab, settings and any small tools or notes in a state where another person can continue without asking me about every detail.

Q: What would you do in your first week on this project?
A: Build and run the project to see how it plays. Read the pipeline docs. Look at how existing features are built. Then take a small real task. I ask questions early instead of guessing and getting stuck.

Q: What does "production-ready" mean for a feature?
A: It works on the phones we target and fits the frame and memory budget. It handles all the states and edge cases without crashing. It also fits the project's loading, build and content pipeline, not just the scene itself. It's tested and reviewed, and another person can understand and maintain it without depending on knowledge that lives only in my head.

Q: How do you verify it's tested enough?
A: I check that the important paths are covered - the normal flow, edge cases and error states. Then I run it on the target phones and play a few longer sessions to see if anything breaks.
