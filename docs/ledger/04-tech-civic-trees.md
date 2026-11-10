# Tech and Civic Trees: The Progress Engine

Source: custom write-up. **All numbers on this page were read from the owner's own game database** (`DebugGameplay.sqlite`, 2026-11-10, both expansions loaded, 77 techs and 61 civics) with `tools/dbdump.py`, then analyzed here. Rules in plain words; no tech or civic names are used (hard rule 8), nodes are described by era and position. Tags: `[sure]` = read from the database, `[derived]` = computed from database numbers, `[verify]` = still unconfirmed.
Builds on [`00-base-math.md`](00-base-math.md) (the science and culture meters).

**Correction notice:** an earlier draft of this page used a web table of costs. It was for a different version and was wrong by up to 40% in the middle eras. This version replaces it.

## Step 0 · The big picture

> **A tree is a list of unlockable things, each with a price, a set of things you must already have, a discount if you do a certain act on the map, and a list of rewards. Two trees run side by side: one paid with science, one with culture.**

```
SCIENCE per turn -> fills TECH meter -> tech done -> unlocks units, buildings, improvements, districts
CULTURE per turn -> fills CIVIC meter -> civic done -> unlocks governments, policy cards, some buildings/units
                       ^
        BOOST (do a map act) -> 40% off that node
```

## Step 1 · What one node is

Every node has the same fields `[sure]`:

| Field | Plain meaning |
|---|---|
| Cost | How much of the meter you must fill |
| Era | Which age of history it belongs to |
| Prerequisites | Other nodes you must already have (0 to 4 for techs, 0 to 2 for civics) |
| Boost | A map act that gives a partial discount |
| Unlocks | What you receive |

A tech can also be flagged repeatable (only the very last one is).

## Step 2 · The tech tree, in numbers

| Era | Techs | Cost range | Average | Era total | Cost jump vs. previous era |
|---|---|---|---|---|---|
| 1 | 11 | 25 to 80 | 51 | 565 | n/a |
| 2 | 8 | 120 to 200 | 160 | 1,280 | ×3.12 |
| 3 | 8 | 300 to 390 | 345 | 2,760 | ×2.16 |
| 4 | 9 | 600 to 730 | 658 | 5,920 | ×1.91 |
| 5 | 8 | 930 to 1,070 | 1,000 | 8,000 | ×1.52 |
| 6 | 8 | 1,250 to 1,370 | 1,310 | 10,480 | ×1.31 |
| 7 | 8 | 1,480 to 1,660 | 1,548 | 12,380 | ×1.18 |
| 8 | 9 | 1,850 to 2,155 | 1,952 | 17,565 | ×1.26 |
| Future | 8 | 2,200 to 2,600 | 2,288 | 18,300 | (last one repeats) |

- **69 techs in the eight eras, 58,950 science total** `[derived]`; with the future era, 77 techs and 77,250. `[sure]`
- Costs rise fast at first (×3.1, ×2.2) and flatten to about ×1.2 late. Each era has **two price levels** inside it: a cheaper first group and a dearer second group. `[derived]`
- Cost is shifted by about **−20% for a node older than the current game era and +20% for one newer**, so players who fall behind get a discount and leaders pay more. `[sure]` that the two settings exist; the exact rule for "behind" `[verify]`.
- Game speed multiplies every cost: **marathon 3.0, epic 1.5, standard 1.0, quick 0.67, online 0.5**. `[sure]`
- No evidence of cost scaling with the number of cities. `[sure]` (no such setting exists)

**Worked out here:** at a flat 100 science per turn, the eight eras (without boosts) take about 590 turns. The first three eras cost only 4,600 combined (8% of the tree); the last three cost 40,400 (69%). So almost the whole tree is paid late, by a large economy.

## Step 3 · The tree's shape (the part the web could not give)

All figures are for the 69 eight-era techs; future techs have no recorded prerequisites, so they are handled apart.

| Shape measure | Value |
|---|---|
| Nodes / links between them | 69 / 95 |
| Starting nodes (no prerequisite) | **5**, all in era 1 |
| Ending nodes (nothing depends on them) | 7 |
| Longest chain (depth) | **15 steps** |
| Prerequisites per node | 0: 5, 1: 37, 2: 24, 3: 2, 4: 1 |
| Dependents per node | 0: 7, 1: 37, 2: 17, 3: 8 |
| Links inside one era / to the next era | 29 / 66 |
| Links that skip an era | **0** |

Width by depth (how many nodes sit at each step from the start):

`5, 8, 4, 4, 7, 6, 4, 4, 4, 5, 5, 5, 2, 3, 3`

Reading that: the tree **opens up in the first two steps (up to 8 side by side), stays 4 to 7 wide through the middle, and narrows to 2 or 3 at the end**: a funnel. Most nodes (54%) have a single prerequisite and a single dependent, so the middle is a set of long parallel chains with occasional joins (the 24 two-prerequisite nodes and 3 with more).

- **Hubs:** the starting nodes unlock almost everything: the first-era starters gate 45 to 48 of the other 68 techs each. `[derived]`
- **Critical chain:** the most expensive single chain to one end tech costs **13,980 science, only 24% of the whole tree**. So you can reach the last tier while skipping three quarters of the tree. `[derived]`
- **No era skipping:** every link goes to the same era or the next, never further. That keeps the tree readable.

**Design note:** a tree with one hard rule (links never skip an era), 1 to 2 prerequisites per node, a few starting nodes, and a funnel-shaped end is a simple, copyable recipe. Total node count (69) is about where players can still remember the whole tree.

## Step 4 · The civic tree, in numbers

| Era | Civics | Cost range | Average | Era total | Cost jump |
|---|---|---|---|---|---|
| 1 | 7 | 20 to 70 | 49 | 340 | n/a |
| 2 | 7 | 110 to 175 | 131 | 920 | ×2.71 |
| 3 | 7 | 220 to 420 | 334 | 2,340 | ×2.54 |
| 4 | 6 | 440 to 720 | 587 | 3,520 | ×1.75 |
| 5 | 7 | 800 to 1,210 | 1,013 | 7,090 | ×1.73 |
| 6 | 9 | 1,540 to 1,715 | 1,608 | 14,475 | ×1.59 |
| 7 | 5 | 1,955 to 2,415 | 2,231 | 11,155 | ×1.39 |
| 8 | 7 | 2,880 to 3,100 | 2,963 | 20,740 | ×1.33 |
| Future | 6 | 3,200 to 3,500 | 3,250 | 19,500 | |

- **55 civics in the eight eras, 60,580 culture total**; with the future era, 61 and 80,080. `[sure]`/`[derived]`
- The same ±20% era shift and game-speed multipliers apply as for techs. `[sure]`
- **Civics get more expensive than techs in the late game:** the last era averages 2,963 culture versus 1,952 science. `[derived]`

Shape `[derived]`:

| Shape measure | Value |
|---|---|
| Nodes / links | 55 / 78 |
| Starting nodes | **1** (one civic opens the whole tree) |
| Ending nodes | 13 |
| Longest chain | **17 steps** |
| Prerequisites per node | 0: 1, 1: 30, 2: 24 (never more than 2) |
| Links inside one era / to the next | 41 / 37 |
| Links that skip an era | 0 |

Width by depth: `1, 2, 4, 3, 4, 3, 4, 4, 2, 4, 3, 3, 3, 6, 2, 3, 4`

- The civic tree **starts as a single trunk**: the first civic gates all 54 others, and the next few civics each gate 43 to 48. `[derived]`
- It is **deeper and flatter** than the tech tree (17 steps, steady width of 3 to 4, no wide opening). The most expensive chain costs 18,435 culture (30% of the total).
- Its 13 ending nodes include the end-of-line unlocks: the highest-tier governments and policy chains (page 05).

**Where the trees differ** `[derived]`:

| | Tech tree | Civic tree |
|---|---|---|
| Starts | 5 side-by-side starters | 1 trunk |
| Shape | wide opening, funnel end | long, steady width |
| Depth | 15 | 17 |
| Max prerequisites | 4 | 2 |
| Late cost | cheaper | dearer |
| Mostly unlocks | things you build and make | rules you choose (page 05) |

**Design note:** the contrast is intentional and worth keeping: science is a branching map of options, culture is a narrow road you walk in order, and the second one is dearer. Open question: do you want two trees, or one tree with two node types?

## Step 5 · Boosts: the map acts that discount research

- **Both trees:** a boost takes **40%** off the node (not 50%). `[sure]` One late civic is the exception, at 90%. `[sure]`
- **Coverage:** 73 of 77 techs and 53 of 61 civics have an entry. The three first starter techs and the repeatable end tech have none. Of the 73, **11 are placeholders** (a late "critical tech" label, no real trigger), so about **62 techs have a real boost**. `[derived]`
- **Number of trigger kinds:** 45 different trigger types for 126 rows. `[sure]`

What the triggers ask you to do `[derived]`:

| Trigger family | Rows | Plain meaning |
|---|---|---|
| Build or own something | 84 | have N buildings, improvements, districts, wonders, units, cities, great people |
| Chain: get another node first | 10 | research or learn a related node |
| Combat | 10 | kill a unit type, clear a camp, receive or declare war |
| Placeholder (no boost) | 11 | late techs with no normal trigger |
| Diplomacy and trade | 6 | meet a civ, have an alliance, maintain trade routes |
| Explore | 3 | discover a continent or natural wonder, extract an artifact |
| Religion | 2 | found a religion or pantheon |

**Two thirds of all boosts (67%) are "build or own something."** Only 10 involve fighting and 6 involve other players.

**What a boost is worth** `[derived]`: with every boost, the eight-era tech tree costs about 35,400 instead of 58,950. A single boost on a 1,500-cost tech saves 600 science, 6 turns at 100 science per turn.

**Guardrail:** research is not only a number to grow. The tree tells you what to build.
**Design note:** boosts turn the tree into a **quest list that rewards playing the map**. Rating **9 out of 10** for your tile game. Two things to improve: (1) the "build or own" family dominates, so research mostly follows what you were building anyway; add more world-facing triggers. (2) 11 techs have none, which feels like a gap.

## Step 6 · Eras: the clock the trees run on

- Eras advance as you move through the **science** tree. `[sure]`
- Era 2's great-person base cost is 60; by era 8 it is 1,320. See page 05.
- A "next era" timer of 10 turns exists. `[sure]` Era score, confirmed `[sure]`: golden age needs **25**, dark age is below **25** (base thresholds); each past dark age makes the next threshold **10 easier**, each past golden age **5 harder**. What earns era score: 162 "moment" types worth 0 to 5 each (page 07, Step 8). `[sure]`

## Step 7 · How the trees connect to everything else

| From | To | Rule in plain words |
|---|---|---|
| Citizens, districts, buildings (pages 00, 03) | Science, culture meters | the sources |
| Science / culture | Tech / civic node | fills the cost |
| Map act | Boost | 40% off one node |
| Tech node | Units, buildings, districts, improvements | new options on the map |
| Civic node | Governments, policy cards | rule choices (page 05) |
| Game era vs. node era | Cost ±20% | catch-up discount, leader surcharge |
| Game speed | All costs | ×0.5 to ×3 |

**Core loop to test in your game:** *more land and buildings → more science and culture → nodes done → new buildings, units, and rules → more land and buildings.* Boosts add a second input: *do the thing the tree asks → 40% off.*

**What the nodes unlock** (counted from the database including units, page 07): techs average 4.1 unlocks in era 1 and 1.8 in era 8; civics average 3.7 to 5.1 until era 7. Every tech and civic in eras 1 to 7 unlocks something. Most of a civic's unlocks are policy cards; 45 of 77 techs unlock at least one unit. See [`07-effects-system.md`](07-effects-system.md).

## Open items

- Which techs and civics each boost belongs to (the trigger details: counts, item types). The dump has them, a follow-up page can list the shape of each trigger without names.
- What each node unlocks (needs the unlock tables).
- Exact meaning of "behind the game era" for the ±20% rule.
- Era score thresholds.
- Future-era prerequisites (random per game).

## Sources

- Everything above: the owner's game database, read with `tools/dbdump.py`. No web figures remain on this page.
