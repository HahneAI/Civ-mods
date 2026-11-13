# Custom change: Heroes and Legends rework (DRAFT)

Source: custom (owner request, 2026-11-13) plus a web check. **Status: design draft. Nothing is built.** Ledger first, then build (TODO Phase 5). Plain words only; nothing copied (hard rule 8).

Tags: `[sure]` = seen in the owner's own game logs. `[verify]` = from public sources or general knowledge, dated around the 2020 launch, still to be confirmed from the game database (round 5, section 8). `[owner]` = a decision that belongs to the owner.

## 1. What the owner wants

1. **Heroes should be rarer.**
2. **Getting a hero onto the map should take more infrastructure** than it does now.
3. **The AI should use heroes better,** through better AI strategy tuning, so opponents can take advantage of the mode too.

## 2. What the rule does today

- The mode exists, is owned, and ran in playtest 002. The log said "Hero MODE is: ON". `[sure]`
- **12 unique heroes.** Each has to be discovered before anyone can claim it. `[verify]`
- **Discovery is partly luck.** Sending an envoy to a city-state has about a 10% chance of revealing a hero; becoming a city-state's first suzerain guarantees one. A repeatable city project, available in cities with a Monument, also discovers a random hero. `[verify]`
- **Claiming:** a city with a Monument can recruit a discovered hero through a devotion. A claimed hero is gone for every other civ. `[verify]`
- **Lifespan:** each hero lasts a set number of turns, then leaves. It can be recalled with faith once per era, in the city that first claimed it, at a rising price. `[verify]`
- **On death or expiry** a hero leaves relic-type great works with lasting bonuses. `[verify]`
- **Claiming a hero** also gives a one-time production bonus, and the mode lengthens lifespans. Source is one forum post; exact numbers unconfirmed. `[verify]`
- **Power:** players describe heroes as very strong, one even enough to wreck a civ, and growing by era. The design intent players cite is a catch-up mechanic, a way to recover from a bad early game. `[verify]`

**The key finding for goal 2:** today the only infrastructure gate in the claiming path is a **Monument**, the cheapest early building. `[verify]` That makes "more infrastructure" an easy lever to turn.

## 3. Where it lives

- In the logs the mode loads as `Heroes_*` components (data, files, in-game UI) and a `Babylon_ProductionPanel_MODE` replacement of the production panel. CQUI also replaces the production panel, and the two coexisted fine in playtest 002. `[sure]`
- Table names, columns and values: **unknown until the round 5 dump.**

## 4. What the mods changed

- Our seven active or planned mods do not touch heroes as far as we know. `[verify]`
- **Real Strategy (AI):** its page lists Heroes and Legends as a mode that fits, because it only adds content. It does not say it teaches the AI to use heroes. Whether the AI discovers, claims or recalls them at all is **unknown** (no discussion found). Test in play before assuming anything. `[verify]`
- Civilizations Expanded and Steel and Thunder: not installed; not checked.

## 5. The three goals, lever by lever

### Goal 1: rarer
Possible levers, to be matched against real data:
- The per-envoy discovery chance (about 10% today).
- Whether the first-suzerain discovery stays guaranteed.
- Cost or availability of the repeatable discovery project.
- How many of the 12 heroes are in play per game (for example a random subset).
- Lifespan length, recall cost and recall limits (rarer in time, not just in number).
- Whether relics left behind make recalls too easy.

### Goal 2: more infrastructure
- Raise the gate above a Monument: a specific district, a building tier, or a count of districts.
- Gate by era, or by hero (a war hero needs military buildings, a builder hero needs industry).
- Scale the price with the number of cities.
- **Watch the AI.** If the gate is something the AI rarely builds, heroes become player-only. Pick gates the AI already prioritizes, or goal 3 has to teach it.

### Goal 3: AI that uses heroes
Three possible layers, cheapest first:
1. **Observe.** Play a game, count heroes discovered, claimed and recalled by each AI civ.
2. **Data only.** Adjust the AI's priority lists so hero-related projects and units get scored. Low risk if confined to hero entries.
3. **Lua logic.** Real decisions (when to recall, where to send the hero). Highest effort and risk.

Constraints:
- Real Strategy's author says mixing it with other AI-altering mods gives weird results. So this change must be **our own small patch file, loaded after Real Strategy, touching only hero entries.** We never edit Real Strategy's files.
- Keep the no-cheating rule: the AI only uses information a player could see, and gets no free heroes.

## 6. Design decisions `[owner]`

| Goal | Options | My lean | Decision |
|---|---|---|---|
| 1 Rarity | lower discovery chance / remove guaranteed discovery / fewer heroes per game / shorter lifespan / costlier recall | combine two: lower discovery odds plus costlier recall, after seeing real numbers | |
| 2 Infrastructure | raise the gate / era gates / per-hero gates / price by city count | raise the gate to something the AI already builds, then tune | |
| 3 AI | observe only / data-only tuning / Lua | observe first, then data-only | |

**Suggested order:** goals 1 and 2 (small, testable data edits), measure the effect on the AI, then goal 3.

## 7. Honest ratings

| Goal | Rating | Why |
|---|---|---|
| 1 Rarity | **8/10** | A data edit, easy to test, and strong players already see heroes as very powerful. |
| 2 Infrastructure | **7/10** | Same kind of edit. Risk: the gate may hit the AI harder than the player. |
| 3 AI use | **5/10** | Least predictable, hard to measure in a 50-turn test, and it sits close to Real Strategy's files. Do it last. |

**One real risk:** goals 1 and 2 make heroes harder to get, and the AI is probably worse than a human at meeting infrastructure gates. That is a guess. If true, the changes shrink the AI's hero use, which goal 3 then has to fix. This is why the order matters.

## 8. Round 5 dump: what to read from the game database

1. **List the hero-related tables** (the dump tool now lists any table with "Hero" in its name, with row counts and first columns).
2. **The 12 heroes:** names, abilities, unit stats, lifespan, recall cost and limits.
3. **Discovery rules:** the envoy chance, the first-suzerain rule, the project's cost and prerequisites.
4. **Claim rules:** what the devotion needs (Monument?), cost, who can claim.
5. **AI side:** any AI list or strategy entries that mention heroes.
6. **Real Strategy:** whether its tables mention heroes. (Needs the mod's files in `vendor/`.)

## 9. Build plan (later, TODO Phase 5)

- Files go in `mod/CivLayer/Data/custom/` with `CL_` names where new types are needed (hard rule 3).
- Gate with Criteria so the layer loads without the New Frontier Pass content (hard rule 5).
- Cite this page in every file header (hard rule 6).
- One change per commit; the owner playtests each change alone before the next.

## 10. Open questions for the owner

1. How rare is "rarer"? Roughly half as often, or only one or two heroes per game?
2. Should the change apply to the AI and the player equally, or give the AI a softer gate?
3. Which infrastructure matters to you: a particular district, a building tier, or a count?
4. Do you want heroes to feel different per type (war, builder, diplomacy)?
5. Should hero recall stay in the mode?
