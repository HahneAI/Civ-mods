# Design Variables: Four Open Questions as Things to Test

Source: custom design note. Evidence from ledger pages 00 to 07 (read from the owner's game database) and a short web check (see "Sources"). No Civ 6 names or text are used (hard rule 8). Machine form: `docs/schema/variants.json`; the example dataset that follows the decisions: `docs/schema/example-data.json`.
Tags: `[sure]` = from the database, `[web]` = from public discussion, `[decision]` = my choice, made on the owner's instruction ("make these decisions yourself").

## Why variables

The ledger records how Civ 6 works. The owner's game will differ. Four questions were left open at the end of the schema draft. Each is now a **switch with a current decision** (a `rules_config` key in the dataset). The decision is a starting point, not a verdict: flip the switch, run `tools/schemacheck.py`, see what in the data must change, playtest, compare the metrics below.

## Variable 1 · `tree_layout`: one tree or two

| Option | Meaning |
|---|---|
| `two_trees` | science tree and culture tree, each paid with its own yield |
| `one_tree` | one shared tree, each node paid with either yield |

**Evidence.** The reference trees differ in shape on purpose `[sure]`: the science tree starts wide (5 roots), is widest early (8 side by side) and funnels to 2 or 3; the culture tree is one trunk (1 root), steady width 3 to 4, deeper (17 steps vs. 15) and dearer late (ledger 04). The data shape is identical (`node` with a `tree` field), so the choice is configuration.

**Decision `[decision]`: `two_trees`, rating 8/10.** The contrast is the best design idea in the data, and it costs nothing to undo.

**Test it.** Same mini-game under both options. Watch whether players still *choose* between yields in `one_tree`, or whether one yield always wins. Metrics: share of nodes finished with a boost; turns spent per tree per era; times a player is blocked by a single yield.
**What the checker does.** V1: in `two_trees` every node's `paid_with` must equal its tree; in `one_tree` every node must be tree `main`.

## Variable 2 · `religion_mode`: how religion works

| Option | Meaning |
|---|---|
| `pressure_only` | beliefs spread by pressure from nearby cities and trade routes; **no spread units**; faith buys great people and religious buildings |
| `units_and_pressure` | pressure plus bought spread units with charges (the reference game) |
| `off` | no religion |

**Evidence.** In the reference data a belief is a single sentence (condition + tile or building filter + yield, ledger 07) `[sure]`; spread is pressure within 10 tiles, 1 point per turn, ×4 for the holy city, ×2 for the holy-site district, and 1.0 / 0.5 per trade route (ledger 03, 06) `[sure]`. The unit layer is three units with 3 charges each (ledger 06) `[sure]`. Public discussion is mostly about that layer: long waves of missionary units across the map and little way to defend `[web]`.

**Decision `[decision]`: `pressure_only`, rating 7/10** (the unit version stays at 6/10). Keep what players like (beliefs, spread by distance), drop what they complain about. Faith keeps a job so it is not a dead yield.

**Test it.** Does religion still spread fast enough to matter by the middle eras? If it stalls, first raise the pressure multipliers or add one small active action; only then bring units back. Metrics: share of cities with a religion by turn; turns until the first religion forms; faith spent per sink.
**What the checker does.** V2: `pressure_only` needs beliefs, a religion, pressure settings, faith sinks and **no** faith units; `units_and_pressure` needs units; `off` needs no religion data.

## Variable 3 · `late_tail`: keep the thin end of the tree?

| Option | Meaning |
|---|---|
| `keep` | late nodes may unlock nothing (prerequisite-only) |
| `trim` | every node unlocks at least `min_unlocks_per_node` things (default 1) |

**Evidence.** Counted with units included, every tech and civic in eras 1 to 7 unlocks something; only 4 of the 8 future techs, 2 era-8 civics and 1 future civic unlock nothing; average unlocks per tech fall from 4.1 (era 1) to 1.8 (era 8) (ledger 07) `[sure]`. 11 late techs also have no boost (ledger 04) `[sure]`. Design writers argue a node whose only benefit is "needed for another node" is weaker than one with a direct reward, though they also say a pure-enabler tree is not necessarily bad `[web]`.

**Decision `[decision]`: `trim`, minimum 1, rating 8/10.** Plus a boost rule: a node with no boost is allowed only in the first era (R15 in the schema).

**Test it.** Play the last era under both options. If `trim` crowds the end, drop the minimum to 0 for the final era only. Metrics: share of researched nodes the player uses at once; nodes the player skips; turns of "just end turn" in the last era.
**What the checker does.** V3: under `trim`, each node needs at least the minimum number of unlocks. `min_unlocks_per_node` can be raised to 2 to see the pressure.

## Variable 4 · `great_person_pool`: shared or personal

| Option | Meaning |
|---|---|
| `shared_finite` | each person exists once in the world; first to the points claims them |
| `personal` | each community has its own supply; no race |

**Evidence.** In the reference data: 212 people, about 3 to 6 per class per era, each unique `[sure]` (ledger 05); points per turn are a flat 1 per specialty district plus 1 per building tier (ledger 05) `[sure]`. The race only means something if rivals exist. A game in this genre has rival communities (AI at minimum), so a shared pool works; a solo mode can use `personal`. The web check found little public criticism of the shared pool specifically, so this is more `[decision]` than `[web]`.

**Decision `[decision]`: `shared_finite`, rating 7/10.**

**Test it.** One game with rivals. If the player is often locked out of a whole class, add a catch-up discount (the reference game already does this for late nodes: about -20% for a node older than the game era) before switching to `personal`. Metrics: share of people claimed by rivals first; points wasted when a person is taken; how often a player gives up on a class.
**What the checker does.** V4: every great person has `max_claims = 1` (shared) or `null` (personal).

## What the extended example shows

`docs/schema/example-data.json` is one mini-world built on all four decisions: 10 nodes (6 science, 4 culture) over 3 eras; 3 districts; 6 buildings; 6 cards; 3 governments; 4 beliefs and one religion with no spread units; 4 great people. Every node unlocks something, every unboosted node is in era 1, the six boost families are used, and the three governments have 2, 4 and 6 slots. It passes all 20 rules (R1 to R15, V0 to V4).

## Open items

- Playtest the metrics above: this needs a playable build; until then they are written down, not measured.
- Decide whether `faith_sinks` needs price rules (not in the dataset yet).
- Add catch-up discount settings to the schema if the shared pool is kept.

## Sources

- Religion discussion: [What Do We Think of Religion in Civ VI?](https://forums.civfanatics.com/threads/what-do-we-think-of-religion-in-civ-vi.666703), [Missionaries](https://forums.civfanatics.com/threads/missionaries.695140), [Religious battle and diplomacy](https://forums.civfanatics.com/threads/religious-battle-and-diplomacy.694034) (CivFanatics).
- Tech tree design: [Is the tech/civic tree profound enough?](https://forums.civfanatics.com/threads/is-the-tech-civic-tree-profound-enough.612165/page-2), [Fixing things that weren't broken](https://forums.civfanatics.com/threads/fixing-things-that-werent-broken.400810/page-3), [Will Civilization VII Finally Get the Tech Tree Right?](https://www.superjumpmagazine.com/will-civilization-vii-finally-get-the-tech-tree-right/).
- Everything marked `[sure]`: the owner's game database, via ledger pages 00 to 07.
