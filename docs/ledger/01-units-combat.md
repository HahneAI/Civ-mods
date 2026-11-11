# Units and Combat: How Units Interact With the Map

Source: custom write-up. **`[sure]` numbers were read from the owner's own game database** (2026-11-10, via `tools/dbdump.py`); the rest is general knowledge plus a web check. Plain words, nothing copied. Same tags as page 00.
Builds on [`00-base-math.md`](00-base-math.md): units are bought with production, paid for with gold, and some need a citizen.

## Step 0 · The big picture

> **A unit is a bundle of numbers (strength, health, movement). Fights compare two strengths, turn the gap into damage, and the map adds flat bonuses to those strengths.**

```
BUILD (production)  ->  UNIT (strength, HP, moves)  ->  MOVE (terrain cost, ZOC)
                                  |
                                  v
                         FIGHT: strength gap -> damage  ->  HEAL / DIE / CAPTURE CITY
```

## Step 1 · What a unit is (its stat sheet)

| Stat | Plain meaning |
|---|---|
| Combat strength | How well it fights up close and when defending |
| Ranged strength + range | How well it hits from a distance, and how far |
| Bombard strength | Attack against cities and walls only (siege) |
| Hit points (HP) | Health, starts at 100; at 0 the unit is destroyed `[sure]` |
| Movement points | How many tile-steps it gets per turn |
| Cost / upkeep | Production to build, gold per turn to keep |
| Resource need | Some units require a strategic resource (e.g. iron) |

`[sure]`. A sample from the database (159 units loaded):

| Early unit | Melee | Ranged / range | Moves | Build cost | Upkeep | Needs |
|---|---|---|---|---|---|---|
| Scout | 10 | n/a | 3 | 30 | 0 | none |
| Warrior | 20 | n/a | 2 | 40 | 0 | none |
| Slinger | 5 | 15 / 1 | 2 | 35 | 0 | none |
| Archer | 15 | 25 / 2 | 2 | 60 | 1 | none |
| Spearman | 25 | n/a | 2 | 65 | 1 | none |
| Swordsman | 35 | n/a | 2 | 90 | 2 | a strategic resource |
| Settler | n/a | n/a | 2 | **80** | 0 | **1 citizen** |
| Builder | n/a | n/a | 2 | 50 | 0 | none |
| Trader | n/a | n/a | 2 | 40 | 0 | none |

Two rules read from the table: **civilians cost more as they matter more** (a settler costs the most and eats a citizen), and **each step up in strength costs more production and more upkeep**.

**Guardrail:** every unit has a production cost and a gold upkeep, so army size is paid for by the economy on page 00.
**Design note:** keep "stat sheet + cost + upkeep". Open question: do you want resource-gated units, or only cost-gated?

## Step 2 · The one combat formula

Step A: strength gap.

```
gap = attacker strength (with bonuses) - defender strength (with bonuses)
```

Step B: damage. Each fight deals damage to one side (or both):

```
damage  ≈  random(24 to 36)  x  e^(gap / 25)
```

**Confirmed** `[sure]`: base damage **24**, plus a random extra of up to **12** (so 24 to 36); the strength-gap scale is **0.04 (= 1 divided by 25)**; the damage multiplier never drops below **0.25**; minimum damage per hit is **1**; max HP is **100**; one attack per unit per turn.

What that means in numbers (average base of 30), worked out here:

| Gap | Multiplier | Average damage |
|---|---|---|
| -25 | 0.37 | ~11 |
| -10 | 0.67 | ~20 |
| 0 | 1.00 | 30 |
| +10 | 1.49 | ~45 |
| +25 | 2.72 | ~82 |
| +40 | 4.95 | ~149 |

So: equal fighters trade about 30 HP each, ten extra strength is about +50% damage, and a gap of 40 kills a full-health unit in one hit.

**Who takes damage:**
- Melee attacks a unit: both take damage (each from its own gap). `[sure]`
- Ranged attacks a melee unit: only the target takes damage. `[sure]`
- Ranged vs ranged: the target may hit back. `[approx]`

**Guardrail:** the smooth curve means strength advantages grow fast but never flip the result with certainty (the random part always adds variance).
**Design note:** the exponential curve is the most "reusable" formula in the game: one rule, easy to tune with one number (the 25). Keep it, rename it.

## Step 3 · Where the map changes the fight

Bonuses are **flat additions** to strength, not percentages:

| Source | Effect | Tag |
|---|---|---|
| Defender on any hills tile | **+3** defense | `[sure]` |
| Defender fortified | **+3 per turn, up to 2 turns (so up to +6)** | `[sure]` |
| Defender on a river edge | **+5** | `[sure]` |
| Flanking (each extra friend next to the target) | **+2 attack** | `[sure]` |
| Support unit beside a melee unit | **+2** | `[sure]` |
| Corps / army formation | **+10 / +17** strength modifier | `[sure]` |
| Ranged attacking a city or district | **-17** | `[sure]` |
| Amphibious attack | **-10** | `[sure]` |
| Garrisoned city militia | **+10** | `[sure]` |
| Fighting on your followers' land (religion) | +5 (+15 on the holy city tile) | `[sure]` |
| Promotions, policies, great people | + strength | `[sure]` |

Because the damage formula is exponential, a flat +3 is always worth about +13% damage (e^(3/25) ≈ 1.13), no matter how strong the units are. Small bonuses stack into real power.

**Guardrail:** terrain tilts every fight, so where you stand matters more than what you own. This is the main link between combat and the tile system on page 00.
**Design note:** keep terrain-based bonuses; they make the map matter. A wounded-unit damage setting of **10** exists (`COMBAT_WOUNDED_DAMAGE_MULTIPLIER`), which suggests damaged units fight weaker; my earlier note that they don't was likely wrong. The exact rule `[verify]` in play. Decide whether wounded units should lose strength in your game.

## Step 4 · Moving on the map

- Movement cost, confirmed `[sure]`: flat land **1**, hills **2**, forest, jungle and marsh **+1** extra; mountains are impassable to land units; coast and ocean cost 1. Terrain sight and defense: hills **+3 defense**, flat and mountain terrain 0.
- **Zone of control (ZOC):** a military unit exerts control on adjacent tiles. An enemy unit that steps into a controlled tile must stop. `[sure]`
- **Stacking:** one military and one civilian unit per tile. `[sure]`
- Roads and rivers can lower travel cost. `[approx]`

**Guardrail:** ZOC and stacking limits stop one big stack from running through the map. They shape front lines.
**Design note:** ZOC is a cheap, strong rule for making borders and choke points real. Strong keep.

## Step 5 · Damage, healing, death

- HP regained per turn, confirmed `[sure]`: **land: 15 in friendly territory, 10 neutral, 5 enemy; city garrison 20; navy: 20 in friendly waters, 0 elsewhere; walls repair 10 per turn after a 3-turn cooldown; a religious unit's heal charge is 40.**
- A city or unit needs at least 1 of the strategic resource it uses to heal. `[sure]`
- At 0 HP the unit is gone. A civilian unit touched by an enemy military unit can be captured instead. `[sure]`
- A city that is surrounded (all six neighbors held or controlled by enemies) cannot heal. `[sure]`

**Guardrail:** healing time is the real cost of a fight; it forces rests between battles.

## Step 6 · Cities as targets

- A city has its own strength and HP, much more than a normal unit (about 200 HP `[approx]`). Its strength comes from **population (1 strength per 2 citizens, `[sure]`)**, era, being a capital, and districts (+2 strength per district type `[sure]`).
- A city shoots back with a minimum strike strength of **3**. `[sure]` A captured city loses **50%** of its HP; a captured city loses 25% of its citizens. `[sure]`
- **Walls** add a separate outer layer: attackers must break wall HP first, and until then city damage is reduced. `[sure]`
- Ranged and siege units are better against walls; melee units are weak against them. Wall damage splits, confirmed `[sure]`: **melee 15%, ranged 50%, bombard 100%** of normal damage reaches the wall; ranged hits on a city also stop at a threshold of 50.
- A city is taken when its HP reaches 0 and a melee unit walks in. `[sure]`

**Guardrail:** a city cannot be taken by ranged fire alone, and walls make the first defense cheap and strong.
**Design note:** the outer wall layer is a neat rule: it makes attackers bring the right unit type. Consider keeping a two-layer defense.

## Step 7 · How combat connects back to the economy

| From | To | Rule in plain words |
|---|---|---|
| Production | Unit | building cost in production |
| Gold | Unit upkeep | per-turn gold, can run the treasury negative |
| Population | Settler | a settler costs citizens, so expansion slows growth (page 00) |
| Strategic resource | Unit | some units cannot be built without it |
| Terrain | Combat strength | flat bonus per terrain/feature |
| Culture/borders | Movement and supply | where you may move freely; borders gate other players' units `[approx]` |
| Military capture | Tile ownership | taking a city flips its tiles to you |

## Open items

- Per-unit stat sheet for all 159 units (loaded; not written up).
- City HP and wall HP (district table has a hit-point column not in this dump).
- Exact rule for the wounded-unit penalty.
- Promotion values, unit upgrade paths.

## Sources

- Settings, healing, bonuses, wall splits, unit stats: the owner's game database.
- Damage formula shape: [Hans Lemurson figures out the Combat Formula](https://forums.civfanatics.com/threads/hans-lemurson-figures-out-the-combat-formula.606147/latest) (CivFanatics); the settings names also appear in modder threads.
- City combat and walls: [City combat](https://forums.civfanatics.com/resources/city-combat.27737/).
- General overview: [Civ 6 wiki, Combat](https://civilization.fandom.com/wiki/Combat_(Civ6)).
- Gap-to-damage table: computed here from the formula, not a source figure.
