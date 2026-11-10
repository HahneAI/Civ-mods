# Governments, Policy Cards, and Great People

Source: custom write-up. **`[sure]` numbers were read from the owner's own game database** (2026-11-10, via `tools/dbdump.py`); the rest is general knowledge plus a web check. Plain words, nothing copied; government and person names are left out on purpose (hard rule 8). Tags as before.
Builds on [`04-tech-civic-trees.md`](04-tech-civic-trees.md) (civics unlock governments and cards) and [`00-base-math.md`](00-base-math.md).

**Honest warning:** this is the thinnest page so far. I got slot counts by tier and a per-era cost list for great people, but not policy swap costs, per-government bonuses, or confirmed point rates.

## Part A · Governments and policy cards

## Step 1 · A government is a set of slots plus a built-in bonus

- A **government** is chosen from those your civics have unlocked, one at a time. `[sure]`
- It gives (a) a fixed **built-in bonus**, and (b) a set of **slots** into which you place **policy cards**. `[sure]`
- Slot types: military, economic, diplomatic, and a flexible **wildcard** that takes any type. `[sure]`
- Higher-tier governments have more slots. Confirmed from the database `[sure]`: **13 governments**: a starting one with 2 slots (1 military, 1 economic), then three each in tiers 1 to 4:

| Tier | Slots per government | Typical mix (military / economic / diplomatic / wildcard) |
|---|---|---|
| Start | 2 | 1 / 1 / 0 / 0 |
| 1 | 4 | e.g. 1/1/1/1, 2/1/0/1, 0/2/1/1 |
| 2 | 6 | e.g. 2/1/1/2, 2/2/1/1, 1/2/2/1 |
| 3 | 8 | e.g. 4/1/1/2, 3/3/1/1, 1/3/2/2 |
| 4 | 10 | **5 wildcard slots each**, e.g. 3/1/1/5, 1/1/3/5, 1/3/1/5 |

Tier 1 unlocks from an early civic, tiers 2 and 3 from mid-tree civics (one civic per government), tier 4 from the three last civics in the tree (page 04). A start-of-game government exists with no civic needed.

## Step 2 · Policy cards

- A card is a small rule with a cost: for example +X% of a yield, a discount on a unit type, or a bonus under some condition. `[sure]`
- Cards are unlocked by civics (page 04). `[sure]`
- You slot a card into a matching slot. Wildcard slots take anything. `[sure]`
- Card cost knobs, confirmed `[sure]`: base **25**, exponent **1.5**, an increase-to-be-exponentiated of **3**, a displayed-cost divisor of 5, and a **50% discount for a card that was already enacted**. How they combine into a swap price `[verify]`. The game has 157 cards in this install, including 12 for the great-person slot type. An anarchy-turn setting of 2 exists; whether it applies `[verify]`.
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
- Base cost per era, **read from the database** `[sure]`: **30, 60, 120, 240, 420, 660, 960, 1,320** for eras 1 to 8 (the future era stays 1,320).
  - Worked out here: each step up is 60 bigger than the last, so cost = 30 × (1 + k(k−1)/2) for era number k (k=1 gives 30). The pattern fits all eight numbers. `[derived]`
- You can also **buy** a person with gold or faith; the price depends on how many points you still lack. A forum guess: faith about 150 + 10 per missing point, gold about 200 + 15 per missing point. `[verify]` (not in the dump)
- If no one of your type is left to claim, your points turn into faith, **1.0 faith per point**. `[sure]`
- Class to district link, confirmed `[sure]`: general to the military-camp district, admiral to the harbor, engineer to the industrial district, merchant to the commercial district, **prophet to the faith district (only 1 per player)**, scientist to the campus, and writer, artist and musician all to the theater district.
- The roster has **212 people**; per class and by era `[derived]`:

| Class | People | Era spread |
|---|---|---|
| Writer | 29 | 2 to 8 |
| General | 24 | 2 to 8 |
| Merchant | 24 | 2 to 8 |
| Scientist | 24 | 2 to 8 |
| Admiral | 23 | 2 to 8 |
| Artist | 23 | era 4 on |
| Engineer | 21 | era 3 on |
| Musician | 18 | era 5 on |
| Prophet | 16 | eras 2 to 4 only |

About **3 to 6 people per class per era**: a small, finite pool.

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

## Open items

- Policy card list, effects and swap price formula.
- Government built-in bonuses (text columns not dumped).
- Great-person points per building and district; patronage price.
- Who wins a tie for the same person.

## Sources

- Slots, card cost knobs, great-person classes, era costs, roster: the owner's game database.
- Slots by tier (earlier draft): [Civ 6 wiki, Government](https://civilization.fandom.com/wiki/Government_(Civ6)) and [Policy card](https://civilization.fandom.com/wiki/Policy_card_(Civ6)); the snippets disagree on some tier counts and legacy bonuses.
- Great person costs: [On the cost of GPs](https://forums.civfanatics.com/threads/on-the-cost-of-gps.609359/latest) (per-era list), [Civilopedia, great people](https://www.civilopedia.net/en-US/rise-and-fall/concepts/greatpeople_2/) (points per district, patronage, faith conversion). An older base-plus-increment formula from a forum is unverified and I did not use it.
- Patronage guess: [Formula Thread](https://forums.civfanatics.com/threads/formula-thread.600534/). Unverified.
