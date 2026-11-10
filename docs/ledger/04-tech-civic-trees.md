# Tech and Civic Trees: The Progress Engine

Source: custom write-up from general Civ 6 knowledge plus a web check (see "Sources"). Plain words, nothing copied. In line with hard rule 8, **no tech or civic names are used here**; nodes are described by era and position. Tags as before: `[sure]`, `[approx]`, `[verify]`. Real numbers come through [`db-check.md`](db-check.md).
Builds on [`00-base-math.md`](00-base-math.md) (science and culture meters, Step 8).

**Why this page is longer:** the owner flagged the two trees as the favorite system, so this page goes deeper and separates what is measured from what is guessed.
**What I could and could not get:** I got a real per-tech **science cost table** for the base game (computed below). I could **not** get per-civic culture costs, the exact boost percentage for civics, or the boost trigger list. Those are marked.

## Step 0 · The big picture

> **A tree is a list of unlockable things, each with a price, a set of things you must already have, a possible discount if you do a certain act on the map, and a list of rewards. Two trees run side by side: one paid with science, one paid with culture.**

```
SCIENCE per turn -> fills TECH meter -> tech done -> unlocks units, buildings, improvements, districts
CULTURE per turn -> fills CIVIC meter -> civic done -> unlocks governments, policy cards, some buildings/units
                       ^
        BOOST (do a map act) -> instant partial credit on that node
```

## Step 1 · What one node is (the data row)

Every node in either tree has the same five fields `[sure]`:

| Field | Plain meaning |
|---|---|
| Cost | How much of the meter you must fill |
| Era | Which age of history the node belongs to |
| Prerequisites | Other nodes you must already have (0 to 3 in the base tech table) |
| Boost | A map act that gives a partial discount (the trigger) |
| Unlocks | What you receive: units, buildings, districts, improvements, policy cards, governments |

**Design note:** five fields is a very small, very reusable data shape. It is the cleanest part of the system to keep.

## Step 2 · The tech tree in numbers (base game)

Measured from a community table of the base game (no expansions) `[approx]`, then summed and compared here:

| Era | Techs | Cost range | Average cost | Era total |
|---|---|---|---|---|
| 1 | 11 | 25 to 80 | 51 | 565 |
| 2 | 8 | 120 to 200 | 160 | 1,280 |
| 3 | 7 | 300 to 390 | 339 | 2,370 |
| 4 | 9 | 540 to 660 | 593 | 5,340 |
| 5 | 8 | 805 to 925 | 865 | 6,920 |
| 6 | 7 | 1,035 to 1,135 | 1,092 | 7,645 |
| 7 | 8 | 1,225 to 1,375 | 1,281 | 10,250 |
| 8 | 9 | 1,540 to 1,795 | 1,625 | 14,625 |
| End | 1 | about 2,050 | 2,050 | repeatable final tech |

- **Totals:** 67 techs in the eight eras plus 1 final tech = 68 `[approx]`; about **49,000** science to finish the eight eras.
- **Cost jump per era** (average of one era divided by the one before): ×3.1, ×2.1, ×1.75, ×1.46, ×1.26, ×1.17, ×1.27. So costs rise fast early, then flatten toward a **near-linear** climb late. `[derived here]`
- **Inside an era** there are usually two price levels (cheap first half, dearer second half), about +25% to +65% between them in the early eras, about +10% to +15% in the late ones. `[derived here]`
- Prerequisites: 5 techs in the first era need nothing, so the tree starts with 5 roots. Others need 1 to 3 earlier techs (the count includes either-or alternatives). Most nodes need 1 or 2. `[approx]`
- Game speed multiplies all costs (faster speeds cut them, slower raise them). `[verify]` multipliers.
- I found **no evidence** that tech or civic cost grows with your number of cities (unlike some other games). `[verify]`

**What it means for play, worked out here:**
- At a rough 100 science per turn, the entire eight-era tree would take about 490 turns without boosts. That is why science output has to grow by many times over a game.
- The early eras are short and cheap (4,215 total for the first three), the late eras hold most of the cost (35,000 of 49,000 are in the last four).

**Guardrail:** price escalation means no tree is ever "finished" cheaply; each era demands a bigger economy (page 00) than the one before.
**Design note:** a price ladder that flattens into a linear climb is easy to tune with two numbers (a start and a late slope). This is a great candidate to rebuild in your own terms.

## Step 3 · Boosts: the map acts that discount research

- Each node has a trigger tied to something you do on the map (found, build, kill, meet, own a resource, and so on). Doing it gives a **large partial credit** to that node. `[sure]` that this exists.
- Size of the credit for techs: **50%** in one community table, **40%** in another guide. Likely differs by patch. `[verify]`
- Size for civics: **sources disagree widely** (a modding guide said 10%, other material said 40 to 50%). `[verify]`
- A few triggers are automatic (done in every game), most depend on how you play. `[approx]`
- The end-game repeatable tech has no boost. `[approx]`

**What a boost is worth, worked out here** (taking 50%): with every boost, the tree costs about **24,500** instead of 49,000. A single boost on a cost-1,500 tech saves about 750 science, which at 100 science per turn is 7 turns.

**Guardrail:** research is not only a number to grow. It is also a list of things to do. The tree tells you what to do on the map.
**Design note:** boosts turn the tree into a **quest list that rewards playing the world**. This is the single best idea in the system for a tile game: it ties science to action on the tiles. Strong keep, rating **9 out of 10**. A caution from the web search: boost lists can feel like a checklist, so vary triggers, avoid duplicates.

## Step 4 · The civic tree

- Same five-field shape as techs, paid with **culture** `[sure]`.
- Civics unlock: **governments**, **policy cards** (see page 05), and some buildings and units. `[sure]`
- Cost: a few examples from one list show mid-tree civics in the **low hundreds** and later ones at several hundred, with a separate cost list for the expansion rules. Full table: `[verify]`, needs db-check.
- Civic boosts exist and are called inspirations. `[sure]` Percentages: see Step 3.
- Like techs, civics are grouped by era. Counts differ widely by source (`[verify]`, expansions add many).

**Where the two trees differ in role** `[approx]`:

| | Tech tree | Civic tree |
|---|---|---|
| Paid with | science | culture |
| Mainly unlocks | things you **build or make** | **rules you choose** and governments |
| Feels like | what you can do | how you are run |

**Guardrail:** two currencies means two different pressures; a civilization short on culture is held back in governance even if its science is high.
**Design note:** keeping "build things" separate from "choose rules" is a strong shape. Open question: do you want two trees, or one tree with two node types?

## Step 5 · Eras: the clock the trees run on

- Eras advance as you move through the **science** tree. `[sure]`
- Each era has an **era score** (points for notable acts). At a new era, your score is compared to two thresholds: below the low one is a **dark age**, above the high one is a **golden age**, in between is normal. `[sure]` for the idea, numbers `[verify]` and vary per game.
- A dark age eases the next threshold, giving a recovery path. `[approx]`
- Sources conflict on whether a "heroic" age exists in the current version. `[verify]`

**Guardrail:** falling behind in the moment is a real cost, but not permanent.
**Design note:** a score-per-era with a comeback rule is a neat pacing tool. Decide whether it is needed.

## Step 6 · How the trees connect to everything else

| From | To | Rule in plain words |
|---|---|---|
| Citizens, districts, buildings (page 00, 03) | Science, culture meters | the sources of research |
| Science | Tech node | fills the cost |
| Culture | Civic node | fills the cost |
| Map act (build, kill, meet...) | Boost | partial credit on a node |
| Tech node | Units, buildings, districts, improvements | unlocks new options on the map (pages 01, 03) |
| Civic node | Governments, policy cards | unlocks rule choices (page 05) |
| Tech/era progress | Era score | clock for golden or dark age |
| Trade, diplomacy (page 02) | Some boosts | triggers can need contact or trade |

**Core loop to test in your game:** *more land and buildings → more science and culture → nodes done → new buildings, units, and rules → more land and buildings.* Boosts add a second input: *do the thing the tree asks → get ahead.*

## Open items (fill in using db-check.md)

- Full tech and civic cost tables from the actual game, including the expansions.
- Exact prerequisite graph (the shape: how many branches, how wide, how deep).
- Boost list per node, boost percentage by tree, and trigger types.
- Game-speed multipliers.
- Era score thresholds and what earns era score.

**Next step for the trees:** if you run the page 04 queries, I can draw the actual tree shape (width and depth per era, number of dead ends) and turn the five-field row into a data schema for your own game.

## Sources

- Tech cost table, prerequisite counts, boost flags: [CivFanatics Civ 6 technology info](https://civfanatics.com/civ6/info/technology/), summed and analyzed here. Treat as base-game only.
- Boost percentage: [On Towards the Stars: Eurekas and Inspirations](https://theahura.substack.com/p/on-towards-the-stars-eurekas-and) (40%) vs. the table above (50%).
- Civic data and boost sizes: [Civ 6 wiki, List of civics](https://civilization.fandom.com/wiki/List_of_civics_in_Civ6) (could not be fully read; the fetch was blocked), [Civ 6 wiki, Technology](https://civ6.fandom.com/wiki/Technology).
- Era score thresholds: [Civ 6 wiki, Age](https://civilization.fandom.com/wiki/Age_(Civ6)); sources conflict.
- The per-era average, jump ratios, totals, and "turns to finish" figures are computed here, not source figures.
