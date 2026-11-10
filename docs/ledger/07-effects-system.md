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
- **Counted unlocks (districts, buildings including wonders, improvements, cards, governments; units not counted):**

| Era | Techs: unlocks per tech | Civics: unlocks per civic |
|---|---|---|
| 1 | 3.1 | 3.6 |
| 2 | 3.0 | 5.1 |
| 3 | 1.9 | 3.7 |
| 4 | 1.3 | 4.3 |
| 5 | 1.6 | 3.9 |
| 6 | 1.9 | 2.7 |
| 7 | 1.0 | 3.4 |
| 8 | 0.2 | 1.3 |
| Future | 0.2 | 1.3 |

Total unlocks counted: **34 districts, 116 buildings, 43 improvements, 118 cards, 12 governments.** Every civic in eras 1 to 7 unlocks something; **7 of 9 era-8 techs unlock none of these** (their reward is units and victory progress, not counted here).
- **Civics hand out more than techs in every era** (cards dominate: 118 of the unlocks). Late techs are almost pure prerequisites. `[derived]`

**Design note:** unlocks front-loaded into the first four eras, a long tail of prerequisite-only late nodes. If you copy the trees, decide whether you want that tail.

## Step 6 · What beliefs do `[sure]`

Beliefs are 88 rows, **64 of them wrappers** ("attach this other modifier to cities that follow the religion"), 9 add a religious building, 4 are tile adjacency bonuses (a holy-site bonus from tundra, desert, jungle, etc.), and a few are direct (+10% city growth, +15% border expansion). The real effect sits one level down in the attached modifier, so beliefs are not fully readable from this dump. `[verify]` (a follow-up resolves one level of wrapping)

## Step 7 · Condition sets `[sure]`

An effect's "when" is a named set of requirements shared between many effects (for example "city has a commercial hub", "city follows this religion", "building is the palace or a tier-N government building"). Requirement sets are **reused**, which keeps the data small. Their full contents were not dumped. `[verify]`

## Step 8 · Era score and ages `[sure]`

- Golden age base threshold: **25 era score**. Dark age base threshold: **25**. A past dark age makes the next threshold **−10 easier**, a past golden age **+5 harder**. This confirms the comeback rule from page 04.
- A few buildings add to era score directly (for example, +1 per "pride moment" up to a limit), so era score can be built.

## Step 9 · Other systems the dump surfaced `[sure]`

| System | Numbers |
|---|---|
| **Governors** | 12 types (7 standard, 1 leader-linked, 4 secret-society), 64 promotions arranged in levels 0 to 3 and columns; each carries identity pressure 8 (10 for secret-society ones) and a transition strength of 100 to 150; 116 modifier rows between them |
| **Barbarians** | Camps limited to 3 per major civ, at least 4 tiles from a city and 7 from another camp; "boldness" rises 2 per turn, +15 per kill, −30 per camp attacked; clans bribe cost 50 per city |
| **Espionage** | Spy max level 4; escape base chance 10%; fomenting unrest costs the target −15 loyalty (−5 per spy level) and adds identity |
| **Climate** | 45% of coastal lowlands flood at the max level; units give 50% of CO2 |
| **Resources** | 55 resources: 34 luxury, 11 bonus, 7 strategic, 2 artifact, 1 ley line. Each luxury gives **4 amenities** (3 of them give 6). Luxuries give gold +1 to +3, food +1 to +2, and 1 culture, faith, science or production in ones and twos; bonus resources give +1 food (6 of 11) or +2 gold (3); strategic give +1 to +3 production, plus 1 science or 1 food for 4 of them |
| **Improvements** (17 buildable base ones) | farm +1 food; mine +1 production; quarry +1 production; fishing boat +1 food; pasture +1 production; plantation +2 gold; camp +2 gold; lumber mill +2 production; a few late ones (corporation-type +10 production, industry-type) are large; farms, boats, pastures, plantations and camps give **1 housing per 2 improved tiles** `[approx]` |

## Open items

- One more level of wrapping (what the attached modifiers do) for beliefs and many cards.
- The contents of the condition sets.
- Which unit unlocks each tech gives (units were not in the dump).
- Era-score earners (the moments table was not found under the guessed name).

## Sources

- The owner's game database: modifier tables, GlobalParameters, resources, improvements, governors, eras. All counts and sums on this page were done here.
