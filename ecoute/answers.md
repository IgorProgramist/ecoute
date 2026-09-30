UNITY KNOWLEDGE (facts AI can use):

FROM BRIEF / MOCKUP TO FEATURE:
- From mockup to feature: list states (idle, available, in progress, done, error), inputs, content and animations before building. Ask about missing states early.
- Prototype first: a rough working version in Unity shows problems (layout, timing, performance) before polish.
- Edge cases: no internet, no money, double tap, interrupted animation, long translated text, small screen.
- Hand-off ready: prefab clean and named, states tested, no missing references, performance checked, short notes for the next person.
- Read a Miro board as a list: screens, states, transitions, data (prices, timers), triggers, and what the player feels at each step.
- Questions to ask early: which states exist, what happens offline, what data comes from server, localization, target devices, deadline, what is must-have vs nice-to-have.
- Technical plan before building: prefab structure, canvas split, animation approach, asset groups (local/remote), memory budget, which parts reuse existing systems.
- Vertical slice: one fully working state path (buy -> build -> ready) first, then widen to all variants.
- Definition of done: looks right on two aspect ratios, all states tested, no console errors, profiled, addressables grouped, clean prefab, notes for QA.
- Build flow for a buildable item: available (marker, price card) -> buy -> under construction (cloud, hammers) -> built (pop-in, rewards fly to the counter).
- Retest with several real examples: one working example hides bugs that the second one shows.
- State flow from a mockup: Closed -> Opening -> Active -> Reward/Result -> Closing; list states before building.
- Build order: static uGUI layout on target resolutions first, then interactions and states, then animation, then polish.
- Animation contract per state: name, duration, easing, interruption rule, fallback pose.
- Prototype with mock data through the same interface production data will use, so going live means swapping content, not rewriting.
- Placeholder sprites should have the final sizes and aspect ratios; keep them in a marked folder and replace without changing prefab references.
- Debug controls in a prototype: open any state, change data, force errors.
- Estimate by parts (assets, prefab setup, states, animation, data, polish, testing, optimization); give optimistic, expected and risk-adjusted numbers.
- Technical spike: a short test when an unknown (new shader, new loading path) could change the architecture.
- Hand-off pack for reviewers: a demo scene that just works, a half-page README quick start (requirements, install, menu paths), a 30-60 s video, known limitations.
- A good animation brief states: purpose, what moves and what must NOT move, entrance order and stagger, start/rest poses, timing, feel, emphasis, idle loop, exit and trigger, interruption policy (close during intro), and acceptance checks.
- Plan a reduced-motion / short variant of frequent animations (settings toggle or repeat views).
- Island scene split: world content (sky, island, items, shadows, FX) as SpriteRenderers under an orthographic camera; persistent HUD (bars, popups) on a Canvas with anchors and safe area.
- A tech-art write-up: short (5-8 pages), decision-oriented, screenshots that support decisions (base hierarchy, variant overrides, Animator, Addressables groups, atlas, import settings, two aspect ratios, tool window, profiler), trade-off table, known limitations, honest measurement labels.
- Show restraint: no unused abstractions, no framework for seven items, no Timeline where Animator solves it; recording and write-up must match.
- Extras after the required flow: protect the core slice first; then highest value per hour (validator tool, sound/haptic hooks on the shared clip, short intro, completion banner, performance HUD); put extras under a separate hierarchy with toggles.
- Extras that backfire: unfinished economy, weather without art direction, pinch-zoom that breaks tap and reward targets, global scripts with hidden side effects, late third-party packages, debug HUD in the final video.
- Over-engineering signals: thin scripts wrapping built-in features, many tests on trivial behaviour, tools for problems the project does not have; keep code for dynamic data, flow, reward positioning, safe area and tools; use Animator/UI events for simple visuals.

PREFABS AND VARIANTS:
- Prefab Mode: edit a prefab in isolation (or in context) without touching the scene; changes apply to all instances.
- Overrides: instance changes show in bold with a blue bar; Overrides dropdown lets you apply to the prefab or revert, per property.
- Prefab variant chain: a variant can be based on another variant; keep chains short so changes are easy to trace.
- Added GameObjects and components on an instance are overrides too; removing a base child from a variant is not allowed, disable it instead.
- Prefab references in scenes point to the prefab asset GUID; moving or renaming the file in Unity keeps links, moving it outside Unity breaks them.
- Unpack a prefab only when it must become unique; unpacked objects no longer receive fixes from the prefab.
- Object pooling: reuse spawned prefabs (coins, particles, popups) instead of Instantiate/Destroy each time to avoid GC spikes. Unity has UnityEngine.Pool.ObjectPool<T>.
- Prefab structure contract: fixed child names and components (anchors, states, FX points) let animations, scripts and tools find parts in every variant.
- Components over inheritance: small components (view, controller, sound, FX hooks) combine into different items without deep class trees.
- Base prefab + variants: one base owns the structure (children, components, Animator); every item is a direct variant that changes only sprite, data, anchors, collider size or FX scale.
- Path contract: animation clips bind to children by path (e.g. ObjectAnchor/ObjectVisual). Renaming or moving a child silently breaks every clip that animates it.
- Apply All from a variant pushes its overrides into the base and changes every other variant. Apply only the override you mean.
- Nested prefabs: keep them shallow (1-2 levels) and only for parts reused in many places (build marker, construction FX).
- Updating an asset: delete + create gives a new GUID and breaks references. Update in place (EditorUtility.CopySerialized, SaveAsPrefabAsset on the loaded contents).
- PrefabUtility.LoadPrefabContents edits a prefab without a scene; always pair with UnloadPrefabContents.
- Variant overrides take precedence over base values; applying an override can push the change into the parent prefab.
- Variants that differ only by serialized values should be data (ScriptableObject), not variants.
- Variant chain: base + one level is ideal, 2-3 levels is the practical maximum.
- Split a part into its own nested prefab when it has its own lifecycle, reuse or owner.
- Marker components (RewardAnchor, VfxSpawnPoint, IconTarget) are safer than finding children by name.
- Prefer serialized references on a root controller over repeated Transform.Find; validate them in OnValidate.
- Cleaning overrides: open the variant in Prefab Mode, check the Overrides dropdown, revert overrides equal to the base.
- Pool reset list: transform, alpha, Animator state, tweens, particles, timers, text, listeners, async callbacks.
- ObjectPool<T> (UnityEngine.Pool) is stack-based and not thread-safe - fine for main-thread UI and effects; set a max size.
- Do not pool rarely opened static screens; pooling adds lifecycle complexity.
- Path contract as a test: a test that checks the base prefab still has every child path the clips animate catches renames before they break animation.
- Prefab data model: sprites live on the variant, the ScriptableObject definition holds id, name, price, card preview sprite and rewards.
- Moving assets inside Unity (AssetDatabase.MoveAsset) keeps GUIDs, so references survive a folder reorganisation.
- Review traps in prefab work: unexplained transform overrides, Apply into base by mistake, renaming animated paths, copies instead of variants.
- Build hierarchy for animation from the start: separate nodes for each animated beat, pivots where the motion needs them.
- HideFlags.HideAndDontSave objects cannot be saved with PrefabUtility.SaveAsPrefabAsset ("No objects were found for saving into prefab").
- Safest scripted prefab edit: PrefabUtility.EditPrefabContentsScope (load, edit, save, unload), or LoadPrefabContents + SaveAsPrefabAsset + UnloadPrefabContents in try/finally.
- Change a nested prefab by editing its own asset; editing it through the parent creates overrides or requires unpacking.
- Buildable item base prefab: stable child names (state containers Available / UnderConstruction / Built, ObjectVisual, ShadowVisual, anchors for marker and FX), one shared Animator Controller and one state script; variants override only sprites, anchor offsets, FX scale and data.
- Keep in the base: hierarchy and names, Animator + controller, transitions and parameter names, state script, event wiring, FX and marker structure, default sorting and materials, collider type.
- Use dedicated anchors (FXRoot, MarkerAnchor, ShadowAnchor) so a variant overrides one anchor instead of many children; ten deliberate overrides read better than fifty random transform changes.
- Open the base prefab only to change shared behaviour; edit variants for item values; check the Overrides list before Apply; never "Apply All" from a variant by accident.
- Name prefabs clearly (BuildableItem_Base, BuildableItem_House) and document which fields variants may override.
- Item data split: ScriptableObject holds identity and reusable data (id, price, rewards, icon); the prefab variant holds presentation overrides. Keep variants visually meaningful, not all identical with differences hidden in data.
- Nest prefabs for real reusable modules (BuildMarker, ConstructionFX); simple SpriteRenderer children stay inside the base; expose a few parameters instead of editing a nested prefab's internals per variant.
- Place prefab instances in scenes, never unpacked copies; keep critical config in prefabs/data, not only on scene instances; validate references (Animator, renderers, FX, collider, data) with a small checker.
- Keep variants one level deep (direct variants of the base) unless a real category layer is needed; variant-of-variant makes override ownership confusing.
- Pick one source of truth for item sprites: the prefab variant (clear for reviewers) with data holding id, price, icon and preview; do not silently copy values in OnValidate.
- Create a variant from code: PrefabUtility.InstantiatePrefab(base), modify the instance, PrefabUtility.SaveAsPrefabAsset(instance, path); nested prefab instances stay nested.
- Variants inherit new children added to the base; the link breaks only by unpacking or changing the base reference; renaming root assets does not break it (link is by GUID).
- Variants should not override the root transform when placement assumes the root is at the ground point; position scene instances instead.

REUSE, DATA AND SCALABLE CONTENT:
- ScriptableObject: an asset that holds data (item price, reward, sprite). Many prefabs share it; designers tune values without touching code or scenes.
- Data-driven content: new item or level = new data row or asset, not new code. Tables (CSV/ScriptableObject) scale to hundreds of variants.
- Prefab variants vs copies: a variant inherits from its base, so a fix in the base reaches all variants. A copy drifts and every fix must be repeated.
- Nested prefabs: reusable parts (marker, FX, button) live as their own prefab inside bigger prefabs. Change once, update everywhere.
- Animator Override Controller: reuse one state machine and swap clips per variant.
- Overrides: keep variant overrides small (sprite, data, anchors). Many overrides on a variant mean the base is wrong.
- ScriptableObject events/channels decouple systems: a UI listens to an event asset instead of a direct reference to the gameplay object.
- Configuration in one place: one settings asset per feature so designers tune timings and numbers without code changes.
- Content table to prefabs: a tool that reads a table and builds or updates prefabs keeps hundreds of variants consistent and repeatable.
- Theme reuse: the same prefab and logic with a different sprite set, color tint or material makes a new theme cheaply.
- Data tables (CSV) diff well in Git; turn them into ScriptableObjects or prefabs with a tool, so one row = one variant.
- One picture reused with scale, rotation or mirror is cheaper than a redraw.
- Prefabs keep one source of truth: change the prefab and every instance updates; Unpack Completely cuts the link.
- Shared materials batch together; creating a material instance per object (renderer.material) breaks batching and leaks memory if not destroyed. Use sharedMaterial when reading.
- Identical rigs can share animation clips; one clip library for many characters.
- RequireComponent adds needed components automatically and prevents removing them.
- Data formats: ScriptableObjects for authored content with asset references, CSV for big designer tables, JSON for runtime/backend payloads, Remote Config for flags and tuning.
- Keep a local default for every remote value so the feature still works when Remote Config fails.
- Never use display text as an ID; stable IDs for events, rewards, currencies and analytics.
- Generic event runtime with states Locked, Available, Active, Completed, Expired; a new event = new data + art.
- Theme asset with semantic slots (Background, PrimaryButton, RewardIcon, Header): prefabs reference roles, a reskin swaps one theme asset.
- ScriptableObject event channels decouple systems but can become hidden global state; unsubscribe in OnDisable, keep payloads typed.
- Content validators in CI: required fields, ranges, unique IDs, atlas membership, prefab contracts; a golden sample set must always pass.
- Special-case booleans (isHalloween, isChristmas) in code are a sign the feature is not data-driven.
- Renaming content names later touches prefabs, data and Addressables addresses; pick unique theme-specific names (SnowOwl, SpookyLighthouse) when the content is created.
- Identical elements (lanterns, tickets) use one sprite asset; copies differ only by scale, rotation or mirror.
- Give every item a stable id (house_01) for saves; never use display names as save keys.
- Tuning values (timings, start values, delays) in a ScriptableObject settings asset; scene references stay as serialized fields on the MonoBehaviour.
- ScriptableObject assets edited in Play Mode keep the changes after Play stops; revert through version control or work on a runtime copy (Instantiate(settings)).

CANVAS UI (uGUI, TextMeshPro):
- Canvas: a change rebuilds the whole Canvas it belongs to. Split static and often-changing UI into separate Canvases by update frequency, not as many as possible. Never change text every frame on one big canvas.
- Localization: show text in many languages. Unity Localization package or CSV/PO tables. Fonts must support all languages.
- Text: use TextMeshPro, it is crisper and has more features than old UI Text.
- Localization: leave space for long text (German, Ukrainian), use Auto Size with min/max or layout that grows, test with pseudo-localized text.
- Unity Localization package: String Tables and Asset Tables per locale; LocalizeStringEvent updates TMP text when the language changes.
- Right-to-left languages and some scripts need special font assets and shaping; check early if they are in scope.
- Layout Groups rebuild often; for big static lists, disable the layout after it builds or use fixed positions.
- Scroll views with many items: pool the items (recycling list) instead of instantiating hundreds.
- UI particles: Particle Systems do not render inside a Screen Space - Overlay Canvas; use a Camera canvas with sorting, or a UI particle solution.
- Canvas layers: a full-bleed background layer (no raycast), a Safe Area root for bars and buttons, and an overlay layer for popups and flying rewards.
- Canvas Scaler for portrait mobile: Scale With Screen Size, reference like 1080x2400, Match Width Or Height about 0.5-0.7.
- Anchors: pivot and anchor presets decide how an element moves when the screen changes. Corner elements anchor to the corner, bars stretch along one edge.
- Raycast Target: turn it off on decorative Images and texts. Only buttons and hit areas should catch taps.
- CanvasGroup: alpha fades a whole UI branch; interactable and blocksRaycasts turn input off for it. Cheaper and cleaner than fading each child.
- Screen Space - Overlay canvases are not drawn by cameras, so Camera.Render and render-texture captures miss them. Screen Space - Camera canvases are captured.
- Dynamic width: ContentSizeFitter + HorizontalLayoutGroup; fixed borders with 9-slice (Sprite Border + Image Type Sliced).
- Custom UI shaders must keep the stencil properties (_Stencil, _StencilComp, _ColorMask...) or Mask stops working on them.
- UI shaders read vertex color: Image color and CanvasGroup alpha arrive as vertex color, so the shader must multiply by it.
- RectMask2D clips by rectangle without stencil and supports softness (soft edges); Mask uses stencil and any shape.
- Paused game (timeScale = 0): UI animation should use unscaled time (Animator Update Mode Unscaled Time, tweens with unscaled time).
- Render modes: Screen Space - Overlay (no camera, always on top), Screen Space - Camera (a plane in front of a camera, can mix with world), World Space (UI as an object in the scene).
- EventSystem: exactly one per scene; without it no UI element receives clicks.
- RectTransform: all UI uses RectTransform with anchors and pivot instead of plain Transform.
- Anchor presets: a 3x3 grid plus stretch options; Shift+Alt also sets pivot and position.
- UI layer: new UI objects go on the UI layer; a camera Culling Mask can hide the whole UI.
- TextMeshPro fonts are SDF font assets (Font Asset Creator); SDF text stays crisp at any scale. Add fallback fonts for other languages.
- TMP overflow modes: Overflow, Ellipsis, Truncate, Page; Auto Size fits text between min and max size (costly if it runs every frame).
- TMP rich text: <b>, <i>, <color=#RRGGBB>, <size>, <sprite> tags style parts of a line.
- Image vs RawImage: Image uses Sprites (sliced, tiled, filled, atlases); RawImage shows any Texture (render textures, video) and does not batch with atlas sprites.
- Image Type: Simple, Sliced (9-slice), Tiled, Filled (radial or linear fill for progress and timers).
- Set Native Size makes an Image match its sprite's pixel size.
- Canvas Group Ignore Parent Groups: a child group can ignore the parent's alpha/interactable settings.
- Graphic Raycaster: sits on the Canvas and finds which UI element was hit; a Canvas without it cannot be clicked.
- Nested Canvases: a child Canvas rebuilds separately from its parent; put frequently changing elements (timers, counters) into their own Canvas.
- Canvas batching breaks when material, texture or sorting changes between siblings; keep siblings on the same atlas and material.
- Pixel Perfect on a Canvas snaps UI to pixels for crisp art; costs extra when UI moves.
- Layout rebuild: RectTransform, layout property or child count changes. Graphic rebuild: vertices, color, material, texture or enabled state changes.
- Profile UI with the UI and UI Details (Canvas) profiler modules; watch Canvas.SendWillRenderCanvases, Layout.Rebuild, Graphic.Rebuild, Canvas.BuildBatch.
- Canvas split by update frequency: static backgrounds, dynamic counters/timers, and each independently animated popup on its own Canvas.
- Too many small nested Canvases add overhead; split only where it avoids a measured rebuild.
- Remove Graphic Raycaster from Canvases that take no input.
- Content Size Fitter and Layout Group on the same object, or nested Layout Groups, cause repeated rebuilds; prefer anchors for stable layouts.
- Batch UI changes: enable the hierarchy once, set data once, rebuild layout once per frame.
- Long lists: virtualized/recycled cells with explicit positions instead of Layout Groups over hundreds of children.
- Safe Area: convert Screen.safeArea into the root Canvas space and apply to one SafeArea RectTransform; never apply padding twice in nested panels.
- Full-screen overdraw: one opaque background, one dimmer per popup only while open, merge static decorative layers, disable hidden panels.
- Fewer batches does not mean less overdraw; check both.
- 3D objects inside UI: a dedicated camera renders into a RenderTexture shown by a RawImage (low resolution, own culling mask).
- TMP fonts: static font assets for known languages (stable memory), dynamic for chat/user text; split atlases by script (Latin, Cyrillic, CJK, Arabic).
- TMP static atlases are generated from the localization character set (including punctuation and currency symbols).
- Fallback font glyphs can differ in baseline and weight - test them visually.
- Design buttons for the longest translation, not English; test with pseudo-localization (+30-50% length).
- TMP Auto Size is costly on counters, timers and list cells; use fixed sizes with fitted containers, strict min/max when needed.
- Unity Localization: String Tables for text with semantic keys, Asset Tables for localized sprites/fonts/audio, Smart Strings for plurals, numbers and dates.
- Split localization tables by feature; preload common UI tables, load event tables with the event.
- Never build sentences from localized fragments in code; keep grammar inside one localized entry.
- Arabic/Hebrew need shaping and bidirectional ordering, not just a font; mirror layout (alignment, arrows, progress) but not numbers or logos.
- TMP draw calls: share font asset and material, use material presets only for real style differences, avoid heavy outline/underlay/glow.
- Prewarm dynamic TMP glyphs before a screen appears to avoid atlas growth spikes.
- Dimming the whole background: one semi-transparent layer between sky and island is cheaper than changing every material.
- "Tap anywhere to continue": a full-screen Button with a transparent Image; a CanvasGroup keeps it non-interactable for the first 0.8 s.
- Top bar numbers: one TMP material with outline + underlay, fixed width, right alignment, no Content Size Fitter - digits do not shift the layout.
- Bottom nav: equal slots with a Horizontal Layout Group, but a big centre button breaks equal slots - use fixed anchors then.
- Selected nav slot: +6-12 px and x1.05-1.12 over 0.15-0.22 s, driven by an Animator bool (IsSelected).
- Top bar anchored to the centre with offsets recomputed for 1080 width keeps both halves in place on a tablet.
- World sprites (sky, island, items, FX) stay SpriteRenderers; only HUD (bars, popups, safe area) goes on a Canvas.
- A TMP font is referenced through its SDF font asset, not the .ttf; a search for prefabs that use the .ttf finds nothing even when it is used.
- Buttons dead in Play with "You are trying to read Input using the UnityEngine.Input class": EventSystem has StandaloneInputModule while the project uses the Input System package; use InputSystemUIInputModule.
- In Unity 6 TextMeshPro ships inside com.unity.ugui; no separate TMP line in manifest.json does not mean TMP is missing.
- Create UI objects with a RectTransform from the start (new GameObject(name, typeof(RectTransform))); adding UI components later to a plain Transform object can fail.
- Photoshop tracking/leading do not map 1:1 to TMP spacing (PS tracking 40 = TMP Character 4).
- Text inside a scaled Smart Object: TMP position and size = Smart Object point + position inside x scale.
- 9-slice only elements that stretch (buttons, panels); set borders in the Sprite Editor so corners do not stretch.
- 9-slice borders can be asymmetric (L28 R42 T34 B25) when the button has bevel and shadow on one side.
- Button width from its text: HorizontalLayoutGroup + ContentSizeFitter on a 9-slice button.
- Mirror uGUI elements by 180 degrees Y rotation, not negative scale; negative scale can break RectTransform and layout math.
- Several TMP materials on one font asset (outline variants) keep one atlas while changing the look.
- TMP SDF font asset typical settings: atlas 1024x1024 (512 for small sets), padding 9, sampling point size near the max that fits.
- One font can appear under two PostScript names (Volkswagen-Serial-Bold / VolkswagenSerialBold); map aliases to one TMP asset.
- TMP SDF atlas size vs sampling point size: a 512 atlas forces a lower sampling size; check edges of the largest text before shrinking.
- Build the TMP character set from the real texts, not all of ASCII; check with TMP_FontAsset.HasCharacters(text, out missing).
- Photoshop Stroke maps to TMP Outline, Drop Shadow to Underlay; free-form gradients, Outer Glow, Bevel and per-pair kerning do not transfer.
- A LayoutGroup on a parent overwrites children's anchoredPosition; computed positions are silently lost.
- uGUI has no MaterialPropertyBlock; per-element data goes into vertex data (UIVertex uv1-uv3 via a BaseMeshEffect), so many Images can share one material and batch.
- Canvas batching breaks on a material change or a texture change; 25 UI effects with 25 materials = 25 batches, 2 materials = 2.
- UI shaders must support Mask (stencil), RectMask2D (_ClipRect), UI ZTest and ColorMask, or they break inside masks and scroll views.
- UI effects that should run during pause use unscaled time (Time.unscaledTime / a global unscaled time property), not _Time.
- Custom uGUI shader checklist: _Stencil, _StencilComp, _StencilOp, _StencilReadMask, _StencilWriteMask, _ColorMask properties + Stencil block; ZTest [unity_GUIZTestMode], ZWrite Off; UNITY_UI_CLIP_RECT + _ClipRect + UnityGet2DClipping; UNITY_UI_ALPHACLIP; multiply vertex colour; [PerRendererData] _MainTex.
- RectMask2D softness in a custom UI shader needs _UIMaskSoftnessX/_UIMaskSoftnessY, vertex mask data and a fragment alpha fade; UnityGet2DClipping gives only hard clipping. Copy the logic from the UI/Default shader of your version.
- uGUI batches elements in one Canvas that share material and texture and are not split by masks or draw order; different material instances never batch, even if identical.
- Put masked elements in their own group; Mask adds stencil passes and splits batches inside and outside the mask.
- For UI Image, sprite Pixels Per Unit only sets the native size together with the Canvas Scaler's Reference Pixels Per Unit; the final size comes from RectTransform and Canvas Scaler.
- Canvas Scaler Match: 0 favours width, 1 favours height; around 0.7 is a portrait starting point, then check the real bars on tall phones and 4:3 tablets.
- Tap world items with Physics2DRaycaster on the camera + a Collider2D + IPointerClickHandler; avoid invisible UI buttons over world objects; make touch colliders a bit larger than the art.
- Reward flying from a world item to a HUD counter: WorldToScreenPoint, then RectTransformUtility.ScreenPointToLocalPointInRectangle into the Canvas, then animate to the counter; a fixed pre-authored start only works for one layout.
- Fixed bar heights with layout groups only where content changes; ContentSizeFitter everywhere causes needless layout rebuilds.
- Build a UI-only test scene (Canvas, bars, safe area) to check scaling without the world.
- A world-space price label: use TextMeshPro (3D text renderer) rather than a nested world-space Canvas; it sorts like a normal renderer.
- Rebuild a top bar from a 9-sliced background plus fixed-size currency clusters; do not scale the whole artboard; on tablets stretch only the background centre and spacing.
- Currency labels: fixed font size, right alignment, width for large numbers, no resizing of the slot per value, small punch on change - the bar must not jump.
- Bottom navigation: equal slots via HorizontalLayoutGroup (fixed anchors when a big centre button breaks equality); the whole slot is the Button hit area; selected state shown by position, scale, colour and label, not colour alone.
- Full-bleed bar backgrounds sit outside SafeAreaRoot (behind notch and home indicator); interactive content inside it; apply Screen.safeArea once to one root, not per element; background Images raycastTarget off.
- Casual game number fonts (OFL, free to ship): Luckiest Guy, Lilita One, Titan One for big counters; Fredoka or Baloo 2 for smaller readable text.
- TMP stroke + drop shadow in one SDF material preset: Outline (width, colour) + Underlay (offset, colour, softness); no Outline/Shadow components or duplicated text objects.
- Counters that change often: fixed-width right-aligned TMP sized for the maximum value, no ContentSizeFitter, word wrapping off; cap huge values (999M+).
- A fully transparent Image with Raycast Target on still receives clicks - handy for a full-screen tap catcher, but it blocks UI under it; disable it when not needed.
- Hide UI cheaply: canvas.enabled = false on a (nested) Canvas stops drawing but keeps its geometry, so re-enabling does not rebuild; CanvasGroup alpha 0 + blocksRaycasts/interactable false hides without removing; SetActive(false) destroys the batch data and rebuilds (plus OnEnable work) when re-enabled.
- Canvas Scaler Match = 1 on very wide screens spreads left/right clusters far apart; limit the bar's content width with a max-width container if it looks odd.
- A full-screen sky gradient on its own Screen Space - Camera Canvas behind the world (lowest layer) is a simple valid background; UI stays unaffected by Light2D.
- Changing Image.color rebuilds that graphic's mesh; fine for one element over a short fade, costly only for many elements every frame.
- Dim the world in a finale with one full-screen translucent overlay between sky and island (animate its alpha) instead of recolouring every renderer or particle.
- TMP SDF font for bold display text at 34-72 px: sampling 90-120 pt, padding 8-10, atlas 512 (1024 for full ASCII), SDFAA, static font asset for a fixed character set; dynamic assets for unpredictable text.
- TMP material presets share the font atlas but each preset is a different material and breaks batching; a few presets per font is normal.
- Photoshop stroke to TMP outline width: outlineWidth about strokePx / atlasPaddingPx (2-3 px stroke with padding 8 = 0.25-0.375), then match by eye.
- A plate with a vertical gradient that stretches only in width: Image Sliced with top and bottom borders covering the gradient (3-slice); Tiled repeats bands, Simple distorts.
- Hierarchy names: PascalCase English nouns by purpose (GemsCounter/ValueText, BuyButton, ShieldIcon); never "Group 199", "copy 9" or number contents as names; keep containers only for layout, anchors, grouping or code.
- Safe area: no built-in uGUI component; a small fitter sets anchorMin/anchorMax from Screen.safeArea (normalised by Screen.width/height) and re-applies when it changes (rotation); apply only to content that must avoid notches.
- Draw order in a Canvas = Hierarchy order: later sibling draws on top; change it by reordering or SetAsFirstSibling / SetAsLastSibling / SetSiblingIndex.
- Render Mode: Screen Space Overlay draws on top of everything; Screen Space Camera is drawn by a camera at a distance (camera settings affect it, e.g. perspective); World Space canvas sorts with scene objects (diegetic UI).
- Anchors are fractions of the parent rect (0 = left/bottom, 1 = right/top); anchors together = fixed size (Pos X/Y, Width, Height), anchors apart = stretch (Left/Right/Top/Bottom padding).
- Pos X/Y is the pivot position relative to the anchors; Shift while dragging an anchor moves the rect corner with it.
- Auto layout gives space in order: minimum sizes first, then preferred, then flexible; Image and Text report preferred size from sprite / text.
- Layout Element component overrides min / preferred / flexible size of one element.
- Content Size Fitter sizes its own object (Preferred = fit text); a Layout Group sizes and places its children but not itself; Aspect Ratio Fitter ignores min/preferred sizes.
- Values driven by a layout controller are read-only in the Inspector, not saved in the scene, and do not mark it dirty.
- Layout computes widths first, then heights (children bottom-up for input, parents top-down for set), so height can depend on width but never the reverse.

UI THAT FOLLOWS GAME STATE:
- UI from state: UI listens to game state (events, observable values) and only shows it. Game logic does not live inside UI or animations.
- Events: C# events or UnityEvents push changes to the UI. Unsubscribe in OnDisable/OnDestroy to avoid leaks and calls on destroyed objects.
- Avoid Update polling for UI: set text or fill only when the value changes. Changing text every frame rebuilds the Canvas mesh.
- Button states: disable interactable when the player cannot act (not enough coins); show why with a visual state, not a silent no-op.
- Fast inputs: UI must stay correct when events come fast or out of order (double tap, reward during animation). Guard with state checks, not timers.
- Animator from state: drive animations with parameters/triggers from the state (SetTrigger("Build")), so the visual always follows the real state.
- Timers and cooldowns: store the end time (UTC) and compute remaining time; do not count down with a float that pauses when the app sleeps.
- Server time for rewards: daily rewards based on device time can be cheated by changing the clock; validate on a server.
- Popups: one popup manager with a queue avoids two popups fighting for the screen.
- Loading states: show a loading or disabled state while async content loads; never let a button act on half-loaded data.
- Tuning numbers (start coins, timings, flight speed) belong in a ScriptableObject settings asset, not hard-coded in scripts.
- Card/popup views only read state and data (price, rewards, button enabled) and never own the game logic.
- Button OnClick: a UnityEvent in the Inspector or AddListener in code; remove listeners you add in code when the object is destroyed.
- Button transitions: Color Tint, Sprite Swap or Animation (Normal, Highlighted, Pressed, Selected, Disabled states).
- Slider/Toggle/Input Field/Dropdown expose On Value Changed events; Input Field also has On End Edit.
- Toggle Group makes toggles act like radio buttons (only one on).
- EventTrigger component adds pointer enter/exit/down/up events to any UI element.
- Sibling order: RectTransform.SetAsLastSibling brings UI to the front, SetAsFirstSibling sends it back; UI draws in hierarchy order.
- Model-View separation: the data class changes, the view reacts and redraws; the view never owns the numbers.
- Canvas Receives Events can be turned off so a Canvas stops taking input.
- MVP: presenter drives a passive view. MVVM: view binds to a view model, good when many screens share state.
- Observables for values (currency, energy, progress); events for one-time actions (popup request, reward, error).
- Timer text: update only when the displayed second changes; one timer service for all labels instead of Update() per label.
- Time.realtimeSinceStartupAsDouble measures local time unaffected by timeScale; device wall clock is untrusted for rewards.
- On resume, recalculate remaining time from the stored end time; clamp at zero and fire expiration exactly once.
- Popup request as data: id, priority, payload, exclusivity, expiry, dedup key; equal priority keeps FIFO order.
- Complete a queued popup only after its reward/action is committed, not when its animation starts.
- Fast/out-of-order events: request IDs, idempotent operations, sequence numbers to drop stale updates, redraw from the latest model snapshot.
- Animation completion must never decide whether a transaction succeeded.
- Animator from UI state: bools for persistent states (IsOpen), triggers for one-shots (Show, Claim), Play/CrossFade for restore; use hashed IDs.
- Remote content UI states: Idle, Loading, Ready, Empty, Offline, Error, Retrying; "no content" is different from "failed to load".
- Retries: timeout, cancellation, retry limit and exponential backoff; only one request in flight.
- Counters: the model holds the real value at once; the view rolls the number over 0.25-0.45 s and punches 1 -> 1.12 -> 1 over 0.16-0.22 s.
- Appearance timers should start in OnEnable, not from a field set at scene load.
- One reusable fly-to-target component for all rewards (source, target RectTransform, icon, count, stagger, arc, duration, arrival punch, callback), pooled icons.
- Reward flights: convert the source once at spawn (null camera for Screen Space Overlay, the Canvas camera for Screen Space Camera); 2-4 icons, not 6+; signed arcs so reward types curve differently; punch only the target counter.
- Rolling counter: interpolate the displayed integer to the new value; change the real value at the transaction, the UI is not the source of truth.
- Offer card: answers what, how much, where to press; hides at once on tap; the next card slides in (0.25-0.35 s) around the item reveal; pass a direct reference to the world item, never find it by name.
- Keep one economy authority (a single place that changes currencies); UI and effects only read it.
- Counter roll duration scales with the change but is clamped (min about 0.25 s, max about 1.0-1.2 s), ease-out; animate spends too, maybe slightly faster.
- Rewards arriving during a roll: retarget (target += amount, keep rolling from the current displayed value); queue only when rewards are far apart and must read individually.
- Ignore taps for the first 0.5-1 s of a celebration screen (or until its title is revealed) so the previous tap does not skip it.
- Block input during intros with a full-screen transparent raycast-target Image that is removed afterwards; CanvasGroup.blocksRaycasts does not stop Physics2DRaycaster clicks; disabling EventSystem risks a stuck state.
- Reward flights: pooled UI icons on a Bezier give exact landing; particles with force fields orbit and overshoot, not precise enough to hit a HUD element.

ANIMATION (Animator, Timeline, tweens):
- Animation: use Animator for simple clips, code/Tween for simple moves (Scale, Fade, move). Do not make huge animation controllers.
- Timeline: a sequencer asset (TimelineAsset) played by a PlayableDirector. Good for cutscenes, intros and scripted sequences with many objects in sync.
- Signals: a Signal Emitter on a Signal Track calls a Signal Receiver (UnityEvent) at a time - Timeline's way to trigger game code, sounds or FX.
- Timeline vs Animator: Timeline for a fixed, authored sequence; Animator for states that react to gameplay. They can work together (Timeline can override an Animator while it plays).
- PlayableDirector Wrap Mode: Hold keeps the last frame, Loop repeats, None resets; Update Method can use Unscaled Game Time for UI during pause.
- Timeline Control Track can start and stop Particle Systems in sync with the sequence and scrub them in the editor.
- Tweening (DOTween, LeanTween): code-driven moves for simple UI (punch scale, fade, move along path) with easing; kill tweens on destroy to avoid errors.
- Animation curves and easing: ease-out for things arriving, ease-in for things leaving, overshoot (back ease) for pops and rewards.
- Animator Override Controller keeps one state machine and swaps clips for each character or item variant.
- Keep Animators off idle UI: an Animator on every static UI element updates every frame and dirties the Canvas; disable it when not animating.
- Animator.Play on the current state restarts it on the next update. Wait one frame (or call Animator.Update(0)) before reading state info.
- Animation Events call methods on scripts on the same GameObject as the Animator. Forward them from there to other components.
- Reading an Animator mid-transition gives in-between values; wait until the transition ends before checking the final state.
- In EditMode tests editor time does not tick; coroutine yields only continue when something really advances.
- Looping motion: the last frame must match the first, or the loop jumps. Ping-pong or frac(time) phases avoid seams.
- Animator parameters: Float, Int, Bool, Trigger; set from code with SetFloat/SetInteger/SetBool/SetTrigger. Use Animator.StringToHash for speed.
- CrossFade blends from the current state to another over a time; good for smooth switches without extra transitions.
- Animation compression (Keyframe Reduction/Optimal) makes clips smaller on disk and in memory.
- Animator Controller needs states even for one clip; Entry, Exit and Any State are built-in nodes. Any State can start a transition but cannot be a target.
- Has Exit Time on: the transition waits for the clip to reach its exit time. Off: it fires as soon as the condition is true. Duration 0 = instant switch.
- Trigger resets itself after it is used; Bool stays true until set false. Conditions: Equals, NotEqual, Greater, Less.
- StateMachineBehaviour scripts on a state get OnStateEnter, OnStateUpdate and OnStateExit callbacks.
- Blend Trees blend clips by parameters (1D: one value like speed; 2D: two values like direction and speed); transitions switch, blend trees mix.
- Loop Time must be on for idle and walk clips; frame-by-frame sprite clips use a sample rate matching the art (e.g. 12 fps).
- Animator Update Mode: Normal, Animate Physics (with FixedUpdate), Unscaled Time (plays while timeScale = 0).
- Constant curves are optimized automatically; clip compression settings are chosen per clip on import.
- The Animator window during Play shows live parameter values and the active state - the first place to debug animation.
- Animating layout properties (size, anchors) triggers layout rebuilds; animate scale, position or CanvasGroup alpha instead.
- Animator.Rebind is expensive; avoid calling it often.
- Write Defaults On resets unanimated properties to defaults; Off keeps last values. Most teams standardise on Off with clips that key every needed property; never mix both in one controller.
- Animator Override Controller: same states and parameters, different clips per variant; use normalized exit time so clip lengths can differ.
- Build flow: gameplay/server owns one state enum; the Animator only presents it; one-shot celebration clips separate from persistent states.
- Every state must be restorable from a snapshot (reload, reconnect, pooling).
- Code callbacks for gameplay; StateMachineBehaviour for presentation enter/exit; Animation Events only for cosmetic timing (sound, particles).
- Never grant currency or complete construction from an Animation Event; clips get replaced and retimed.
- Paused game: UI Animator Update Mode Unscaled Time, Time.unscaledDeltaTime in custom code, WaitForSecondsRealtime in coroutines.
- State not restarting: Play(stateHash, layer, 0f). Trigger stuck: ResetTrigger, do not set every frame. Transition skipped: check conditions, exit time, interruption.
- After pooling: reset parameters and restore properties, or the animation resumes mid-way.
- Timeline tracks: Animation (RectTransform, CanvasGroup, sprites), Activation (panels, FX), Audio, Signal (named moments), Control (particles, nested timelines, prefabs).
- Signals: one SignalAsset per semantic event, a receiver on the feature presenter calls a small idempotent method; never grant rewards from a signal.
- Signals can fire twice or be skipped when seeking, looping or skipping; guard receivers.
- Reuse one Timeline asset: bind different objects through the PlayableDirector (bindings live on the director); validate bindings before Play().
- One owner per animated property at a time: Timeline for sequence properties, Animator for persistent state; after Timeline ends, set the gameplay state explicitly.
- Skippable Timeline: stop, apply the final visual state, fire required callbacks once; gameplay state is committed independently of the animation.
- PlayableDirector update mode: unscaled time for pause-safe UI sequences, manual mode for deterministic stepping.
- Tweens for procedural UI motion (punch, fade, slide, fly-to-target); Animator for named reusable states; never both on the same property at once.
- DOTween: SetLink(gameObject) kills the tween with its target; also kill in OnDisable for pooled UI; SetId to kill a feature's tweens.
- DOTween SetRecyclable reduces allocations but clear references in OnKill; avoid closures in thousands of short tweens.
- World-to-UI flight: Camera.WorldToScreenPoint with the world camera, then RectTransformUtility.ScreenPointToLocalPointInRectangle with the Canvas camera (null for Overlay).
- Reward flight: quadratic Bezier arc, stagger multiple icons, pool them, update the real counter only after the transaction is committed.
- Easing: OutQuad/OutCubic for entrances, InQuad for exits and flying into a target, small OutBack for pops, Elastic rarely; most UI tweens 0.12-0.35 s.
- Testable animation: durations and easing in data, an animation service with Play/Skip/Complete/Kill, zero-duration fakes in tests.
- Build sequence as one clip with timed keys (stars, marker off, cloud and hammers, pop-in 0.85 -> 1.06 -> 1.0, reward flight) is easy to tune in the Animation window; animate alpha/scale, not SetActive.
- Pop-in squash: X 1.03 / Y 0.94 for 0.06-0.08 s, then overshoot 1.06 and settle to 1.0.
- Idle markers bob and pulse; use Animator Cycle Offset so identical markers do not move in sync.
- Hammer props: pivot near the handle (parent + art child) so the Animator rotates them like a real swing.
- Measure a reference video frame by frame (burn timestamps with ffmpeg drawtext) before timing a feature; eyeballed timings drift.
- Buy-build-ready reference rhythm: tap to item visible about 1.1 s; dust cloud 1.0-1.2 s; item grows out of the cloud in its last 0.3 s; next offer lands with the item.
- In an .anim file per-component curves (m_AnchoredPosition.y, m_Alpha) live in m_EditorCurves; from C# read them with AnimationUtility.GetCurveBindings + GetEditorCurve.
- A clip's last 0.5-0.7 s of ease-out settle is almost invisible; a video looks "finished" earlier than the clip ends. Take duration from the clip, feel from the video.
- Curve wrap modes: generated curves should use the same preWrap/postWrap (ClampForever) as the reference, or a late-starting curve jumps to its first key before its start.
- Compare two animations by pose at many times t, not by curve end values; ends can match while motion differs.
- Motion start = the last key before the value changes, not the first key.
- AnimationCurve with WrapMode.Default evaluated exactly at the last key time can return the first value; clamp time in code to hold first/last values.
- Read a transition state during the transition and the result after it; a test of a state change must prove the change started.
- DOTween DOPunchScale stacks offsets when replayed; call DOComplete before the next punch.
- One Animator on a popup root drives all children; extra child Animators with missing controllers play nothing and only cost.
- Frequent popups: Show about 0.3-0.6 s; a long 1.5 s Show fits a one-time intro.
- Read motion from the clip or full-frame-rate video; 6 fps frames can make "drop + fade in" look like "grow".
- Popup items "appear" often by drop + CanvasGroup alpha, not by scale; central pivots are fine for position animation.
- CanvasGroup on every group that fades: one alpha for the whole group.
- Empty 0x0 container nodes (Item_N_Container) act only as move/rotate points so the whole group animates together.
- Animating RectTransform pivot itself gives a sway around a shifted point without an extra wrapper node.
- Popup structure: Show clip once (no loop), then an Idle loop (about 5 s); the transition lives in the Animator Controller. A long 1.5 s Show fits only special or first-time popups.
- Show to Idle transition: Has Exit Time on, Exit Time about 0.75-1.0 of Show, Idle loops.
- "Auto Generate Animation" on a Button creates a controller with empty Normal/Highlighted/Pressed/Selected/Disabled clips; delete it if unused.
- AnimationClip bindings (EditorCurveBinding.path) are relative path strings; renaming a node after animating silently unbinds it. Rename first, then animate.
- Stagger: identical groups share one motion with offset start times (e.g. three items 0.1-0.2 s apart).
- Popup Show choreography: beats in a clear order (platforms rise, content drops with bounce, logo drops, text and buttons pop, balloons float in), staggered 0.08 s between identical items.
- Idle loop: decor moves all the time with different phases; main items "wink" one after another (about 1 s, 2.3 s, 3.2 s) so the popup does not breathe in sync.
- Show end values must equal Idle start values, or the Show to Idle transition jumps.
- Use scale mostly for button-like things (badges, text, buttons); move big elements by position and alpha.
- A readable motion vocabulary (DropIn, RiseIn, PopIn, FadeIn, Bob, Sway, Pulse, Wink) turns a text brief into keys; overshoot and peak time control feel.
- Buttons should become clickable only when their Show animation is far enough; state it as an acceptance check (e.g. clickable from 1.4 s).
- Popup timing for frequent popups: intro 250-600 ms, outro 150-300 ms; up to about 1 s only for special or first-time moments. Consider a full intro first time and a short one later.
- Easing: intro ease-out with small overshoot (OutBack), idle soft sine, outro ease-in (InQuad/InSine) without overshoot.
- Break idle sync with different loop lengths (3.2 / 4 / 6 s), phase offsets (Animator Cycle Offset, or Play(state, 0, normalizedTime)) and small amplitude differences.
- On close: disable the popup's buttons at once, play the outro, deactivate at the end; block input on the popup, not the whole screen.
- UI motion: timing and easing matter most; subtle anticipation and small overshoot help; strong squash-stretch, big arcs and heavy elastic wobble make UI feel unstable.
- Popup Animator layout: Show (default) -> Idle by exit time; Idle -> Out by trigger without exit time; Any State -> Out so the popup can always close.
- Know when Out finished: an Animation Event on the last frame is the most exact; StateMachineBehaviour.OnStateExit fires when the exit transition starts.
- Two Animators writing the same property fight; one owner per property path (root Animator, or children animating only what the root does not touch).
- Animator vs tweens for UI: Animator for authored, designer-tuned sequences; tweens (DOTween, PrimeTween, LitMotion) for frequent small motions and runtime-driven counts and staggers.
- Procedural motions relative to rest position (start = rest + offset) survive layout changes; do not bake absolute positions.
- Editor preview without Play: AnimationMode.StartAnimationMode, BeginSampling, AnimationMode.SampleAnimationClip(go, clip, time), EndSampling, StopAnimationMode (restores values).
- Curves from code: set tangent modes explicitly (AnimationUtility.SetKeyLeftTangentMode/RightTangentMode, ClampedAuto for smooth UI, Constant for on/off); weighted tangents via Keyframe.weightedMode.
- Timeline basics: PlayableDirector holds a TimelineAsset and bindings; tracks (Animation, Activation, Audio, Control, Signal) hold clips; wrong or missing bindings = "Timeline does nothing".
- Code to Timeline: director.Play/Pause/Stop, director.time = t then director.Evaluate(), speed via director.playableGraph.GetRootPlayable(0).SetSpeed(x); events director.played / director.stopped.
- Timeline clip extrapolation (None, Hold, Loop, Ping Pong, Continue) sets what happens before/after a clip; Director Wrap Mode (Hold, Loop, None) sets what happens at the end.
- Animator and PlayableDirector on the same object fight over properties; give one clear owner (disable or park the Animator while the Timeline plays).
- Keep popup Animator simple: one layer, 3-5 states; use parameters for variants instead of separate controllers.
- Plan a popup with a timing chart: every element on one time axis, grouped by function (background, platforms, rewards, text, button).
- Three main accents per popup (container, main reward, button); overshoot and settle only on those, smaller amplitude for secondary elements.
- Wave cascade: delay grows linearly per element; a short micro-pause (50-150 ms) before the final button makes it land.
- Idle variety: different elements move on different axes (X, Y, rotation) rather than all bobbing on Y.
- Very short popups (errors, toasts): fade + micro-scale only, 150-250 ms.
- Common UI motion names to know: slide in (4 directions), scale in/out, fade, flip (cards), shake (error), bounce (success), flash/highlight, count-up, float, shimmer/glint, typewriter.
- Default feel without numbers: DropIn/RiseIn 0.35-0.5 s OutBack; SlideIn 0.25-0.4 s OutCubic; PopIn 0.25-0.35 s OutBack 8-12% overshoot; FadeIn 0.2-0.3 s; Bob 2.5-4 s InOutSine 8-20 px; Pulse 1.5-2.5 s scale 1.05-1.1.
- Typical mistakes of generated animation: everything moves at once, no lead element, bounce/elastic everywhere, abrupt starts; fix with a lead element, 60-120 ms child stagger, simple eases by default.
- Anticipation as data: a small opposite move before the main one (scale 1 -> 0.9 -> pop); follow-through: a small overshoot and settle after it.
- Compare two motions by max error, RMS error, key-pose timing (landing), and overshoot; align by landing time to tell a timing shift from a shape difference.
- Rough visibility thresholds for UI motion: under 2-3 px, under 1% scale, under 0.03 alpha and under 30 ms timing are hard to see; over 8-10 px or 80-100 ms is clearly visible.
- Generated clips should end exactly at the rest pose, and Idle clips must have Loop Time on.
- Check generated animation data for conflicts: two beats writing the same property of the same object at overlapping times.
- Estimate an idle loop's period from its curve with autocorrelation to compare loops by phase and period.
- Rebuilding an AnimationClip in place: copy data through public APIs (GetCurveBindings/GetEditorCurve/SetEditorCurve, object-reference curves, events, AnimationClipSettings), not EditorUtility.CopySerialized, which can leave internal binding data stale.
- Rebuild an AnimatorController in place: reuse states by name and only swap state.motion, reuse parameters and transitions; removing states while the Animator window shows the graph can throw inside the window.
- If the state machine shape is fixed, keep one controller and swap clips with an AnimatorOverrideController instead of regenerating the graph.
- Overshoot/bounce models: Penner Back (one overshoot), Elastic (amplitude, period), Bounce (impact hops), cubic-bezier with y > 1 (one overshoot), spring (response + damping ratio; below 1 oscillates, 1 settles without bounce).
- Measured reference shapes: a badge overshoots to about 1.29 of the distance at 85% of the time, a button to about 1.2 at 78%, balloons ease with no overshoot.
- Contents that lag behind their container and squash on landing = overlapping action / follow-through with drag and impact squash (scaleY about 0.94, scaleX about 1.05 for 0.1 s).
- Child lag should be in the container's local space, or it lags twice (own offset + inherited motion).
- Setting a tangent mode recalculates tangents; set AnimationUtility.SetKeyBroken and SetKeyLeft/RightTangentMode(Free) first, then write explicit inTangent/outTangent.
- Keyframe fields: time, value, inTangent, outTangent, inWeight, outWeight, weightedMode; tangent modes Free, Auto, ClampedAuto, Linear, Constant.
- No official human-editable format round-trips a Unity AnimationClip losslessly; the .anim YAML is native but internal - generate it, do not hand-author it.
- Settling time = the moment a motion enters and STAYS within a 2% or 5% band of its final value (scan back to the last exit); "first sample in the band" is wrong for overshooting curves.
- Landing of a falling or overshooting motion = first directed crossing of the target, not settling time.
- Tolerances by property: position in screen pixels (about 1.5 px), scale relative to its value, rotation in wrapped degrees, alpha about 0.02; one absolute scale tolerance fails on large values like 241.
- Compare loops by phase: check start/end continuity (value and velocity), normalise one cycle, find the phase shift with circular cross-correlation, then compare shape; report raw and aligned error and the shift.
- Animator for sprite animation makes sense for unique sequences, animation events, gameplay-state links and few objects; not for 50 identical explosions.
- One shared Animator Controller for all variants if hierarchy is identical; AnimatorOverrideController only when the same states need different clips; animated child paths are an API - do not rename or remove them.
- Without new code, a Button/EventTrigger can call Animator.SetTrigger via UnityEvent; but currency, saving and double-tap protection still need a small script. Code owns state, the Animator only presents it.
- One BuildSequence clip is easier to audit than many tiny exit-time states; animate alpha and scale of always-active objects rather than GameObject active flags.
- Build flow Animator: Available -> (trigger Build) -> BuildSequence -> (exit time) -> Built; add a debug Reset trigger to replay; disable the tap collider during the sequence.
- Item reveal: alpha from 0 and scale 0.85 -> 1.06 -> 1.0 over 0.25-0.3 s makes the object feel placed, not just unhidden.
- Premium-casual build beat: card hides at tap, star burst 0.03-0.25 s, cloud and hammers 0.2-0.8 s, star flies to the counter, item appears in the cloud about 1.0-1.15 s and settles by about 1.4 s, rewards and next card overlap until about 1.9 s; never make the player wait over 2 s for the next action.
- Overlap feedback events aggressively; do not hold the next card until every effect has finished.
- A permanent building should not squash like a character: keep anticipation subtle and overshoot moderate (1.06).
- Shadow supports the landing: smaller and lighter while the object is "high", briefly larger and darker on landing, then settles; felt, not noticed.
- Save camera shake for special moments (final item, landmark, island completed); a normal build already has enough feedback.
- Hammer hits: fast swing toward impact, hold 1-2 frames, tiny scale pulse, small dust puff, slower return; 3-5 hits per second, staggered between hammers.
- Build marker motion: slow idle bob, small scale pulse, occasional shimmer/wiggle; an invitation, not an alarm. A ghost silhouette at low opacity previews the future item.
- An Animator on the base animating ObjectAnchor.localScale keeps working in variants that override ObjectVisual.localPosition; if a variant overrides the animated property, it becomes the new baseline the animation writes over.
- Idle floating island: pure vertical sine translation, about 60-80 px peak-to-peak on a 2400 px screen, 3-3.5 s per cycle; clouds/shadow with 50-70% amplitude and a 10-30% different period; no squash on terrain.
- A single procedural idle (float, hover) is cheaper and clearer as a tiny script (base + sin(t)) than an extra Animator on a parent of animated children.
- Animator Culling Mode (Always Animate, Cull Update Transforms, Cull Completely) reduces cost for off-screen animators; scale curves cost more than position/rotation.
- "Island falls from the sky" intro: start above the camera, fall about 0.6 s ease-in, one overshoot bounce (5-10%), 1-2 smaller settles; 0.9-1.5 s total; show the full intro only the first time, later a short 0.2-0.3 s pop-in.
- Never let an Animator and a script write the same transform: drive the intro on an empty parent (IslandRoot) while the Animator floats the child, or disable the Animator during the intro.
- Replay a UI state from the start: animator.Play("Show", 0, 0f), or ResetTrigger then SetTrigger; a trigger on an already playing state does not restart it.
- Switching a UI Animator off at the clip end via an Animation Event (animator.enabled = false) stops per-frame Canvas dirtying; nested Canvases isolate rebuilds of animated parts.
- Re-enabling a GameObject with an Animator rebinds it (small cost); keep UI Animators on objects that stay active and switch the component instead.
- Time.timeScale = 0 pauses the game: Update still runs but deltaTime is 0; use Time.unscaledDeltaTime for UI animation that must keep playing during pause or slow motion.
- Button Transition = Animation uses an Animator (not legacy Animation); several buttons can share one Animator Controller.
- Animator cost grows with its state machine (states, transitions, layers, parameters); StateMachineBehaviour OnStateMachineEnter/Exit forces main-thread evaluation.
- 2D character animation: frame-by-frame (classic look, expensive to make and to run), cutout (separate sprites move, no bending), skeletal (2D Animation package, bones bend the sprite).
- Animation window can key position/rotation/scale, any component property (material color, light intensity, sound volume), your script's float/int/enum/vector/bool fields, and Animation Events.
- Animation Event calls a function by name on scripts of the same GameObject as the Animator, with one Float, Int, String or Object parameter (e.g. play a footstep, spawn a VFX prefab).
- Imported clips can carry Curves (X = normalized time 0-1); a curve with the same name as an Animator parameter drives that parameter.
- Animation Layers: Override replaces lower layers, Additive adds on top (additive clip must animate the same properties); an Avatar Mask limits a layer to some body parts or transforms.
- Synced layers reuse another layer's state machine structure with different clips (e.g. "wounded" walk/run).
- Even a single clip needs an Animator Controller to play through an Animator; one controller can be shared by many objects.
- Legacy Animation can be cheaper for very simple animations with few curves (simple UI); Mecanim (Animator) is recommended for complex ones with many curves and blending.
- Rotation interpolation: Euler goes the full angle (a 365 degree key spins a full turn), Quaternion takes the shortest way (365 = 5 degrees).
- Animation updates transforms after Update and before LateUpdate: override bones or animated values from code in LateUpdate (e.g. LookAt).
- Clips are sampled at the game's variable frame rate: never check "rotation == 90" to detect a moment; use an Animation Event. WrapMode.Once may skip the exact last frame; ClampForever holds it.
- Imported FBX clip keys are read-only; copy keyframes (Ctrl+C) into a new clip to edit them; missing target properties show yellow.
- Animator Solo / Mute on transitions: preview only chosen transitions while debugging a state machine (Mute wins over Solo).
- Import Mask on a clip strips unused bones' data: smaller file, less memory, faster blending.

PARTICLES AND VFX:
- Texture Sheet Animation: set Tiles X/Y to the real grid of the sheet (4x4 = 16 frames); a wrong grid shows parts of two frames.
- Renderer Max Particle Size is a fraction of the screen height (default 0.5); big particles get capped and look different on other resolutions.
- Auto Random Seed: keep it on so copies of the same effect do not move in sync.
- One-shot effect: Looping off, bursts at set times, short lifetime, Stop Action Destroy or Disable, and return to a pool.
- Particle System vs VFX Graph: Particle System runs on CPU and works everywhere; VFX Graph runs on GPU compute and suits huge counts, but needs compute support and does not fit small mobile UI effects.
- Particle shaders in URP: use URP Particles (Unlit/Lit) materials; legacy Particles shaders do not work with the SRP Batcher.
- Emission: Rate over Time (per second), Rate over Distance (per unit moved), Bursts (count at a time, with cycles, interval and probability).
- Collision module: World collision High uses physics (expensive); Medium/Low cache in a voxel grid and suit static scenes. Planes mode is the cheapest.
- Sub Emitters spawn another system on Birth, Collision or Death of a particle and can inherit velocity or color.
- Renderer Mesh mode with GPU instancing draws mesh particles much faster than one by one.
- Custom Data and custom vertex streams send extra per-particle values to the shader (e.g. dissolve progress, random seed).
- Lights module adds real-time lights to a share of particles; expensive, use sparingly on mobile.
- Texture Sheet Animation frame blending with custom vertex streams gives smoother flipbooks with fewer frames.
- Main module: Duration, Looping, Prewarm (starts as if already running), Start Lifetime/Speed/Size/Color, Gravity Modifier, Simulation Space, Max Particles.
- Max Particles is a hard cap that stops runaway cost.
- Shape module: Sphere/Hemisphere for explosions, Cone for fountains, Edge for lines, Box, Circle, Sprite and Mesh emitters.
- Size over Lifetime and Color over Lifetime shape the life of each particle (grow, shrink, fade).
- Trails module draws a ribbon behind particles; Ratio sets how many get a trail.
- Blend looks: Additive for fire and glow, Alpha Blend for smoke, Subtractive darkens, Multiply/Modulate tints.
- Unlit particle shaders are cheaper than lit ones; use Unlit unless the effect must react to lights.
- Scene preview plays the selected Particle System; Particle System Curves panel edits curves for many modules at once.
- Starting budget: a local effect 20-100 live particles, a big screen burst 100-300; overdraw matters more than particle count.
- Most effects: one or two systems and one shared material.
- Texture Sheet Animation: 4-16 frames for simple bursts, 256-512 atlases for small effects; Whole Sheet for one sequence, Single Row for variations.
- Frame blending only when it visibly improves the effect; it costs extra sampling.
- Particles over uGUI need a Screen Space - Camera or World Space Canvas (or a dedicated camera / maintained UI-particle package); Overlay UI does not sort with renderers.
- Pool whole effect prefabs; before returning: Stop(true, ParticleSystemStopBehavior.StopEmittingAndClear).
- Pool capacity from measured peak concurrency; prewarm only common effects.
- One effect across devices: author in local units, one logical scale parameter, scale by target size (not screen resolution), clamp extremes.
- Quality tiers for effects: particle count, texture size, lights, trails, optional sub-effects.
- Common mistakes: large textures with empty space, full-screen alpha layers, lit/distortion/soft shaders for simple UI effects, collision or lights not needed, looping systems left on hidden screens.
- Particle sorting: Renderer Sorting Layer and Order in Layer for coarse placement; Sorting Fudge only for small tie-breaks (lower = more in front).
- ParticleSystem.Emit on a stopped system gives no particles (measured in EditMode); call Play() first - Play alone emits nothing if emission is off.
- Manual Emit pattern for reward sparkles: emission module off, Play() once, then Emit(EmitParams, count) at the position you need.
- Build cloud: one particle 0.7-0.8 s, 4x4 Whole Sheet flipbook, no random start frame, Alpha blend (not additive), local space, no loop.
- A Particle System with Play On Awake off is not started by the Animator; a small component with Play() called from an Animation Event (or from code) starts it.
- Baking an expensive procedural shader into a flipbook atlas moves the math to bake time; in game it is one texture sample.
- Bake rules: restore shared materials after baking, capture quad fills the frame exactly (2 x orthoSize), Point filter for pixel art, per-effect cycle length, keep both scale axes, prove baked frames still change.
- VFX Graph has no public API to build graphs from code (only exposed parameters of a hand-made graph); Particle System is fully scriptable, so tool automation goes through Particle System.
- VFX Graph runs on the GPU (compute), is production-ready mainly for HDRP; in URP and on mobile support is limited - check the target devices before choosing it.
- Study a professional particle pack (e.g. Cartoon FX Remaster) to learn which modules real effects enable.
- Particle gravity is Main module's gravityModifier (there is no separate gravity module); a pro pack used non-zero gravity in about 1 of 10 systems.
- A sub-emitter child system needs its own Burst (or rate); the trigger says WHEN, the child's emission says HOW MANY. A child with burst 0 emits nothing, silently.
- Cone and Box shapes emit along local +Z; in 2D rotate the shape only by +-90 around X, and tilt the emitter object around Z.
- Particle shapes without new materials: Texture Sheet Animation in Sprites mode with small white sprites keeps one shared particle material.
- ParticleSystem.IsAlive(true) stays true while paused, even with 0 particles; a pool that returns effects on !IsAlive will not reclaim an effect frozen off-screen (culling Pause).
- Deterministic particle bakes: useAutoRandomSeed = false and a fixed randomSeed; then Simulate(t) gives the same frame every time.
- With Time.timeScale = 0, pooled effects pause and are not reclaimed until time resumes - correct pause behaviour, not a leak.
- Most 2D effects should be Unlit; Lit particle materials add 2D light cost with little visible gain.
- Pooling pays off for effects spawned often (hit sparks 10+/s); a rare one-off explosion can just be instantiated.
- OnParticleSystemStopped does not fire for systems paused by off-screen culling; do not rely only on it to return pooled effects.
- VFX Graph flipbooks need a uniform grid texture; a Sprite Atlas with arbitrary rects will not work as a VFX flipbook.
- A particle pool needs a guard against releasing the same instance twice.
- VFX Graph keeps simulating off-screen (GPU simulation has no frustum culling by default); invisible effects cost full price unless culling flags are set.
- Exposed VFX Graph properties can be floats, vectors, gradients, textures, bools, curves; set them from code with VisualEffect.SetFloat/SetVector3/SetGradient/SetTexture.
- URP VFX Graph can output 3D: Output Particle Mesh, Lit Mesh, Cube; the other outputs are quads, lines, points, decals.
- Core particle modules in a pro pack (62 prefabs): Main, Emission, Shape, Color over Lifetime, Size over Lifetime on 76-100%; Noise 18%, Trails 8%, Sub Emitters rare.
- Game feel beyond particles: hit-stop, camera shake, flash on hit - VFX packs do not include these; they live in code.
- Pixel-art effects: flipbook frames, not smooth shader interpolation; "smoother" means "blurrier" for pixel art.
- Pool rules: looping effects stay until explicitly stopped (aura, campfire); one-shot effects return to the pool when !IsAlive.
- Particle System scripting: optional modules (noise, collision, trails, lights, subEmitters) are disabled by default; set .enabled = true before writing their values, or nothing happens silently.
- startLifetime/startSpeed/startSize/startColor are MinMaxCurve/MinMaxGradient; assigning a float gives Constant mode - build new ParticleSystem.MinMaxCurve(min, max) for a random range.
- var main = ps.main; main.startLifetime = 2f; changes the system directly (module structs are handles); there is no ps.main setter.
- maxParticles is a ceiling, not a measurement; check the live particleCount at the densest moment of the effect.
- Pro effects are several tiny systems (about 3.5 per effect): flash (1 particle), sparks (about 7), smoke (about 5), debris; median maxParticles 5, median burst 1, most systems do not emit continuously.
- Pro-pack medians: startLifetime 0.6 s (0.4-1.0), startSize 0.85, maxParticles 5 (q75 30), burst count q75 7; only 1.8% of systems exceed 500 particles.
- Texture Sheet Animation is used in about 42% of pro effects; Custom Data (68%) there feeds the pack's own shader.
- Modules beginners overuse: Collision (per-particle physics; fake gravity looks the same), Trails (extra material and width curve), Sub Emitters, Noise (one of the most expensive; high frequency multiplies cost).
- Texture Sheet Animation without a real flipbook atlas samples one frame; a silent mistake.
- The particle Lights module spawns regular Lights, not Light2D; it does nothing useful in the URP 2D Renderer.
- Effect playback from code: playOnAwake = false, loop = false, Stop(true, ParticleSystemStopBehavior.StopEmittingAndClear) before Play so a replay does not mix with the previous one.
- Set emission bursts with SetBursts(array) to replace them; re-applying a config that adds bursts accumulates duplicates.
- Particle Render Mode Billboard turns sprites toward the camera; in a 2D orthographic game it is fine, but pixel-perfect art may need an aligned mode.
- Reduce flipbook frames two ways: drop exact duplicate neighbours (lossless) vs keep every Nth frame (lossy); report which one was used.
- Particle bake outputs: sprite animation (SpriteRenderer + Animator), a baked quad with a flipbook shader, or a Particle System with Texture Sheet Animation.
- Pool return: main.stopAction = ParticleSystemStopAction.Callback calls OnParticleSystemStopped; add a timer fallback for effects without particles and an IsAlive watchdog.
- A Particle System's duration cannot be changed while it plays; Stop(true, StopEmittingAndClear) first.
- Only exposed properties of a VFX Graph (Blackboard, Exposed ticked) can be driven from code or data tables; values inside nodes are fixed constants.
- Starting particle budgets for a 2D action game: hit spark 8-30, muzzle flash 3-12, small explosion 20-80, big explosion 80-200, smoke/fire 20-80, aura 10-40, screen rain 100-300, ultimate 150-500.
- Feedback effects are short: hit spark 0.1-0.35 s, muzzle flash 0.03-0.12 s, slash 0.15-0.4 s, magic hit 0.25-0.7 s, small explosion 0.4-1.2 s, big explosion with smoke 1-3 s.
- Hits, bullets and explosions use Bursts, not continuous emission: they end predictably and return to the pool cleanly.
- Particle collision only for a few large debris pieces; raycast the projectile itself instead of colliding every particle.
- Many decor effects (100 torches): full effect near the camera, a few particles or an animated sprite at mid range, a static sprite far away, off outside the camera.
- VFX Graph Output Particle Octagon cuts the empty corners of round particles compared to a Quad, reducing overdraw.
- Tint particles with particle start colour / Color over Lifetime (vertex colour) instead of new materials.
- Particle System Culling Mode (Automatic, Pause, Pause and Catch-up, Always Simulate) controls off-screen simulation.
- VFX Graph culling depends on its Bounds: too large = always simulated, too small = pops out early; set real bounds in the Graph Inspector.
- VFX LOD by screen size: at a few pixels an effect needs no bloom, noise or lights; keep particle-count multipliers per quality level.
- A big effect is mostly illusion: flash, a few big shapes, sparks, smoke and screen shake read as huge with few particles.
- Expensive screen distortion only for short phases (spawn 0.2-0.4 s, attack), with the cheap core running between.
- Starter recipes: hit spark = burst 20-50, white to yellow fade, 0.3-0.5 s; coin pickup = size up then fade, gold gradient, 0.6 s; muzzle flash = burst ~10, cone, 0.15 s.
- Starter recipes: campfire = cone up, rate ~15/s, yellow-orange-red, medium noise, 1.5 s; rain = wide box, ~100/s, strong gravity, 1 s; poison cloud = circle, ~5/s, strong noise, green to clear, 4 s.
- Starter recipes: shockwave = size 0 to large then fade, white to clear, 0.8 s; teleport = burst ~50, expanding sphere, 0.6 s; aura = circle around the character, ~10/s, pulsing size, 2 s loop.
- Flipbook in Particle System: Texture Sheet Animation with Tiles X/Y (4x4 = 16 frames), about 12 fps for stylised fire/explosions.
- Flipbook frame counts for a 1 s explosion: small/far 12-16 (4x4), gameplay 20-24 (6x4), hero 30-36 (6x5/6x6), cinematic 48-60. Mobile default: 24 frames, 6x4.
- Simulate VFX at 60 fps in EmberGen/Houdini but export 24-30 frames (frame stride); timing is uneven: fast flash and expansion first, slow fade last.
- Split a baked explosion into layers (core, smoke, sparks) rather than one huge flipbook; small on screen = fewer frames and smaller texture.
- Flipbook LODs: LOD0 30 frames 1024-2048 atlas, LOD1 24 frames 1024, LOD2 12-16 frames 512 or a simple particle effect.
- VFX Graph flipbook modes: Flipbook (hard switch), Flipbook Blend (cross-fade), Flipbook Motion Blend (motion vectors); Particle System Texture Sheet only switches frames.
- Sub-emitters simulate in the editor only with Simulate(t, withChildren: true, ...); a child GameObject system is not a sub-emitter unless it is assigned in the Sub Emitters module.
- Simulate restart: true replays from 0 to t every call (repeatable, slower, good for bakes and random access); restart: false steps forward (fast preview, depends on previous state).
- Sub-emitter spawn conditions: Birth, Death, Collision, Trigger, Manual (ParticleSystem.TriggerSubEmitter); Collision/Trigger and Rate over Distance make bakes non-deterministic.
- Deterministic bakes need fixed seeds on the root AND every child/sub-emitter system.
- Pixel-art particles: keep simulation smooth and snap in the vertex shader, or snap only spawn positions; per-particle CPU snapping (GetParticles/SetParticles every frame) is expensive; rotation breaks crisp pixels - bake rotation variants.
- VFX Graph with the URP 2D Renderer: use a Shader Graph based output; for 2D lights use a Sprite Lit Shader Graph; check the camera uses the 2D Renderer Data.
- VFX Graph not visible checklist: wrong Renderer Data, incompatible Shader Graph, bounds not covering particles, culling, no compute support, sorting or culling mask.
- VFX Graph flipbook setup: Output Particle Quad UV Mode Flipbook (or Flipbook Blend / Motion Blend), Tiles X/Y, a Flipbook Player block in Update driving texIndex; unused grid cells must be transparent or texIndex clamped.
- Particle System vs VFX Graph: keep small, often-spawned, deterministic, collision/sub-emitter, UI and pixel-perfect effects in Particle System; move massive smoke, thousands of sparks, GPU trails and force fields to VFX Graph. Many small VFX Graph instances are not automatically cheaper.
- Hide the VFX backend behind one gameplay API (Play at position) so quality level can pick VFX Graph on high-end and Particle System on low-end.
- VFX Graph + URP 2D lights: replace Output Particle Unlit with Output Particle Shader Graph Quad and assign the hidden VFXSpriteLit Shader Graph (eye icon in the picker); the Light 2D must target the effect's sorting layer.
- Debug a new VFX Graph with a Single Burst of one particle (lifetime 5, size 1) before adding flipbook, blending or distortion.
- VFX Graph particle not visible: capacity 0, lifetime 0, size 0, no spawn, culling mask, bounds, sorting, graphics API.
- Partial flipbook grid (18 frames in 6x4): clamp texIndex to start..start+count-1, or drive texIndex from age over lifetime (start + floor(age01 * (count - 1))); Flipbook Player Cycle = 1 plays once.
- Flipbook Blend needs a float texIndex in 0..N-1 (no floor), or the last frame blends into the first; hold the last frame by clamping.
- Unity ObjectPool<ParticleSystem> pattern: main.stopAction = Callback, a script on the SAME GameObject calls pool.Release in OnParticleSystemStopped; collectionCheck true during development catches double release.
- OnParticleSystemStopped fires only after emission stops, duration ends and all particles die; a looping system never gets there on its own.
- Pool prefabs with several systems, lights, trails or audio through a wrapper component; reset colour, size, speed, transform, trails and seeds in OnGet.
- Prewarm pools for combat VFX (create instances at load) to avoid the first-burst Instantiate spike on mobile.
- Stop Action Disable does not tell the pool anything; use Callback for pooling. StopEmitting keeps existing particles alive; StopEmittingAndClear removes them.
- VFX Graph compiles compute shaders per system; many near-identical graphs cost compile time and variants - parameterise one graph instead.
- Texture Sheet Animation: Frame over Time curve (Time Mode Lifetime/Speed/FPS) animates frames; Start Frame random gives each particle a different static frame (debris, variety); both are cheap.
- Particle atlases on mobile: 512x512 or 1024x1024 per effect type; 2048+ rarely needed for small VFX.
- Warm up a looping system before baking or capturing: simulate for duration + max start lifetime so the population reaches a steady, repeating state.
- ParticleSystem.GetParticles(buffer) is allocation-free with a preallocated buffer; one buffer can be reused across systems if you read only the returned count.
- Particles using scaled time freeze at timeScale 0 and their stop callback waits until time resumes; Main module Use Unscaled Time makes UI/pause effects keep playing.
- Unity Gradient holds at most 8 colour keys and 8 alpha keys; VisualEffect.SetGradient passes it to exposed gradient properties.
- On devices without compute shaders VFX Graph renders nothing (no error); the player just sees no effect - always ship a fallback.
- VFX Graph reuse: one graph with exposed properties driven by ScriptableObject configs beats hundreds of near-identical graphs; System/Block/Operator Subgraphs share logic and exposed properties bubble up to the parent.
- Trigger VFX Graph effects with VisualEffect.SendEvent (or Play) on pooled instances instead of Instantiate; Reinit() is expensive - avoid it at runtime.
- Pool VisualEffect like ParticleSystem: Stop(), reset position and exposed values (SetFloat/SetVector3/SetGradient), SetActive(false).
- VFX Graph has no built-in LOD or screen-coverage limit; do distance/size LOD yourself by lowering spawn rate or disabling systems.
- VFX Graph cannot be simulated in EditMode tests; test it in PlayMode and wait frames; there is no public alive-particle count, so detect "draws nothing" by rendering.
- Custom HLSL Block in VFX Graph can read and write particle attributes (position, color, velocity); loops must be bounded, textures sampled with explicit mip level.
- Duplicate .vfx assets with AssetDatabase.CopyAsset (it gives the copy a new GUID) instead of text-patching the YAML; the .vfx format changes between package versions.
- Changing VisualEffect.visualEffectAsset at runtime resets and can hitch; prefer one graph with property overrides.
- Name exposed properties consistently across many effects: shared core names (Intensity, Lifetime, Spawn Rate) plus prefixed type-specific ones; use ExposedProperty constants in code.
- VisualEffect runtime API: SetFloat/SetInt/SetBool/SetVector2-4/SetGradient/SetAnimationCurve/SetTexture/SetMesh, SendEvent, Play/Stop, Reinit; the graph structure (nodes, outputs, shaders) cannot change at runtime.
- A .vfx can be marked as a template (Template Info: Use as Template, name, category) so artists create new graphs from it via "Create from template".
- Effect library structure: a few base graphs per family (sparks, smoke, fire, explosion, magic) with many variants via exposed properties/subgraphs; too few bases with thousands of variants is hard to maintain and search.
- A duplicated .vfx can carry the same internal authoring id and show "Already registered authoring guid" when both are open; reimport the copy.
- Sparks are small by design (tiny size, short life, fast alpha fade): judge "is it working" per effect family, not with one pixel threshold for all.
- Soft particles fade where particles meet geometry; they need the depth texture (URP Depth Texture on) and a transparent (not additive-only) output.
- VFX Graph Prewarm (system settings: Prewarm Time / Step Count) simulates ahead so looping effects start in steady state instead of empty.
- Dust cloud from a sprite sheet: Unlit URP particle material, Texture Sheet Animation with the real grid (check the sheet, not the filename), short burst, expanding size curve, fading colour.
- Hammers or other readable props: SpriteRenderer children animated by the Animator (swing, impact scale, offset timing) read better than particles.
- One-shot build FX: looping off, one burst, local simulation space (follows the anchor), 2-3 cloud particles with random rotation/size, colour over lifetime fade-in then longer fade-out; stars as a separate short (0.25-0.4 s) burst.
- A cloud sheet that is one complete authored puff: play it on a single particle with no random start frame; add at most one subtle secondary particle.
- A white cloud over a light sky needs separation: soft shadow sprite behind it, pale tint or outline in the art, a brief ring; avoid heavy black outlines.
- Reward moment hierarchy: one loud element (item reveal), supporting stars, shockwave and flash quieter; a one-frame flash stays small, never full screen.
- Radial star burst for a point impact, cone only for directional emphasis; size over lifetime with a small mid-life growth; no heavy hue cycling at small size.
- Small per-hit puffs: a separate short burst is easier to place and tune than a Sub Emitter; use Sub Emitters when every particle's death/collision must spawn the same child.
- Fireworks: rocket system with random start colour from a gradient, Sub Emitter on Death to a burst system with "Inherit Color" ticked on the Sub Emitters entry; burst Start Color white; both in World simulation space.
- Firework trails: Trails module on burst particles, URP Particles/Unlit additive, soft round texture (Texture Mode Stretch), Trail Lifetime 0.25-0.4 s, Width over Trail 0.7 -> 0.15, Inherit Particle Color; longer trails look like noodles and add overdraw.
- Casual fireworks starting values: rockets 1.5-2.5/s, speed 5-8, lifetime 0.6-0.9 s, gravity 0.2-0.4; burst 30-45 particles, speed 3-5, lifetime 0.5-0.8 s, gravity 0.2-0.35, drag 0.05-0.15; randomise speed/size 10-20% and rocket timing.
- Particles parented under a scaled Canvas shrink with Scaling Mode Hierarchy; use Scaling Mode Local, or keep them in world space and position them once from the banner's RectTransform.
- Banner confetti: one burst of 30-60, lifetime 0.8-1.4 s, speed 3-6, gravity 0.2-0.4, random start rotation plus rotation over lifetime (optionally 3D rotation to tumble), light noise or drag, random bright colours fading out.
- There is no global alive-particle counter; sum ParticleSystem.particleCount over a cached list of systems each frame and keep the peak.
- TextureSheetAnimation.startFrame from code is normalised 0-1 across the sheet (frame 1 of 4 = 0.25), even though the Inspector shows frame numbers.
- Sky clouds as particles: few (7-10), long lifetime (60-120 s), near-zero gravity, world space, one shared unlit material, small texture, own sky sorting layer, optional low-end toggle.
- Particles suit fire, smoke, liquids, sparks; meshes and sprites suit solid objects.
- Collision Dampen = speed lost, Bounce = speed kept, Lifetime Loss and Min Kill Speed remove leftover particles after a hit; Radius Scale stops sprites sinking into surfaces.
- Send Collision Messages enables OnParticleCollision on the particle object or the collider (particles as projectiles or pickups).
- Color by Speed maps a gradient over a speed range (fast sparks white, slow red).
- Color over Lifetime multiplies with Start Color; a fading alpha gradient is the usual burn-out / dissipate look.
- External Forces module lets Wind Zones and Particle System Force Fields push particles; filter fields by Layer Mask or an explicit List.
- Force over Lifetime with a curve gives rising smoke that slows; Randomize with Two Constants/Curves picks a new direction each frame (turbulent).
- Inherit Velocity (Current = follows emitter every frame, Initial = once at birth) needs Simulation Space = World; used for smoke from a moving car or rocket.
- Lifetime by Emitter Speed scales start lifetime by how fast the emitter moves.
- Lights module: Use Particle Color and Alpha Affects Intensity make the light fade and tint with its particle.
- Limit Velocity over Lifetime with a falling speed curve or Drag = air resistance: fireworks burst fast then slow down.
- Main: Prewarm starts a looping system as if one cycle already ran (no empty first second); Start Delay waits before emitting.
- Main Scaling Mode: Hierarchy uses parent scale, Local only its own, Shape scales spawn positions but not particle size.
- Main Stop Action (Disable / Destroy / Callback OnParticleSystemStopped) fires when all particles died and Duration passed; for looping systems only after Stop() from code.
- Auto Random Seed off + fixed Random Seed makes an effect look identical every play (repeatable reviews, deterministic tests).
- Ring Buffer Mode keeps particles alive until Max Particles, then recycles the oldest (persistent footprints, decals).
- Simulation Space: World for trails that stay behind a moving emitter (smoke, flamethrower); Local for effects that must move with the parent (spark between electrodes).
- Noise module: high frequency + strong for embers, low frequency + soft for smoke; Octaves and Quality raise cost, use the lowest quality that looks right.
- Renderer Render Mode: Billboard (clouds), Stretched Billboard (speed streaks, aligns to velocity), Horizontal (ground rings, spell circles), Vertical (upright, good for orthographic), Mesh (rocks, debris), None (only trails).
- Particle Renderer Masking: Visible Inside / Outside Sprite Mask clips particles to a Sprite Mask (2D).
- Particle Renderer Min/Max Particle Size are fractions of the viewport: clamp stops particles filling the screen when the camera gets close.
- Mesh render mode needs read/write enabled meshes (Unity turns it on); Mesh Weightings set how often each mesh is picked.
- Rotation by Speed makes debris roll in proportion to speed.
- URP has its own post-processing (Volume with Bloom, Vignette, Color Adjustments); the old Post Processing Stack package is for the built-in pipeline.
- VFX Graph needs the Visual Effect Graph package; reusable parts go into Block Subgraphs (a set of blocks used inside a context) and Operator Subgraphs (a set of operators shown as one node).

SHADERS AND MATERIALS (URP, Shader Graph):
- UV scrolling, dissolve (noise vs threshold), flash (lerp to white), outline and shine sweep are cheap shader effects that replace extra sprites or animation.
- MaterialPropertyBlock breaks the SRP Batcher for that renderer. Separate materials are often cheaper in URP.
- Blend modes: Blend SrcAlpha OneMinusSrcAlpha = normal transparency (smoke, dust); Blend SrcAlpha One = additive (light, glow, sparks).
- Shader Graph: only Exposed Blackboard properties show in the material Inspector.
- Sprite shaders for "alive" items: wind bend anchored at the bottom by UV.y, glow pulse, shine sweep, water ripple. Cheaper than animating transforms.
- Render queue: Opaque 2000, Transparent 3000. Transparent objects do not write depth (ZWrite Off).
- A mass shader edit can compile and pass text checks but render nothing (an undeclared property reads 0). Render a sample and count lit pixels.
- Shader Graph: a node editor that builds shaders without code; main nodes include Sample Texture 2D, Multiply, Lerp, Time, UV, Fresnel Effect.
- Shader Graph outputs: Base Color, Alpha, Emission (glow without light), Normal; Sprite Unlit/Lit targets for 2D.
- Blackboard properties (Texture2D, Color, Float with slider) become material properties; set from code with material.SetFloat / SetColor using the reference name (e.g. _Speed). Use Shader.PropertyToID for speed.
- Shader variants multiply build size, memory and load time. Strip unused features in the URP Asset and keep keywords few.
- "Show generated code" on a Shader Graph lets you inspect the real shader and its variants.
- Render Pipeline Converter fixes pink (Built-in) materials after moving to URP.
- LightMode pass tags decide which render pass draws a shader in URP; wrong tags = object not drawn.
- SRP Batcher cuts CPU state-change cost; it does not remove draw calls or overdraw.
- Independent boolean keywords multiply variants exponentially; prefer a material parameter for small options.
- Strict shader variant matching in testing reveals variants stripped by mistake.
- Dissolve (one mask + alpha clip) and flash (tint) are cheap; outline by neighbour sampling costs more - pre-bake it when possible.
- Wind by vertex displacement needs enough vertices; a 4-vertex sprite barely bends.
- uGUI custom shaders: use the URP Canvas Shader Graph target or a UI shader; multiply vertex color, support stencil and RectMask2D clipping.
- Test UI shaders inside a real Canvas (masks, CanvasGroup fade), not on a quad in the Scene view.
- MaterialPropertyBlock does not work cleanly with uGUI; use vertex color or shared material properties there.
- half for colors, normalized UVs, local offsets; float for world positions, long-running time, depth and thresholds.
- Pink = missing/unsupported shader or stripped variant; black = lighting, missing texture, color space; invisible = alpha 0, clipping, render queue, culling, ZTest, stencil.
- Shader debugging: start from a constant-color unlit output, add texture, alpha, masking and effect step by step.
- Sprite-Unlit is cheaper than Sprite-Lit; 2D Lights affect every sprite on their target Sorting Layers and more layers need more light textures.
- Animate many sprites with one shared material: global time + per-object phase in vertex color or a UV channel, instead of material instances.
- Shader warm-up: ShaderVariantCollection for known variants; Unity 6 PSO tracing with GraphicsStateCollection, then WarmUp or WarmUpProgressively.
- HLSL over Shader Graph only when the graph generates extra work or cannot express the needed batching, precision or blend; Custom Function node for one piece of code.
- Mobile shader mistakes: many or dependent texture samples, full-screen blur/distortion, keyword explosion, discard where blending is enough.
- Active render pipeline is set in two places: Graphics Settings (default) and Quality Settings per quality level (overrides it). Check GraphicsSettings.currentRenderPipeline at runtime, not one settings file.
- A texture exported without alpha (RGB shockwave) cannot use alpha blend; use additive or re-export with alpha.
- Keep your own copy of the URP Pipeline Asset and Renderer in your folder; settings changed on an asset inside a third-party (often git-ignored) folder get lost.
- URP Asset: Opaque Texture ON is needed for _CameraOpaqueTexture / Scene Color (distortion, heat haze); Opaque Downsampling None keeps it sharp; turn Depth Texture off in 2D if nothing reads depth.
- MSAA must match on the URP asset and on each camera; shadows (main + additional) off in a 2D sprite game save a pass.
- The 2D Renderer (Renderer2DData) has no Depth Prepass setting; that belongs to the 3D Universal Renderer.
- URP post-processing needs all three: a Global Volume in the scene, a Volume Profile with overrides enabled per field, and Post Processing ticked on the camera (UniversalAdditionalCameraData.renderPostProcessing).
- Bloom reacts to brightness above its threshold (about 0.8-1); plain white (1,1,1) sits at the edge; HDR colour intensity above 1 makes particles glow.
- 2D URP materials: Sprite-Unlit-Default for light sources (fire, magic, explosions), Sprite-Lit-Default for things that should darken with Light2D.
- Pixel-art shader: snap UV to the pixel grid first (uv = (floor(uv * cells) + 0.5) / cells), quantise alpha in steps, take noise per cell, hard discard edges.
- A _ManualTime property (-1 = live _Time.y, >= 0 = frozen) lets tools freeze a shader frame for tests, drive it from code and bake it.
- Additive glow that will be captured: Blend SrcAlpha One, One Zero; plain "Blend SrcAlpha One" squares the stored alpha (0.5 becomes 0.25).
- All material properties must sit in CBUFFER_START(UnityPerMaterial) ... CBUFFER_END, or the shader silently drops out of the SRP Batcher. Check: grep -L "CBUFFER_START(UnityPerMaterial)" *.shader.
- Editing a shader does not update existing .mat files: a new property gets 0, and a property whose meaning changed keeps the old number. Reset with mat.CopyPropertiesFromMaterial(new Material(shader)).
- 2D URP Sprite-Lit objects: once the scene has any Light 2D, areas no light reaches render dark or black with the default Multiply blend style; add a Global Light 2D as the base light.
- Distortion shaders read _CameraOpaqueTexture; with Opaque Texture off in the URP asset they read nothing. The option is on the URP asset (Rendering), and costs a full-frame copy.
- Useful Shader Graph starting values: Fresnel power 2-4, HDR intensity 3-10 for glow, Bloom threshold about 0.8, flipbook 4x4 = 16 frames at about 12 fps.
- Hand-written .shader (HLSL) files are text: diffable and checkable (ShaderUtil.ShaderHasError); a .shadergraph is generated JSON that code cannot safely write.
- UI shaders with "ColorMask [_ColorMask]" need the _ColorMask property declared; undeclared = 0 = writes no colour, the element is invisible.
- URP 2D renderer draws passes tagged Universal2D and untagged (SRPDefaultUnlit) passes; without the Universal2D tag a shader gets no 2D lighting - fine for unlit effects.
- Global shader properties (Shader.SetGlobalX) affect every shader using that name, including package shaders; use unique names.
- Vector material properties that must not be gamma-corrected should be Vector properties, not Color; Color values get colour-space conversion in Linear projects.
- URP 17 Renderer Features use the RenderGraph API; a full-screen distortion feature copies the screen every frame - keep it off by default.
- Post-process starting values for VFX: Bloom threshold about 0.8 intensity 1-3; small Color Adjustments; subtle Chromatic Aberration 0.05-0.1 for action.
- Camera checks for VFX: Allow HDR for strong glow, Post Processing on, Culling Mask includes the VFX layer, Volume Mask includes the Global Volume layer.
- Quick Opaque Texture test: Unlit Shader Graph, Surface Transparent, Scene Color with noise-offset UV into Base Color on a quad over a coloured background; if the background bends, it works.
- Build complex effects (a black hole) in cheap layers first - dark core, Fresnel ring, rotating disc, particles to centre, bloom - and add screen distortion last.
- Renderer Features (Full Screen Pass, custom passes) each add a pass; add them only when an effect needs them.
- Texture budget per VFX shader: pack masks into channels of one texture (R dissolve, G noise, B edge, A alpha); use one noise texture with different tiling/offset instead of two.
- A small noise texture is usually cheaper than Simple/Gradient Noise or Voronoi nodes on large transparent effects; keep procedural noise for single hero effects.
- Expensive shader ops (pow, sin/cos, sqrt, normalize, loops, several noises, Scene Color/Depth samples) belong in hero effects, not in every spark.
- Particle and VFX renderers: Cast Shadows off, Receive Shadows off.
- One master VFX shader (unlit, main texture, tint, UV scroll, intensity) with many materials beats a separate Shader Graph per colour.
- Fake light instead of Light2D per spark: emissive sprite, HDR colour + Bloom, a painted glow circle behind; keep explosion light flashes short.
- Core Shader Graph nodes for VFX: Fresnel Effect (edge glow), Time, Simple Noise, Gradient, Sine, Scene Color (distortion), Multiply/Add for intensity; HDR Color intensity 3-10 with Bloom.
- Sprite Mask shows or hides sprites inside a mask shape (lantern in darkness, fog of war); set its front/back sorting range.
- Motion vector textures import as Linear (sRGB off); agree encoding (0.5 = no motion), Y direction, scale, same tile layout as the colour atlas.
- URP camera motion vectors (for motion blur/TAA) are not flipbook motion vectors; they come from EmberGen/Houdini exports.
- SRP Batcher compatibility: all numeric material properties (including _ST) in one UnityPerMaterial CBUFFER with the same layout in every pass; textures and samplers outside it. Check the shader Inspector ("SRP Batcher: compatible").
- _Time, _SinTime and Shader Graph Time stop when Time.timeScale = 0; pause-menu effects need an unscaled clock passed from C# (Shader.SetGlobalFloat with Time.unscaledTime).
- renderer.material creates a per-renderer material instance (destroy it when done; do not call it every frame); renderer.sharedMaterial changes every user of the material.
- A material property with the same name overrides a global shader property; globals apply only where the material does not define it.
- RenderTextures for colour in a Linear project: sRGB on; for data (normals, masks, depth): sRGB off.
- Keyword that code toggles at runtime (material.EnableKeyword / SetKeyword): declare with multi_compile_local; a material-only toggle can use shader_feature_local (unused variants get stripped).
- Keep shader variants that are enabled only at runtime by adding a ShaderVariantCollection (recorded in Graphics settings) to Preloaded Shaders or referencing them explicitly.
- A Shader Graph used by VFX Graph needs "Support VFX Graph" enabled in Graph Settings; Custom Function nodes (inline or .hlsl file) work there too.
- Port hand-written HLSL into Shader Graph with a Custom Function node (function name with _float/_half suffix, matching inputs/outputs) instead of rebuilding it from nodes.
- Particle motion vectors only matter with TAA, motion blur or frame generation; without those they are cost with no effect.
- Turn off URP features the scene does not use (depth texture, opaque texture, HDR) - they cost without helping.
- URP Particles Unlit blend modes: Alpha, Premultiply, Additive, Multiply; start with Alpha for PSD art; use Premultiply only for premultiplied exports or visible fringes.
- Custom Vertex Streams in the particle Renderer send extra per-particle data (speed, size, rotation, custom data) to the shader; stream order in the list must match the shader struct.
- URP 2D Renderer: Light 2D lights sprites, normal and mask secondary textures add normal mapping; Shadow Caster 2D casts 2D shadows (Shadow Intensity above 0).
- Static branching (#if, compile-time constants) costs nothing at runtime; dynamic branching (if on uniforms) avoids extra variants but costs GPU time and reserves registers for the worse branch.
- Shader Graph Branch node always runs both branches and picks one result.
- A shader in Always Included Shaders gets every keyword combination built, even shader_feature ones.
- In Shader Graph a set of keywords is a Keyword node and its entries are states; Shader Graph keywords are variants only (no dynamic branch option).
- Magenta = error shader (no material, compile error, unsupported, or a Built-in shader in URP); cyan = loading shader while a variant compiles asynchronously.
- Editor compiles shader variants on demand and caches them in Library/ShaderCache (safe to delete); the build compiles all needed variants.
- Count variants: Graphics settings > Shader Loading shows currently tracked variants (Save to asset = ShaderVariantCollection); after a build, search Editor.log for "Compiling shader".
- URP asset Shader Variant Log Level writes stripping totals to Editor.log (remaining/total variants per pass).
- Keywords: local scope cannot be overridden by a global keyword; enable per material with Material.EnableKeyword / SetKeyword, globally with Shader.EnableKeyword.
- More than one (or no) keyword of a variant set enabled gives an undefined "good enough" variant - manage keyword sets so exactly one is on.
- Keep keywords per shader low: above 128 there is a runtime penalty; stage-specific keywords (vertex/fragment only) cut wasted variants in hand-written shaders.
- One shader can drive many materials, but a material uses exactly one shader; materials hold the values, the shader defines the properties.
- Variant count = product of keyword sets (3 colors x 4 quality = 12); ten on/off sets = 1024 - combinatorial explosion; identical variants are deduplicated but still cost compile time and loading.
- Strip variants: prefer shader_feature, declare stage suffixes (shader_feature_fragment), use SHADER_API_MOBILE/DESKTOP macros to build fewer variants on mobile, turn off unused features in the URP asset, IPreprocessShaders for the rest.

SPRITES, TEXTURE IMPORT, ATLASES:
- Atlas: one big texture with many small images. Fewer materials = fewer draw calls. Sprite Atlas in Unity packs images. Use Sprite Atlas instead of packing in Texture Packer when possible.
- Transparent edges in atlases: enable Alpha Is Transparency on the texture (it fills transparent pixels with edge colour) and give the atlas padding; premultiplied alpha is a shader blend choice, not an atlas switch.
- Sprite import baseline: Texture Type Sprite, PPU 100, Read/Write off, mipmaps off for UI/2D, Clamp, Bilinear, max size fitted to the screen size.
- Sprite Mode Multiple: Unity auto-slices on the first import and stores the rects in the .meta. A redrawn PNG keeps the old rects - re-slice it.
- Max Texture Size only caps the imported texture; sprite world size comes from the source pixels and PPU (bounds), not from the cap.
- Sprite Atlas V2: one atlas per group of sprites used together (per screen or per theme). Repack after art changes; check that no atlas overflows to extra pages.
- Atlas settings: padding 2-4 px (more for soft FX), no rotation and no tight packing for UI sprites.
- ASTC block size by content: 4x4 for sharp UI, 6x6 for items, 8x8 for soft shadows and gradients.
- Size by use: measure how big the sprite is drawn on the target screen and import at that size, not a blanket percentage.
- Point filter only for pixel art; everything else Bilinear.
- AssetImporter.importSettingsMissing is true only on the very first import (no .meta yet); import rules can use it to avoid overwriting manual tweaks.
- Sprite rect vs bounds: Sprite.rect is in imported texture pixels and shrinks with the max size cap; Sprite.bounds keeps the world size. Fit objects by bounds.
- Never delete a .meta to "reset" a sprite: it holds the GUID and slice ids that prefabs point to. Re-slice through the importer (Sprite Editor data provider) instead.
- Re-slice keeping links: change the rect of the existing SpriteRect and keep its spriteID and name; a new SpriteRect gets a new internal id and prefab links break.
- Sprite Editor Outline/Physics Shape: a tight mesh outline cuts transparent pixels and reduces overdraw.
- Sprite Editor slicing: Automatic, Grid By Cell Size, Grid By Cell Count; frames appear as sub-assets under the texture.
- PPU mismatch changes size: a 128 px sprite at 64 PPU is 2 units, at 256 PPU half a unit. Keep one PPU across a set.
- Sprite Mask shows sprites only inside (or outside) its shape; Sprite Shape draws fills and edges along a spline.
- 9-slice sprites stretch one small asset to any size without distortion of corners.
- Sprite Renderer color tints the sprite through vertex color; Flip X/Y flips only the drawing, not the colliders.
- Keep ETC2 as Android fallback until the device matrix proves every target supports ASTC.
- Same source sprite in several atlases = duplicated texture memory; check with Analyze and build reports.
- A sprite drawn at 200 px needs a 256-512 px source, not 2048; size from the largest on-screen size on the highest-DPI device.
- Straight alpha blend: SrcAlpha, OneMinusSrcAlpha. Premultiplied: One, OneMinusSrcAlpha. Mixing them gives dark or bright halos.
- Halos: dilate edge colours into transparent pixels, add atlas padding/extrude, inspect the packed atlas texture, not only the PNG.
- Full Rect for UI, 9-slice and small sprites; Tight mesh for large irregular world sprites with lots of transparency (fewer pixels, more vertices).
- Atlas variant with Scale 0.5 halves width and height (about a quarter of the memory) for low-end tiers; do not ship both parent and variant.
- Late binding: SpriteAtlasManager.atlasRequested lets code load a remote atlas when a sprite needs it; Include in Build off for remote atlases.
- Atlas Pack Preview shows empty space; one oversized sprite can force the whole atlas to a bigger size.
- Big land and background art stays out of item atlases; split into tiles or use 9-slice/tiling where possible.
- In a Unity 6 2D project a new PNG imports as Sprite Mode Multiple; an import rule that forces Single on every import wipes artists' slicing.
- Changing importer settings on an existing asset: call AssetDatabase.WriteImportSettingsIfDirty then ImportAsset with ForceUpdate, and check the .meta or sprite count after.
- Items that each draw a shadow then a body belong in ONE atlas with their shadows; two atlases would switch texture on every item and break batching.
- Keep sprites whose shaders read the sprite UV (liquid fill, water shimmer) out of atlases - packing changes their UVs.
- Very large art (a 2241 px island base) and tiny gradient textures (4x4 sky) stay outside atlases.
- Measure atlas pages after packing: one theme atlas filled one 2048x2048 page with 58-67 sprites; overflow to a second page doubles the memory.
- Art bigger than the atlas max size (a 2252x2516 island on a 2048 atlas) cannot go into it whole; keep it separate or split it.
- SpriteRenderer Draw Mode Simple ignores the Size field; drawn size = sprite bounds x transform scale. Size matters only in Sliced/Tiled.
- Find duplicate sprites by content hash, not by name; 13 files were 6 unique pictures.
- Import settings audit: Bilinear + Compressed blurred 59 of 90 UI sprites while every behaviour test stayed green; check pixels, not only logic.
- Copying a sprite from a sheet copies the whole texture; cut the frame by sprite.rect.
- Solid fills cost one pixel: a 293x1 strip stretched by the RectTransform height, or a 1x1 sprite scaled (1, 241, 1) for a thread.
- Cutting a part off (balloon thread from balloon) saves atlas area and lets the part animate separately.
- One white sprite tinted with Image.color gives every colour variant (green slime, purple fog) from one texture.
- Soft art (fog, glow, moon) can be stored at lower resolution and shown with a bigger rect (x1.5-x3); blur hides the upscale.
- One light cone drawn white/light with a coloured semi-transparent Image.color replaces three baked lamp pictures.
- Measure the pixel budget: 56 as-is PNGs = 295% of a 1024 atlas; the optimised set = 35 sprites, 89%, 3.3x fewer pixels.
- Atlas padding (2-4 px) around each sprite stops neighbours bleeding in with bilinear filtering.
- Downscale per sprite by its on-screen importance: big hero art keeps more resolution, background stars can shrink hard.
- Trimming transparent borders must store the offset and original size, or sprites shift when placed back.
- A packer must fail loudly when sprites do not fit; silent dropping leaves a hole in the layout.
- Test an atlas by round-trip: rebuild each sprite from atlas + manifest and compare pixels with the input (catches flipped Y and rotation bugs).
- Text as TMP instead of baked pixels removes it from the atlas completely.
- Finding 9-slice borders from pixels: subtract atlas padding first, or every border shifts by the padding.
- An AssetPostprocessor (OnPreprocessTexture) applies import rules automatically: UI sprites without mipmaps, Clamp, right compression.
- Few atlases for one screen (1-2) keep draw calls low; large backgrounds can stay separate.
- Pixel art: one Pixels Per Unit for the whole game, Point filter, no compression, Pixel Perfect Camera; fractional PPU values mean auto-fit, not a pixel grid.
- Baked flipbook atlases for pixel art: compression None, Point filter, no mipmaps, applied by an AssetPostprocessor on import.
- Pixel Perfect Camera snaps SpriteRenderers; ParticleSystem and custom quads need their own snapping.
- Size each merged atlas sheet to its content, rounded to a power of two; a mostly empty 2048 sheet wastes 4 MB.
- Trimming animation frames: trim symmetric borders (keep the larger margin on both sides) so the frame centre does not shift.
- Mobile builds use platform import overrides (Android, iPhone); without explicit overrides Android defaults to ASTC compression.
- Pixel-art flipbook frame sizes at 32 PPU: 16x16 sparks, 32x32 small impact, 48x48 standard explosion, 64x64 big effect, 96x96+ hero only; choose by pixels on screen.
- Flipbook atlas gutters: Point + no mips + integer scale 0-1 px gutter + 1 px extrusion; blending/motion vectors 2 px gutter + 2 px extrusion; clamp UVs inside the tile (half-texel inset).
- A shader that assumes a uniform grid (uv / columns) breaks if physical gutters are added between frames; include the gutter in the tile math.
- Transparent texels in padding should carry extruded RGB (alpha 0), not black, or bilinear/premultiplied sampling shows dark halos.
- Pixel Perfect Camera setup: Assets PPU = sprite PPU, Pixel Snapping on, Point filter, no compression, no mips, integer scaling, editor grid snap = 1/PPU.
- Pixel snapping with a moving camera: snap in screen space for final pixel alignment, in world space for grid gameplay; snap a quad's centre, not each vertex; never round in two places (camera and shader).
- Pixel Perfect Camera Upscale Render Texture renders at the reference resolution and scales up; shader snapping must then use the reference size, not the screen size.
- Camera follow in pixel art: quantise camera movement to pixel size to avoid sprite jitter against the background.
- Pixel Perfect Camera filter: Point keeps pixels sharp but shimmers on sub-pixel motion; Retro AA reduces shimmering with slightly softer edges.
- Pixel-art textures on mobile: no compression (RGBA32) for key atlases; if compression is required ASTC 4x4, never 6x6/8x8 (block artifacts smear 1-2 px details). Default Normal quality can pick 6x6.
- With Pixel Perfect Camera, do not add a second snap in the shader; choose one snapping authority (PPC, or your own code + shader), never both.
- Uncompressed RGBA32 memory: 2048x2048 = 16 MB, 4096x4096 = 64 MB, 640x640 = 1.6 MB; keep many atlases at 2048 or below.
- Texture2D.Compress at runtime is slow, CPU-bound and lower quality than import-time ASTC; compress at import.
- Set sprite pivots intentionally in the Sprite Editor and document exceptions; pivot differences move markers and FX.
- Halos around FX usually come from wrong RGB in transparent pixels or a baked white background; fix the source image before shader tweaks; Clamp wrap, no mips for small 2D FX.
- ASTC starting points (non-pixel art): island and items 6x6, sky and shadows 8x8, UI and small FX 4x4-6x6; thin outlines or pale edges may need 4x4.
- One atlas per coherent content family (not mechanically per group): local UI atlas never includes remote seasonal art; default max 2048 on mobile; padding 2-4 px without mips, more for soft FX.
- Atlas packing: tight packing can save area for irregular world sprites (test edges); UI rectangular and without rotation (rotation breaks 9-slicing); never pack a flipbook sheet into an atlas.
- For sprites packed into a Sprite Atlas, the atlas's platform overrides (format, max size) decide the final texture; set source textures to no compression to avoid double compression.
- 9-slice: keep the full PNG and set borders (editable, safe with filtering); trim to corners + 1 px only for uniform middles and stable art.
- Sliced sprites in an atlas: Mesh Type Full Rect (tight meshes can sample neighbours), enough padding, no rotation.
- Atlas grouping for a small screen: one UI atlas (ASTC 6x6, 4x4 for small text/icons), one world atlas (6x6), a separate soft atlas for shadows/gradients if they can use 8x8.
- Generate Physics Shape on the sprite importer: turn it off when the sprite never touches Physics2D.

2D SORTING AND RENDER ORDER:
- Sorting Group on a UI-less prefab keeps its parts together; Sort At Root makes it ignore parent Sorting Groups.
- Sorting Group: makes a multi-sprite object sort as one block, so a building's parts do not interleave with another building.
- Sorting Layers and Order in Layer decide 2D draw order; keep few layers (e.g. background, world, FX back, FX front, UI).
- Sorting Layer wins over Order in Layer; Order in Layer only breaks ties inside one layer.
- Camera stacking in URP: Base camera + Overlay cameras; draw order set by the stack and Priority, not Depth as in Built-in.
- Canvas sorting uses the Canvas Sort Order/Sorting Layer and hierarchy order, not Order in Layer of sprites.
- Draw order: Sorting Layer, then Order in Layer, then render queue, then camera distance along the Transparency Sort Axis.
- Sprite Sort Point Pivot for grounded objects (characters, trees, buildings), Center for flat decorations, icons, projectiles.
- Reserve order ranges inside a Sorting Group for body, shadow, props and local effects.
- Sorting Groups fix correctness but can limit batching; one group per logical object, not per sprite.
- Document sorting as number ranges (World background, objects, world FX, world UI).
- Debug sorting: Frame Debugger draw order, exaggerated test orders (-1000/0/1000), temporarily disable Sorting Groups and custom shaders.
- URP camera stacking: every camera renders into the target again - more overdraw and bandwidth; remove unused layers from each camera's culling mask.
- Custom Sorting Layers live in ProjectSettings/TagManager.asset; a prefab only stores the layer ID. For content moved between projects, one Default layer plus Order in Layer ranges (sky -3100, island -2000, items -71..628, FX 1000, markers 2000, UI 3000) travels safely.
- Put a SortingGroup on each item prefab so its body, shadow and FX sort as one unit; keep order inside explicit and do not sort 2D by Z.
- In uGUI hierarchy order is draw order: overlapping neighbours must be ordered so the one behind comes first.
- Create VFX sorting layers (VFX_Back, VFX, VFX_Front) at project start; adding them later means editing every prefab.
- A MeshRenderer quad respects sortingLayer and sortingOrder in 2D without a SortingGroup; SortingGroup is for hierarchies. A different sorting layer beats any order.
- URP 2D sorts transparent renderers by layer, order, queue, then distance; a shader with ZWrite On can break that order.
- Keep per-part sortingOrder inside one effect (a stack of parts 5-35) when moving effects to a VFX sorting layer.
- Effects attached to a character (aura, weapon trail) go under the character's SortingGroup so they sort with it; standalone effects just use the FX sorting layer.
- In URP 2D a batch breaks on a different material, sorting layer or order in layer between neighbours in draw order.
- MeshRenderer has no Sorting Layer / Order in Layer fields in its Inspector; set renderer.sortingLayerName/sortingOrder from code, a custom inspector, or a SortingGroup.
- Sorting tools by purpose: Sorting Layers for broad categories, a SortingGroup per item as an atomic unit, order in layer (or Y-based order on the group root) for item-to-item depth; not Z.
- Y-based sorting: lower on screen = higher order (order = -round(y * precision)) applied to the group root, keeping children's internal order.
- Order inside an item group, e.g. shadow -20, object 0, FX 20, marker 40; test FX on the largest item.
- A child inside an item's SortingGroup cannot sort above renderers outside the group; markers that must always stay on top live in a separate overlay root (or a nested group with Sort At Root).
- Put an item's root pivot at its ground contact point so Y sorting reflects where it touches the ground, not its height.
- SortingGroup.sortAtRoot on a nested group makes it ignore parent groups and sort against root-level renderers by its own layer/order - a marker inside an item prefab can stay on a WorldMarkers layer above everything.
- A dozen SortingGroups are cheap on mobile; sorting cost matters at hundreds; check "reason for not batching" in the Frame Debugger if groups split background batches.
- Y-sorting static sprites with no script in URP 2D: Renderer 2D Data > Transparency Sort Mode = Custom Axis (0, 1, 0) (the Graphics-settings field is for the built-in pipeline); sprites must share sorting layer and order; set Sprite Sort Point = Pivot with a bottom pivot, or sorting uses the sprite centre.
- Particles in front of a Screen Space - Camera Canvas: put them on a sorting layer above the Canvas's layer (e.g. ScreenUI_FX); plane distance matters only when layer and order tie.
- Particle Renderer has Sorting Layer and Order in Layer like a SpriteRenderer; Sort Mode (By Distance, Oldest/Youngest in Front, By Depth) orders particles inside one system; Sorting Fudge biases the whole system against other transparents.

PERFORMANCE AND PROFILING:
- Draw call: one draw call = one material shown on screen. Less draw calls = faster game. Ways to lower: atlases, batching, same material, less UI objects.
- Batching: Unity joins objects with the same material into one draw call. Static batching for static objects, dynamic batching for moving ones. For UI use atlases and one canvas per group.
- Performance: profiler first (Unity Profiler, Memory Profiler, Frame Debugger). Find the biggest problem, then fix it. Do not guess.
- GC allocations: avoid allocating every frame (string concat, LINQ, new lists in Update); use the Profiler's GC Alloc column to find them.
- Update calls: thousands of MonoBehaviour.Update calls cost; use one manager that updates many objects, or events instead of polling.
- Overdraw view (Scene view draw mode) shows stacked transparent pixels; red/white areas are expensive on mobile.
- Target frame rate: Application.targetFrameRate sets it on mobile (default is 30 on many devices); 60 fps costs noticeably more battery and heat.
- SetPass calls: one per material change. Fewer materials (atlases, shared materials) = fewer SetPass calls.
- GPU instancing batches many copies of the same mesh and material; enable it on the material.
- Fill rate: stacked transparent quads cost per pixel; trim sprites and particles to their visible area.
- URP 2D mobile: disable MSAA, shadows and Depth Texture when not used - each costs a pass or bandwidth.
- Post-processing needs a Volume with a Volume Profile and Post Processing enabled on the camera; each effect is a full-screen pass.
- Profiler counters are available in the Editor and Development Builds; profile a development build on the device, not only the Editor.
- Asset Loading profiler module shows bytes read per type (textures, meshes, audio) and per asset, with load time.
- SRP Batcher: keeps material data on the GPU and batches draws that use the same shader variant; the Manual lists MeshRenderer and SkinnedMeshRenderer, not particles - check other renderers in the Frame Debugger.
- Frame Debugger shows every draw call and why a batch was split ("different shader", "different material", "MaterialPropertyBlock").
- Real-time shadows render the scene again into a shadow map; soft shadows cost more than hard shadows.
- Animator Culling Mode Cull Completely stops off-screen animators; big saving for crowds and hidden UI.
- Profiling routine: development build with Autoconnect Profiler, real low-end device, same quality settings as release, capture after warm-up.
- Record device, OS, resolution, build hash, battery and thermal state with every capture.
- GPU tools: Xcode GPU Frame Capture (iOS/Metal), Android GPU Inspector, RenderDoc on debuggable Android builds.
- Frame Debugger: step to the first draw where a batch breaks; the difference (material, texture, stencil, sorting, Canvas) is the cause.
- 60 fps = 16.67 ms per frame; aim CPU and GPU each around 8-12 ms for headroom. A stable 30 beats an unstable 60.
- Compare median, 95th/99th percentile and worst frame, not only average FPS.
- Prove a fix with Profile Analyzer: same device, scene, input and duration before and after; report as a delta (14.2 ms -> 10.8 ms).
- GC.Alloc column with call stacks finds allocations; allocations in scrolling, timers and gameplay matter more than in rare menu builds.
- Release checks: automated smoke scenes (boot, home, popup, event, reward), all quality tiers, sustained thermal play, compare with the previous release.
- Run In Background off: when the editor or app loses focus the player loop stops; if "nothing moves" in Play, check Time.frameCount first.
- Legacy Sprites/Default and legacy Particles/Additive materials are not SRP Batcher compatible; switch FX to URP Particles shaders.
- Physics2DRaycaster + Collider2D per item only if items are tapped in the world; remove them when interaction moved to UI.
- One CanvasGroup alpha on a subtree is simpler than animating 20 Image colours, but still touches every child's vertices when it changes.
- Check UI batching with the Frame Debugger (why a batch broke) and the Profiler UI module (batches, vertices, Canvas rebuild time).
- Profile on a real Android device: Development Build, connect Profiler; report Canvas rebuild ms, batches/draw calls, UI vertices, atlas memory, frame time, with the device model.
- Merging textures into one atlas does not save memory; it saves material switches (SetPass calls). Measure batching gains in materials and SetPass calls, not bytes.
- Per-object data through MaterialPropertyBlock keeps one material, but in URP a renderer with a MaterialPropertyBlock is not SRP Batcher compatible; for sprites/particles prefer vertex colour or custom vertex streams.
- Heavy procedural fragment shaders (Voronoi, many noise samples) cost fill-rate per pixel per frame; that lag is not fixed by fewer draw calls.
- Put a performance threshold in tests with headroom (about 2x the measured value), not right at it, or it flickers instead of catching regressions.
- In 2D URP the VFX risk is screen area and stacked layers, not effect count: 3 effects covering 50% each = 150% overdraw; 30 small ones can be cheaper.
- Opaque Texture costs twice: one full-frame copy per frame, plus every effect pixel that samples it.
- Profiler: GPU time above CPU time points at overdraw or heavy shaders; CPU above GPU points at scripts, Instantiate/Destroy, physics.
- Budget screen-space effects (Scene Color distortion, blur): about 1-2 per frame.
- An optimisation without numbers before and after is a claim, not a result.
- Enter Play Mode Options (disable domain/scene reload) speed up Play entry, but static fields keep old values; reset statics manually ([RuntimeInitializeOnLoadMethod]).
- VFX optimisation order: remove what is not visible, cut overdraw, simplify shaders, then particle counts and draw calls, then system-level work.
- Trim empty transparent borders of VFX textures; transparent pixels still cost fragment work inside the quad.
- Thick smoke: 5-10 larger well-trimmed sprites with a clear shape instead of many soft full-screen layers; alpha clip / dither is cheaper than soft alpha where the style allows.
- Profiler checks for VFX: CPU vs GPU usage, GC Alloc during spawns (fix with pooling), Batches/SetPass (unify materials), FPS drop only with Bloom (raise threshold, lower intensity/scatter).
- Overdraw symptoms: few effects but FPS drops; halving effect scale restores FPS; moving it off camera restores FPS; overlap makes it worse.
- Find the costly Shader Graph node: duplicate the graph as _DEBUG, remove Scene Color, then Scene Depth, then noise nodes, then extra texture samples, re-measure GPU time after each.
- A VFX stress-test scene (spawn 10/50/100/500, quality toggle, active count, FPS, particle count) shows which effect breaks the budget.
- Many identical short effects: Particle System + Texture Sheet Animation with one atlas and one unlit material beats an Animator per effect (50 Animators cost CPU for state machines).
- Changing SpriteRenderer.sprite between frames of the same atlas keeps batching; different atlas pages, material instances, keywords, blend modes, sorting interleave or MaterialPropertyBlock break it.
- Dynamic batching merges small meshes into one draw call; SRP Batcher keeps separate draws but makes their setup cheap. For tiny sprite quads dynamic batching can win.
- Flipbook motion blend costs roughly 2-4x a plain flipbook (two colour + two vector samples); use it only on large main layers, simple blend or none on low quality.
- Per-object colour options: a few shared material variants (4-8 colours), particle colour / vertex colour, GPU instancing with instanced properties, or MaterialPropertyBlock (drops SRP Batcher). GPU instancing and SRP Batcher are alternative paths.
- Benchmark effects on real devices (Adreno and Mali classes, Vulkan/Metal) with the same scene per backend; judge GPU frame time and 99th percentile after thermal load, not average FPS.
- URP Rendering Debugger has an Overdraw view: isolate one effect on a dark background and compare variants (hard flipbook, blended, bigger quads).
- Profiling tools: Rendering Debugger Overdraw (where), Frame Debugger (draw order, passes, batches), Profiler (CPU/GPU time), device captures (Snapdragon Profiler / Android GPU Inspector, Arm Mobile Studio, Xcode GPU Frame Capture) for real mobile cost.
- Editor overdraw view is an approximation; mobile tile-based GPUs behave differently - confirm in a Development Build on the device.
- Benchmark procedure: VSync off, fixed resolution, warm-up, record 300-600 frames, drop the first, report median and p95 GPU time, repeat after a thermal run.
- A large transparent quad costs fragments for its whole area even where alpha is 0; use tight meshes (Sprite Mesh Type Tight), smaller frames, split core and smoke.
- Shader.SetGlobalFloat once per frame is cheap; cache Shader.PropertyToID; avoid per-object setters on hundreds of renderers; global time + per-object phase (vertex colour / custom data) replaces per-object time.
- In URP, SRP Batcher takes priority over GPU instancing for compatible shaders; instancing applies when the SRP Batcher path is not used for that renderer.
- 50 particle effects with one mesh, one material and one sorting layer can render in 1-2 batches; each extra material, shader variant or sorting layer adds batches.
- Game view Stats (Batches, SetPass calls) with effects on and off, and at 0/10/50 instances, shows how batching scales.
- ParticleSystem.Play/Stop/Clear on existing systems allocate no managed garbage; GC comes from Instantiate/Destroy, new collections in Update, closures, strings, LINQ.
- UnityEngine.Pool.ObjectPool<T> (createFunc, actionOnGet, actionOnRelease, actionOnDestroy, defaultCapacity, maxSize) and a hand-made Stack<T> pool are both GC-free once prewarmed.
- A shared mesh across many prefabs saves memory; SRP Batcher cares about shader and material, not the mesh; GPU instancing needs the identical mesh.
- Profile VFX Graph with the VFX.Update / VFX.Dispatch markers (CPU) and the GPU module; ProfilerRecorder can read markers in tests.
- Living island, cheapest first: Animator motion of existing sprites, a few overlay sprites with alpha, small particle systems, sprite-sheet animation, custom shader scrolling, big transparent particle fields.
- Report FX cost at idle and at peak build: CPU/GPU frame time, draw calls, SetPass, batches, particle counts, overdraw note, texture memory, GC during the sequence - measured, never invented.
- Expensive cloud fix order: smaller quad, fewer overlapping particles, tighter crop, lower texture resolution, fewer particles, shorter life, no soft particles/lighting/distortion, Unlit, recheck batching, measure again.
- Update TMP numbers with SetText("{0:#,0}", value) (no garbage) instead of text = value.ToString() every frame.
- Read render stats in code with ProfilerRecorder ("Draw Calls Count", "SetPass Calls Count", "Batches Count"); UnityEditor.UnityStats is undocumented and unreliable.
- Pooling is for frequent spawns; a handful of short-lived UI icons per session can be instantiated directly.
- Motion must be scaled by Time.deltaTime (speed per second, not per frame), or objects move slower when the frame rate drops.
- FixedUpdate runs on Time.fixedDeltaTime (default 0.02 = 50 per second): zero or several fixed steps per frame; a smaller step = more precise physics, more CPU.
- Time.maximumDeltaTime (default 0.333 s) clamps deltaTime after a long hitch, so objects do not jump through walls; Time.time falls behind real time by the clamped part.
- LayoutRebuilder.MarkLayoutForRebuild(rect) rebuilds at end of frame, once, not immediately; call it in setters that change layout and in OnEnable/OnDisable/OnRectTransformDimensionsChange.
- Particle GPU instancing: Renderer mode Mesh + Enable GPU Instancing + an instancing shader (Particles/Standard Surface or #pragma target 4.5); all instances go into one buffer.
- Particle Lights module creates real-time lights for a Ratio of particles; always set Maximum Lights, real-time lights (and their shadows) are expensive.
- Particle Culling Mode: Pause when off screen is cheapest; Pause And Catch-up can spike on return; Always Simulate for one-shots like fireworks.
- Custom Profiler counter: ProfilerCounterValue<int> from the Profiling Core package, in a ProfilerCategory; FlushOnEndOfFrame + ResetToZeroOnFlush send and reset it every frame.
- Profiler counters can be shown in a release build through your own UI (Profiler window is not available there).
- Profiling Play mode: EditorLoop time lands in Others; switch the Profiler target to Editor to see what the Editor itself costs.
- Editor-only samples (GetComponentNullErrorWrapper, CheckConsistency, prefab checks) show as EditorOnly [...]; they do not exist in a build, usually ignore them.
- Script markers: BehaviourUpdate = all Update methods, CoroutinesDelayedCalls = coroutines after their first yield, FixedBehaviourUpdate = FixedUpdate, ScriptRunBehaviourLateUpdate = LateUpdate.
- WaitForTargetFPS / Gfx.WaitForPresentOnGfxThread mean waiting: check the render thread in Timeline; time in Gfx.PresentFrame = GPU-bound, time preparing commands (Camera.Render) = CPU-bound.
- Gfx.WaitForCommands on the render thread means it is idle waiting for the main thread = main thread is the bottleneck.
- GC.Alloc samples = managed allocations that feed the garbage collector; GC.Collect pauses the game (up to hundreds of ms); Incremental GC spreads it over frames.
- Mono.JIT = first-call compile cost of a method under Mono (IL2CPP has none).
- JobHandle.Complete is a sync point; enable Call Stacks and Flow Events in Timeline to find where it waits.
- Avoid several Animators under one Transform root: transform writes are grouped per root, so they cannot run in parallel.
- Legacy Animation AddClip/RemoveClip/Clone at runtime triggers RebuildInternalState (rebinding all curves) - expensive, avoid in gameplay.
- AsyncUploadManager.AsyncBufferResized warning = GPU upload buffer too small; raise Async Upload Buffer Size in Quality settings.
- Deep Profiling instruments every script method: finds hidden costs but adds big overhead and distorts timings; prefer Call Stacks on GC.Alloc instead.
- Call Stacks button records the call stack of GC.Alloc (and Malloc, JobHandle.Complete) samples without Deep Profiling; enable it before recording the frame.
- Editor profiling tips: maximize the Game view in Play mode, close extra windows, use the Standalone Profiler (own process), add only the modules you need, turn Live off; F9 toggles recording.
- CPU Usage views: Timeline shows all threads on one time axis (use it for waits and jobs); Hierarchy groups by call stack with Total/Self %, Calls, GC Alloc, ms; Raw Hierarchy keeps each call separate.
- Hierarchy Self vs Total: Camera.Render can be 16% Total but 0.2% Self - the cost is in what it calls; sort by Self to find the real hot function.
- Keep GC Alloc per frame at zero during gameplay: more allocation = more frequent and longer GC.Collect, and a bigger heap.
- GPU Usage Profiler works in Play mode and builds only, not for the Editor, and not with Graphics Jobs enabled.
- Stats window: Batches = draw call batches; Saved by batching; SetPass = shader pass switches (CPU cost of binding shaders); Tris/Verts matter on low-end phones.
- Batches break when the render state changes: share materials between objects to keep batches low.
- First use of a shader variant can hitch while the driver builds it; prewarm with ShaderVariantCollection.WarmUp / Preloaded shaders, or on DX12/Metal/Vulkan by rendering materials off-screen.
- Shader runtime tips: lookup textures instead of pow/log/sin, built-in normalize/dot, move math from fragment to vertex or to C#, avoid discard and ColorMask on mobile.
- SRP Batcher cuts render-state changes, not draw calls: materials stay in GPU memory; objects batch if they share the shader variant (materials may differ).

MEMORY, BUILD SIZE, LOADING:
- Memory: textures use most memory. Use correct size, compression (ASTC for mobile), remove unused assets. Atlases waste space if not packed well.
- Build size: remove unused sprites, compress textures, split levels with Addressables/AssetBundles.
- Memory Profiler snapshots show every texture, mesh and audio clip with size; compare two snapshots to find leaks.
- Unused assets stay in memory until unloaded: Resources.UnloadUnusedAssets or releasing Addressables handles frees them.
- Audio import: long music as Streaming, short SFX as Decompress On Load or Compressed In Memory; force mono for most SFX.
- Scene loading: LoadSceneAsync with allowSceneActivation shows progress and avoids freezes.
- Texture memory = width x height x bytes per pixel (+33% with mips); a 2048 RGBA32 texture is 16 MB, ASTC 6x6 about 1.8 MB.
- Atlas waste: a quarter-full 2048 atlas still costs the full texture memory. Aim for well-filled pages.
- Some compressed formats (PVRTC, ETC1) need power-of-two or square sizes; ASTC does not, but multiple-of-4 sizes compress cleanly.
- Max Size in the texture importer scales the imported texture without changing the source file.
- Mipmaps add about 33% memory but reduce shimmer and bandwidth at distance; turn them off for UI and screen-sized 2D.
- Texture Type must match use: Sprite (2D and UI) for Image/SpriteRenderer, Default for 3D and RawImage.
- Feature memory: snapshot before load, at worst case, after release; compare A->B for cost, B->C for what stays behind.
- Repeat open/close cycles: memory that grows every cycle is a leak; memory that stays flat after the first cycle is a one-time cost.
- Budget per feature and tier: peak incremental memory, residual memory, download size, load time; a starting target is 20-50 MB peak on low-end.
- Compressed disk size is not runtime memory; always read resident memory in the Memory Profiler.
- Build size: Build Report for the biggest assets, managed code stripping, strip unused engine modules and shader variants, move optional content to remote Addressables.
- Loading spikes come from download, decompression, texture upload, shader compilation, big Instantiate bursts or Canvas rebuilds - profile to see which.
- Resources.UnloadUnusedAssets is expensive; call it at controlled transitions, not on every popup close.
- Progressive loading: shell first, main content second, decoration and VFX last; measure time to first frame and time to interactive.
- Application.lowMemory: release optional content and caches, stop preloading, save transient state; do not run heavy cleanup repeatedly.
- UI opening spikes: many instantiations, dynamic TMP atlas growth, first-use shader compile, nested layouts - fix with preload, pooling and progressive activation.
- Texture memory budget on mobile depends on the device class; low-end phones (2-4 GB RAM) get risky past roughly 100-150 MB of textures.
- Split big art: sky, island base and objects as separate textures (sky can be lower resolution, objects atlased); 2048 max for a fixed home screen, 4096 only if measured visible loss (4x texels).
- Read/Write Enabled keeps a CPU copy of the texture and increases memory; turn it off unless code reads pixels. Mipmaps off for UI, fixed-size 2D sprites and sheets.
- ASTC/ETC control GPU memory; LZ4/LZMA control bundle size on disk and download; Crunch shrinks texture payload but adds runtime decompression - do not use by default for sprites.
- Prove optimisation with a before/after table: build size (Build Report), bundle sizes (Addressables report), texture memory (Memory Profiler), CPU/GPU time, draw calls, SetPass, batches, peak particles, duplicate dependencies; N/A where not measured.
- Report measurements with their conditions (e.g. "measured with placeholder art before atlas rebuild") and re-measure after changes when possible.
- Asset Loading Profiler module is off by default; enable it, then Analyze Markers shows each load with source (file, AssetBundle), asset, type, size and duration.
- Reading AssetBundleRequest.asset/allAssets before isDone stalls the main thread until the load finishes (Profiler warns).
- Textures usually take most build size: use compressed formats, then lower Max Size per texture until it looks worse in the Game view (source file untouched).
- Unity converts assets to its own formats at build: a layered PSD and an exported PNG give the same build size, keep whatever is convenient.
- Unused assets are stripped from the build, except scripts and everything in Resources folders; keep Resources minimal, prefer AssetBundles/Addressables.
- Mesh Compression only shrinks the file, not runtime memory; Animation compression (keyframe reduction) shrinks both - keep it on.
- .NET Standard 2.0 API compatibility level keeps the managed library smaller than .NET 4.x (Framework).
- The same shader referenced from several AssetBundles can be duplicated in each bundle (more memory, broken batching); put shaders in a shared bundle loaded first.
- Player > Shader Variant Loading: Default chunk size and Default chunk count limit how much decompressed shader data stays in CPU memory on low-memory devices.

ADDRESSABLES AND REMOTE CONTENT:
- Addressables: Unity system to load content by address. Load what you need, release when done. Good for big levels, DLC, live content. Better than Resources folder.
- Addressables groups: a group is a set of assets built into one or more AssetBundles. Group by how content is used at runtime (loads together, updates together), not by folders.
- Local vs Remote: local groups ship inside the app build. Remote groups are built to a server path and downloaded at runtime. Core UI, fonts and shaders stay local; seasonal or level content can be remote.
- Profiles: a profile holds Build Path and Load Path variables (Local/Remote). Switch profile for dev, staging, production servers without touching groups.
- Content catalog: a JSON/binary list of all addresses and bundles. With a remote catalog the app can see new content without an app update.
- Content update: "Update a Previous Build" builds only changed remote content, using the addressables_content_state.bin from the release build. Keep that file for every shipped version.
- Bundle Mode: Pack Together = one bundle per group; Pack Separately = one bundle per entry; Pack Together By Label = one bundle per label. Too many tiny bundles cost overhead; one huge bundle forces big downloads.
- Compression: LZ4 for local/cached bundles (fast load, chunk-based); LZMA gives smaller downloads but must be decompressed fully. Remote bundles are often LZ4 because the cache stores them anyway.
- Loading: Addressables.LoadAssetAsync<T>(key) returns an AsyncOperationHandle. InstantiateAsync creates the object and tracks it.
- Releasing: every Load needs a Release (Addressables.Release(handle)); every InstantiateAsync needs ReleaseInstance. The bundle unloads only when its reference count reaches zero.
- Labels: tag assets with labels (e.g. "winter_event") to load or download a whole set by one key.
- Download size: Addressables.GetDownloadSizeAsync(key) tells how many bytes are missing. DownloadDependenciesAsync pre-downloads content, e.g. behind a loading screen.
- AssetReference: a serialized field that points to an addressable asset by GUID. Designers drag assets in the Inspector; code loads them async. Safer than string addresses.
- Duplicate dependencies: an asset used by two groups but not addressable itself is copied into both bundles. Analyze rule "Check Duplicate Bundle Dependencies" finds it; fix by making the shared asset addressable in its own group.
- Play Mode Script: "Use Asset Database" (fast, no build), "Simulate Groups", "Use Existing Build" (real bundles). Test the existing build before release.
- Remote testing: test missing files, slow network and offline start, not only the happy path. Show a retry, not a frozen screen.
- Resources folder: everything inside is always in the build and loaded into an index at startup. Addressables replaces it for content that should load on demand.
- AssetReferenceSprite / AssetReferenceGameObject / AssetReferenceT<T> restrict what can be dragged in and load the right type.
- Scenes can be addressable too; Addressables.LoadSceneAsync loads them additively or single.
- Remote load path uses profile variables like {RemoteLoadPath}; the CDN URL can differ per environment without rebuilding content.
- Caching: downloaded bundles are stored in the Unity cache; Caching.ClearCache or Addressables.ClearDependencyCacheAsync frees them.
- Check for catalog updates at start (Addressables.CheckForCatalogUpdates / UpdateCatalogs) so the app sees new remote content.
- Event Viewer / Addressables Profiler module shows loaded bundles and reference counts - the tool to find leaks.
- Group schema: Content Packing & Loading (build/load path, bundle mode, compression, include in build) and Content Update Restriction.
- Keep remote bundles medium-sized: small enough for fast download, big enough to avoid thousands of requests.
- Keep boot UI, essential shaders and fallback fonts local so the app starts offline; event art, VFX, audio in remote groups.
- Group assets that update together, so a small change does not rebuild a large bundle.
- Update order on the CDN: upload bundles first, the catalog and hash last; never delete files older clients still reference.
- Cannot Change Post Release: changed assets move to new update bundles. Can Change Post Release: the whole affected bundle is rebuilt and re-downloaded.
- Changing a group's update restriction after release breaks update assumptions; do it only with a new full build.
- Unity CCD vs own CDN: both set through profile Build Path / Load Path; keep staging and production buckets separate, versioned folders or cache-busting.
- CI must build with an explicit profile, never the developer's active Editor profile.
- Bundle compression (LZ4/LZMA) and CDN HTTP compression are separate layers; platform-compressed textures barely compress further.
- Releasing an asset may not free memory while another asset from the same bundle is still referenced.
- Test remote content: existing build + update, local HTTP server, cold install, cache miss, offline start, 404/500, interrupted download, old app versions.
- Keep shared shaders local; remote shader variants can stall on first use or be stripped.
- Never update a shader or component contract remotely that older clients cannot run.
- Without Assets/AddressableAssetsData/DefaultObject.asset the Groups window only offers "Create Addressables Settings"; that pointer file lives outside feature folders, so zip the full project or document it.
- The first playable screen must work without the network: bootstrap, loading screen, bars, fonts, common UI, base prefab, first island and first FX stay local; later islands, seasonal content and event banners go remote.
- Group by lifetime and update rhythm: Local_Core and first home content Pack Together; a shared FX group so textures are not copied into every item bundle; remote islands Pack Separately or by label; seasonal event Pack Together.
- Mark core groups Cannot Change Post Release and live content Can Change Post Release; a content update rebuilds only remote groups; code changes need an app update.
- Sprite Atlas ownership: make the atlas Addressable and not its source sprites, or keep a core atlas as local build content; never both.
- Analyze rules to run on the final layout: Check Duplicate Bundle Dependencies, Sprite Atlas to Addressable Duplicate Dependencies, Scene to Addressable Duplicate Dependencies, Resources to Addressable Duplicate Dependencies, Build Bundle Layout.
- Small local bootstrap scene loads the home scene (or modular island content) asynchronously; keep load handles in fields so they can be released.
- Release order when removing a content unit: disable consumers, ReleaseInstance instantiated objects (not only Destroy), release asset handles, unload the scene, clear cached references; Resources.UnloadUnusedAssets only at deliberate memory transitions.
- Addressables counts references but does not know you are done; the loader that owns a handle releases it at the content boundary; verify with a Memory Profiler snapshot after unloading.
- Reviewer red flags: everything in Default Local Group, "remote" groups without remote paths, every asset marked Addressable, Pack Separately everywhere, all islands Pack Together, synchronous loading, no release, Resources folder use.
- Demo remote content without a server: profile RemoteBuildPath = [Project]/AddressableBuilds/Remote/[BuildTarget], RemoteLoadPath = http://localhost/[BuildTarget], Build Remote Catalog on, Play Mode Script "Use Existing Build"; the build works, only runtime loads fail without a host.
- Several prefabs sharing one atlas in one group: Pack Together keeps the atlas in a single bundle; Pack Separately risks duplicating it unless the atlas is its own Addressable.
- One remote group per island (Pack Together), first island local; atlas and shared materials in their own shared group so other bundles depend on them instead of copying.
- Shaders used only from bundles can be stripped from the player; keep shared materials in an early-loaded core group and consider a ShaderVariantCollection there.
- Addresses are unique keys for single assets (LoadAssetAsync("Island_3")); labels tag groups of assets for bulk loads and downloads ("Island", "FX").
- Read group settings in editor code: group.GetSchema<BundledAssetGroupSchema>() (BundleMode, Compression, BuildPath/LoadPath); resolve paths for the active profile with ProfileValueReference.GetValue(settings).
- Analyze rules can run from code (e.g. new CheckBundleDupeDependencies().RefreshAnalysis(settings)); analysis does not build bundles.
- "Build Addressables on Player Build" can stay off for a demo if content is built manually (Build > New Build) and the ServerData output, catalog and Analyze results are shown.
- Audit checks worth automating: remote groups with non-http load paths, local groups with http paths, an atlas and its sprites both Addressable, one atlas used by local and remote groups, large Pack Separately groups, Resources assets also Addressable.
- AddressableAssetSettings.asset gets rewritten by Addressables itself (content hash, default paths) after opening the window or building; commit it as project configuration; ignore only build outputs.
- A scene in Build Settings that references an asset directly pulls it into the player; if the same asset is also in a remote group it ships twice - use an AssetReference or keep the asset local.
- Remote = content not needed on the first screen/session and likely to change after release (future islands, events, A/B variants, optional upgrades); first-session essentials stay local, optionally with a remote premium variant plus local fallback.

MOBILE:
- Mobile: keep textures small, compress audio, avoid many transparent layers, avoid big particle systems. Test on a real low-end device.
- Device testing: the Editor is not a phone. Profile on a real low/mid device; thermal throttling shows only after minutes of play.
- Aspect ratios: test at least a tall phone (19.5:9 or 20:9) and a tablet (4:3). Anchors + Canvas Scaler + Safe Area make UI hold.
- Safe Area: Screen.safeArea gives the area without notch and home bar. Put buttons inside it; backgrounds can go edge to edge.
- Texture compression: ASTC for modern iOS and Android (block size 4x4 = quality, 8x8 = small). ETC2 as Android fallback.
- Overdraw: many stacked transparent pixels (big particles, full-screen UI layers) are expensive on mobile GPUs. Keep transparent layers small and few.
- Build size: check the Editor build log (Build Report) for the biggest assets; store limits and download-over-cellular limits matter.
- Battery and heat: high frame rate, overdraw and post-processing drain battery and cause throttling; profile over several minutes.
- Resolution scaling: URP Render Scale lowers 3D render resolution while UI stays sharp.
- Adaptive Performance (Samsung/Android) can lower quality when the device gets hot.
- App size: Android App Bundle + Play Asset Delivery, iOS On-Demand Resources, or Addressables remote content keep the install small.
- Hit areas: buttons need a tap area of about 88-112 reference pixels even if the icon is smaller.
- URP is the recommended pipeline for mobile; the 2D Renderer adds Light 2D, Shadow Caster 2D and normal-map lighting for sprites.
- Input System: Input Actions asset + Player Input component map touches and sticks to actions; on-screen joysticks come from the Input System samples.
- Thermal and battery: render scale, overdraw, post-processing, particles and high frame rate cost the most; cap FPS in idle menus.
- Application.targetFrameRate is the mobile control; vSyncCount is generally ignored on mobile.
- Adaptive quality with hysteresis: lower render scale, particles and effects when frame time or thermal state stays high, restore slowly.
- Device tiers from measured GPU, CPU, RAM and thermal behaviour; tiers change polish, never gameplay readability.
- Editor surprises: desktop GPU formats and shader variants, no thermal throttling, no real safe areas, stripping that only happens in player builds.
- Camera fit for any aspect: orthographic size = max(content height, content width / aspect) / 2 from the bounds of the content without the sky; a fixed size that fits the narrowest target (9:20) also works.
- Safe Area root: move top bars below the notch instead of shrinking the whole Canvas; reviewers of mobile screens expect safe-area handling.
- Fit the camera for the narrowest target aspect (4:3 for width, 9:20 for height), not for the current Game view.
- VFX Graph on mobile: needs compute shaders and SSBO support (Vulkan/Metal, not OpenGL ES); check SystemInfo.supportsComputeShaders and graphicsDeviceType at startup and keep a Particle System / flipbook fallback.
- Treat world framing and UI anchoring as two separate problems: the camera frames a composition root; the Canvas Scaler + anchors + safe area handle the HUD.
- Save Game view resolution presets for a tall phone (1080x2400) and a tablet (2048x2732) and check every screen in both.
- Older Android devices may lack ASTC; plan ETC2 fallbacks or device tiers and do not claim coverage without device tests.
- Touch targets at least about 44 pt (iOS) / 48 dp (Android); make hit areas larger than the visible icon.
- A fixed orthographic size (height-locked) is a standard portrait choice: vertical framing stays constant, width varies; choose a narrowest supported aspect (9:21-9:22) and keep key art inside it ("safe width").
- Pixel Perfect Camera and Cinemachine are unnecessary for a static home screen; a plain orthographic camera with a stated reason is the clean answer.
- Test aspect ratios with the Device Simulator (Window > General > Device Simulator), which also shows safe areas and notches.
- Android and iOS enforce VSync or a default 30/60 fps cap; the Editor only simulates VSync with WaitForTargetFPS.
- Profile a phone: Development Build + Autoconnect Profiler, Build & Run; or Attach to Player in the Profiler window (Wi-Fi same subnet, or cable; Android also via adb).
- Remote profiling uses ports 54998-55511; open them in the firewall if the device does not show up.
- Use half (16-bit) precision in shaders on mobile: less memory, bandwidth and power; Metal maps it to real half, OpenGL to mediump.

ART PIPELINE (Photoshop / PSD to Unity):
- Naming conventions (prefix by type: UI_, FX_, SP_) make search, atlasing and addressable grouping by name easy.
- Export art at the size it is shown on the target screen (or 2x for high-DPI), not huge source size.
- Transparent PNG edges: bleed or pad colors around edges to avoid dark halos after compression and filtering.
- Keep source files (PSD) outside Assets or in Git LFS and import exported PNGs - unless the team uses the 2D PSD Importer on PSB files on purpose.
- 9-slice needs art with clear borders; set Sprite Border in the Sprite Editor, Image Type Sliced in UI.
- A folder per feature or content set makes Addressables groups and atlases easy to build from folders.
- AssetPostprocessor presets per folder (UI, FX, characters) give every new file the right settings automatically.
- PSD to Unity: export layers as PNG with their positions; layer order in PSD = sibling order in Unity (bottom layer first).
- Smart Objects in a PSD contain nested documents; rasterize or walk into them, or content is missed.
- Layer effects (shadow, glow) grow the exported bounds; place by the exported image position, not the raw layer box.
- Audit a PSD before import (naming, clipping masks, smart objects, hidden layers) so the import is predictable.
- PSD is not the final hierarchy: import gives the parts, then a prefab structure is built on top of them.
- PSD/PSB Importer (2D PSD Importer package) keeps layers as sprites for animation and parallax; flattened PNG for static UI.
- Export rules: logical reference size and 1x/2x, PPU, pivot, 9-slice borders excluding shadows and glows, padding, naming - with a sample package.
- Presets for importer defaults; AssetPostprocessor for path/name rules; both idempotent, with a report-only mode first.
- Avoid full-project searches inside import callbacks; they run for every imported file.
- Replace art at the same path to keep the GUID; renamed layers or slices are breaking changes for prefabs.
- Large PSD/PSB in Git LFS (with locking for single-editor files); document the source-to-runtime export path.
- PSD composites can contain a semi-transparent empty slot on purpose; compare with the layered composite before "fixing" art.
- PSD clipping-mask layers must be merged into their base before export, or the exported sprite shows the unclipped pixels.
- Check layer bounds before export: a bar background whose bbox is 6x wider than the canvas makes a huge texture; use a 9-slice instead.
- PSD type layers become TMP texts in Unity; identify the font early.
- Analyse a PSD recursively into Smart Objects: the top level is a list of placed instances, not the content (3 text layers on top, 26 inside).
- One Smart Object document can be shared by many instances; editing its contents changes every copy at once.
- Illustrator (.ai) Smart Objects are rendered only by Photoshop itself; Python PSD readers cannot rasterize them.
- Find PSD layers by LayerID, not by name or path; names repeat.
- Rebuild a messy PSD before import: base layer + its clipped adjustments grouped (Ctrl+G) and converted to a Smart Object, so adjustments and blend modes bake in.
- Game titles and stylised logos stay images; text becomes TMP only when its font exists in the project.
- PSD flat composites (a pile of tickets, a stack of gifts) should be broken into atoms: one Ticket sprite placed 29 times with rotations beats one big picture.
- Photoshop layer effects (Drop Shadow, Stroke, Outer Glow, Color Overlay) are not reproduced exactly by third-party PSD readers; export through Photoshop itself.
- Drop shadow and glow effects enlarge a layer's bounds; placement must use the effect-inclusive bounds.
- Hidden PSD layers may still be part of the final design; compare with the reference image before exporting only visible layers.
- Photoshop can be driven from Python through COM (Photoshop.Application, DoJavaScript) on Windows.
- PSD to uGUI coordinates: PSD origin is top-left with Y down; RectTransform Y goes up. With anchor top-left: anchoredPosition.x = x + pivot.x * w, anchoredPosition.y = -y - (1 - pivot.y) * h, sizeDelta = (w, h).
- Wrong pivot assumption shifts every element by half its size; the error grows with element size and looks "almost right".
- 1 PSD pixel = 1 canvas unit only when the Canvas Scaler reference resolution equals the PSD size; a tool should refuse other values.
- Place an exported layer by the bounds of the exported PNG (with its glow), not the layer's own bbox; a glow can shift it by 18 px.
- PSD groups with 0x0 bounds can still have children; skip group nodes only when they have no children.
- Photoshop FontSet lists the real font first and a fallback (e.g. MyriadHebrew) after; read only FontSet[0].
- Check each font's licence for commercial use and redistribution of the .ttf before shipping it in a project or package.
- 2D PSD Importer imports layered PSB/PSD from Photoshop as sprites, can keep layers for rigging.

DEBUGGING AND ROOT CAUSE:
- Testing: Unity Profiler shows CPU, GPU, memory. Frame Debugger shows draw calls one by one. Memory Profiler shows textures and leaks.
- Reproduce first: same device, same data, same steps; a bug you cannot reproduce cannot be proven fixed.
- Change one thing at a time and measure again; many changes at once hide what fixed it.
- Pink objects in URP: missing or Built-in shader; invisible objects: wrong layer, culling mask, sorting, alpha 0 or disabled renderer.
- UI not clickable: missing EventSystem or Graphic Raycaster, an invisible Image with Raycast Target on top, or CanvasGroup blocksRaycasts off.
- Blurry sprite: wrong PPU, compression, max size too low, or UI scaled up; check import settings and the Canvas Scaler.
- Missing references after a merge: a lost or regenerated .meta GUID; check the file's GUID in Git history.
- Development build + Autoconnect Profiler + logcat/Xcode console show device-only errors.
- Fix the cause and guard it: add a test, a validator or an import rule so the same bug cannot come back.
- "File replaced" and "texture updated" can both be true while the game still draws the old shape; look at a render, not only the data.
- Silence is not success: a check that inspected nothing must say so, not report clean.
- Measure the same thing twice before trusting an instrument; a number that changes on rerun is noise.
- Negative control: prove a check can say "no" on a known-bad case, not only "yes" on a known-good one.
- Time-based effects (particles) differ between runs unless the simulation is stepped with a fixed seed and time.
- Before acting on a detector's list, look at the value histogram; a threshold inside the noise gives random lists.
- Awake runs first (cache references), then OnEnable, then Start (read other objects), then Update each frame.
- Import Messages on a model show warnings; a warning does not mean the import failed.
- Debug layers in order: source art, import (slicing, pivot, PPU, atlas, compression), prefab, animation/Timeline/tweens, shader, runtime state, loading, platform.
- Disable Animator, Timeline, tweens and scripts one by one to find which system changes the visual.
- Works only in Editor: AssetDatabase or Resources references that do not exist in the player build.
- Wrong on device only: texture compression, sRGB/linear, shader precision, stripped variants, render scale.
- Draw RectTransform bounds and the safe area with a runtime debug overlay to find misplaced UI.
- Isolate import vs shader: test with a known-good UI/unlit shader and an uncompressed texture.
- Logcat (Android) and the Xcode console (iOS) show native errors, shader compile failures and memory warnings.
- Same number before and after a fix: first check the output file was rewritten (mtime newer than the run), then explain.
- A FAIL where raw difference is tiny but the aligned difference is big is a bug in the measuring tool, not in the animation.
- Every search that can answer "not found" should run with a known positive control; if the control is not found, the search is broken.
- Find who dirtied a scene: EditorSceneManager.sceneDirtied with a stack trace, Undo.postprocessModifications (property paths), ObjectChangeEvents.changesPublished, EditorApplication.hierarchyChanged as time markers.
- Time each tool phase with Stopwatch (parse, write assets, refresh, save, tests) before optimising.
- Find which process holds a locked file on Windows with Process Monitor or Sysinternals Handle.
- Camera.Render from an editor script outside Play Mode does not show point Light2D, the opaque texture or post-processing; check those in Play Mode.
- RenderDoc integration: with RenderDoc loaded, right-click the Game/Scene view tab > Load RenderDoc, then a capture button grabs the next frame (Windows, DX11 / OpenGL Core).
- Player > Strict shader variant matching shows the pink error shader plus a console warning when a material needs a stripped variant, instead of silently picking a similar one.
- Frame Debugger > Render Opaques > RenderLoopNewBatcher.Draw shows each SRP batch and why it broke (e.g. "Nodes have different shaders"); many small batches = too many shader variants.
- Stack trace logging per message type: None, ScriptOnly (default) or Full (native too); set in Console menu, Player Settings or Application.SetStackTraceLogType - rebuild the player; do not ship Full.
- Built players do not write to the Console: read the Player.log file for errors and stack traces.

LIVE GAME, RELEASE TIMELINE, PRODUCTION PIPELINE:
- Live game: a change must be safe for players already in the game - old saves, old content versions and players who did not update the app.
- Feature flags / remote config turn a feature on for some players first and off fast if something breaks, without a new build.
- Hotfix vs content update: art and data can often ship as remote content; code changes need a new app build and store review.
- Backward compatibility of remote content: new bundles must still work with the app versions players have; keep old catalogs valid.
- Remote content must be understood by every supported client: optional fields with defaults, no new required components, scripts or shader variants.
- Client capability checks and version-segmented flags before activating content that needs a newer build.
- Freeze binary-dependent Tech Art changes (scripts, shaders, prefab structure, asset formats) before store submission; remote-only content can continue.
- Validate remote Addressables and configs against the exact submitted build, not a newer local one.
- Tag every production binary together with its catalog, content state file and remote deployment.

STEPPING INTO AN EXISTING PIPELINE:
- Joining an existing project: read the folder structure, naming, prefab patterns, addressable groups and Git rules before changing anything.
- Copy the house style: find one or two shipped features and build the new one the same way; new patterns only with the team's agreement.
- Existing tools first: check the team's editor tools, validators and templates before writing new ones.
- Keep conventions when adding tools: same menu location, naming and data format as the existing tools.
- Find the team's tools: search code for MenuItem, EditorWindow, AssetPostprocessor, CreateAssetMenu; check CI and build scripts for validators.
- Run existing validators in report-only mode first; extend an existing tool before writing a parallel one.
- Trace one shipped event end to end (prefab, data, atlas, Addressables group, localization, flag) to learn the real conventions.
- Do not rename shared assets, child objects, Animator states, IDs or labels, and do not change global import settings, without an impact check.
- Do not reserialize the whole project in an unrelated PR.

TESTING (Unity Test Framework):
- Unity Test Framework: EditMode tests run in the editor without Play; PlayMode tests run frames in Play mode ([UnityTest] with yield).
- Test what can break: data rules (prices, counts), prefab contracts (children, components), flows (buy -> built), not pixel layout.
- Assembly definitions for tests reference the code assembly and the test framework; tests are excluded from player builds.
- Run all checks before a PR: tests plus a quick play-through of the changed feature.
- EditMode tests run in the currently open scene. Create test objects in EditorSceneManager.NewPreviewScene and close it in finally.
- A dirty scene makes the Test Runner show a Save dialog that blocks the run; save scenes before running tests.
- Test first, watch it fail, then fix: a test that never failed may test nothing.
- PlayMode tests check behaviour over frames (animation plays, flow completes); EditMode tests check data and prefab structure.
- After external file changes call AssetDatabase.Refresh before checking compile results; the old status is reported until then.
- Tests that use Undo must clear the undo stack for their objects, or destroyed objects can come back.
- A modal dialog (EditorUtility.DisplayDialog) inside tested code hangs the test run; keep dialogs in the window, logic in testable code.
- TestRunnerApi: an EditMode|PlayMode filter runs only EditMode. Run EditMode synchronously, then PlayMode as a separate run.
- Render checks in tests: render with the camera culling only the test layer, because the open scene content is unknown.
- Green tests on generated content are not enough; render or open each generated thing and look before calling it done.
- A tool that returns an empty list on known data is broken, not clean; check its search rule and folder traversal.
- Worth testing for Tech Art: data schemas, prefab contracts, every variant instantiates and resets, event state flows, Addressables load/release symmetry, localization limits.
- Automated leak check: open/close a feature in a test scene and compare memory against an allowed residual.
- Keep a project compiling without the Test Framework package: guard test assemblies with an asmdef Version Define (e.g. TEST_FRAMEWORK_INSTALLED) as a Define Constraint.
- A test calling Button.onClick.Invoke() proves the logic, not the click; the real input path (EventSystem module) is untested.
- EditMode test runs hang while the editor is in Play Mode; check EditorApplication.isPlaying and scene isDirty before running.
- After a compile the new DLL exists before the domain reloads; tests run in that gap use the old code. Wait for an [InitializeOnLoad] timestamp newer than the DLL.
- Test gate is three checks: run completed, total >= expected count, failed == 0; "0 tests, exit 0" is not green.
- Visual tests need a frozen seed and fixed time; otherwise particle or animation frames differ between runs.
- Visual diff renders into a fixed-size RenderTexture (the reference size), independent of the Game view size, or Canvas Scaler changes pixel sizes.
- Test a pose at time t: AnimationClip.SampleAnimation(go, t), then read anchoredPosition, scale, alpha with a tolerance.
- Test Animator logic in EditMode: set the controller, call animator.Update(dt) in a loop, assert GetCurrentAnimatorStateInfo(0).IsName("Idle"), then SetTrigger and check "Out".
- Use a reference video as human reference; turn a few key moments ("container lands at 0.8 s") into pose assertions.
- Cheap animation regression checks: golden curve data and pose snapshots at key times; screenshot tests are more fragile (fonts, anti-aliasing).
- Animation Events can fire during Animator playback in tests and trigger side effects; keep handlers safe or test clips without events.
- Robustness tests for UI animation: many taps during the animation (input storm), open/close many times, pause mid-animation, several resolutions.
- Extract key times from a reference video with frame differencing on a region (OpenCV/FFmpeg): motion peak, then landing where motion stays below a threshold.
- Review generated animation without watching all clips: contact sheets of frames, golden images at key times, numeric reports; watch only warnings.
- Run EditMode tests from editor code with the TestRunnerApi (Execute with a Filter, ICallbacks RunFinished) and write results to a known file.
- Keep pure logic (parsing, defaults, metrics) in plain C# so it can be tested fast without scenes; Unity-side adapters stay thin.
- Command-line tests: Unity -batchmode -runTests -testPlatform EditMode -testResults results.xml (no -quit); filter with -testFilter / -assemblyNames.
- A player build is the real check for generated animation assets; editor playback can hide stale or missing data.
- Make a measuring tool trustworthy: positive controls (same vs same = 0), negative controls (a known-different pair must FAIL), injected single defects, repeatability, edge cases (flat curve, never settles).
- Keep measurement and pass/fail policy separate, and give "not applicable" / "insufficient data" results instead of zeros.
- Render tests (draw into a RenderTexture, count lit pixels) catch bugs text-based tests miss: invisible UI shaders, frozen effects, empty bakes.
- Image comparison against a reference PNG is a soft signal (alpha blending order, sub-pixel jitter); do not make it a hard gate.
- Deterministic particle tests: useAutoRandomSeed = false, fixed randomSeed, ps.Simulate(t, withChildren: true, restart: true, fixedTimeStep: true); determinism holds on one Unity version and machine only.
- Any UnityEngine.Random call near a particle test can break its determinism (shared RNG state).
- Particle tests: particleCount at time t is a hard assert; single-particle positions and Renderer.bounds need tolerances or statistical checks (all within radius R, none above Y=0).
- A particle limit test must count live particles across the whole sub-emitter tree after simulating the densest moment, not read maxParticles.
- Any Debug.LogError during a Unity test fails it ("Unhandled log message"), e.g. GetFloat on a missing material property; use LogAssert.Expect when an error is intended.
- Freeze animated shaders before snapshot tests (speed 0, fixed progress), and sample several moments of a cycle (12, not 3) so short events are not missed.
- Render tests in CI: run Unity without -nographics and with a graphics context (xvfb-run on Linux or a GPU runner); otherwise keep render tests local and run logic tests in CI.
- Pixel values read back with ReadPixels differ between Linear and Gamma colour space (mid grey 0.5 linear is about 0.73 sRGB); fix the colour space, use tolerances and relative checks.
- DestroyImmediate(material) frees the material but not loaded shaders/textures; long editor test loops need Resources.UnloadUnusedAssets.
- Call Canvas.ForceUpdateCanvases() before a manual Camera.Render in tests, or the Canvas may not be rebuilt yet and the capture is empty or stale.
- Camera.Render + ReadPixels is synchronous on DX11/DX12 but may not be on Vulkan/Metal; use AsyncGPUReadback there.
- Under -batchmode -nographics, SystemInfo.graphicsDeviceType is GraphicsDeviceType.Null; use it to skip render tests with a clear message instead of reading a black frame.
- RenderTexture colour space for readback is set by RenderTextureReadWrite (sRGB vs Linear), not by the format.
- Render tests depend on sub-pixel placement even with Point filter; place quads on whole pixels or allow +-1-2 px tolerance.
- VFX Graph does not render into a RenderTexture via camera.Render in EditMode (the Scene view uses its own editor path); capture VFX Graph output in PlayMode.
- Tell "small by design" from "broken" by motion, not brightness: frame-to-frame change and pixel variance > 0 mean alive; identical frames mean frozen.
- Full reference-image tests (ImageComparisonSettings in Unity Graphics Test Framework) for a golden sample of key effects; cheap pixel/motion checks for the rest.
- EditMode tests do not run the MonoBehaviour lifecycle (Awake/OnEnable/Start/OnDisable) for normal scripts ([ExecuteAlways] ones excepted); test lifecycle behaviour in PlayMode, pure logic in EditMode.
- Test internal logic without reflection: move it into an internal method and add [assembly: InternalsVisibleTo("YourTests")] in the runtime assembly.
- ScreenCapture.CaptureScreenshotAsTexture captures the Game view including Overlay UI; Camera.Render to a RenderTexture includes Screen Space - Camera UI but never Overlay canvases.
- Simulate a real tap in tools/tests: raycast with GraphicRaycaster at the button, check parent CanvasGroups (interactable, blocksRaycasts), then ExecuteEvents.Execute(..., pointerClickHandler); Button.onClick.Invoke ignores all of that.
- Tests read as a plus when they cover meaningful logic (data validation, variant integrity, flow states) at a sensible scale; trivial or Unity-behaviour tests read as noise.
- Showing tests to a reviewer: Window > General > Test Runner, EditMode, Run All is enough; tag a few key tests [Category("Smoke")] for a quick core check.
- Undo in synchronous EditMode tests: call Undo.IncrementCurrentGroup() before the tool runs so PerformUndo reverts exactly its changes; leftovers from other tests otherwise make different tests fail each run.
- Isolate scene-changing EditMode tests in a fresh scene per test (EditorSceneManager.NewScene in SetUp, or a preview scene) and clean up in TearDown.
- PlayMode tests from the command line: Unity -batchmode -projectPath <p> -runTests -testPlatform PlayMode -testFilter <name> -testResults results.xml (runTests quits by itself); inside a running editor use TestRunnerApi.Execute.
- Enter Play Mode Options with domain reload off can make PlayMode test runs find 0 tests or use stale assemblies; enable reload for test runs.
- In Editor -batchmode, WaitForEndOfFrame does not work (animation, physics and timeline are not updated); WaitForSeconds, WaitUntil, WaitWhile, WaitForFixedUpdate and AsyncOperation do.

EDITOR TOOLS AND AUTOMATION:
- Custom Inspectors and PropertyDrawers make data easier and safer to edit (ranges, dropdowns, previews).
- Undo.RecordObject before changing objects in a tool, so artists can Ctrl+Z; mark scenes dirty so changes save.
- EditorPrefs remember a tool's settings per user; ScriptableObject settings share them with the team.
- Batch tools should report what they did (made, updated, skipped with reason) and be safe to run twice.
- Presets (Preset Manager) store default import or component settings per type or folder without code.
- Command line and CI: Unity -batchmode -executeMethod runs editor code for builds and checks without the UI.
- Editor windows use IMGUI (EditorWindow.OnGUI); game UI uses uGUI Canvas. Keep them separate.
- Tool shape: a thin window over a core class. Test the core in EditMode; keep the window simple.
- Idempotent tools: a second click updates in place and duplicates nothing, so artists can rerun safely.
- A tool must say what it could not do (missing sprite, wrong count), never skip silently.
- AssetPostprocessor applies import rules automatically (size, compression, sprite settings) when art lands in a folder.
- Validators: a read-only check with PASS/WARN/FAIL and the reason, clickable to select the object, catches broken prefabs before release.
- Save scenes with EditorSceneManager.SaveScene(scene) and check the file; SaveOpenScenes returns true even when nothing was dirty and nothing was written.
- The active scene can change between calls; read GetActiveScene().path right before saving and compare with the target.
- AssetDatabase.StartAssetEditing batches imports, but folders created inside it do not exist in the database until StopAssetEditing. Create folders first.
- Create assets complete: fill the object in memory, then AssetDatabase.CreateAsset once. An empty asset filled later can stay empty on disk.
- Entering Play mode triggers an asset refresh; editing scripts during a PlayMode test run recompiles and kills the run.
- Logs printed when Play mode exits can be lost; print end-of-run results while still in Play.
- EditorUtility.RequestScriptReload forces a domain reload, e.g. when the unfocused editor does not reload by itself.
- A body-only change to a script rebuilds only its own assembly; dependent assemblies rebuild only when the public API changes.
- Split code into assemblies (asmdef) so an edit recompiles only its part of the project.
- Tags cannot be renamed; Layers and Sorting Layers can be renamed and reordered in Tags and Layers.
- Animator window keys: F focuses the selection, A frames all; Solo and Mute on transitions help preview.
- Useful Tech Art tools: asset validator, prefab contract validator, batch importer, prefab builder, content dashboard (memory, bundle size, duplicates), theme/event generator, animation auditor, UI preview for aspect ratios.
- UI Toolkit (UXML/USS) is Unity's recommendation for big new editor tools; IMGUI stays fine for small tools, inspectors and property drawers.
- Keep tool logic independent of the UI framework; use SerializedObject/SerializedProperty so Undo and prefab overrides work.
- Safe tools: dry-run mode, explicit scope, deterministic ordering, save once at the end, never silently overwrite artist changes, support cancel.
- CI: Unity -batchmode -nographics -quit -executeMethod Class.Method for validators and builds; fail on non-zero exit or missing reports.
- After a package version change the editor can stop responding until its window gets focus; queued editor commands from that time must be rerun.
- While scripts compile and the domain reloads, the main thread is busy; editor commands sent then time out or get lost - wait for the reload to finish.
- One settings ScriptableObject for tool paths (no project names in code) makes tools portable between projects.
- Editor menu items and tool windows in English only - reviewers and teammates read them.
- Dev-only UI (debug launchers, cheat buttons) must be hidden in release builds: check Debug.isDebugBuild / Application.isEditor and deactivate in Awake.
- Sort generated file names numerically (item_2 before item_10), or reports and contact sheets come out in the wrong order.
- A generator that passes on one sample input can fail silently on others; test edge variants (empty, bad cells, case, missing state, extreme numbers).
- Find assets by name or GUID (AssetDatabase.FindAssets), not by hard-coded path; paths break after folder moves.
- Inspect a prefab without touching the scene: PrefabUtility.LoadPrefabContents, then UnloadPrefabContents.
- Share tools as a UPM package (package.json, Editor asmdef, declared dependencies) or a .unitypackage; keep content (prefab) separate from tools.
- Clean-project import check in batchmode: Unity -batchmode -quit -projectPath <tmp> -logFile <log> -executeMethod <Validate>; fail on EditorUtility.scriptCompilationFailed or errors in the log.
- Local UPM package: reference it in Packages/manifest.json as "file:../path/to/package".
- Driving an editor from outside: give each request an id and write a result file per id; after a timeout look for the result instead of resending.
- Editor busy state for external tools: EditorApplication.isCompiling, isUpdating, isPlaying, and CompilationPipeline / playModeStateChanged callbacks written to a status file.
- Data-driven generator order: parse, validate schema, resolve defaults (explicit value > preset > profile > fallback), expand plan, check conflicts, read rest pose, build curves, write assets, write report.
- Keep generated assets in their own folder, reproducible and disposable; never hand-edit them.
- Validation findings need severity levels (Info, Warning, Error); not every issue should block a build.
- scene.isDirty is an editor flag, not a content hash; a dirty scene may save byte-identical. Causes: Undo.RecordObject, OnValidate writes, PlayableDirector rebinding, prefab overrides, asset replacement.
- Assign references only when different (if (director.playableAsset != timeline) { Undo.RecordObject(...); assign }); repeated identical writes still dirty the scene.
- DeleteAsset + CreateAsset gives a new GUID and object identity; update AnimationClip, AnimatorController and TimelineAsset in place (load, clear, refill, SetDirty, SaveAssets).
- OnValidate runs on load, import and inspector changes; it should only validate, never generate assets or add objects.
- Prefab instance checks: PrefabUtility.IsPartOfPrefabInstance, HasPrefabInstanceAnyOverrides; adding components to an instance creates overrides.
- Safe scripted build order: update assets in place inside StartAssetEditing/StopAssetEditing (try/finally), refresh once, wait for imports, reload assets by path, change the scene only where values differ, save, wait a frame, verify.
- Build heavy generated content in an additive temporary scene (EditorSceneManager.NewScene EmptyScene Additive), then close it; the user's scene stays clean.
- Get-or-add components (GetComponent, then Undo.AddComponent only if missing) so a rebuild with the same input changes nothing.
- A generator run twice with the same input should change nothing (same asset hashes, scene clean); make that a test.
- One Undo group per tool command (Undo.IncrementCurrentGroup, SetCurrentGroupName, CollapseUndoOperations) lets the user undo the whole step.
- Record the scene's dirty state before a tool runs; never save or clear flags for changes the tool does not own.
- Static fields are lost on domain reload; persist queued work to disk (or SessionState) and resume from [InitializeOnLoad].
- Editor readiness: not compiling, not updating (EditorApplication.isUpdating), not in or entering Play Mode, and stable for a couple of editor frames.
- Avoid modal dialogs in automated tool paths (check Application.isBatchMode); a modal blocks the main thread.
- Validate every target path and component before writing anything; fail early instead of leaving a half-generated result.
- EditorApplication.delayCall runs after inspectors update, so it can stall when the editor is unfocused; use EditorApplication.update with a timeout as the automation clock.
- Write generated reports outside Assets (temp file, then File.Replace / os.replace) and import into Assets only what Unity must see.
- After a recompile, prove the new code runs: an [InitializeOnLoad] marker written after the reload (new id each domain), or a probe returning a build id, before running tests.
- AssemblyReloadEvents.beforeAssemblyReload / afterAssemblyReload: save pending work before, re-install hooks after.
- A long editor session with many recompiles grows lag; restarting the editor helps. To prove a real leak, compare Total Allocated Memory in Statistics twice with a pause.
- Files written from outside Unity are not imported until the editor gets focus; call AssetDatabase.Refresh(ImportAssetOptions.ForceUpdate) in the same call as the work that needs them.
- For temporary render/bake scenes use EditorSceneManager.NewPreviewScene and set camera.scene; NewScene(Additive) throws next to an untitled scene.
- Editor tool pattern: data asset (ScriptableObject, no logic) + Core static class (Problems(spec) checks before Build(spec)) + thin IMGUI window; logic stays testable without UI.
- Tool windows for artists: group by what the effect should feel like (Hit, Pickup, Death, Dust), 6-8 real fields, real units (count, ms, degrees), live preview.
- Tool hub pattern: one dockable EditorWindow for navigation (sidebar categories, search, recent), each tool a module with its own service class (no UI dependency), settings asset and report.
- Where editor tool data lives: team presets in a ScriptableObject in the repo, personal prefs in EditorPrefs, session-only state in SessionState, project-wide settings via SettingsProvider.
- Put project actions under Tools/ and dockable windows under Window/; do not make every small action a top-level menu.
- Long editor operations: EditorUtility.DisplayProgressBar (clear in finally) or the Progress API, cancel support, work split over EditorApplication.update, no Refresh inside the loop.
- Batch asset tools: dry run first (show counts, old/new values, skips), then apply; log changed paths; SaveAssets once at the end.
- EditorWindow [SerializeField] fields survive domain reload but not closing the window; ScriptableSingleton<T> with [FilePath(..., Location.ProjectFolder or PreferencesFolder)] persists editor state between sessions (call Save(true)).
- Prefix EditorPrefs keys with the tool/company name to avoid collisions; do not store asset references or team settings there.
- Do not call ScriptableSingleton.Save from OnValidate; save on change events (debounced) or OnDisable.
- Editor main thread blockers: Task.Wait()/.Result, synchronous network calls, Process.WaitForExit, heavy InitializeOnLoad work, recursive AssetDatabase.Refresh.
- An AssetPostprocessor cannot block a commit, but it can fix settings on import and log errors that CI can fail on.
- Internal Unity editor APIs (via reflection) are unsupported and can break between minor package versions; guard them with version checks and a fallback.
- Unity 6.3 upgrade notes: URP Compatibility Mode removed, Scene.handle type change, stricter [SerializeField] (fields only); compile editor tools in the target editor, not just check warnings in the newer one.
- Keep Unity projects on a local ASCII path; OneDrive/Dropbox/network paths and long paths break Hub, Package Manager and some editor versions.
- Create a project from the command line: Unity.exe -createProject <path> -quit (then open with -projectPath); check the Editor log on failure.
- Unity Recorder Movie Recorder: MP4 H.264 at a constant frame rate (Playback Constant, 60 fps for small fast FX), record the Game View or a camera, not the editor UI.
- Good validators: run on the selection or a folder, actionable messages with severity, ping the offending asset, never change assets unless the action says so, safe to re-run; keep validation separate from mutation.
- Useful buildable-item validator checks: required child paths, shared Animator assigned, sprites and shadow present, collider usable, SortingGroup set, unexpected variant overrides.
- Unity Recorder Output Resolution sets the capture size (e.g. 1080x2400) regardless of the Game view window size.
- Custom Profiler module: a class derived from ProfilerModule with [ProfilerModuleMetadata("Name")] and a list of counter descriptors; the Profiler window finds it automatically (or build one in Profiler Module Editor, no code).
- Unchecking Preferences > Compress Assets on Import speeds up Editor imports; builds are still compressed.

GIT AND UNITY:
- .meta files: every asset has a .meta with its GUID and import settings. Always commit the .meta with the asset. A lost .meta = new GUID = broken references everywhere.
- Force Text serialization: Editor Settings > Asset Serialization = Force Text, so scenes and prefabs are YAML and can be diffed and merged.
- Visible Meta Files: Version Control mode must show meta files so Git can track them.
- .gitignore for Unity: ignore Library, Temp, Obj, Logs, Build, UserSettings. Library is rebuilt from Assets and meta files.
- Git LFS: store big binaries (PSD, FBX, WAV, large PNG) in LFS so the repo history stays small.
- Merge conflicts in scenes: two people editing the same scene conflict often. Split work into prefabs and small scenes; use UnityYAMLMerge (Smart Merge) as merge tool.
- Small PRs: keep prefab and scene diffs small and focused so reviewers can read them. Do not commit unrelated reimport noise.
- fileID + GUID: a reference in YAML = GUID of the file + fileID of the object inside it. Sub-sprites and sub-assets have their own fileID.
- Pull requests for Unity: describe what changed in the scene/prefab, add a screenshot or short video, list how to test.
- Prefab over scene: build features as prefabs so changes land in small files and scenes change less.
- Never commit Library or Temp; after a pull, Unity reimports changed assets automatically.
- Line endings: Unity YAML files can get CRLF/LF noise; a .gitattributes file keeps them stable.
- Review your own diff before a PR: unexpected .meta or prefab changes often mean an accidental edit or reimport.
- Branch per feature, small commits with clear messages, rebase or merge often to avoid big scene conflicts.
- A file held open by another process (sync tool, Git client, import) can refuse writes; retry or write to a new file and swap.
- Pin the Unity and package versions so different editors do not reserialize assets differently.
- Open merged scenes and prefabs in Unity to verify them; a clean text merge is not proof.
- Widespread fileID churn or whole-file YAML changes in a PR are a warning sign.
- Mobile branching: trunk-based with feature flags plus short release branches for submission and hotfixes.
- CI checks for missing metas, orphan metas, duplicate GUIDs and LFS pointer mistakes.
- Before deleting an asset, trace references by GUID through the whole dependency chain (prefab to SDF asset to font file).
- .gitignore: ignore only generated folders; a whitelist fails silently (a file saved elsewhere never shows in git status).
- Keep huge PSD/PSB out of plain Git; GitHub rejects files over 100 MB and one commit can jam the repo. Use LFS or keep sources outside.
- A .unitypackage made in a newer Unity may not import in an older one; compatibility goes forward only. State the build version.
- Check references both ways: files nobody references and references to files that do not exist (Animators pointing to missing controllers).
- Check a package for hidden dependencies: scan its YAML for guid: references and list GUIDs that resolve outside the package; then import it alone into a clean project.
- Keep a live Unity project out of cloud-sync folders (Drive, OneDrive, Dropbox); sync drivers lock files mid-import and cause write errors.
- Delete assets through AssetDatabase.DeleteAsset while the editor is open; rm on an Assets folder leaves .meta orphans or the folder is recreated.
- A new asset's .meta is written by Unity on import, so it can appear after you staged the asset; check git status for .meta files before committing.
- Moving work to an older Unity: never downgrade the only copy; create a clean project in the target version and copy Assets folders with every .meta, not Library; recreate URP assets there; resolve packages manually.
- Risk when moving assets to an older editor: URP assets and Addressables settings high; scenes, sprite atlases, Timeline medium; prefabs, anims, controllers, materials, ScriptableObjects low-medium; missing .meta files critical.
- Moving to another Unity version: start from the target template's manifest, add only needed packages, let Package Manager write the lock file; do not copy a newer packages-lock.json.
- Sprite Atlases, Timeline and Addressables add version risk to a cross-version delivery; drop them if the review does not need them, or reopen, repack and rebuild in the target editor.
- In a new project in an older version, recreate by hand: Sorting Layers, tags, Graphics/Quality (URP asset), 2D Renderer (Transparency Sort Mode), URP asset and 2D Renderer, input settings, Physics 2D matrix; do not copy the whole ProjectSettings folder.
- Downgraded-project checks: no compile errors or missing scripts, variants still linked to base, Animator states and parameters intact, no pink materials, TMP renders, Addressables groups valid and build OK, EditMode tests, Play smoke test, device build.
- Zip for a reviewer: Assets (with .meta), Packages/manifest.json and lock, needed ProjectSettings, a README (version, setup, structure, limitations); exclude Library, Temp, Logs, Build.
- UnityYAMLMerge (Smart Merge) merges .unity and .prefab YAML by object; set it as the Git mergetool (merge -p BASE REMOTE LOCAL MERGED); mergerules.txt tunes arrays, exclusions and float tolerance.

AI TOOLS IN THE WORKFLOW:
- AI coding assistants: good for drafts of editor tools, test code, API lookup and repetitive changes. Output must be read, compiled and tested in Unity.
- AI + tests: writing the test first gives the AI a clear target and proves the result. A green test without a failing run first proves nothing.
- AI limits: AI can invent API names or old Unity APIs. Check against the Unity docs for the version in use.
- AI for art: generated images need a human pick, cleanup and consistent style; import settings and slicing still matter.
- Good AI tasks in Unity work: editor tool drafts, test scaffolds, batch refactors, log/profiler analysis, checklists from specs, documentation.
- Verify AI output: compile, run the tests, look at the result in the editor; check Unity API names against the docs.
- AI for research: compare approaches (Animator vs Timeline, Addressables grouping) and list risks, then decide with measurements.
- AI image generation for placeholders or content needs consistent style prompts, cleanup, correct transparency and import setup.
- Give AI the Unity version, package versions, project conventions and acceptance criteria; ask for tests and failure cases with the code.
- Never let AI commit, overwrite assets, change GUIDs or apply prefab changes without review.
- Treat AI output as a fast junior's draft: small inspectable changes, tests, diff review, version control.


Q: Hi Igor, nice to meet you. How are you?
A: Hi! Nice to meet you too. I'm good, thank you. A little excited about the interview, but in a good way. How are you?

Q: How are you today?
A: I'm good, thank you. I'm happy we can talk today. How are you?

Q: How is your day going?
A: Pretty good, thanks. Just a normal work day. I was excited for our call.

Q: Did you have a busy week?
A: Yes, very busy, but that is normal for me. I usually do Unity work, animations, UI work, fix problems, and talk with artists and developers.

Q: Tell me about yourself
A: I am a Unity Technical Artist. I have worked in games for over seven years. Now I work on mobile and live games. I do UI, art, animation, Spine, atlases, localization, optimization, and fix visual and technical problems in Unity. In my job now, I add art and UI, make popup animations, and handle production content and performance tasks. I started with Flash and ActionScript 3, so I can talk well with developers. I love turning visual ideas into things that work well in the game.

Q: Can you walk me through your experience?
A: I began in development with Flash and ActionScript 3. Then I moved to Technical Art. I worked on mobile games, Unity UI, animation, Spine, atlases, localization, 2D and 3D, and optimization. Now I build art setups in Unity and fix problems.

Q: Why did you choose Technical Art?
A: I love both art and solving technical problems. I can talk with artists about visual ideas, then talk with developers about how to build them. I like connecting both sides and turning an art idea into something real in the engine.

Q: Why do you want to work at Playtika?
A: I like how this role works. It is more than adding art files. I would own the whole feature. I would build it in Unity and handle UI, animation, speed, memory, and loading until release. I also enjoy working with art, code, design, and product teams together. That teamwork is my strong point.

Q: Why are you interested in Project Innplay?
A: I like that this role lets me own a feature from start to finish. Turning an early idea into a real Unity feature sounds great. I enjoy the whole process: visuals, behavior, technical setup, performance, and how it fits the pipeline.

Q: Why are you interested in this position?
A: This job fits my skills and my goals. I already use Unity, UI, animation, art, optimization, and fixing problems. This role adds new things like Addressables, reusable systems, and working close with product and engineering. That is my next step.

Q: What do you expect from Playtika?
A: I want a strong production setup where Technical Art has real ownership. I want to work with skilled artists, developers, designers, and product people, learn your pipeline, and add value fast. I care about owning features, scalable workflows, performance, and learning from a mature live-game setup.

Q: What are you looking for in your next role?
A: I want a hands-on Technical Artist job with more ownership. I want to keep working with Unity, UI, animation, integration, optimization, and debugging. I want to own a feature from early idea to release. I also want to improve workflows and reuse systems.

Q: What did you like about your previous companies?
A: I liked having real responsibility. I could see my work working in the live game. I also liked the variety. One task had UI and popup animation. Another had Spine or atlases. Others had localization, 3D content, scene setup, or debugging. This let me move easily between art and technical work.

Q: What do you like most in your current job?
A: I love the hands-on work. I put art, UI, or animation into Unity. I fix the problems and make it work in production. I also like talking with people. I connect the artist's visual goal with the developer's technical needs.

Q: What didn’t you like in your previous jobs?
A: I work best when priorities and ownership are clear. If requirements change without enough context, it can create extra rework. I try to fix this by asking questions early, confirming the goal, and talking about technical consequences before too much work is done.

Q: Why are you looking for a new job?
A: I want to grow in my job. I know Unity Technical Art well. I want to own more of the work, use a bigger shared pipeline, and learn more about scalable content systems, performance, Addressables, and live content workflows.

Q: Why did you leave your previous job?
A: I left because I want to grow. I want harder Unity work, more ownership, and a clearer path to become a Senior Technical Artist. I want my next job to give me more responsibility, not just a new company name.

Q: Why should we hire you?
A: I already work between art and engineering, which this role needs. I have hands-on skills in Unity UI, animation, art integration, Spine, atlases, localization, optimization, and mobile production. I investigate problems alone and own work fully until it is production-ready.

Q: What is your greatest strength?
A: I don't give up on hard problems. I work step by step, not by guessing. If something is wrong, I list the possible causes — art, settings, prefab setup, UI, animation, rendering, loading, or code — and check each one. I find the real cause, not just a quick fix.

Q: What is your biggest weakness?
A: Sometimes I go too deep into technical details. I now check the goal first: what must ship, the deadline, the risk, and how much solution is enough. This keeps good depth without doing too much.

Q: How would you describe yourself as a person?
A: I am calm, responsible, and easy to work with. I don't create drama. I ask questions when things are not clear. If something is broken, I find it and fix it. I work well alone and like learning new things.

Q: What motivates you most at work?
A: I like seeing a real feature come together. I start with art or an early idea, do the Unity setup, fix the technical problems, and see it work in the game. I also like saving team time when the workflow is used again for future content.

Q: What kind of tasks do you enjoy the most?
A: I like tasks that mix visual quality with technical thinking. UI features, animations, content integration, visual debugging, optimization, or adding features to existing systems. I especially enjoy tasks where the answer is not obvious and I must understand how the whole system works.

Q: What achievement are you most proud of?
A: I am proud I moved from development into Technical Art. I can now do real work on art, UI, animation, integration, and optimization. I can take visuals, handle technical limits, and work with artists and developers. That independence means more to me than one task.

Q: Tell me about a difficult task you had
A: Hard tasks are often when the real cause is hard to see. Looking like an art problem but could be import settings, animation, UI setup, performance, or integration. I reproduce the issue, reduce possible causes, test one at a time, change one thing at a time, then prevent it in the pipeline.

Q: Tell me about a mistake you made
A: I learned that perfect code is not always the best answer. I once spent too much time making something better than needed. Now I ask about the goal, deadline, and quality first. I balance quality with release time.

Q: How do you react to feedback or criticism?
A: I am okay with feedback. First, I try to understand why it was given. If I am not clear, I ask questions. Then I make the change and remember it for next time. I never take feedback personally.

Q: How do you deal with conflict?
A: I see conflict as a difference in what people care about, not a fight. An artist wants good looks. A developer cares about memory, loading, and easy fixes. I find out what matters to both. Then I test things or use profiler data, not just opinions.

Q: Do you prefer to work independently or in a team?
A: I like both. I can own a feature and work alone on technical details. But Technical Art needs talking with artists, developers, designers, and product. Best for me: clear ownership, with easy access to people who have the info I need.

Q: What do you expect from your manager?
A: I want clear priorities, context, and honest feedback. I don't need someone to watch every small step. I can work alone. But I want to know what matters most, what result is expected, and what the limits are. Early feedback helps a lot.

Q: Where do you see yourself in five years?
A: In five years, I want to be a strong Senior Technical Artist. I want to own features fully. I want to know the visual side, code, speed, tools, and how work flows. I want to help newer people too. Later, I may take more leading roles, but I still want to work hands-on with Unity.

Q: What did working on slot and mobile games teach you?
A: Slot and mobile games taught me to care about how things look and also how they are built. These games need animation, feedback, translation, updates, and good speed. A nice result is not enough if it is hard to keep up or slow on weak phones. This helps with any live mobile product.

Q: What do you think is important when working on mobile games?
A: Performance, memory, build size, loading, and device differences matter a lot. I think about technical cost while adding content, not after it gets slow. But I don't optimize blindly. I test the real problem first and keep good looks where they matter.

Q: How strong is your Unity experience?
A: Unity is one of my main tools. I use it for UI, art and animation, Spine, atlases, localization, scenes, prefabs, fixing bugs, and making things faster. I am very good with UI-heavy work. I can also join an existing project and follow its rules.

Q: How strong are you with Photoshop?
A: I use Photoshop often in my Technical Art work. I make and fix 2D art, use layers, check size and transparency, clean up files, and get them ready for Unity. I'm not a concept artist. My strength is making art ready for the game.

Q: How do you use Photoshop in a Technical Artist workflow?
A: I mostly use Photoshop between source art and Unity. I check layers, fix or clean assets, check size and transparency, and get files ready for the engine. I fix art problems in Photoshop and import or layout problems in Unity.

Q: How do you use AI tools?
A: I use AI a lot for research, comparing tools, writing documents, making checklists, fixing problems, and repetitive work. I also use it for code tasks. But I never trust AI blindly. I check it, test it, and compare with real documents.

Q: Can you give me a practical example of how AI helps your workflow?
A: For example, when fixing bugs or making a plan, I use AI to list possible causes, compare options, or make a checklist or small code test. Then I check the important parts in Unity, docs, or the project. It saves time, but I make the final decision.

Q: Do you use AI coding tools?
A: Yes, I use AI as a coding helper. It drafts small tools, checks APIs, and speeds up repeat work. I still read the code, follow project rules, and test it. AI saves time but I must still understand the code.

Q: Do you have programming experience?
A: Yes. At Technical Art, I worked with Flash and Flex using ActionScript 3. I built game logic, worked with old code, client-server systems, MVC, OOP, XML, JSON, and web tools. I'm not a gameplay programmer, but this helps me read code, talk with developers, and understand technical systems.

Q: How comfortable are you with C#?
A: I am not a full-time C# developer. But I can write scripts when a Technical Art task needs it. My coding background helps me read code and logic. I made custom scripts in my Unity projects. C# is one more tool for me, for small tools and automation.

Q: What do you do when you don’t know how to solve something?
A: First, I find out what I don't know. Then I read documents, look at old project examples, or ask someone who knows. If I can, I make a small test. I am happy to say, "I don't know yet." What matters is how fast I find the right answer.

Q: How do you handle stress?
A: I make things simple. I find the top task, break work into small parts, and speak up early about delays. Hard work is fine for me. Not knowing what matters first is the problem. A clear plan keeps me calm.

Q: How do you feel about overtime?
A: I know live production can have surprise deadlines or release problems. I can be flexible then. But overtime should not be normal. Good planning and early talking are better for the team long-term.

Q: Would working on weekends be a problem?
A: For a big release or problem, I can work on weekends. But I want to know how often this happens. Then we both know what to expect.

Q: This role may require office work when needed. Is that okay?
A: Yes, I can come to the office when needed. I would just like to know the normal schedule and how it usually works for the team.

Q: What is important to you in a company?
A: I want work that is interesting. I want to grow my skills. I want clear tasks. I like teams that talk openly about problems. I want to own my work. I like seeing my work help the product. I like quality and release speed balanced well.

Q: How would your colleagues describe you?
A: My colleagues would say I am responsible, calm, and reliable. I finish what I start. I ask questions when things are not clear. I know the technical side well. I keep trying until problems are fixed.

Q: What are your salary expectations?
A: I am open to talk about pay. I want pay that fits my experience and the market. Please share the range you have for this job. Then we can talk more.

Q: How comfortable are you working in English?
A: I can work in English about technical and production topics. My speaking is still getting better. But I am comfortable asking questions, explaining technical problems, and making details clear. I always want communication to be clear.

Q: What is your educational background?
A: I studied at Ukrainian State University of Chemical Technology. My subject was automation of production. I learned engineering. This helped me think in a clear, planned way. Later, this helped me a lot in programming and Technical Art.

Q: What was your major?
A: I studied automation of production at Ukrainian State University of Chemical Technology. This taught me engineering and how to think about systems. Later, this helped me with programming and Technical Art.

Q: Why do you want to work in games?
A: I like games because the work mixes tech, art, design, and how players feel. As a Technical Artist I get to be part of all of it. I love seeing a feature turn real for players.

Q: What do you like about being a Technical Artist?
A: I like that Technical Art mixes creative work with solving problems. I work with visual content, but I also think about how it runs in Unity, how it affects speed and loading, and how to make the workflow better.

Q: How do you work with artists and developers?
A: With artists, I talk about the visual goal and how things should look and feel. With developers, I talk about how it works, integration, limits, speed, and easy upkeep. I connect both sides so we keep good looks without tech problems.

Q: How do you work with designers and product?
A: First, I ask why players need the feature, not just what to build. When design or product shows me a Miro board or early mockup, I ask about states, edge cases, and what matters most. Then I build it in Unity and explain trade-offs early.

Q: How do you approach optimization?
A: I don't guess. I find the real problem first. It could be texture memory, UI batching, rendering, loading, or animation. Then I make one focused change and measure it. I also check risks early, not at the end.

Q: What is your experience with UI?
A: UI is a big part of my Technical Artist work. I build screens and popups. I make UI animations and transitions. I work with localization. I give support on UI-heavy mobile projects. I take art from artists and set it up in Unity so it works well.

Q: How would you troubleshoot a UI screen that looks correct but performs badly?
A: First, I make the problem happen again on the device. I measure before changing anything. Then I check each possible cause: memory, UI batching, overdraw, layout rebuilds, or animation. I change one thing, measure again, and keep it only if it helps. I don't change many things at once. I wouldn't know what fixed it.

Q: What is your experience with animation?
A: I have worked with popup animations, UI transitions, tween animations, Spine integration and editing, and imported animations. I do animation work often. I can set up visuals and make animation fit the technical needs and states.

Q: What is your experience with Animator?
A: I know Animator well. I can use clips, states, transitions, and parameters. I link animation states to how a feature works. I keep the logic simple. I do not make big, hard Animator graphs when a simple one works.

Q: What is your experience with Timeline?
A: I know Timeline well. I can use it when a feature needs sequenced animation or timed events. My deepest skills are UI animation, Animator, tween workflows, and Spine. But I can join a Timeline setup fast and learn the project quickly.

Q: How do you decide between Animator, Timeline, tweening, and code-driven animation?
A: I pick based on the job. Animator for state changes. Timeline for ordered sequences. Tweening for simple UI moves. Code when logic controls motion. I use the simplest tool that stays clear and easy to change.

Q: What is your experience with Spine?
A: I use Spine in Unity. I have added Spine animations and edited them. I did this in projects with character and UI animations. I know the workflow well. I make sure everything works well in the game.

Q: What is your experience with atlases?
A: I have made atlases for production and mobile builds. I pack and improve them. I think about grouping, image quality, memory, and render cost, not just packing. If I change an atlas for speed, I check it works, not guess.

Q: How would you integrate a new 2D asset into Unity?
A: First, I learn how the new image will be used: in the UI, as a Sprite, panel, animation, or particle. Then I check import settings, size, alpha, compression, and platform overrides. After adding it, I test how it looks. If needed, I check memory and loading speed too.

Q: What is your experience with visual effects?
A: My best skills are UI, animation, Spine, and integration. I can also do particle effects in Unity. I handle effects from the Technical Art side: integration, timing, consistency, and performance. I am not a full VFX specialist.

Q: What is your experience with particle systems?
A: I work with particle systems when adding features and polish. I think about the effect, what starts it, how it fits the animation and UI state, and its runtime cost. I am not mainly a VFX artist. My strength is making effects work right inside the feature and the project's technical limits.

Q: What is your experience with live projects?
A: I like working on live projects and new updates. I know a change must fit the current systems, localization, performance limits, release dates, and how players really act. I also know "works on my machine" is not enough. It must be safe for the live build.

Q: Do you have experience with localization?
A: Yes. I have done localization work on several projects. I helped with UI and visual content in many languages. I made sure the layout stayed correct when text length or content changed.

Q: How do you handle a disagreement between an artist and a developer?
A: I split the goal from the tech limits. I first learn what the artist wants to keep and what the developer wants to protect — like memory, loading, speed, or easy code fixes. Then I find a fix that keeps the visual part but costs less tech work. I like quick tests or profiler data more than just arguing.

Q: How do you work when requirements change during production?
A: First, I ask what changed and what is most important now. Then I check what work I can keep and what I must redo. I tell others early if the change affects prefab structure, animation states, Addressables, performance, or release timing. I want to adapt without breaking things.

Q: How do you know when a feature is ready to hand off?
A: I check four things. First, the visual result matches the requirement. Second, the prefab and Unity setup are clean and easy to understand. Third, key states and transitions work. Fourth, the content fits existing project rules. I also check I didn't cause slow performance or loading problems. I want my work to be something another person can pick up and keep working on.

Q: What does end-to-end feature ownership mean to you?
A: It means I don't do just one small step. I follow the feature from the first idea. I check what is needed, build it in Unity, add art and animation, check edge cases, watch speed and loading, talk with the team, and stay with it until release. I don't do every type of work, but I own the Tech Art part.

Q: How would you turn a Miro board or mockup into a production-ready Unity feature?
A: First, I study the design. I look at states, clicks, content, animations, and what I need. I ask questions to product, design, art, and dev if things are unclear. Then I make a small test build in Unity. When it works, I make the real reusable prefab and UI. I add animation and effects. I hook up the game state. Last, I check speed, memory, loading, and edge cases before release.

Q: What do you do when the brief is incomplete?
A: I ask clear questions early. I find what is known and what is not. I make safe guesses where I can. I may build a small prototype. I keep working. I don't make big risky choices alone.

Q: What is your experience with prefabs?
A: I use prefabs in Unity. They keep repeated things the same and easy to reuse. I split shared parts from special parts. I keep things clear and tidy. I don't copy whole objects to change one small thing. A live project must stay easy to fix.

Q: How do you design a prefab so it can be reused for variants?
A: I find the stable parts first: hierarchy, behavior, shared references, animation, and UI logic. Then I open up parts that change: art, text, colors, data. I use one clear base plus controlled variants, not copies that drift apart.

Q: How do you avoid creating too many duplicated variants?
A: I first check if the difference is real or just data and looks. If behavior is the same, I reuse the existing prefab or system and change its settings. Copying is sometimes fastest first, but in a live project every fix must be repeated in many copies.

Q: How would you build UI that responds to real-time game state?
A: I keep game state and visuals separate. The UI gets updates and changes visuals. I don't hide game logic in animations. The UI must show the true state and stay predictable when inputs come fast or out of order.

Q: How do you think about performance before a feature reaches production?
A: While building a feature, I check for things that cost a lot: big textures, copies of the same content, too many materials, heavy UI, extra animation or particles, memory use, loading spikes, or content that costs a lot to update. I don’t optimize everything early, but I catch big risks before the feature is locked for release.

Q: How do you think about memory, size, and loading together?
A: I see them as different but linked problems. A small download does not mean low memory. Low memory does not mean fast loading. I ask what is loaded, when, how long it stays, how big it is, and if the feature needs it all at once.

Q: What is your experience with Addressables?
A: I know Unity assets well: atlases, UI, animation, and optimization. With Addressables, I know the basics: grouping content, choosing what ships in the build versus downloads, building it, and loading and unloading it to save memory on phones. I have not owned a huge Addressables setup, but I can join one, learn it, and use it carefully.

Q: How would you organize Addressables groups?
A: I would organize Addressables groups by how content is used at runtime, not just by folders. I would check what loads together, what is remote or local, and what updates together. I would also follow existing project rules first.

Q: What is remote content delivery with Addressables?
A: Some content does not need to be inside the app. It can be downloaded when needed. So a content update does not always need a full app update. I group assets well. I check content is ready when needed, controls downloads and loading, checks dependencies, and handles slow networks or missing content.

Q: How would you troubleshoot an Addressables content loading problem?
A: I first find the cause: wrong address, bad build or catalog data, remote files, loading issues, or memory. I copy the exact same settings and content version. I check what the system asks for. I don't change groups without reason. For remote content, I test when files are missing, not just the good case.

Q: How do you avoid memory problems with dynamically loaded content?
A: I ask who owns the content, how long it is needed, and when to release it. Loading is only half of the job. If a closed feature still holds content, memory grows. So I check load, use, and release, then verify real memory, not assume.

Q: How comfortable are you with Git and a PR-based workflow?
A: I know Git well and use PRs to share my work. I make small, clear changes with simple commit messages. I check my work before review. In Unity, I keep prefab and scene changes small so others can review them easily.

Q: How do you work in a shared codebase without breaking other people’s work?
A: I learn the project rules first. I keep my changes small and focused. I check my diff before submitting. If I touch shared code, I tell the team early, not at review. I don't surprise anyone.

Q: How do you communicate technical trade-offs to non-technical teammates?
A: I don't start with tech words. I explain what happens: looks, loading speed, memory, risk, build time, or future fixes. Then I show options and their costs. Example: "This looks better but slows phones. This looks a bit worse but is safe for mobile."

Q: How do you step into an existing pipeline and become productive?
A: I watch first, then change. I study how prefabs, folders, naming, Addressables, UI, animation, Git, and features are set up. I find one or two examples already in production. I copy them. Then I work fast and don't make new pipelines the team must maintain.

Q: How do you investigate a visual or technical issue independently?
A: I first make the bug happen again and find out what is wrong. Then I check each layer: source asset, import settings, prefab or Canvas, animation, material or rendering, runtime state, loading, or code. I test one idea at a time. I use the profiler or debugger for speed problems. I want the fix and the root cause.

Q: What does root-cause analysis mean to you?
A: To me, it means not stopping at the first fix. If a prefab is wrong because one value was changed by hand, I ask why it got wrong and if other prefabs have the same problem. A good fix also stops the same problem from coming back.

Q: How do you balance visual quality and performance?
A: First, I find what visuals matter most to the player. I find what slows things down. Then I choose the cheapest fix. Maybe a smaller texture, a different effect, better loading timing, reusing content, or cutting things players barely notice. I use evidence, not guesswork.

Q: How do you deliver within a release timeline when the feature is still changing?
A: I split work into must-haves and extras. I find big decisions early that could cause costly rework. I keep code simple and modular. I tell people fast when changes hurt the plan. If time is short, I ship a smaller stable version rather than miss the release.

Q: How do you prioritize when several things are urgent?
A: I check how each task affects the release, who is blocked, the risk, and the cost of waiting. If priority is unclear, I ask. I do the biggest-impact work first and tell people early if I can't do two urgent things at once.

Q: Have you created editor tools or scripts for artists?
A: I know how to code. I write small scripts when a job repeats a lot. Not every task needs a tool. But if artists do the same risky steps again and again, a small editor tool or check script is a great help.

Q: When would you build an editor tool instead of doing the task manually?
A: I check three things: how often the task happens, how many mistakes people make, and if the tool is hard to keep working. One time? Do it by hand. Every week with the same errors? Build the tool. But the tool must stay easy to keep working.

Q: How do you care about visual detail without slowing down production?
A: I tell the difference between real quality problems and just my own fussiness. If the player will see it, I fix it. But I also check if it matters for the current release and if there is a quicker fix. I want good quality, not endless polishing with no value.

Q: Do you have any questions for me?
A: Yes, thank you. I want to know what full ownership means for a Technical Artist on Project Innplay. What feature would I own first? How ready are the Addressables and remote-content tools? What team problems can I help solve?

Q: Do you have any questions for us?
A: Yes, thank you. What does success look like in this role after three to six months? How does the team review Technical Art changes in Git/PR? Which part of the pipeline gives most trouble now — feature integration, Addressables, UI state, performance, or tooling?

Q: What would you like to know about the team?
A: I want to know how Technical Art works with artists, developers, designers, and product each day. Who owns a feature when many teams are involved? How do code and prefab reviews work? How much can a Technical Artist change the workflow?

Q: Is there anything else you would like to add?
A: I would add that this role fits how I like to work. I am already strong in Unity, UI, animation, art integration, optimization, and working across teams. This job is special because I get more ownership: build a solution, fit it into the pipeline, and stay responsible until release.

Q: Thank you, Igor. It was nice speaking with you.
A: Thank you for your time. I really enjoyed our talk. The role sounds very interesting. I like the mix of Unity, owning features, UI and animation, integration work, Addressables, performance, and live production. I am happy to move to the next stage. Have a great day!

UNITY TECH DRILL (short technical questions, short answers):

Q: What is the difference between a prefab variant and a nested prefab?
A: A nested prefab is a prefab inside another prefab, it keeps its own asset. A variant inherits from a base prefab and stores only the overrides. I keep the chain short: base plus one level, two or three at most.

Q: How do you apply or revert prefab overrides safely?
A: I check the Overrides dropdown first, so I see exactly what changed. Then I apply only the changes that belong to the base, and revert local experiments.

Q: When do you use ScriptableObjects?
A: For shared data and settings: item lists, tuning numbers, configs. One asset can feed many prefabs, and designers can change values without touching code or scenes.

Q: How do you set up a Canvas for a portrait mobile game?
A: Canvas Scaler set to Scale With Screen Size, a reference resolution like 1080x2400, Match about 0.5-0.7. Then I test on a tall phone and on a tablet aspect.

Q: How do anchors work in a RectTransform?
A: Anchors are fractions of the parent rect. Anchors together mean fixed size; anchors apart mean the element stretches with the parent. I set anchors and pivot first, then position.

Q: What is the difference between Content Size Fitter and a Layout Group?
A: Content Size Fitter sizes its own object, for example a label to its text. A Layout Group sizes and places its children but not itself. Putting both on one object with Control Child Size causes conflicts.

Q: Why can a big Canvas be slow?
A: When one element changes, the whole Canvas rebuilds its mesh. I split static and often-changing UI into separate Canvases, so a timer does not rebuild the whole screen.

Q: What makes a UI button not react to clicks?
A: Usually a missing EventSystem, a missing Graphic Raycaster, Raycast Target off, or an invisible Image on top that catches the click. With the Input System package the EventSystem needs InputSystemUIInputModule.

Q: How do you handle the notch on phones?
A: I put top and bottom bars inside a Safe Area root that follows Screen.safeArea, instead of shrinking the whole Canvas.

Q: How do you fade a whole popup?
A: A CanvasGroup on the popup root: one alpha for everything inside, and I can turn off interactable and blocksRaycasts while it is hidden.

Q: Why should UI shaders use vertex color?
A: Image color and CanvasGroup alpha reach the shader as vertex color. If the shader ignores it, tint and fade stop working.

Q: How do you show a UI animation while the game is paused?
A: Animator Update Mode set to Unscaled Time. For particles, Delta Time set to Unscaled. Otherwise they freeze at timeScale 0.

Q: Animator or tween for a simple button pop?
A: For a small one-shot pop, a tween or a short clip is fine. I avoid an Animator on every idle UI element, because an active Animator dirties the Canvas every frame.

Q: How do Animator parameters work?
A: Float, Int, Bool and Trigger. Code sets them with SetFloat, SetBool, SetTrigger. A Trigger resets itself when a transition uses it. I cache ids with Animator.StringToHash.

Q: What are Animation Layers used for?
A: To play different animation on top of the base, for example upper body. Override replaces lower layers, Additive adds on top, an Avatar Mask limits the layer to some parts.

Q: How do you sync a sound or VFX with an animation?
A: With an Animation Event at the exact frame. I never check a value like "rotation equals 90", because Unity samples clips at a variable frame rate and can skip that value.

Q: When do you use Timeline?
A: For sequences with several objects and timing: intro, reward sequence, cutscene. Tracks for animation, activation, audio, signals, control for particles. One Timeline asset can drive different objects through PlayableDirector bindings.

Q: Why override bone or object values in LateUpdate?
A: The animation system writes transforms after Update and before LateUpdate. If I change them in Update, the Animator overwrites my value.

Q: How do you make a particle burst for a reward?
A: Emission with a Burst: count, cycles, interval. Short lifetime, Size and Color over Lifetime for pop and fade, Stop Action to disable or return to the pool when it ends.

Q: What does Simulation Space do?
A: Local moves particles with the parent. World leaves them behind in the world, for smoke or trails from a moving object.

Q: How do you keep particle effects cheap on mobile?
A: Few systems per effect, one shared material, small Max Particles, low overdraw, no real-time lights, collision off or Planes mode, and culling when off screen.

Q: Why use Prewarm?
A: A looping effect with Prewarm starts as if one cycle already ran, so it does not appear empty for the first second.

Q: How do you make an effect look the same every play?
A: Turn off Auto Random Seed and set a fixed Random Seed. Useful for reviews and tests.

Q: How do you sort particles with sprites in 2D?
A: The Particle System Renderer has Sorting Layer and Order in Layer like a SpriteRenderer. Sort Mode orders particles inside one system.

Q: Shuriken or VFX Graph?
A: Built-in Particle System for most mobile effects, it runs on CPU and works everywhere. VFX Graph runs on GPU and suits very many particles on hardware that supports compute shaders.

Q: What is the SRP Batcher?
A: In URP it reduces render-state changes between draw calls. Objects batch when they use the same shader variant, even with different materials. The shader must keep material properties in the UnityPerMaterial buffer.

Q: What breaks SRP Batcher compatibility?
A: A shader without the UnityPerMaterial CBUFFER, or a MaterialPropertyBlock on the renderer. The shader Inspector shows if it is compatible.

Q: shader_feature or multi_compile?
A: shader_feature when the option is set per material; unused variants are stripped from the build. multi_compile when code switches the keyword at runtime; it builds all combinations.

Q: What does a magenta or cyan object mean?
A: Magenta is the error shader: missing material, compile error, or a Built-in shader in URP. Cyan is the loading shader while a variant compiles.

Q: How do you check how many shader variants you have?
A: Graphics settings show tracked variants in the Editor. After a build I search Editor.log for "Compiling shader", and the URP asset can log stripping totals.

Q: Sprite-Lit or Sprite-Unlit?
A: Sprite-Lit reacts to Light 2D. Sprite-Unlit ignores lights and is cheaper, good for UI-like sprites and glowing effects.

Q: How do you animate a material without breaking batching?
A: I animate a shared value through the material or a shader time value. MaterialPropertyBlock is fine in the Built-in pipeline, but in URP it takes the renderer out of the SRP Batcher.

Q: What is Pixels Per Unit?
A: How many sprite pixels make one Unity unit. I keep one PPU per art set so sizes match. Double PPU makes the sprite half as big on screen.

Q: What is a Sprite Atlas for?
A: It packs many sprites into one texture, so they can batch into fewer draw calls. I group sprites that appear together on one screen.

Q: How do you choose texture compression for mobile?
A: ASTC on modern iOS and Android: 4x4 for sharp UI, 6x6 for items, 8x8 for soft shadows and gradients. ETC2 as Android fallback.

Q: Why turn off Read/Write and mipmaps?
A: Read/Write keeps a CPU copy and doubles memory. Mipmaps add about a third more memory and are not needed for fixed-size 2D sprites and UI.

Q: Why do you set Mesh Type to Tight?
A: The sprite mesh follows the shape, so less transparent area is drawn. Less overdraw, especially for round or diamond sprites.

Q: How does 2D render order work?
A: Sorting Layer first, then Order in Layer, then distance along the Transparency Sort Axis. A Sorting Group makes a multi-sprite object sort as one unit.

Q: How do you sort sprites by Y?
A: In URP 2D I set Transparency Sort Mode to Custom Axis (0,1,0) on the Renderer 2D Data, keep sprites on the same layer and order, and set Sprite Sort Point to Pivot with a bottom pivot.

Q: How do you read the Profiler when the game is slow?
A: I profile a development build on the device. In the CPU Timeline I check: if the render thread waits in Gfx.PresentFrame, it is GPU-bound; if it prepares commands, it is CPU-bound.

Q: What is GC.Alloc and why care?
A: Managed memory allocated this frame. More allocation means more garbage collection pauses. I keep it at zero per frame in gameplay and use Call Stacks to find where it comes from.

Q: Why is profiling in the Editor not enough?
A: Play mode runs inside the Editor process, so Editor work is mixed into the numbers. I use the Editor only to iterate on problems I first found on the device.

Q: What do you look at in the Frame Debugger?
A: The draw calls in order and why a batch broke. For the SRP Batcher it shows the reason, for example different shaders.

Q: What is overdraw and how do you reduce it?
A: Drawing the same pixel many times with transparent layers. I use tight meshes, fewer full-screen transparent images, smaller particles, and I check the Overdraw view.

Q: How do you prove an optimization helped?
A: Same device, same scene, same input, before and after. I report the delta, for example 14.2 ms to 10.8 ms, and I look at percentiles, not only average FPS.

Q: What usually takes the most build size?
A: Textures. First compression, then a smaller Max Size per texture until it starts to look worse. Everything in Resources folders is always in the build, so I keep Resources minimal.

Q: How do you release memory from Addressables?
A: Every load or instantiate needs a matching Release or ReleaseInstance. The bundle unloads only when all its assets are released.

Q: What is Cannot Change Post Release?
A: For static content. When an asset changes, it moves to a new update bundle, so shipped bundles stay valid. Can Change Post Release rebuilds and re-downloads the whole bundle.

Q: How do you check Addressables duplicates?
A: With the Analyze tool and the Build Layout report. An asset used by two groups without its own group gets copied into both bundles.

Q: How do you ship a content update?
A: "Update a Previous Build" with the content state file from the shipped version. Only changed remote content is rebuilt. I keep that file for every release.

Q: How do you fit a 2D camera for different phones?
A: Orthographic size from the content: max of height and width divided by aspect, divided by two. I test the narrowest aspect, not only the Game view.

Q: What do you check first when a sprite looks wrong in the game?
A: I go layer by layer: source art, import settings (slicing, pivot, PPU, compression), prefab, animation, shader, runtime state, loading.

Q: How do you find where an error comes from in a build?
A: The Player.log file, with stack traces turned on for errors and exceptions. The Console only shows Editor output.

Q: What is the difference between EditMode and PlayMode tests?
A: EditMode tests run in the Editor without Play, good for tools and data. PlayMode tests run frames, coroutines and physics, good for gameplay and UI flow.

Q: Why does a test fail with "Unhandled log message"?
A: Any Debug.LogError during a test fails it. If the error is expected, I use LogAssert.Expect.

Q: How do you run Unity tests in CI?
A: Unity -batchmode -runTests with -testPlatform, -testFilter and -testResults. Without -quit, because runTests quits by itself.

Q: How do you make an editor tool safe for artists?
A: Undo support for every change, clear errors instead of silent defaults, a dry run or preview, and it only touches the folders it should.

Q: Why do files written from outside Unity not appear?
A: Unity imports on focus or on AssetDatabase.Refresh. A script that writes files must call Refresh before it uses them.

Q: How do you avoid merge conflicts in scenes and prefabs?
A: Small prefabs instead of one big scene, clear ownership, Force Text serialization, and UnityYAMLMerge as the merge tool.

Q: What must always be committed with an asset?
A: Its .meta file. The GUID lives there; without it references break.

Q: How do you check AI-written Unity code?
A: I compile it, run the tests, and look at the result in the Editor. I check every API name against the docs for our Unity version, because AI can invent or use old APIs.

Q: A popup opens with a visible hitch. What do you check?
A: The Profiler on the frame it opens: instantiate cost, texture upload, shader variant compile, layout rebuild, GC.Alloc. Then I fix the biggest one, for example pool or preload the popup, or prewarm the shader.

Q: A screen looked fine in the Editor but is blurry on the phone. Why?
A: Usually texture Max Size or compression for that platform, a wrong Canvas Scaler setting, or the sprite scaled up above its source size. I check the platform override in the importer first.

Q: A sprite has a thin line or halo at its edge. How do you fix it?
A: Usually bleeding from neighbours in the atlas or from transparent pixels. I raise atlas padding, check the alpha edges of the source, and avoid bilinear sampling across the sprite border.

Q: Text looks different on device than in the Editor. What do you check?
A: The font asset and its fallback fonts, missing glyphs, atlas size of the font asset, and the Canvas Scaler. Fallback glyphs can have a different baseline, so I test them visually.

Q: The build is too big. Where do you start?
A: The build report or Build Layout: which assets take the most space. Usually textures, then audio and fonts. Then compression, Max Size, stripping unused content, and moving optional content to remote Addressables.

Q: Memory grows every time a player opens a screen. What is it?
A: Probably something is loaded and never released: Addressables without Release, instances not destroyed, or events still subscribed. I compare two Memory Profiler snapshots before and after.

Q: How do you use the Memory Profiler?
A: I take a snapshot, do the action, take another and compare. I look at textures, meshes and objects that should be gone, and what still references them.

Q: What is the difference between Destroy and SetActive(false)?
A: SetActive(false) hides the object but keeps it in memory, ready to reuse. Destroy removes it. For objects that come back often I disable or pool them.

Q: When do you use object pooling?
A: For things created often: coins, bullets, reward effects, list items. I size the pool from the measured peak and prewarm only the common ones. Rare screens do not need pooling.

Q: How do you make a scroll list with many items fast?
A: Reuse a small number of item views while scrolling, instead of creating one object per data item. Also a RectMask2D instead of Mask, and a separate Canvas for the scrolling content.

Q: Mask or RectMask2D?
A: RectMask2D for rectangles: it clips without stencil and is cheaper. Mask for custom shapes, but it uses the stencil buffer and breaks batching more.

Q: How do you show a timer that updates every second without cost?
A: Update the text only when the value changes, not every frame, and put it on its own small Canvas so it does not rebuild the whole screen.

Q: How do you keep UI in sync with game data?
A: The UI listens to events or reads one data source, it never owns the data. When data changes, the view updates. Every state must be restorable from the data, for example after reload.

Q: What should an animation never decide?
A: Game logic, for example whether a purchase succeeded. The animation shows the result; the logic decides it and must work even if the animation is skipped.

Q: How do you make a reward flight: coins flying to the counter?
A: Spawn pooled icons, move them from the source to the counter on a curve with a small delay between them, punch the counter when each lands, and update the number at the end.

Q: How do you make a popup Show and Hide?
A: One Animator or tween with Show and Hide: scale and fade in, about 0.3-0.5 s; Hide is a faster mirror. Input is blocked during the transition.

Q: How do you handle an animation that must stop at the last frame?
A: Loop Time off on the clip, and the state waits at the end. For logic after it, an Animation Event at the last frame, not a timer.

Q: What is root motion and do you need it for UI?
A: Root motion moves the object from the animation itself. For UI and most 2D effects I keep it off; movement comes from the animated RectTransform or code.

Q: How do you animate UI without breaking layouts?
A: I animate a child inside the layout element, not the element the Layout Group controls. Otherwise the Layout Group fights the animation.

Q: What is 9-slicing?
A: The sprite border is set in the Sprite Editor; corners stay fixed and edges and centre stretch or tile. One sprite can make panels and buttons of any size.

Q: How do you set a sprite pivot and why does it matter?
A: In the Sprite Editor. The pivot is the point for position, rotation and scale, and also for sorting when Sprite Sort Point is Pivot. For characters and props on the ground I use a bottom pivot.

Q: How do you slice a sprite sheet?
A: Sprite Mode Multiple, then the Sprite Editor: automatic by alpha or by grid cell size. When the image changes, I re-slice but keep the same sprite ids so references do not break.

Q: What happens if you delete a .meta file?
A: Unity makes a new GUID, and every reference to that asset breaks. Sprite slices in a sheet are also stored there.

Q: Why keep source art uncompressed when using an atlas?
A: The atlas platform settings decide the final format. Compressing the source too would compress twice and lose quality.

Q: How do you plan atlases for a screen?
A: Group sprites that are shown together, keep UI apart from world art, and put soft shadows and gradients in their own atlas with a cheaper format.

Q: What does Sprite Atlas "Include in Build" do?
A: If on, the atlas ships with the build and loads with the sprites. If off, you must provide it at runtime, for example through Addressables late binding.

Q: How do you make light effects in URP 2D?
A: Light 2D components on the 2D Renderer, with normal maps as secondary textures for volume. Unlit sprites for things that glow by themselves.

Q: What is a Shader Graph Sub Graph for?
A: Reusing a group of nodes, for example a dissolve or a UV scroll, in many graphs. One fix updates all of them.

Q: How do you make a dissolve effect?
A: A noise texture compared with a threshold; pixels below it are discarded, with a thin bright edge near the threshold. The threshold is animated from 0 to 1.

Q: How do you make a UV scroll for water or energy?
A: Offset the UV by time multiplied by speed and sample the texture with wrap mode Repeat. Two layers at different speeds look richer.

Q: Why is alpha clipping cheaper than transparency?
A: It is not always cheaper. Clipping avoids blending and sorting problems, but on mobile tile-based GPUs discard can cost more than simple blending. I measure on the device and pick per effect.

Q: Additive or alpha blended particles?
A: Additive for light, fire, sparks: it brightens and order does not matter much. Alpha blended for smoke and dust, where the dark parts must cover what is behind.

Q: How do you keep VFX readable in a busy screen?
A: A clear shape and timing, contrast with the background, and not too many effects at once. The effect must support the gameplay moment, not hide it.

Q: What is a Sub Emitter?
A: A particle system spawned by events of another, for example on death or collision: a spark that bursts into smaller sparks.

Q: How do you pool particle effects?
A: Stop Action Callback or Disable, then return to the pool. Guard against returning the same instance twice, and use unscaled time for effects that play during pause.

Q: What do you check if a particle effect does not appear?
A: Is it playing and in view, sorting layer and order, material and shader, Max Particles, emission rate, Simulation Space, and whether the camera culling mask includes its layer.

Q: What is a draw call and a batch?
A: A draw call asks the GPU to draw something. A batch groups compatible draw calls. Fewer state changes and fewer calls usually mean less CPU time.

Q: Why does the Stats window show fewer batches but the frame is not faster?
A: Batches measure CPU work. The frame can be limited by the GPU instead, for example overdraw or heavy shaders. I check both.

Q: What is fill rate and why does it matter on mobile?
A: How many pixels the GPU can shade per second. Mobile GPUs have little, so full-screen transparent layers and big particles cost a lot.

Q: What frame budget do you target?
A: 16.6 ms for 60 fps, 33.3 ms for 30 fps, and leave margin because phones heat up and slow down. I watch the 95th and 99th percentile, not only the average.

Q: How does thermal throttling affect testing?
A: A phone slows down after some minutes of load. I test long sessions on a real device, not just the first minute.

Q: Why test on a low-end device?
A: Most problems in memory, loading and frame time show up there first. If it runs well on low-end, high-end is usually fine.

Q: How do you load a scene without freezing?
A: LoadSceneAsync with a loading screen, and load heavy content in the background with Addressables. I avoid big synchronous loads on the main thread.

Q: What is the difference between Resources and Addressables?
A: Everything in Resources always ships in the build and is hard to unload. Addressables load by address from local or remote, handle dependencies, and can be released.

Q: How would you split Addressables groups?
A: By when the content is needed and how it changes: a local group for core UI, remote groups per feature or per island, so a player downloads only what he uses.

Q: What is a catalog in Addressables?
A: The list of addresses and where each bundle lives. The game can check for a new remote catalog to get updated content without a new app build.

Q: How do you test remote content before release?
A: Use a local hosting service or a test profile, build the content, and run the player against it. I test the update path too, not only a fresh install.

Q: What is the difference between Update, FixedUpdate and LateUpdate?
A: Update runs every frame, FixedUpdate on the physics step, LateUpdate after animation and Update. Camera follow and bone overrides go in LateUpdate.

Q: Why use Time.deltaTime?
A: So movement is per second, not per frame. Without it, objects move slower when the frame rate drops.

Q: When do you use a coroutine?
A: For simple sequences over time: wait, then do something. For many timed UI sequences a Timeline or an Animator clip is easier to tune.

Q: What are UnityEvents good for?
A: Wiring simple actions in the Inspector, for example a button calling a method. For core game logic I prefer C# events, because references are visible in code.

Q: How do you make an Inspector easier for artists?
A: Clear field names, [Range] sliders, [Tooltip], [Header] groups, and hiding fields they should not touch. For bigger tools, a custom editor or window.

Q: When do you write an AssetPostprocessor?
A: To apply import rules automatically, for example compression and Max Size by folder, so artists cannot import textures with wrong settings.

Q: How do you validate content before a build?
A: An editor check that scans prefabs and assets for missing references, wrong import settings and too many materials, and fails with a clear list.

Q: What do you do when a teammate's prefab change breaks your screen?
A: Find the exact change in Git history, talk to the owner, and agree on a fix. I do not silently override their work.

Q: How do you review a prefab in a pull request?
A: I open it in Unity, not only the YAML diff: I check hierarchy, references, overrides and that it works in its scene.

Q: What is Force Text serialization?
A: Scenes, prefabs and assets are stored as text YAML, so Git can diff and merge them. It is the default and needed for team work.

Q: How do you report a bug so it is easy to fix?
A: Steps to reproduce, expected and actual result, device and build version, a screenshot or video, and the log.

Q: How do you estimate a task you have not done before?
A: Split it into small parts, build a rough prototype of the risky part first, and give a range, not one number. I update the estimate when I learn more.

Q: What would you do in your first week on this project?
A: Build and run the project, read the pipeline docs, look at how existing features are made, and take a small real task. I ask questions early instead of guessing.

Q: You said you split Canvases. How many is too many?
A: Each Canvas is its own batch group, so too many also costs draw calls. I split by how often things change: one for static background UI, one for often-changing parts like timers and counters, and popups on their own.

Q: Why does a nested Canvas help if it adds batches?
A: It limits the rebuild. A change inside the nested Canvas rebuilds only it, not the parent. A few more batches is cheaper than rebuilding a big screen every frame.

Q: What exactly causes a Canvas rebuild?
A: Changing a Graphic: color, sprite, text, enabled state, or a RectTransform size or position under a layout. Moving an object with no layout under a Canvas is cheaper, but still marks it dirty.

Q: Why is Graphic Raycaster a cost?
A: It tests every raycast target under that Canvas on input. I turn off Raycast Target on decorative images and remove the Raycaster from Canvases that take no input.

Q: And if the designer wants the whole background clickable?
A: One invisible full-size raycast target behind the content, or a button on the root, instead of making every decorative image a raycast target.

Q: What if a Layout Group is slow?
A: Layout groups recalculate when children change. For a static layout I let it compute once and then disable it, or I place elements by anchors. For long lists I reuse views.

Q: What if the artist gives you a PSD with 200 layers?
A: I agree with the artist which layers are separate elements and which can be merged. Only what animates or changes at runtime stays separate; the rest is flattened into fewer sprites.

Q: The artist wants a 4096 texture for a small icon. What do you say?
A: I show it at the real screen size on a phone and compare with 512. If nobody sees the difference, we save memory. If they do, we look for a middle size together.

Q: Why not just use one big atlas for the whole game?
A: The whole atlas stays in memory while any sprite from it is used. A screen that needs one icon would load everything. I group by screen or feature.

Q: When would a sprite not batch even in the same atlas?
A: When the material or shader is different, a different sorting layer sits between them, or another texture is drawn in between in the render order.

Q: Why can Tight mesh be worse sometimes?
A: A very complex outline makes many vertices. For small or simple sprites Full Rect can be cheaper. I check the vertex count and the overdraw together.

Q: How do you choose between ASTC 4x4 and 8x8 for a specific texture?
A: By the content and viewing size. Sharp edges and small text need 4x4; soft gradients, shadows and big blurry backgrounds are fine with 8x8. I compare on the device.

Q: Why keep mipmaps off for UI but maybe on for world sprites?
A: UI is shown at a fixed size, so mipmaps only waste memory. World sprites that zoom out a lot can shimmer without mipmaps.

Q: You said SRP Batcher needs the same shader variant. How do keywords affect that?
A: Each keyword combination is a different variant. Two materials with the same shader but different keywords break the batch. Fewer keywords, more batching.

Q: Why not GPU instancing for all identical sprites?
A: SpriteRenderers do not use GPU instancing in the normal way, and in URP the SRP Batcher already takes compatible objects. Instancing helps for many identical meshes with one material.

Q: If a shader is slow on one phone only, what do you do?
A: Check that GPU with a frame capture or the platform profiler, look for expensive math, many texture samples or discard. Then simplify, use half precision, or move work to the vertex stage.

Q: Why is discard expensive on mobile?
A: Many mobile GPUs use tile-based rendering with early depth tests. Discard breaks that optimization, so the GPU cannot skip hidden pixels early.

Q: Why do you prefer lookup textures over pow or sin?
A: A texture sample can be cheaper than complex math on mobile GPUs, and it gives the artist a curve to edit. But I measure; texture bandwidth also costs.

Q: What if an effect looks right in the Editor but pink on the device?
A: Usually a shader variant that was stripped, or a shader not supported on that graphics API. I turn on strict variant matching to see which variant is missing.

Q: A shader variant hitch on first use. How do you avoid it?
A: Prewarm it during loading: a ShaderVariantCollection with WarmUp, or render the material once off-screen. Then the first real use does not stall.

Q: You pool particles. What goes wrong most often?
A: Reusing a system that is still playing, returning the same instance twice, or state left from last use: color, scale, parent. I reset on take and guard on release.

Q: Why would a particle effect stop working after it was pooled?
A: Stop Action set to Destroy, so the object is gone. Or it was disabled while playing and never restarted with Play.

Q: How do you decide how many particles is too many?
A: I measure the effect on the lowest target phone, together with the rest of the screen. Overdraw and fill rate usually limit before the particle count.

Q: What if an effect must be very big and heavy for one moment?
A: I make it short, keep other effects quiet at that moment, use fewer but bigger particles, and test the peak frame on a low-end device.

Q: You said animation must not decide logic. Give an example of the bug.
A: A reward is given in an Animation Event at the end of the clip. If the player closes the screen early, or the Animator is disabled, the reward is never given.

Q: Animator vs code for a counter that rolls up numbers?
A: Code or a tween, because the value comes from data. An Animator is good for the fixed motion around it, like the punch scale.

Q: Why do Animator transitions sometimes feel late?
A: Exit Time is on, or the transition duration is long. For instant reactions to input I turn Has Exit Time off and use a short duration.

Q: What if two Triggers are set in one frame?
A: Only one transition consumes its Trigger; the other stays set and fires later, unexpectedly. I reset Triggers or use Bools for states.

Q: When would you use Timeline instead of an Animator for UI?
A: When the sequence has many objects and exact timing, and it plays once, like a level complete screen. The Animator is better for states that switch back and forth.

Q: What if the game must support both short and very tall phones?
A: I design for the safe area and anchors, test the extremes (4:3 and 9:20), and let backgrounds extend beyond the safe area while buttons stay inside it.

Q: How do you handle a slow texture upload when opening a screen?
A: Preload the screen's textures before it opens, keep textures smaller, and raise the Async Upload settings if the Profiler shows upload spikes.

Q: What if Addressables loading fails on a bad network?
A: Handle the failed operation: show a retry, fall back to local content if possible, and do not leave the handle unreleased.

Q: What if a player has an old catalog and new code?
A: Remote content must stay compatible with the shipped code. New code that needs new content ships with an app update, or checks the content version first.

Q: How do you stop the same texture from being in two bundles?
A: Put shared assets in their own group, or make them explicit Addressables, so both bundles depend on one copy. Analyze rules show the duplicates.

Q: What is the risk of Can Change Post Release?
A: Any change rebuilds the whole bundle, so players download all of it again. Good for small frequently changed content, bad for big static packs.

Q: How do you know a memory problem is textures and not code?
A: The Memory Profiler shows by type: textures, meshes, managed heap. If textures dominate, it is content; if the managed heap grows, it is code keeping references.

Q: Why can Destroy not free memory right away?
A: Destroy marks the object; the asset it used can stay loaded while anything still references it. Resources.UnloadUnusedAssets or releasing Addressables frees it later.

Q: What if the Profiler shows a GC.Collect spike every few seconds?
A: Something allocates every frame: string concatenation, LINQ, boxing, new lists, closures. I find it with GC.Alloc call stacks and cache or reuse.

Q: What allocates in UI code that people forget?
A: Setting text with string formatting every frame, GetComponent in Update, and creating new lists for layout. Update text only when the value changes.

Q: Why is FindObjectOfType bad in gameplay code?
A: It searches the whole scene every call. I keep references from the Inspector or register objects once.

Q: The frame rate is fine but the game feels stuttery. Why?
A: Uneven frame times: spikes from GC, loading or shader compile. Average FPS hides them; I check the frame time graph and the worst frames.

Q: Why do you test with a release build too?
A: A development build has extra checks and the Profiler connection. Some problems, like stripping or timing, only appear in release.

Q: How would you explain a performance trade-off to a designer?
A: With numbers and a choice: "this effect costs 4 ms on the low phone; we can keep it smaller, or keep it only on high-end." Not "it is too heavy".

Q: How would you convince an artist to change their workflow?
A: Show the problem on the device and a small tool or preset that makes the new way easy. If the new way is more work for them, it will not stick.

Q: What if a developer and an artist both want different solutions?
A: I find the goal behind each one, prototype the risky part, and compare on the device. The data usually decides, not the opinion.

Q: What if you find a bug in someone else's system close to release?
A: I report it with steps and evidence to the owner right away, suggest a fix if I have one, and do not patch it silently.

Q: What if the deadline cannot be met?
A: I say it early, with what can be done by the date and what must move. Cutting scope is better than shipping broken.

Q: How do you keep a tool from becoming abandoned?
A: It solves a real repeated task, is simple to use, has a short guide, and I watch the first artists use it and fix what confuses them.

Q: Why do you write tests for editor tools?
A: Tools change assets for the whole team. A test proves the tool does the right thing and keeps it working when Unity or the project changes.

Q: What makes a good test in Unity?
A: It checks behaviour, not the hierarchy names; it is independent of the open scene; it cleans up what it created; and it fails with a clear message.

Q: What if a test is flaky?
A: I find the cause: timing, frame count, shared state or the open scene. I do not just add a longer wait; I wait for a condition instead.

Q: How do you handle a merge conflict in a scene?
A: Try UnityYAMLMerge first. If it fails, take one side and redo the other change in the Editor, then check the scene works. Big scenes split into prefabs avoid this.

Q: What goes into .gitignore for Unity?
A: Library, Temp, Obj, Logs, Build and UserSettings folders, and IDE files. Assets, Packages and ProjectSettings stay in Git.

Q: Why use Git LFS for art?
A: Big binary files like PSD and FBX make the history huge. LFS stores them outside the normal Git history.

Q: What if AI gives you a Unity API that does not exist?
A: That is why I compile and check the docs for our version. I treat AI output as a draft from a fast junior: useful, but I review every line.

Q: Where does AI help you most as a Technical Artist?
A: Small editor tools, batch scripts, first drafts of shaders, and explaining unfamiliar code. It saves time on routine work; I still own the result.

Q: What is the first thing you check in someone else's prefab?
A: Missing references, the hierarchy and naming, which components do the work, and overrides on instances in scenes that could break.

Q: What would you improve first in a new project pipeline?
A: Nothing in the first weeks without understanding why it is like that. Then the thing that wastes most time for the team, measured, with a small safe change.

Q: What does "production-ready" mean for a feature?
A: It works on target devices, meets the frame and memory budget, handles all states and errors, is tested, reviewed, and another person can work with it.

Q: How do you hand over a feature?
A: A short note: what it does, how it is built, how to change it, known limits. Plus the prefab and settings in a clean state in Git.
