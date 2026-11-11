# Trade and Diplomacy: How Players Interact With Each Other

Source: custom write-up. **`[sure]` numbers were read from the owner's own game database** (2026-11-10, via `tools/dbdump.py`); the rest is general knowledge plus a web check. Plain words, nothing copied. Tags as before.
Builds on [`00-base-math.md`](00-base-math.md) (yields, gold) and [`01-units-combat.md`](01-units-combat.md) (war).

**Honest warning:** these two systems have the thinnest public math of the three pages. Trade yields are mostly per-building lookups, and diplomacy is mostly a tuned score, so there is less clean formula to record. Where I could not confirm a number, I say so.

## Step 0 · The big picture

> **Trade turns the map into a network of links between cities. Diplomacy turns other players into numbers (a relationship score) that gate what you may do: trade, ally, or go to war.**

```
 BUILD TRADER (production) -> PICK ROUTE (range, capacity) -> YIELDS to both ends
                                                       |
 BEHAVIOR (promises, wars, agendas) -> RELATIONSHIP SCORE -> allowed actions
                                                       |
                                  war declaration -> combat page (01)
```

---

# Part A · Trade

## Step 1 · A trade route is a link between two cities

- A **trader** unit is built with production, walks (or sails) from its home city to a target city, and starts a route. `[sure]`
- Target can be one of your own cities (**domestic**) or another player's (**international**). `[sure]`
- While the route is active, both ends receive yields every turn. `[sure]`

## Step 2 · The three limits on a route

| Limit | Plain meaning | Tag |
|---|---|---|
| Capacity | How many routes you can run at once. Raised by certain civics and buildings. | `[sure]` that it exists; how it grows `[verify]` |
| Range | **15 tiles** on land; **30** over water (refuel distances). | `[sure]` |
| Duration | **20 turns** base. | `[sure]` |

**Guardrail:** you cannot spam routes. Capacity caps how many you run; range caps where. This is what makes "who is near whom" matter.

## Step 3 · What a route pays

The yield is built from what exists at the two ends:

```
route yield  ≈  sum of lookups on the destination city's districts and buildings
              + extra for international vs domestic
              + modifiers (policies, buildings, wonders)
```

What community testing found `[approx]`:
- Domestic routes lean toward **food and production**, and the amount depends on the difference between the two cities' yields. Sending a trader from a food-poor city to a food-rich one helps the poor one.
- International routes lean toward **gold**, and a harbor at the destination adds gold.
- City population and era did not affect the yield in a tester's results. `[verify]`
- Roads: a route **builds roads** along its way. `[sure]`
- **Yield table, read from the database** `[sure]`: the route pays by **what districts the destination city has**, and the origin city collects it. Origin-side values are all 0.

| Destination district | Domestic route pays | International route pays |
|---|---|---|
| City center | +1 food, +1 production | **+3 gold** |
| Commercial hub, harbor (and their unique versions) | +1 production | **+3 gold** |
| Industrial zone, military camp (and unique versions) | +1 production | +1 production |
| Campus-type | +1 food | +1 science |
| Faith district | +1 food | +1 faith |
| Theater-type | +1 food | +1 culture |
| Entertainment-type | +1 food | +1 food |
| Government district | +1 food, +1 production | +2 gold |
| Diplomatic quarter | +1 food, +1 production | +1 culture |

So a destination with many different districts pays more, and **international routes pay gold from trade-type districts and a little of everything else**. There is also a separate setting of about +2 gold per district at each end. `[sure]` (how it combines with this table `[verify]`)
- Trade routes also carry religion (page 06): **1.0 pressure at the destination and 0.5 at the origin**, and add tourism (+25%). `[sure]`

**Guardrail:** yields reward linking different cities. Routing between two identical cities pays little.
**Design note:** the idea that "routes move surplus from where it exists to where it is needed" fits a community-building game well. This is a strong keep. The per-building lookup table, however, is just data and is easy to redesign.

## Step 4 · Trade and war

- A trader can be pillaged or captured by an enemy military unit on the route. `[sure]`
- Declaring war on a partner ends international routes with that partner. `[approx]`

## Step 4b · Diplomacy numbers read from the database `[sure]`

| Rule | Value |
|---|---|
| Minimum turns of war before peace | 10 |
| Minimum turns of peace before a new war | 10 |
| Declared friendship, alliance, defensive pact, denounce: how long each lasts | 30 turns |
| Alliance levels | 3 (level 2 at 320 points, level 3 at 960) |
| Alliance points | +1 per trade, +2 per deal, +2 per society action, ×4 multiplier |
| Grievances for a denouncement | 25 |
| Grievances from breaking a promise | ×200 (scale) |
| Warmonger points by era (conquering) | 0, 6, 12, 18, 24, then flat at 24 |
| Grievances per turn for holding a conquered capital / other city | 3 / 1 |
| Diplomatic victory points needed | 20 |

### The relationship ladder, read from the database `[sure]`

Each major player has a relationship **level from 0 to 100**; its state maps to a yield bonus (a bonus or penalty on shared yields):

| State | Relationship level | Yield bonus |
|---|---|---|
| Allied | 100 | +50 |
| Declared friend | 83 | +25 |
| Friendly | 66 | +25 |
| Neutral | 50 | 0 |
| Unfriendly | 33 | -25 |
| Denounced | 16 | -75 |
| War | 0 | -100 |

How you move between states. The numbers are read from the transition table, but **my reading of what they mean is `[approx]`** (the table has four threshold columns I interpreted as score limits):

| From | To | Condition |
|---|---|---|
| Neutral | Friendly | score rises past about 15 |
| Neutral | Unfriendly | score falls past about -15 |
| Friendly | Declared friend | needs score of about 25 and a free action; can be offered |
| Declared friend | Allied | needs about 35 and an alliance offer |
| Unfriendly | Denounced | score at or below -25, by action |
| Denounced | War | score at or below -35, by action |

The step sizes are small (5 to 35), so state changes come from lots of small acts adding up. `[derived]`

**Promises** (a request one player makes of another, kept by paying 30 favor; refusing costs 25 grievances; each broken-promise incident costs 25): *don't spy on me, don't convert my cities, don't dig my artifacts, don't settle near me.* `[sure]`

**Alliances** have five types (military, economic, research, cultural, religious) and three levels (levels 2 and 3 at 320 and 960 points). `[sure]` Each type adds effects by level, 24 in total: level 1 is mostly extra trade-route yields of the alliance's kind (gold, faith, culture, science), or combat strength for the military type; level 2 adds things like shared vision, envoy points, research agreements, and great-person points; level 3 adds free unit upgrades, shared suzerain, and shared science, culture and tourism from your ally. `[sure]`

**Visibility** (what lets you read another leader) comes from nine sources: a tech, a trader, a delegate, an ally, a spy, a high-level spy (needs spy level 3), a trait, a trading-post trait, and one great person. `[sure]`

## Step 5 · Links back to other systems

| From | To | Rule in plain words |
|---|---|---|
| Production | Trader unit | cost in production, upkeep in gold |
| Districts/buildings | Route yield | destination buildings set what the route pays |
| Route | Both cities' food/production/gold | per-turn yield to origin and, for foreign routes, a smaller share to the target |
| Diplomacy | Routes | needs peace and contact to route with a foreign city |
| Combat | Routes | enemy units can break a route |

---

# Part B · Diplomacy

## Step 6 · Every other player is a relationship score

Rule in words: each AI leader keeps a running opinion of you.

```
relationship  =  sum of (things you did) + sum of (things they care about)
```

- **Things you did:** keeping promises, trading, sharing borders peacefully, joining their wars (positive); breaking promises, denouncing, warring on friends (negative). `[sure]`
- **Agendas:** each leader has an **open agenda** (visible, never changes) and a **hidden agenda** (revealed through contact). Acting against an agenda costs you a lot. `[sure]`
- **Visibility:** the more you have seen of a leader (embassy, spies, gossip), the more of their agenda you can read. `[sure]`

**Guardrail:** AI behavior is predictable if you read the agenda. Information is the resource.
**Design note:** two layers (a visible trait and a hidden one) plus a visibility mechanic is a clean way to make AI readable without hand-holding. Strong keep.

## Step 7 · The ladder of states

| State | What it allows | Tag |
|---|---|---|
| Unmet | nothing | `[sure]` |
| Met / neutral | basic talks, trades | `[sure]` |
| Declared friend | allies possible, cannot war or denounce each other | `[sure]` |
| Alliance | shared vision and defense; cannot war each other | `[sure]` |
| Denounced | penalties for both sides | `[sure]` |
| War | combat page (01) takes over | `[sure]` |

## Step 8 · Going to war has a price (grievances)

In the Gathering Storm rules:
- Declaring war creates **grievances** in the eyes of other players. `[sure]`
- The amount depends on war type (surprise, formal, joint, with a casus belli); per-turn values fade over eras. `[approx]`, fan-forum numbers, `[verify]`.
- Grievances fade after peace. `[sure]`
- A **joint war** (two players attack a third together) needs a specific civic. `[sure]`
- Promises are part of the score: refusing or ignoring a promise request costs about -6, fading with time. `[approx]`

**Guardrail:** wars are not free. Attacking quietly is more expensive than a justified war, which pushes players toward reasons for war.
**Design note:** "a justified war costs less than a surprise one" is a clear rule. Keep. Decide whether war should cost standing in your game at all.

## Step 9 · City-states and envoys

- **City-states** are small neutral cities. You send **envoys** to them (not to normal players). `[approx]`
- More envoys than anyone else gives you **suzerain** status and extra bonuses; envoy thresholds unlock tiered bonuses. `[sure]` for the idea, `[verify]` thresholds.
- Wonders, governments, and some policies raise envoy output. `[approx]`

**Guardrail:** envoys are a fixed supply to spend, so you must choose which city-states to back.
**Design note:** a small supply spent on competing neutral parties is a lean influence mechanic. Worth a **7 out of 10** for reuse: it's simple and creates real choice, but the bonus list itself is a big pile of special cases.

## Step 10 · How it all connects

| From | To | Rule in plain words |
|---|---|---|
| Behavior (promises, wars) | Relationship score | each act adds or subtracts |
| Agenda + visibility | What you can predict | more contact, more you can read |
| Relationship state | Allowed actions | friend, ally, denounce, war |
| War declaration | Grievances | other players' opinion drops |
| War | Combat (page 01) | ends trade, starts fighting |
| Peace + contact | Trade (Part A) | foreign routes need it |
| Envoys | City-state bonuses | influence race decides the reward |
| Trade gold/food | Economy (page 00) | yields flow into city budgets |

**Core loop to test in your game:** *peace and contact → trade links → richer cities → bigger armies → pressure on neighbors → grievances and alliances → back to peace or war.*

## Open items

- Route capacity sources, per-district yield table (the dump has route gold per district; capacity not in it).
- Relationship score change per action, agenda list (112 agendas exist; names not needed for the ledger), casus belli list.
- Envoy thresholds and city-state bonus list (influence settings: **3 envoys for suzerain**, `[sure]`).

## Sources

- Route range, duration, gold, diplomacy numbers: the owner's game database.
- Trade yields and routes (shape): [Trade Routes Guide](https://forums.civfanatics.com/threads/trade-routes-guide.604710/latest), [What effect trade route yield and by how much?](https://forums.civfanatics.com/threads/what-effect-trade-route-yield-and-by-how-much.601907), [Civ 6 wiki, Trade Route](https://civilization.fandom.com/wiki/Trade_Route_(Civ6)). The "pre-patch" yield-difference findings may be out of date. One widely quoted formula is from Civ 5 and was not used.
- Diplomacy and grievances: [Civ 6 wiki, Diplomacy](https://civilization.fandom.com/wiki/Diplomacy_(Civ6)), [Grievances Guide](https://forums.civfanatics.com/threads/grievances-guide.642164), [Grievances balance](https://forums.civfanatics.com/threads/grievances-balance.647197).
- Envoys and city-state bonuses: thin coverage; not confirmed.
