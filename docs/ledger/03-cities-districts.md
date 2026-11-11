# Cities and Districts: The Placement Puzzle

Source: custom write-up. **`[sure]` numbers were read from the owner's own game database** (2026-11-10, via `tools/dbdump.py`); the rest is general knowledge plus a web check. Plain words, nothing copied (district names are described by role, hard rule 8). Tags as before.
Builds on [`00-base-math.md`](00-base-math.md) (tiles, citizens, housing) and [`01-units-combat.md`](01-units-combat.md) (city defense).

**Honest warning:** the district population limit and adjacency values below come from fan guides and a third-party coding library. Several numbers disagree between sources. I found nothing on how a district's cost rises, or on city spacing and settler cost, so those are from memory and marked.

## Step 0 · The big picture

> **A city is a center tile plus a set of special tiles (districts). Each district uses up one tile of land, and what it pays depends on what sits next to it. So the map is the puzzle, and where you place things is the skill.**

```
FOUND CITY (settler = 1 citizen)  ->  OWN TILES in range 3 (page 00)
        |
        v
PLACE DISTRICTS on owned tiles -> ADJACENCY bonus from neighbors -> BUILDINGS inside -> yields, housing, amenities
        ^                                                                |
        +------------------- more citizens / specialists <---------------+
```

## Step 1 · Founding a city

- A **settler** unit founds a city on a tile. `[sure]`
- Building a settler **costs the home city one citizen and 80 production**. `[sure]`
- A new city must be at least **3 tiles** from other cities (the minimum-range setting is 3). `[sure]` A city's buy range is 3 as well.
- On founding, the city claims the center and nearby ring (page 00), and the center tile gets a free yield floor. `[approx]`

**Guardrail:** expansion costs population, so the economy slows briefly each time you found a city. Spacing keeps cities from overlapping everything.
**Design note:** "a new town costs people" is a clean tradeoff. Keep.

## Step 2 · What a district is

- A **district** is a special tile in the city that holds buildings of one kind: science (campus-style), faith (holy-site-style), gold (commercial), production (industrial), culture (theater), military, harbor and so on. `[sure]`
- Each district goes on **one tile you own**, within the city's range of 3. `[sure]`
- A tile holding a district no longer gives its normal tile yield. It gives the district's own yields and buildings instead. `[approx]` (the tile is "spent")
- If you place a district on a tile with an improvement, the improvement is replaced. `[approx]`
- Some districts have placement rules: one of them cannot touch the city center; others must be on the coast, on a river, or not on certain terrain. `[sure]`

**Guardrail:** every district costs a whole tile of land. Land is the limited resource, so you give up yield now for a building slot.
**Design note:** this is the heart of the design: **land is scarce, so what you use it for matters.** Strong keep.

## Step 3 · How many districts a city may have

Rule in words: the number of special districts a city can have rises with its population. A third-party list gives:

```
specialty districts allowed  ≈  1 + floor((population - 1) / 3)
```

| City size | Districts allowed (approx) |
|---|---|
| 1 to 3 | 1 |
| 4 to 6 | 2 |
| 7 to 9 | 3 |
| 10 to 12 | 4 |

**Confirmed:** the game's setting is **one district per 3 citizens** (`DISTRICT_POPULATION_REQUIRED_PER = 3`). `[sure]` The exact starting count (the "+1" in the formula) is `[approx]`.

**Districts that are not "one per city"** (so you can build many; whether they skip the cap is `[approx]`) `[sure]`: the housing district (**+4 housing**), the dam (+3 housing, +1 entertainment), the canal, and one unique housing district (+5). Utility districts that count as one per city: aqueduct, bath-type, spaceport, preserve (+1 housing), and others.

**District cost** `[sure]`: a standard specialty district has a base cost of **54 production**; unique replacements cost **27**; the aqueduct costs 36 and a bath-type unique costs 18; the government district costs 30; the spaceport 1,800; wonders 0 (they are priced separately). Cost then **rises with a "progression model"**: for most specialty districts it depends on how many districts you already have compared with average plus your tech level (parameter 40); for housing and utility districts it rises with game progress (parameter 1,000). `[sure]` that the models exist; the exact curve `[verify]`.

Every specialty district also gives the city **+2 city strength** (see page 01). `[sure]` Entertainment districts give 1 to 3 amenities by type (complex 1, carnival 2, hippodrome 3). `[sure]`

**Guardrail:** a small city cannot be everything. Size (page 00) gates how much special land you can use.
**Design note:** a "one district per three citizens" ladder ties growth directly to variety. That is an easy rule to copy or tune, and a sharp link between food and buildings.

## Step 4 · Adjacency: the placement bonus

Rule in words: a district gains extra yield from what sits on the tiles touching it.

```
district bonus  =  sum over neighbors of (value for that neighbor type)
```

Adjacency rows read from the database, **complete** `[sure]`. The bonus is "+N per M matching neighbors" for the tiles around the district:

| District | Neighbor and bonus |
|---|---|
| Science (campus-type) | mountain **+1 each**; jungle **+1 per 2**; reef **+2 each**; thermal fissure **+2**; any other district **+1 per 2**; government district **+1** |
| Faith (holy-site-type) | natural wonder **+2**; mountain **+1 each**; forest **+1 per 2**; any other district **+1 per 2**; government district **+1** |
| Gold (commercial-hub-type) | river **+2**; harbor-type district **+2**; any other district **+1 per 2**; government district **+1** |
| Culture (theater-type) | wonder **+2**; entertainment-type district **+2** (four kinds); any other district **+1 per 2**; government district **+1** |
| Production (industrial-type) | quarry **+1 each**; mine **+1 per 2**; lumber mill **+1 per 2**; aqueduct, canal, dam, or bath-type district **+2 each**; strategic resource **+1**; any other district **+1 per 2**; government district **+1** |
| Harbor | sea resource **+1**; city center **+2**; any other district **+1 per 2**; government district **+1** |

Military camp, entertainment, aqueduct, and housing districts have **no adjacency bonus**. `[sure]`

Fractions floor (round down) per source, so a pile of small bonuses can be wasted. `[approx]`
Some neighbors are the map's gift (rivers, mountains, wonders); others you build yourself (a district next to a district).

**Guardrail:** the best site for a district is decided by terrain you did not choose. You plan around it.
**Design note:** this is the **placement puzzle** that gives the genre its depth. My rating: **9 out of 10** for your tile game. Reason: lots of community praise for city layout depth, and lots of complaints about bookkeeping and "perfect adjacency" micromanagement. Keep the puzzle, cut the pile of per-type exceptions.

## Step 5 · Inside a district: buildings and specialists

- Each district holds a short ladder of **buildings** (cheap first, stronger later). Buildings add yields, housing, or amenities. `[sure]`
- A district with buildings gets **specialist slots**: a citizen can be assigned there instead of working a land tile, and produces that district's yield. `[approx]`
- Wonders sit on their own tile and give a one-time unique effect. `[sure]`

This is the link to page 00: a citizen is either a **farmer/worker on land** (tile yield) or a **specialist in a building** (district yield). Both cost 2 food.

**Guardrail:** you cannot put every citizen in a building; slots are limited by what you built.

**The building ladder inside a district, from the database** `[sure]`: each specialty district holds a short run of buildings in cost steps of roughly **90 to 150, then 250 to 330, then 440**. Typical yields per building: first tier +2 (science, gold) to +3 (production), mid tier +4 to +5, last tier +3 to +4 on top. Faith buildings run **+2, +4, then +3 to +6**. Every building in a specialty district has **1 citizen slot** (so a specialist can work it), and entertainment, aqueduct and housing districts have **no citizen slots**. Maintenance is 0 to 3 gold per building, rising with tier. The city center holds a granary-type (+2 housing, +1 food), a monument-type (+1 culture, 60 cost), walls (80), a castle (220) and a sewer (200, +2 housing).

## Step 6 · Housing and amenities from districts

- Districts and buildings are the main source of **housing** (growth brake, page 00) and **amenities** (happiness gate, page 00). `[sure]`
- Housing from water, confirmed `[sure]`: **no water 2, coast 3, river or lake 5**. A city-center tile also guarantees 2 food and 1 production (page 00).
- Aqueduct-style and neighborhood-style districts exist to raise housing, which is why they don't count against the cap. `[approx]`

**Guardrail:** the same buildings that give yields are also the ones that let you grow, so every city faces "yield or room to grow."

## Step 7 · City defense and loyalty

- A city has about 200 HP, and its defense strength comes from its garrison, walls, districts (+2 each), population (1 per 2 citizens), being a capital, and hills. `[sure]` for the districts and population parts.
- A city fires back at attackers; with no ranged units built, its strength is low. `[approx]`
- Districts can be pillaged or damaged. `[approx]`
- **Loyalty** `[sure]`: a city starts at **100** (the maximum). Nearby citizens exert identity pressure within **10 tiles**; a city can gain or lose up to **20 loyalty per turn** from it. After capture by combat a city restarts at **50**; after liberation or a cultural flip, at **100**. Low loyalty can make a city rebel or flip. **Loyalty levels, confirmed** `[sure]`: 76 to 100 is the top band (no yield penalty, +1.0 growth change); 51 to 75 (−0.25 yield, +0.75 growth); 26 to 50 (−0.5 yield, +0.25 growth); 0 to 25 (−1.0 yield, 0 growth).

**Guardrail:** conquest needs to be able to hold what it takes, so taking a city requires loyalty pressure, not just force.
**Design note:** loyalty is a second control layer next to borders. Decide if your game needs both.

## Step 8 · How it all connects

| From | To | Rule in plain words |
|---|---|---|
| Citizen | Settler | 1 citizen is spent to found a new city |
| Tile ownership | Districts | a district goes only on an owned tile in range |
| Population | District limit | more citizens unlock more special districts |
| Production | District / building | pay once, then the slot is yours |
| Terrain next to district | Adjacency bonus | neighbors set the yield |
| Buildings | Housing, amenities, yields | feeds the growth and happiness loop (page 00) |
| Building slots | Specialists | a citizen can leave a land tile to work a slot |
| Districts, walls | City defense | stronger city in combat (page 01) |
| Neighbor cities | Loyalty | pressure holds or flips a city |

**Core loop to test in your game:** *land → citizens → districts on the best tiles → buildings → housing and yields → more citizens → more land.* The new twist over page 00 is that land is **spent**, not only worked.

## Open items

- Per-improvement housing and yields (Improvements dumped; not yet written up).
- City HP and wall HP; exact district cost curve.
- Exact start of the district limit.

## Sources

- Settler, spacing, district costs and housing, loyalty, adjacency rows: the owner's game database.
- District types and adjacency (earlier draft): [Civ 6 wiki, List of districts](https://civilization.fandom.com/wiki/List_of_districts_in_Civ6), [Civ 6 district guide](https://pcgamesn.com/civilization-vi/civ-6-district-guide), [What do we know about these adjacency bonuses](https://forums.civfanatics.com/threads/what-do-we-know-about-these-adjacency-bonuses.573900/latest).
- District population limit start: a third-party library page, [civ6lib](https://playbooks.com/skills/benchflow-ai/skillsbench/civ6lib). Its "per 3 citizens" matches the database; the start is unconfirmed.
- City defense: [City Strength](https://forums.civfanatics.com/threads/city-strength.619428), [City combat](https://forums.civfanatics.com/resources/city-combat.27737/). Some linked material describes Civ 5.

