INFO:
ABOUT ME:
- Unity Technical Artist, 7+ years in game development
- Started as a developer with Flash and ActionScript 3, moved to Technical Art
- Worked at VOLMI, Mad Brain Games, GamePoint, Sigma Software, Skywind Group
- Now at Custom Game Studio: mobile and slot game projects
- Main skills: Unity UI integration, animations, Spine, atlases, localization, performance optimization
- I take art content, set it up in Unity, fix technical problems, make it work well in the game
- I like working between artists and developers, I understand both sides
- I know C# basics, I can read and fix code, I used to write Flash games
- I speak Ukrainian and English

UNITY KNOWLEDGE (facts AI can use):
- Canvas: every Canvas rebuild can be slow. Use many small canvases, split static and moving UI. Never change text every frame on one big canvas.
- Atlas: one big texture with many small images. Fewer materials = fewer draw calls. Sprite Atlas in Unity packs images. Use Sprite Atlas instead of packing in Texture Packer when possible.
- Draw call: one draw call = one material shown on screen. Less draw calls = faster game. Ways to lower: atlases, batching, same material, less UI objects.
- Batching: Unity joins objects with the same material into one draw call. Static batching for static objects, dynamic batching for moving ones. For UI use atlases and one canvas per group.
- Memory: textures use most memory. Use correct size, compression (ASTC for mobile), remove unused assets. Atlases waste space if not packed well.
- Addressables: Unity system to load content by address. Load what you need, release when done. Good for big levels, DLC, live content. Better than Resources folder.
- Spine: 2D skeletal animation tool. Better than many frame animations: less memory, smooth movement, easy to mix animations. Needs runtime in Unity.
- Localization: show text in many languages. Unity Localization package or CSV/PO tables. Fonts must support all languages.
- Performance: profiler first (Unity Profiler, Memory Profiler, Frame Debugger). Find the biggest problem, then fix it. Do not guess.
- Mobile: keep textures small, compress audio, avoid many transparent layers, avoid big particle systems. Test on a real low-end device.
- Text: use TextMeshPro, it is crisper and has more features than old UI Text.
- Animation: use Animator for simple clips, code/Tween for simple moves (Scale, Fade, move). Do not make huge animation controllers.
- Premultiply alpha: image setting for correct transparency in atlases. Turn on for atlases with transparent pixels.
- Build size: remove unused sprites, compress textures, split levels with Addressables/AssetBundles.
- Testing: Unity Profiler shows CPU, GPU, memory. Frame Debugger shows draw calls one by one. Memory Profiler shows textures and leaks.

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