# Religion and Faith: The Slow-Spread System

Source: custom write-up. **`[sure]` numbers were read from the owner's own game database** (2026-11-10, via `tools/dbdump.py`); the rest is general knowledge plus a web check. Plain words, nothing copied; belief and unit names are left out (hard rule 8). Tags as before.
Builds on [`03-cities-districts.md`](03-cities-districts.md) (faith district), [`05-governments-great-people.md`](05-governments-great-people.md) (great prophet), and [`01-units-combat.md`](01-units-combat.md) (religious units).

**Honest warning:** the web check found no clean public number for **how religion spreads per turn**, **how strong religious combat is**, **how many religions a map allows**, or **the religious victory rule**. Those are marked `[verify]` or left open. Also, several search hits described Civ 5 or Civ 7 religion, which is different, so I did not use them.

## Step 0 · The big picture

> **Faith is a third resource that buys two things: a belief system, and units that spread that belief city by city. Each city ends up following one religion, and that choice quietly adds bonuses to every city that follows it.**

```
FAITH per turn (holy district, buildings, wonders) 
      |-> small first reward: PANTHEON (a first belief)
      |-> GREAT PROPHET points -> found a RELIGION (pick more beliefs)
      |-> BUY religious units -> SPREAD to other cities (pressure + charges)
                |-> each city follows one religion -> its beliefs give yields
```

## Step 1 · Where faith comes from

- Faith is earned by a **faith district** and the buildings inside it, by some wonders and natural wonders, and by pantheon and belief effects. `[sure]`
- It has **almost no base source** (page 00, Step 8). You get faith only if you build for it. `[sure]`
- Adjacency matters here too: the faith district likes mountains and natural wonders (page 03). `[approx]`
- Unused great prophet points turn into faith one for one. `[sure]` (1.0 faith per point)

**Guardrail:** faith must be chosen; it does not leak in from your citizens. That makes it the "optional" resource.

## Step 2 · Stage 1: the pantheon (the first belief)

- When your stored faith reaches a small threshold (**25**, confirmed), you may adopt a **pantheon**: one small belief. `[sure]`
- It is free of any unit cost; it just consumes the faith.
- Each pantheon belief can be taken only once in the world, so rivals pick different ones. `[approx]`

**Design note:** a cheap first belief that rewards early faith investment and has a small, immediate payoff is a good opener. Keep.

## Step 3 · Stage 2: founding a religion

- To found a **religion**, you need a **great prophet** (page 05, points from the faith district), then you spend that prophet in a faith district. `[sure]`
- The number of religions in a game is **limited**, so late players can miss out. The database holds **12 named religions and 12 spare custom slots**; the limit per map size was not in the dump. `[verify]` A new religion starts with **2 beliefs**. `[sure]`
- Founding lets you pick a set of **beliefs**, one per type:

| Belief type | Who benefits | Plain meaning |
|---|---|---|
| Follower | any city following the religion, any owner | a bonus for believers |
| Worship | the same, tied to a worship building | a bonus unlocked by a worship building |
| Founder | only the founder | a bonus for starting it |
| Enhancer | only the founder | a bonus once you strengthen the religion |

A religion holds up to four beliefs (one per type), plus the earlier pantheon. `[approx]` **Belief pool, confirmed** `[sure]`: pantheon 23, follower 9, worship 9, founder 9, enhancer 9 (59 in all).

**Guardrail:** religions are a limited, first-come set; being first matters.
**Design note:** separating "benefits everyone who follows" from "benefits the founder" makes spread worth doing for both sides. Keep the idea. Decide whether you want four belief types or two.

## Step 4 · Spreading: how a city picks a religion

- Every city has a **majority religion**, decided by comparing how many followers each religion has there. `[sure]`
- A religion spreads by **pressure**: nearby cities with that religion push followers into a city each turn; pressure rises with the strength of a source (buildings add some) and weakens with distance. **Confirmed settings** `[sure]`: a city pushes pressure to other cities within **10 tiles**, **1 point per turn** each; a holy city pushes **×4** and a holy-site district **×2**; each trade route carries **1.0 pressure at the destination and 0.5 at the origin**; winning a religious fight gives **250** and capturing a unit **125** (within 6 tiles); having no religion (atheism) adds 50 per citizen. A strength multiplier of 200 scales it. Exact per-turn totals depend on how these combine `[verify]`.
- Units speed this up: a **missionary-type** unit has a few **spread charges**; each use moves many followers into a city. A stronger **apostle-type** unit has more abilities (spread belief, start an inquisition). `[sure]`
- Units are bought with **faith**. The price **rises with each one you already bought**. **Base costs, confirmed** `[sure]`: missionary **75**, inquisitor **75**, apostle **200**, all with 4 movement. All three have **3 spread charges**. Religious strength: missionary **100**, apostle **110**, inquisitor **75**. Each use removes a share of foreign followers: **10%, 25%, 75%** respectively (the inquisitor is the remover). A fourth unit type (guru) has 0 spread charges and **3 heal charges**. How the price rises with each buy `[verify]` (the rule is engine-side).

**Guardrail:** you cannot flip the world with a button; spread is limited by charges, faith cost, and distance.
**Design note:** "pressure by distance plus a push unit" gives both a slow background effect and an active player lever. Good shape.

## Step 5 · Defending and fighting for hearts (religious combat)

- Religious units fight **theological combat** with their own strength, in friendly territory stronger than outside it. `[approx]` Related confirmed numbers: a unit fighting on its religion's land gets **+5**, on the holy city's tile **+15** combat strength; religious healing is **×3**; a religious unit's heal charge is 40. `[sure]`
- An **inquisitor-type** unit removes other religions from a city. It becomes available after your religion has been strengthened. `[sure]`
- Combat works like page 01's idea (strength compare, damage), but on religious strength, not combat strength. `[approx]` the exact formula `[verify]`.

**Guardrail:** a city does not give up its religion for free; the defender has a home advantage.

## Step 6 · What religion gives back (growth mechanics)

- Beliefs give yields (faith, food, gold, culture, housing, amenities) to cities that follow them, often tied to a building or terrain. `[sure]`
- A cathedral-type building adds faith, great prophet points, and pressure all at once. `[approx]`
- Holding followers in many cities earns the founder yields, which feed the economy (page 00). `[approx]`
- A religious victory exists as a win condition (convert the majority of other civs). The exact rule `[verify]`.

**Guardrail:** religion is a slow investment; it rewards early planning more than late scrambling.
**Design note:** rating for reuse in your game: **6 out of 10**. The "benefit everyone who follows" belief idea and the pressure-by-distance spread are both worth keeping. But the web check found that many players find the religious game fiddly (many units, many purchases), and the system's core payoff is faith, not a unique player decision. If your game has a community-building focus, religion may fit better as a **cultural influence layer** than as a separate unit-based system. Open question for you.

## Step 7 · All the links

| From | To | Rule in plain words |
|---|---|---|
| Faith district + buildings | Faith, prophet points | faith is chosen, not given |
| Faith | Pantheon | small first reward |
| Prophet points | Found a religion | needs a prophet, limited slots |
| Religion | Beliefs | follower, worship, founder, enhancer |
| Faith | Missionary-type units | buy charges to push followers |
| Pressure from neighbors | Majority religion | slow background spread |
| Majority religion | City yields | beliefs apply to followers |
| Religion | Combat (page 01) | theological combat, inquisition |
| Religion | Diplomacy (page 02) | can cause friction between players (agenda-style) `[approx]` |
| Faith | Great people (page 05) | faith can buy a person |

## Open items

- Religions allowed per map size; religious victory rule.
- Belief effects (the effect text is in the modifier tables, not dumped).
- How price rises per unit bought.

## Sources

- Pantheon cost, pressure settings, unit costs, belief pool: the owner's game database.
- Overview (earlier draft): [Civ 6 wiki, Religion](https://civilization.fandom.com/wiki/Religion_(Civ6)), [Pantheon](https://civ6.gamepedia.com/Pantheon), [Complete religion guide](https://outsidergaming.com/civ-6-complete-religion-guide-and-religious-victory-strategy/).
- Belief types: [List of beliefs](https://civilization.fandom.com/wiki/List_of_beliefs_in_Civ6). Some sources describe Civ 5; I ignored those.
- Unit costs and strengths: figures from low-quality sites; treat as unverified.

---

# Master Map: How the Six Systems Fit Together

This section sums up the base systems, as asked. Each row is one loop from the pages above.

| # | System (page) | The loop in one line | What limits it |
|---|---|---|---|
| 00 | Economy and land | tiles → citizens → food/production → growth → more tiles | food basket, housing, amenities |
| 01 | Units and combat | production → units → fight on terrain → win or lose tiles | upkeep, stacking, ZOC, healing |
| 02 | Trade and diplomacy | peace → trade links → richer cities; behavior → relationship → allowed actions | capacity, range, grievances |
| 03 | Cities and districts | land → special districts → adjacency → buildings → growth | district cap by population, land is spent |
| 04 | Tech and civic trees | yields → science/culture → nodes → new options; map acts → boosts | rising node costs, prerequisites |
| 05 | Governments and great people | civics → slots → cards; districts → points → unique people | slot cap, shared finite pool |
| 06 | Religion and faith | faith → belief → spread → follower yields | limited religions, charges, distance |

**Three levers appear on every page, and they are the real "rules of the game":**
1. **A meter that fills, then resets** (food basket, culture meter, science meter, great person points, faith). Same shape, different names. In your game, build one meter system and reuse it.
2. **A cap that grows with something else** (housing vs. citizens, districts vs. population, slots vs. government tier, capacity vs. civic). Caps are how the game forces tradeoffs.
3. **A link from the map to the tree** (terrain feeds adjacency, boosts reward map acts). This is what keeps the map important after the first turns.

**Shortest path through all of it:** *own land → citizens work it → yields fill meters → meters unlock options (units, districts, rules, beliefs) → options let you hold more land.* Everything else is a tuning variation of that loop.

**Best candidates to keep, ranked by my ratings:** placement puzzle with adjacency (9), boosts that tie research to map acts (9), government slots as an editable ruleset (8), envoy-style influence race (7), shared finite pool of great people (7), religion as a separate unit system (6).
