# Units and Combat: How Units Interact With the Map

Source: custom write-up from general Civ 6 knowledge plus a web check (see "Sources"). Plain words, nothing copied. Same tags as page 00: `[sure]`, `[approx]`, `[verify]`. Exact values get filled in through [`db-check.md`](db-check.md).
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

`[sure]` for the idea; each unit's numbers are in the `Units` table (see db-check).

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

`[approx]` The base of 24 plus up to 12 random extra is reported by modders as game settings (`COMBAT_BASE_DAMAGE`, `COMBAT_MAX_EXTRA_DAMAGE`).

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
| Defender on hills / forest / jungle | + defense strength | `[sure]` that it exists, `[verify]` numbers |
| Defender fortified (stood still) | + defense strength | `[verify]` |
| River crossing attacked across | attacker penalty | `[approx]` |
| Flanking (more friends adjacent to target) | + attack strength | `[approx]` |
| Support units next to a melee unit | + strength | `[approx]` |
| Promotions, policies, great people | + strength | `[sure]` |

Because the damage formula is exponential, a flat +3 is always worth about +13% damage (e^(3/25) ≈ 1.13), no matter how strong the units are. Small bonuses stack into real power.

**Guardrail:** terrain tilts every fight, so where you stand matters more than what you own. This is the main link between combat and the tile system on page 00.
**Design note:** keep terrain-based bonuses; they make the map matter. Decide whether wounded units should also lose strength (reported as not the case in Civ 6, `[verify]`).

## Step 4 · Moving on the map

- Each tile costs movement points by terrain: flat is cheap, hills and forest cost more, mountains and deep water block most units. `[sure]`, exact costs in `Terrains` / `Features`.
- **Zone of control (ZOC):** a military unit exerts control on adjacent tiles. An enemy unit that steps into a controlled tile must stop. `[sure]`
- **Stacking:** one military and one civilian unit per tile. `[sure]`
- Roads and rivers can lower travel cost. `[approx]`

**Guardrail:** ZOC and stacking limits stop one big stack from running through the map. They shape front lines.
**Design note:** ZOC is a cheap, strong rule for making borders and choke points real. Strong keep.

## Step 5 · Damage, healing, death

- A unit regains HP when it rests, faster in friendly land and fastest in a city. `[approx]` Rates are `[verify]`.
- Units under 100 HP still fight at full strength in Civ 6. `[verify]`
- At 0 HP the unit is gone. A civilian unit touched by an enemy military unit can be captured instead. `[sure]`
- A city that is surrounded (all six neighbors held or controlled by enemies) cannot heal. `[sure]`

**Guardrail:** healing time is the real cost of a fight; it forces rests between battles.

## Step 6 · Cities as targets

- A city has its own strength and HP, much more than a normal unit. Its strength comes from size/era, being a capital, and districts (a flat bonus each). `[approx]`
- **Walls** add a separate outer layer: attackers must break wall HP first, and until then city damage is reduced. `[sure]`
- Ranged and siege units are better against walls; melee units are weak against them. Reported wall damage splits: melee about 15%, ranged about 50%, bombard about 100% of normal. `[approx]`
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

## Open items (fill in using db-check.md)

- Exact base damage, extra damage, and the divisor 25.
- Exact terrain and fortify bonuses, flanking and support values.
- Healing rates per location.
- City base strength, wall HP, wall damage splits.
- Per-unit stat sheet (all units).

## Sources

- Damage formula: [Hans Lemurson figures out the Combat Formula](https://forums.civfanatics.com/threads/hans-lemurson-figures-out-the-combat-formula.606147/latest) (CivFanatics); the settings names also appear in modder threads.
- City combat and walls: [City combat](https://forums.civfanatics.com/resources/city-combat.27737/).
- General overview: [Civ 6 wiki, Combat](https://civilization.fandom.com/wiki/Combat_(Civ6)).
- Gap-to-damage table: computed here from the formula, not a source figure.
