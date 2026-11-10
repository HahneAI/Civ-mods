# Trade and Diplomacy: How Players Interact With Each Other

Source: custom write-up from general Civ 6 knowledge plus a web check (see "Sources"). Plain words, nothing copied. Tags as before: `[sure]`, `[approx]`, `[verify]`. Real numbers come through [`db-check.md`](db-check.md).
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
| Capacity | How many routes you can run at once. Raised by certain civics and buildings. | `[sure]` that it exists, `[verify]` how it grows |
| Range | The target must be within a set distance of the trader's start. Sea routes can go farther. | `[approx]` |
| Duration | A route runs for a fixed number of turns, then ends. | `[verify]` |

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
- Roads: a route can leave a road path along its way. `[approx]`

**Guardrail:** yields reward linking different cities. Routing between two identical cities pays little.
**Design note:** the idea that "routes move surplus from where it exists to where it is needed" fits a community-building game well. This is a strong keep. The per-building lookup table, however, is just data and is easy to redesign.

## Step 4 · Trade and war

- A trader can be pillaged or captured by an enemy military unit on the route. `[sure]`
- Declaring war on a partner ends international routes with that partner. `[approx]`

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

## Open items (fill in using db-check.md)

- Trade: capacity sources, range, route length, per-district yield table.
- Diplomacy: score values per action, agenda list, grievance values, casus belli list.
- City-states: envoy thresholds and suzerain bonus list.

## Sources

- Trade yields and routes: [Trade Routes Guide](https://forums.civfanatics.com/threads/trade-routes-guide.604710/latest), [What effect trade route yield and by how much?](https://forums.civfanatics.com/threads/what-effect-trade-route-yield-and-by-how-much.601907), [Civ 6 wiki, Trade Route](https://civilization.fandom.com/wiki/Trade_Route_(Civ6)). The "pre-patch" yield-difference findings may be out of date. One widely quoted formula is from Civ 5 and was not used.
- Diplomacy and grievances: [Civ 6 wiki, Diplomacy](https://civilization.fandom.com/wiki/Diplomacy_(Civ6)), [Grievances Guide](https://forums.civfanatics.com/threads/grievances-guide.642164), [Grievances balance](https://forums.civfanatics.com/threads/grievances-balance.647197).
- Envoys and city-state bonuses: thin coverage; not confirmed.
