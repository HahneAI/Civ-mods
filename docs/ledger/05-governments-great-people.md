# Governments, Policy Cards, and Great People

Source: custom write-up from general Civ 6 knowledge plus a web check (see "Sources"). Plain words, nothing copied; government and person names are left out on purpose (hard rule 8). Tags as before: `[sure]`, `[approx]`, `[verify]`. Real numbers come through [`db-check.md`](db-check.md).
Builds on [`04-tech-civic-trees.md`](04-tech-civic-trees.md) (civics unlock governments and cards) and [`00-base-math.md`](00-base-math.md).

**Honest warning:** this is the thinnest page so far. I got slot counts by tier and a per-era cost list for great people, but not policy swap costs, per-government bonuses, or confirmed point rates.

## Part A · Governments and policy cards

## Step 1 · A government is a set of slots plus a built-in bonus

- A **government** is chosen from those your civics have unlocked, one at a time. `[sure]`
- It gives (a) a fixed **built-in bonus**, and (b) a set of **slots** into which you place **policy cards**. `[sure]`
- Slot types: military, economic, diplomatic, and a flexible **wildcard** that takes any type. `[sure]`
- Higher-tier governments have more slots: about **4, 6, 8, and 10** slots for tiers 1 to 4 (the fourth tier is expansion-only). `[approx]`

## Step 2 · Policy cards

- A card is a small rule with a cost: for example +X% of a yield, a discount on a unit type, or a bonus under some condition. `[sure]`
- Cards are unlocked by civics (page 04). `[sure]`
- You slot a card into a matching slot. Wildcard slots take anything. `[sure]`
- Changing cards: allowed freely at certain moments (when a new civic is completed); otherwise may cost gold. `[verify]` I found no confirmed rule.
- A government's inherited bonus is described in some sources as accumulating over time or being kept as a "legacy" after you switch. The exact rule differs by source and patch. `[verify]`

**Guardrail:** slots are the limit. You can't take every good card; you must pick a build for your kind of empire.
**Design note:** this is the **editable-ruleset layer**: the player chooses which small rules apply to them, within a cap. Rating: **8 out of 10** for your game. The cap-by-slot design is simple; the long list of one-off cards is the costly part. Keep the slots, trim the cards.

## Step 3 · Links

| From | To | Rule in plain words |
|---|---|---|
| Civic | Government / card | unlocks the choice |
| Government | Slots + built-in bonus | sets how many rules you can run |
| Card | Yield, cost, or combat modifiers | a rule applied empire-wide (pages 00, 01) |
| Culture | Everything above | civic meter feeds it all (page 04) |

## Part B · Great people

## Step 4 · What they are

- A **great person** is a unique named individual who gives a big, one-time or lasting benefit. `[sure]`
- They come in types tied to a district type (science, culture, faith, military, and so on). `[sure]`
- Each one exists only once: when a person is claimed by one player, nobody else can get them. `[sure]`

## Step 5 · Great person points

- Districts and the buildings inside them produce **points per turn** toward their type. `[sure]`
- Points are tracked per type; points for one type do not count toward another. `[sure]`
- Cost to claim the next person: depends on that person's **era**. `[sure]`
- Community figures, per era after the first: **60, 120, 240, 420, 660, 960, 1320** `[approx]`.
  - Worked out here: each step up is 60 bigger than the last step, so cost = 60 × (1 + k(k−1)/2) for era number k. That fits all seven numbers; the pattern is mine, not the game's. `[derived here]`
- You can also **buy** a person with gold or faith; the price depends on how many points you still lack. A forum guess: faith about 150 + 10 per missing point, gold about 200 + 15 per missing point. `[verify]`
- If no one of your type is left to claim, your points turn into faith, one for one. `[approx]`

## Step 6 · Why this is a race

- The pool of people is shared. You compare your points against your rivals' points for the same person. `[approx]`
- Whoever gets there first takes the person; the others wait for the next one. `[approx]`

**Guardrail:** great people reward focus (build lots of one district type) and punish being late, because the person can be taken.
**Design note:** a **shared, finite pool of unique rewards** makes every player's progress matter to every other player. Rating **7 out of 10** for your game: strong on competition, but it needs multiple players or AI rivals to work, and a solo game will feel empty.

## Step 7 · Links

| From | To | Rule in plain words |
|---|---|---|
| District / building (page 03) | Great person points | each one yields points per turn |
| Era | Cost | newer era, higher price |
| Gold or faith (pages 00) | Instant purchase | pay for missing points |
| Great person | Yields, units, boosts, wonders | one-shot or lasting effect |
| Rival players | Availability | people can be taken before you get there |

**Core loop to test in your game:** *build districts of one kind → points accumulate → claim a unique person → the benefit feeds that district's yields → more points.* A snowball, limited by the shared pool.

## Open items (fill in using db-check.md)

- Governments: exact slots per type, inherited bonuses, legacy rule.
- Policy cards: full list, costs, swap rule.
- Great people: full roster by era, point rates per building, how the race tie-break works.
- Patronage price formula.

## Sources

- Slots by tier: [Civ 6 wiki, Government](https://civilization.fandom.com/wiki/Government_(Civ6)) and [Policy card](https://civilization.fandom.com/wiki/Policy_card_(Civ6)); the snippets disagree on some tier counts and legacy bonuses.
- Great person costs: [On the cost of GPs](https://forums.civfanatics.com/threads/on-the-cost-of-gps.609359/latest) (per-era list), [Civilopedia, great people](https://www.civilopedia.net/en-US/rise-and-fall/concepts/greatpeople_2/) (points per district, patronage, faith conversion). An older base-plus-increment formula from a forum is unverified and I did not use it.
- Patronage guess: [Formula Thread](https://forums.civfanatics.com/threads/formula-thread.600534/). Unverified.
