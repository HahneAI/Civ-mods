# Base Math: How the Resource Systems Connect

Source: custom write-up, from general Civ 6 knowledge plus a web check (see "Sources"). Rules described in plain words, no copied code or text.
Purpose: a reference for the owner's own tile game. Each section ends with a **Guardrail** (the rule that limits the player) and a **Design note** (keep / change / cut / open question).

**Confidence tags:** `[sure]` = standard, widely documented. `[approx]` = numbers vary by source. `[verify]` = not confirmed; check in game or in the debug DB before relying on it.

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
- A **city center** tile is always worked for free and gets a minimum floor of 1 food and 1 production. `[sure]` (exact floor rules `[verify]`)

**Guardrail:** terrain and features are the map's fixed "budget". You choose which tiles to use, not how much they give.
**Design note:** this additive tile sum is the easiest thing to keep. Open question: do you want adjacency bonuses (placement puzzles) in your game?

---

## Step 2 · Who may work a tile (ownership + citizens)

Three plain rules:

1. **Ownership:** a tile must belong to the city. Cities start with the center plus the ring around it, then claim more over time. `[sure]`
2. **Range:** a city can only work tiles within 3 tiles of its center. `[sure]`
3. **One citizen per tile.** A tile worked by one city cannot be worked by another. Enemy units standing on it block it. `[sure]`

How tiles are gained: the city fills a **culture** meter and claims the cheapest nearby tile each time it fills, or the player **buys** a tile with gold. Each tile claimed makes the next one cost more. `[sure]`

Culture cost of the next tile `[approx]`, from modder testing:

```
cost = first_plot_cost + (later_multiplier x (tiles_claimed - 1)) ^ later_exponent
```

Older builds: first = 10, multiplier = 6, exponent = 1.3. Later builds appear to use bigger numbers (first about 20, multiplier about 15, exponent about 1.35), which is why sources disagree. Policies and civ traits can cut this cost by about 25%. Gold buy price has its own base (about 50) `[approx]` and is computed inside the game engine, not in a readable table, so the formula may not be recoverable from the database.

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

The formula has three knobs in the game's settings table (`GlobalParameters`): a per-size multiplier (default about 8), an exponent (about 1.5), and a flat start (about 15). `[approx]` names/values from modder posts. Turns to grow ≈ food needed ÷ surplus. Example: needs 24, surplus +4 → 6 turns.

**Guardrail:** growth gets slower as you get larger, so a city cannot snowball forever on food alone.
**Design note:** the rising basket is a "soft cap". Keep the idea, tune the numbers yourself.

---

## Step 5 · Housing: the brake on growth

Each city has a **housing** number (from water access, buildings, districts). Compare it with population (called "headroom"):

| Housing minus population | Growth speed | Tag |
|---|---|---|
| 2 or more | full speed | `[sure]` |
| 1 | half speed | `[approx]` |
| 0 to slightly over | about quarter speed | `[approx]` |
| 5+ over | growth stops | `[approx]` |

Typical starting housing: a bit higher with fresh water (river/lake) than none. `[verify]` exact numbers.

**Guardrail:** food cannot buy unlimited size; you must also build housing. Housing is the link from *infrastructure* back to *citizens*.
**Design note:** this is where "build things" becomes a requirement for "grow things". Keep. Open question: do you want a single housing cap, or the stepped slowdown?

---

## Step 6 · Amenities: the happiness gate

Rule in words: a city needs a number of amenities that rises with its population, about **1 per 2 citizens, rounded up, with the first few citizens free**. `[approx]` Sources disagree on where it starts (some say from size 3), so treat the exact start as `[verify]`.

- Enough or more: bonus to yields and growth.
- Short a little: growth slows.
- Short a lot (unrest): all non-food yields drop by about 30%, and rebellion risk starts. `[approx]`

`[verify]` exact thresholds and percentages.

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

No game database is reachable from this chat (no computer is linked and the repo has no copy), so none of this was read from game data. Numbers above are from community posts. This map tells you where to look. Table and column names are `[verify]`.

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

## Open items (check against the real game/debug DB before treating as final)

- Exact city-center yield floors.
- Exact housing numbers by water type, and exact stepped growth percentages.
- Exact amenities thresholds and penalty percentages.
- Border culture cost knobs for your installed version; gold tile-buy formula (may be engine-only).
- Gold purchase cost formula for production.
- Base science/culture per citizen.

These can be pulled with `tools/sqlcheck.py` / the debug database once Phase 2 tooling exists, then marked `[sure]` here.

## Sources

- Growth formula and housing steps: community Civ 6 wiki growth page (https://civilization.fandom.com/wiki/Growth_(Civ6)), cross-checked against forum posts. Numbers differ by 1 at some sizes, hence `[approx]`.
- Border cost and growth knobs: CivFanatics modding threads, e.g. [City Tile Purchase Cost?](https://forums.civfanatics.com/threads/city-tile-purchase-cost.606599/latest), [Help with adjusting food growth](https://forums.civfanatics.com/threads/help-with-adjusting-food-growth.613552), [Calculating Border Growth Speed](https://forums.civfanatics.com/threads/calculating-border-growth-speed-bugs.663825).
- Amenities: [Civ 6 wiki, Amenity](https://civilization.fandom.com/wiki/Amenity_(Civ6)); its own examples contradict each other.
- Everything else: general game knowledge, not yet confirmed in game.
