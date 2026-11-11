# The Effects System: How the Game Stores "What Things Do"

Source: custom write-up. **All numbers were read from the owner's own game database** (round 3 dump, 2026-11-10) and counted here; rules in plain words, no names or text copied (hard rule 8). Tags: `[sure]` = read from the database, `[derived]` = counted or computed here, `[verify]` = unconfirmed.
Builds on every earlier page. This page matters most for the future game: it shows **how rules are expressed as data**, which is the part you can copy as a design pattern.

## Step 0 · The big picture

> **Everything that has an effect (a policy card, a belief, a building, a civic, a government, a great person, a promotion) is stored as a short list of the same kind of row: *who* it applies to, *what* it changes, *how much*, and *when*. The game then applies those rows. There is no special code per card.**

```
OWNER (a card, building, belief...)
   -> WHO gets it        (this player, all their cities, all their units, all districts...)
   -> WHAT it changes    (an "effect": add yield, change cost, grant an ability...)
   -> HOW MUCH / WHICH   (arguments: Amount=10, YieldType=gold, UnitClass=...)
   -> WHEN               (an optional condition: "city has a commercial hub", "city follows this religion")
```

## Step 1 · The size of it `[sure]` / `[derived]`

| Where effects live | Effect rows | Different effect kinds used |
|---|---|---|
| Policy cards | 458 | 103 |
| Buildings (including wonders) | 305 | 100 |
| Unit abilities | 256 | 69 |
| Great-person actions (when used) | 226 | 72 |
| Unit promotions | 188 | 55 |
| Great works (art, writing, music) | 160 | 6 |
| Governor promotions | 116 | 73 |
| Great-person birth | 107 | 3 |
| Beliefs | 88 | 14 |
| Improvements | 69 | 14 |
| Project completions | 60 | 17 |
| Commemorations (era goals) | 54 | 43 |
| Governments | 47 | 19 |
| Civics | 46 | 13 |
| Districts | 22 | 17 |
| Techs | 17 | 12 |
| **Total** | **2,219** | **422 different kinds** |

(Civilization and leader content is not counted: that is content, not base rules.)

## Step 2 · What the effects mostly are `[derived]`

The ten most common effect kinds cover **more than half** of all rows:

| Kind of change | Rows | Plain meaning |
|---|---|---|
| Grant an ability | 170 | give units or players a named ability (a bonus rule defined elsewhere) |
| Unit production percent, by unit class and era | 140 | +% production for one unit class in one era (**139 of them are policy cards**, repeated per class per era) |
| Combat strength change | 132 | +/- strength under some condition |
| City yield percent | 127 | +/- % of one yield in a city |
| Attach another modifier | 88 | a wrapper: "when X, also apply Y" (**64 of the 88 belief rows**) |
| Unit purchase cost | 53 | cheaper to buy a unit type |
| Plot yield | 48 | +N of a yield on a tile |
| Military unit production | 33 | +% production of military in a city |
| Unit movement | 30 | +1 movement |
| Building yield change | 28 | +N yield from a certain building |

Next in the list (13 to 28 rows each): unit experience, random resource from a project, city growth, great person points, housing from great works, influence tokens, loyalty pressure, free units, tourism, governor points, trade route capacity, spy chances, amenities.

**Plain reading:** the game's effects are mostly **percent and flat changes to yields, costs, strength, and growth, plus named ability grants.** There are only a handful of true "mechanic changes" (trade route capacity, free units, extra spies, extra envoys).

## Step 3 · The repeated-card pattern `[derived]`

**458 policy-card rows but only 103 distinct effects, and 139 rows are the same effect repeated** (+50% production of one unit class in one era; one card has about 6 to 12 rows, one per class and era). A card's apparent size is mostly bookkeeping repetition.

**Design note:** if your game uses "+X% production for this unit class in this era", store it **once per card with a class list and an era list**, not as 12 rows. That cuts 30% of the policy data.

## Step 4 · What governments actually do (from the same table) `[sure]`

Each government is a handful of rows (47 across all 13). The pattern:

| Government | Fixed bonus | Plus |
|---|---|---|
| Tier 1, three of them | **+10% wonder construction; +20% combat experience; +15% great person points** (one each) | +1 to every yield in a city that has a palace or a government-tier building (the first one); +1 amenity and +1 housing in cities with a specialty district (the second); a melee bonus ability |
| Tier 2, three | **+50% envoy points; +15% faith purchases; +15% district production** | +1 housing per wall age (monarchy); +0.5 faith per citizen in a governed city (theocracy); +10% gold in a governed city (merchant) |
| Tier 3, three | **+50% unit production; +15% gold purchases; production and science bonuses** | +0.6 production per citizen in a governed city (communism); +4 food and production on trade routes with allies and suzerains (democracy); war weariness changes (fascism) |
| Tier 4, three | overall production bonuses | +10% production with a commercial hub or encampment and −10% science (corporate); +2 amenities and +2 culture per district (digital); +30% project production and −10 tourism (technocracy) |

Three of the tier 2 and 3 bonuses **only work in a city that has a governor** (theocracy, merchant republic, communism).

**Caution:** the government table and the modifier rows label two of the fixed bonuses differently (gold purchases versus district production, between one tier-2 and one tier-3 government). The modifier rows are the ones that apply, but which tier gets which is `[verify]`; page 05's tier table follows the government table.

## Step 5 · What techs and civics actually give `[sure]` / `[derived]`

- **Techs have almost no effects of their own** (only 17 rows in the whole table: movement, embarking, one diplomatic vision, one spy, urban defense, and the end-game promotions). **A tech's reward is mostly an unlock**: it makes a building, district, improvement, unit, or card available.
- **Counted unlocks (districts, buildings including wonders, improvements, units, projects, cards, governments)** `[sure]`/`[derived]`:

| Era | Techs: unlocks per tech | Civics: unlocks per civic |
|---|---|---|
| 1 | 4.1 | 3.7 |
| 2 | 4.6 | 5.1 |
| 3 | 4.5 | 4.3 |
| 4 | 2.7 | 4.8 |
| 5 | 3.5 | 4.1 |
| 6 | 3.4 | 2.9 |
| 7 | 2.9 | 3.6 |
| 8 | 1.8 | 1.3 |
| Future | 0.6 | 1.5 |

Total unlocks counted: **34 districts, 116 buildings, 115 units, 43 improvements, 15 projects, 118 cards, 12 governments (453)**. Every tech and civic in eras 1 to 7 unlocks something. Only 4 of 8 future techs, 2 era-8 civics and 1 future civic unlock nothing, **and each of those carries at least one bonus effect of its own, so no node in the game gives nothing** (checked against the technology and civic effect rows). **This corrects the earlier draft** (before units were counted) that said most era-8 techs unlock nothing: they unlock units.
- **Units:** the game has **159 units**; **44 need no tech at all** (starting, civilization-unique, and civilian/great-person ones), and **45 of the 77 techs unlock at least one unit** (medieval techs unlock the most: 21 units in era 3).
- Techs still give more unlocks of things you **build or make**; civics give more **rules**: cards are 118 of the civic unlocks. Techs lead in the early eras (4.1 to 4.6 per tech vs. 3.7 to 5.1); civics lead from era 4 to 6.

**Design note:** unlocks are richest in the first three eras (about 4 to 5 per node) and thin out to about 2 per node by the end, but **no node gives nothing**: where a node unlocks little, it carries a bonus effect. That is the rule worth copying (schema variable `node_rewards`).

## Step 6 · What beliefs do `[sure]`

Beliefs are 88 rows, **64 of them wrappers** that attach another modifier. After resolving one level (round 4), the real effects are:

| What the belief does | Rows |
|---|---|
| +1 or +2 of a yield on tiles with a certain improvement or resource | 13 |
| Add a yield tied to the belief (faith per building, etc.) | 12 |
| +N from a certain building | 4 |
| More yield from international trade routes | 4 |
| Unit strength, unit cost, free unit, housing, great-person points, tourism, wonder production | 2 each or fewer |

The typical pantheon-style belief reads: *"for cities that follow this belief, tiles with improvement X give +1 (or +2) of yield Y."* The typical religion belief reads: *"for cities that follow this religion, building X gives +N of yield Y, or can be bought with faith."* Combat-flavored ones give faith for kills (50% of the defeated strength), healing near holy sites (+30%), or +25% military production in early eras. 4 belief rows are direct tile adjacency bonuses; a few are direct (+10% city growth, +15% border expansion).

**Design note:** a belief is a single sentence: **condition (follows this belief) + tile or building filter + yield bonus.** Nine in ten need no special code. That is the best part of the system to copy.

## Step 7 · Condition sets `[sure]` / `[derived]`

There are **880 named condition sets**; each is a short list of requirements joined together (and some inverted, "must not"). The most common requirement kinds:

| Requirement | Uses |
|---|---|
| Player type or level (major, minor, and so on) | 115 |
| City has building X | 102 |
| Player met another player N turns ago | 85 |
| Player has technology X | 84 |
| Tile has improvement, terrain, feature or district type X | about 40 each |
| Unit is attacking; unit domain matches; opponent's unit class matches | 30 to 42 each |
| Another set is met (nesting) | 32 |
| City has district X | 26 |
| Tile adjacent to the owner | 29 |

**Plain reading:** conditions are mostly *what the city or tile has* (a building, district, improvement, terrain, feature) and *who you are or what you know* (player type, technology, contact). Combat ones check who is attacking and what class is opposite. A set can use another set, so conditions nest. `[derived]`

**Design note:** about 15 requirement kinds cover almost every card. A small, closed list of condition kinds is a good target for your game.

## Step 8 · Era score and ages `[sure]`

- Golden age base threshold: **25 era score**. Dark age base threshold: **25**. A past dark age makes the next threshold **10 easier**, a past golden age **5 harder**.
- **Era score comes from "moments"**: the database lists **162 moment types**. Each is worth **0 to 5 era score**:

| Score | Moments |
|---|---|
| 0 (no score) | 7 |
| 1 | 42 |
| 2 | 50 |
| 3 | 43 |
| 4 | 15 |
| 5 | 5 |

Adding every moment type once gives **356** points; the threshold of 25 is about 7% of that, so a golden age needs a spread of several different moments, not one big one.
- **Two copies of many moments:** 42 "first time you do it" and 43 "first in the world" versions (the world-first is worth one more point). The five 5-point moments are all world-firsts or conquests: meeting every other major player first, a trading post in every civ first, first air unit, first to sail around the world, defeating a player's last city.
- **Moment categories** by count: city (25), unit (15), district (10), project (10), player (9), military formation (8), government (8), improvement (8), building (7), and smaller groups (heroes, great people, religion, trade, spies, barbarians).
- **12 commemoration categories** (scientific, cultural, infrastructure, religious, exploration, economic, industrial, military, tourism, aeronautical, espionage, automaton). At each new era you pick one to commemorate; each has a **golden-age bonus, a normal-age bonus, and a dark-age bonus**, and each is available only for certain eras (the early ones classical to medieval, the last ones era 8 on). 54 effect rows sit behind them.
- Each era lasts **40 to 60 turns** (minimum and maximum) before it can end; liberating a city-state gives **2, 3, 3, 6, 6, 9, 9, 9** envoys by era. Grievance decay per turn falls from **10 to 2** across the eras (so old wars are forgiven more slowly later). Trade routes' minimum length rises by 10 turns every two eras (0, 0, 10, 10, 20, 20, 20, 30, 30). `[sure]`
- A few buildings add era score directly (for example, +1 per "pride moment").

**Design note:** era score is a *scoreboard of varied firsts* with a comeback rule. The world-first bonus (+1) is a clean way to reward being early without making it the only path.

## Step 9 · Other systems the dump surfaced `[sure]`

| System | Numbers |
|---|---|
| **Projects** | 81 projects, 15 of them gated by a tech and some by a district (for example, space launches need the space district and a late tech, and cost 800 to 1,500 production) |
| **Governors** | 12 types (7 standard, 1 leader-linked, 4 secret-society), 64 promotions arranged in levels 0 to 3 and columns; each carries identity pressure 8 (10 for secret-society ones) and a transition strength of 100 to 150; 116 modifier rows between them |
| **Barbarians** | Camps limited to 3 per major civ, at least 4 tiles from a city and 7 from another camp; "boldness" rises 2 per turn, +15 per kill, −30 per camp attacked; clans bribe cost 50 per city |
| **Espionage** | Spy max level 4; escape base chance 10%; fomenting unrest costs the target −15 loyalty (−5 per spy level) and adds identity |
| **Climate** | 45% of coastal lowlands flood at the max level; units give 50% of CO2 |
| **Minor-power types** | 6 city-state bonus types (scientific, religious, trade, cultural, militaristic, industrial); suzerain at 3 envoys `[sure]` |
| **Resources** | 55 resources: 34 luxury, 11 bonus, 7 strategic, 2 artifact, 1 ley line. Each luxury gives **4 amenities** (3 of them give 6). Luxuries give gold +1 to +3, food +1 to +2, and 1 culture, faith, science or production in ones and twos; bonus resources give +1 food (6 of 11) or +2 gold (3); strategic give +1 to +3 production, plus 1 science or 1 food for 4 of them |
| **Improvements** (17 buildable base ones) | farm +1 food; mine +1 production; quarry +1 production; fishing boat +1 food; pasture +1 production; plantation +2 gold; camp +2 gold; lumber mill +2 production; a few late ones (corporation-type +10 production, industry-type) are large; farms, boats, pastures, plantations and camps give **1 housing per 2 improved tiles** `[approx]` |

## Open items

- Full list of condition-set contents per card (the digest is in the dump; a per-card readout would need a join).
- Moment trigger details (what exactly counts), and the per-category commemoration bonuses (text not dumped).
- Per-unit stat sheet for all 159 units (loaded; not written up).
- Policy card effects after unwrapping (only beliefs were summarized here).

## Sources

- The owner's game database: modifier tables, GlobalParameters, resources, improvements, governors, eras. All counts and sums on this page were done here.
