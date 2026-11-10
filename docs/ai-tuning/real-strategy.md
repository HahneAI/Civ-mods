# Real Strategy (AI): working notes

Owner priority: **AI tuning.** This page records what the mod does, how it can be inspected, and what to watch in playtests. Sources are the owner's screenshots of the Workshop page (2026-11-10), the mod's CivFanatics page, and Workshop stats fetched the same day. Everything below is paraphrased in our own words (hard rule 8).

## Identity

| | |
|---|---|
| Author | infixo |
| Workshop ID | **1617282434** (confirmed against the live page) |
| Version | 2.3.1 (Aug 2023). Posted Jan 6, 2019; last updated Aug 5, 2023; 23 change notes |
| Tagged for | Base Game, Rise and Fall, Gathering Storm |
| Size | about 1 MB |
| Reach (2026-11-10) | about 121,900 subscribers, 289,600 unique visitors, 9,000 favorites, 2,156 ratings, 1,229 comments |
| Home | CivFanatics thread "Real Strategy (AI)" (discussion preferred there); a GitHub repo is linked from the Workshop page |
| Part of | the author's "Real Mods Series" |

## How it works

Two layers working together:
1. **Lua "thinking."** Scripts that look at the game situation each turn, judge what other civs are doing, and steer the AI's goals.
2. **Tuned AI lists.** The AI's own data tables (leader behavior lists, flavors, strategies, tactics) were fixed and extended. Per the author, practically all original entries are kept and many are added, with errors fixed.

It runs inside the mod system only, so it tunes the AI's priorities and inputs. It does not replace the game's decision engine.

## What it changes (as described by the author)

- **Victory strategy.** The AI weighs which victory to chase by assessing its own position and what others are doing. The author calls this the core of the mod, built from ideas used in Civ 5, re-done for Civ 6. Each victory strategy was revised; diplomatic victory is supported.
- **Anti-strategies.** Better handling when a victory type is disabled in game setup.
- **Naval play.** From the tiles it has revealed, a civ decides which situation it is in (Pangea, Default, Coastal, Island) and adjusts its behavior.
- **Flavors.** Leaders, policies, wonders and a few other things carry flavors that signal what kind of game is being played.
- **Leader behavior lists.** Extended and bug-fixed so leaders can pursue their own goals.
- **Supporting strategies** (author says simple, to be improved): peace and war posture; catching up when lagging in military (weak civs get killed first); science or culture push; emergency defense when a strong civ attacks.
- **Time strategies.** Revised and updated.
- **Tactics and operations.** Light tweaks to behavior trees, mostly so the AI sieges better (rams and similar) and prepares for war.
- **Air and nukes.** Uses bombers heavily; also nukes.
- **Start biases.** Missing biases added for civs, based on geography.
- **Settling.** Slightly revised parameters, better spots "a bit." The author says the settling system is too simple for any grand result.
- **Great person handling.** Scripts for better handling exist but are **temporarily disabled.**
- **Later versions (from search, not the screenshots):** 2.3 made the AI more aggressive in later eras; 2.3.1 added Gold and Faith balance changes for Gathering Storm and AI building walls.

## No-cheating policy

The "thinking" code only uses information a human player would also have (for example, it knows nothing about another civ until it has met them). The mod gives the AI **no free units, boosts or yields.** This is why it pairs with ordinary difficulty instead of fighting it.

## Rules from the author's page

| Rule | What it means for us |
|---|---|
| Works with vanilla, Rise and Fall, Gathering Storm and all DLC in any configuration, but is **balanced for Gathering Storm** | Our ruleset. Good fit. |
| **Do not use with scenarios** (they have their own AI rules) | Don't play the owned scenarios (Conquests of Alexander, Gifts of the Nile, multiplayer scenarios) with it on. |
| The "affects save files" flag is FALSE; it stores its own data in the save, so it can be switched on or off mid-game and a reload continues its behavior | Safe to add to an existing save. |
| **Not compatible with AI+.** Expect database errors with both | Never run both. |
| **Not recommended with other AI-altering mods.** They might work technically, but results get weird | Keep it the only AI mod. Matters for Civilizations Expanded later. |
| Game modes that change AI behavior fit badly: **Barbarian Clans and Zombies** | Owner owns Barbarian Clans. **Leave that mode off.** |
| Game modes that only add content are fine: Tech Shuffle, Monopolies and Corporations, Secret Societies, Heroes and Legends | Heroes and Legends was on in playtest 002, so that's fine. |
| Multiplayer: supported. Setting file `RST_Params.sql` has three random-number options: 0 (none), 1 (single-player only, `math.random`), 2 (single and multiplayer, engine random; **default**) | Leave at the default. Revisit only if we ever test multiplayer. |

## Diagnostics the author provides

- Post **Lua.log** with any issue; it holds the key information.
- A small **FireTuner panel tool** (posted on CivFanatics) lets you see how the AI behaves with the mod. Not set up yet; worth looking at when we study the AI.

## Reception and the limits of the mod

- Most often recommended AI overhaul in the sources found, with AI+ the main alternative (see popularity below).
- The author himself says settling gains are modest.
- A Steam discussion thread found neither Real Strategy nor AI+ made a dramatic difference toward real strategic play, and one CivFanatics user reported them making the AI worse in some respects. These are individual reports.
- **Expect better, not brilliant.**

## Popularity check (2026-11-10)

- Real Strategy: **about 121,900 subscribers.** That is very large for a Civ 6 mod.
- The only other AI mod stats we could fetch: "Game Balancing (For A Better AI)" by Tiramisu, **314 subscribers**, and it says it changes no AI behavior.
- AI+ (by Siesta Guru): found on CivFanatics, **no Workshop page found,** so no comparable count. The mod list already calls it unmaintained.
- Not verified: subscriber counts for Schwarzpol's Smoother Difficulty, Harder AI, or Balance of Power. So we can say Real Strategy is the **default pick and the biggest one we could measure**, not proven to be the biggest overall.

## Risks in our stack

1. **Workable 4th Ring.** The AI's settling and city-work logic assumes the normal 3-ring range. Guess, not a known problem. Watch AI city spacing.
2. **CQUI.** No confirmed report of a conflict. One commenter suspected one around city behavior. Watch for Lua errors.
3. **Civilizations Expanded and Steel and Thunder (later groups).** They change civs, leaders and units. Real Strategy assigns flavors and start biases per civ and leader, so new or changed ones may lack entries. One modder reported needing to comment out the start-bias lines to make two mods work together (mod unnamed). Test Real Strategy alone first, then add each.
4. **Barbarian Clans.** Avoid.

## What to watch in playtests (AI tuning log)

Fill in per playtest in `docs/playtests/`. Starting list:
- Where do AI cities settle: coast, fresh water, near resources, or crowded together?
- Do AI civs pick a victory direction and stick to it, or flip-flop? (Check a late save.)
- Naval behavior on island or coastal maps.
- War: do they bring sieges? Do weak civs get picked off? Do AI use bombers?
- AI turn length. Note any long stalls.
- Any Lua errors with an RST prefix or from the mod's scripts. We don't know the exact log prefix until the first run.

## Ledger hooks (for the owner's own game)

Ideas worth recording in `docs/ledger/` (AI page), described in our own words:
- A strategy layer that **scores victory paths** from current position and what rivals appear to be doing.
- **Flavors**: tags on leaders, policies and wonders that tell the AI what kind of game it is in.
- **Goal lists per leader**, so personalities differ.
- **Behavior trees** for war operations (siege, prepare, defend).
- A **no-cheat information rule**: the AI only sees what a player could see.
- **Catch-up and emergency behaviors** (military, science, defense) as named strategies.
- **Start biases** tied to geography.
Design decision for each: keep, change, cut or replace. Owner to decide.
