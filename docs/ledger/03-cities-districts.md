# Cities and Districts: The Placement Puzzle

Source: custom write-up from general Civ 6 knowledge plus a web check (see "Sources"). Plain words, nothing copied. Tags as before: `[sure]`, `[approx]`, `[verify]`. Real numbers come through [`db-check.md`](db-check.md).
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
- Building a settler **costs the home city one citizen** (and production). `[approx: exactly 1 pop, city must be big enough]`
- A new city must be some minimum distance from other cities (cities cannot sit side by side; about 3 tiles apart). `[verify]`
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

`[approx]` Some districts do not count against this cap (water, housing, and utility types such as aqueduct, neighborhood, canal, dam). Which ones are `[verify]`.

Each district also costs production, and that cost rises as the city builds more. `[approx]` The way it rises is `[verify]`.

**Guardrail:** a small city cannot be everything. Size (page 00) gates how much special land you can use.
**Design note:** a "one district per three citizens" ladder ties growth directly to variety. That is an easy rule to copy or tune, and a sharp link between food and buildings.

## Step 4 · Adjacency: the placement bonus

Rule in words: a district gains extra yield from what sits on the tiles touching it.

```
district bonus  =  sum over neighbors of (value for that neighbor type)
```

Examples, from fan guides `[approx]`:

| District | Likes (per neighbor) |
|---|---|
| Science | mountains (+1 each), jungle, other districts (small) |
| Faith | natural wonders (+2), mountains (+1), forest and other districts (+½) |
| Gold | rivers and harbors (+2), other districts (+½ to +1 per two) |
| Government | gives +1 to several neighboring district types |

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

## Step 6 · Housing and amenities from districts

- Districts and buildings are the main source of **housing** (growth brake, page 00) and **amenities** (happiness gate, page 00). `[sure]`
- The city center gives a base housing number depending on water access. `[verify]`
- Aqueduct-style and neighborhood-style districts exist to raise housing, which is why they don't count against the cap. `[approx]`

**Guardrail:** the same buildings that give yields are also the ones that let you grow, so every city faces "yield or room to grow."

## Step 7 · City defense and loyalty

- A city has about 200 HP, and its defense strength comes from its garrison, walls, districts, being a capital, and hills. `[approx]`
- A city fires back at attackers; with no ranged units built, its strength is low. `[approx]`
- Districts can be pillaged or damaged. `[approx]`
- **Loyalty:** nearby cities and their population pull a city toward their owner. A city with low loyalty can rebel or flip. `[approx]`

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

## Open items (fill in using db-check.md)

- Exact district-limit rule, and which districts are exempt.
- District cost and how it rises.
- Full adjacency table (district x neighbor x value).
- Settler pop cost, minimum city distance.
- City-center housing by water type; specialist slot counts and yields.
- City HP, defense strength parts, loyalty values.

## Sources

- District types and adjacency: [Civ 6 wiki, List of districts](https://civilization.fandom.com/wiki/List_of_districts_in_Civ6), [Civ 6 district guide](https://pcgamesn.com/civilization-vi/civ-6-district-guide), [What do we know about these adjacency bonuses](https://forums.civfanatics.com/threads/what-do-we-know-about-these-adjacency-bonuses.573900/latest).
- District population limit: a third-party library page, [civ6lib](https://playbooks.com/skills/benchflow-ai/skillsbench/civ6lib). Not official; treat as `[approx]`.
- City defense: [City Strength](https://forums.civfanatics.com/threads/city-strength.619428), [City combat](https://forums.civfanatics.com/resources/city-combat.27737/). Some linked material describes Civ 5.
- Settler cost, spacing, loyalty values: not confirmed by search; from memory.
