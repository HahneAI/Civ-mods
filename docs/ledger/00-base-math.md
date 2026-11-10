# Base Math: How the Resource Systems Connect

Source: custom write-up. **Numbers marked `[sure]` were read from the owner's own game database** (2026-11-10, both expansions loaded, via `tools/dbdump.py`); the rest is from general knowledge and a web check. Rules described in plain words, no copied code or text.
Purpose: a reference for the owner's own tile game. Each section ends with a **Guardrail** (the rule that limits the player) and a **Design note** (keep / change / cut / open question).

**Confidence tags:** `[sure]` = read from the database or standard and documented. `[approx]` = numbers vary by source. `[verify]` = not confirmed; check in game or in the debug DB before relying on it.

---

## Step 0 · The big picture in one line

> **Tiles make yields → citizens work tiles → yields feed the city → the city grows, which means more citizens and more tiles to work.**

Everything below is one link in that loop.

```
 TILE OWNERSHIP ──> TILES YOU MAY WORK
        ^                  |
        |                  v
     CULTURE <──── CITIZENS (pop) ──> YIELDS: food, production, science, culture, faith, gold
        ^                  ^               |
        |                  |               v
        +--- HOUSING <-----+---- FOOD <----+--> PRODUCTION --> buildings (more housing, more yields)
```

---

## Step 1 · A tile has yields

A tile's output is a small sum, nothing more:

```
tile yield = terrain + feature (forest, hills...) + resource + improvement + bonuses (adjacency, policies)
```

Example: Grassland (2 food) + a Farm (+1 food) = 3 food. `[sure]`

- Yields are whole numbers per turn: Food, Production, Gold, Science, Culture, Faith.
- A **city center** tile is always worked for free and gets a minimum floor of **2 food and 1 production**. `[sure]` (database: the city center is treated as at least that)

**Base yields, read from the database** `[sure]` (food / production unless noted):

| Terrain | Yield | Feature | Adds |
|---|---|---|---|
| Grassland | 2 food | Forest | +1 production |
| Grassland hills | 2 food, 1 prod | Jungle | +1 food |
| Plains | 1 food, 1 prod | Marsh | +1 food |
| Plains hills | 1 food, 2 prod | Floodplains | +2 food |
| Tundra, tundra hills | 1 food (+1 prod hills) | Oasis | +3 food, +1 gold |
| Desert, snow | 0 | Reef | +1 food, +1 prod |
| Coast | 1 food, 1 gold | Natural wonders | each has its own set (3 to 5 of a kind) |
| Ocean | 1 food | | |

Desert hills and snow hills give 1 production. Resource and improvement yields are in the dump and will get their own table later. Game speed scales costs everywhere: **marathon 3.0, epic 1.5, standard 1.0, quick 0.67, online 0.5**.

**Guardrail:** terrain and features are the map's fixed "budget". You choose which tiles to use, not how much they give.
**Design note:** this additive tile sum is the easiest thing to keep. Open question: do you want adjacency bonuses (placement puzzles) in your game?

---

## Step 2 · Who may work a tile (ownership + citizens)

Three plain rules:

1. **Ownership:** a tile must belong to the city. Cities start with the center plus the ring around it, then claim more over time. `[sure]`
2. **Range:** a city can only work tiles within 3 tiles of its center. `[sure]`
3. **One citizen per tile.** A tile worked by one city cannot be worked by another. Enemy units standing on it block it. `[sure]`

How tiles are gained: the city fills a **culture** meter and claims the cheapest nearby tile each time it fills, or the player **buys** a tile with gold. Each tile claimed makes the next one cost more. `[sure]`

Culture cost of the next tile, formula from modder testing `[approx]`, **knobs confirmed in the database** `[sure]`:

```
cost = first_plot_cost + (later_multiplier x (tiles_claimed - 1)) ^ later_exponent
```

**This install: first = 10, multiplier = 6, exponent = 1.3** `[sure]` (other sources quoted bigger numbers from other versions). Example: tile 2 costs 10 + 6^1.3 ≈ 20, tile 6 costs 10 + 30^1.3 ≈ 93. `[derived]` Other confirmed settings: a tile can be bought up to **3 tiles** from the center; the gold buy price starts from a **base of 50**, and the full gold formula is computed inside the game engine. One citizen works one tile. Policies and civ traits can cut the culture cost by about 25%. `[approx]`

**Guardrail:** land you do not own, or that is out of range, produces nothing for you. This is the rule that makes borders matter.
**Design note:** a very strong idea to keep. It ties culture (a soft resource) directly to map control. Decide if you want gold to be able to buy land.

---

## Step 3 · Citizens eat

```
food eaten per turn = 2 x population
food surplus        = food produced - food eaten
```

`[sure]` Example: size 4 city eats 8. If its tiles make 11 food, surplus is +3.

- Surplus positive → the "food basket" fills.
- Surplus zero → the city stays the same size.
- Surplus negative → the city starves (shrinks) once the basket empties. `[approx: exact starvation handling]`

**Guardrail:** every citizen has an upkeep of 2 food. A citizen working a 1-food tile is a net loss; this pushes you toward good food tiles.
**Design note:** one of the cleanest "base laws". Keep as the core economy tension.

---

## Step 4 · Growth: filling the food basket

The basket you must fill to gain +1 population gets bigger as the city gets bigger. Community formula `[approx]`:

```
food needed to grow from size P  ≈  15 + 8 x (P - 1) + (P - 1)^1.5     (rounded)
```

| Current size | Food to reach next size (approx) |
|---|---|
| 1 | 15 |
| 2 | 24 |
| 3 | 33–34 |
| 4 | ~44 |

The formula has three knobs in the game's settings table (`GlobalParameters`): **a flat start of 15, a per-size multiplier of 8, and an exponent of 1.5**. `[sure]` The exact way they combine is the community formula above `[approx]`. Food eaten per citizen: **2** `[sure]`. Turns to grow ≈ food needed ÷ surplus. Example: needs 24, surplus +4 → 6 turns.

**Guardrail:** growth gets slower as you get larger, so a city cannot snowball forever on food alone.
**Design note:** the rising basket is a "soft cap". Keep the idea, tune the numbers yourself.

---

## Step 5 · Housing: the brake on growth

Each city has a **housing** number (from water access, buildings, districts). Compare it with population (called "headroom"):

| Housing minus population ("headroom") | Growth speed | Tag |
|---|---|---|
| 2 or more | full speed | `[sure]` |
| 1 | half speed (50%) | `[sure]` |
| 0 | quarter speed (25%) | `[sure]` |
| -4 or lower | growth stops | `[sure]` |
| -1 to -3 | between 25% and 0 (steps not in this dump) | `[verify]` |

Starting housing from water access, confirmed: **no fresh water 2, coast 3, river or lake 5**. `[sure]` Two aqueduct settings also exist (a boost of 2 and a minimum size of 6); how they combine `[verify]`. This corrects the earlier draft, which said growth stops at 5 over; the real stopping point is 4 over.

**Guardrail:** food cannot buy unlimited size; you must also build housing. Housing is the link from *infrastructure* back to *citizens*.
**Design note:** this is where "build things" becomes a requirement for "grow things". Keep. Open question: do you want a single housing cap, or the stepped slowdown?

---

## Step 6 · Amenities: the happiness gate

Rule in words: a city needs **1 amenity per 2 citizens** (rounded), none given for free. `[sure]` The city's *amenity score* is amenities it has minus what it needs. That score picks a mood, and the mood changes growth and every non-food yield `[sure]`:

| Mood | Score | Growth | Non-food yields | Rebellion points per turn |
|---|---|---|---|---|
| Ecstatic | 5 or more | +20% | +20% | -1 |
| Happy | 3 to 4 | +10% | +10% | -1 |
| Content | 0 to 2 | normal | normal | -1 |
| Displeased | -1 to -2 | -15% | -10% | -1 |
| Unhappy | -3 to -4 | -30% | -20% | 0 |
| Unrest | -5 to -6 | stops (-100%) | -30% | +1 |
| Revolt | -7 or less | stops | -40% | +4 |

Two more confirmed rules: a **negative gold balance** costs amenities, and **war weariness** costs amenities (points build up to 400 per lost amenity). `[sure]`

**Guardrail:** a big city must be kept happy, so size alone doesn't win.
**Design note:** consider merging amenities and housing into one "comfort" system in your game, if two separate meters feel like bookkeeping. This is a *change* candidate, not a fact.

---

## Step 7 · Production: building things

```
turns to finish = cost ÷ production per turn
```

- Leftover production beyond the cost carries over `[approx]`.
- Gold can buy the remaining cost; price grows faster than linearly as the remaining cost grows. `[verify]` formula.
- Production comes from tiles (hills, forests, mines) and from buildings.

**Guardrail:** a city does one build at a time (per queue), so you must choose what to build now and what to wait on.
**Design note:** keep the single queue. It forces tradeoffs without extra rules.

---

## Step 8 · Science, Culture, Faith: the three "progress meters"

All three work the same way:

```
meter fills at (yield per turn)
when full → unlock something → next meter costs more
```

| Resource | Fills… | Unlocks | Main sources |
|---|---|---|---|
| Science | tech meter | technologies (units, buildings, improvements) | citizens, campus-style buildings |
| Culture | civic meter, and city border meter | civics (policies, governments), tiles | citizens, theater-style buildings, wonders |
| Faith | religion/belief purchases | beliefs, religious units | shrine/temple-style buildings |

- Small base science and culture come from population itself. `[approx]` the exact per-citizen amount `[verify]`.
- **Boosts:** doing something specific (e.g. mining a resource) can fill about half of a tech's cost for free. `[approx]` This rewards playing the map, not just stacking science.
- Faith has almost no base source; it only exists if you build for it. `[sure]`

**Guardrail:** progress is rationed. You cannot unlock everything at once, and each unlock raises the next price.
**Design note:** culture doing two jobs (civics + borders) is the neatest link in the whole design. Boosts are the other link worth keeping: they tie research to *what you do on the map*.

---

## Step 9 · Gold (support resource)

```
net gold per turn = gold income - upkeep (buildings, units)
```

`[sure]` Gold buys production, tiles, and units. Negative net gold drains the treasury and eventually disbands things. It's the "pressure valve" that turns surplus into any other resource.

---

## Step 10 · All the links on one page

| From | To | Rule in plain words |
|---|---|---|
| Culture | Tile ownership | meter fills → claim next tile (price rises) |
| Gold | Tile ownership | pay to claim a tile now |
| Tile ownership | Citizen work | citizens only work owned tiles within range 3 |
| Citizen work | All yields | each worked tile adds its yield sum |
| Food surplus | Population | surplus fills the basket → +1 citizen |
| Population | Food eaten | 2 food per citizen |
| Housing | Growth speed | less headroom → slower growth |
| Amenities | Growth + yields | too few → penalties |
| Production | Buildings | cost ÷ production; buildings add housing, amenities, yields |
| Population | Science/Culture | small base amount per citizen |
| Buildings | Science/Culture/Faith | the main source of these three |

**Core loop to test in your game:** *more land → more citizens → more food/production → buildings → more housing and meters → more land.* Every guardrail above is a place that loop gets slowed on purpose.

---

## Step 11 · Where each number lives (for the database check)

Table names below were checked against the owner's database; the ones marked read in the left column fed this page.

| Rule | Likely place |
|---|---|
| Food per citizen (2), growth knobs, border cost knobs, tile buy base | `GlobalParameters` (Name, Value) |
| Terrain / feature / resource / improvement yields | `Terrain_YieldChanges`, `Feature_YieldChanges`, `Resource_YieldChanges`, `Improvement_YieldChanges` |
| Building yields and housing | `Building_YieldChanges`, `Buildings` (Housing column) |
| Amenity effects by happiness level | `Happinesses` |
| Tech and civic costs, boosts | `Technologies`, `Civics`, `Boosts` |

Note: in later game builds these parameters are split across several files, so one file may not hold every value.

### How to check

See [`db-check.md`](db-check.md) for the setup steps and the exact queries. Paste the rows into the chat and every `[approx]` above gets replaced.

## Open items

- Housing steps between -1 and -3, and how the aqueduct settings combine.
- Gold price of a tile and of production (engine-only; may need testing in game).
- Base science and culture per citizen.
- Per-tile yields of resources and improvements: parsed but not yet written up (see `docs/ledger/db-check.md`, follow-up list).

## Sources

- Growth knobs, housing steps, amenity table, border knobs: the owner's game database (`GlobalParameters`, `Happinesses`).
- Growth formula shape: community Civ 6 wiki growth page (https://civilization.fandom.com/wiki/Growth_(Civ6)). Numbers differ by 1 at some sizes, hence `[approx]`.
- Border cost and growth knobs: CivFanatics modding threads, e.g. [City Tile Purchase Cost?](https://forums.civfanatics.com/threads/city-tile-purchase-cost.606599/latest), [Help with adjusting food growth](https://forums.civfanatics.com/threads/help-with-adjusting-food-growth.613552), [Calculating Border Growth Speed](https://forums.civfanatics.com/threads/calculating-border-growth-speed-bugs.663825).
- Amenities: [Civ 6 wiki, Amenity](https://civilization.fandom.com/wiki/Amenity_(Civ6)); its own examples contradict each other.
- Everything else: general game knowledge, not yet confirmed.
