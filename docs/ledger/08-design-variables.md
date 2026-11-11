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
| `keep` | the last `tail_eras` eras (default 1) may hold thin nodes that unlock nothing and need no boost; every other node still unlocks at least `min_unlocks_per_node` |
| `trim` | every node unlocks at least `min_unlocks_per_node` things (default 1): no thin tail |

**Evidence.** Counted with units included, every tech and civic in eras 1 to 7 unlocks something; only 4 of the 8 future techs, 2 era-8 civics and 1 future civic unlock nothing; average unlocks per tech fall from 4.1 (era 1) to 1.8 (era 8) (ledger 07) `[sure]`. 11 late techs also have no boost (ledger 04) `[sure]`. Design writers argue a node whose only benefit is "needed for another node" is weaker than one with a direct reward, though they also say a pure-enabler tree is not necessarily bad `[web]`.

**Decision: `keep`, made by the owner on 2026-11-11** (my first pick was `trim`, 8/10; I rate `keep` 6/10). The owner's choice stands. The evidence cuts both ways: the reference game keeps a thin tail and it is only the last era `[sure]`, but a node that only unlocks other nodes feels weaker than one with a direct reward `[web]`. So `keep` comes with two guardrails: thin nodes may appear only in the last `tail_eras` eras (V3), so the tail trails and never spreads into the middle; and a tail node may carry an effect of its own instead of being a pure prerequisite (the example's science tail node does, its culture tail node does not). R15 allows a node with no boost in the first era, or as a pure tail node.

**Test it.** Play the last era under `keep`. If tail nodes feel pointless, give each a small direct effect first, and only then try `trim` (the playground converts the data by removing the thin nodes). Metrics: share of tail nodes the player researches; turns spent on the tail as a share of the last era; whether the tail felt pointless or fine.
**What the checker does.** V3: under `trim`, every node needs at least the minimum number of unlocks; under `keep`, the same holds outside the last `tail_eras` eras. R15: a node without a boost must be in era 1, or a pure tail node under `keep`. Raising `min_unlocks_per_node` to 2, or setting `tail_eras` to 0, shows the pressure.

## Variable 4 · `great_person_pool`: shared or personal

| Option | Meaning |
|---|---|
| `shared_finite` | each person exists once in the world; first to the points claims them |
| `personal` | each community has its own supply; no race |

**Evidence.** In the reference data: 212 people, about 3 to 6 per class per era, each unique `[sure]` (ledger 05); points per turn are a flat 1 per specialty district plus 1 per building tier (ledger 05) `[sure]`. The race only means something if rivals exist. A game in this genre has rival communities (AI at minimum), so a shared pool works; a solo mode can use `personal`. The web check found little public criticism of the shared pool specifically, so this is more `[decision]` than `[web]`.

**Decision `[decision]`: `shared_finite`, rating 7/10.**

**Test it.** One game with rivals. If the player is often locked out of a whole class, add a catch-up discount (the reference game already does this for late nodes: about -20% for a node older than the game era) before switching to `personal`. Metrics: share of people claimed by rivals first; points wasted when a person is taken; how often a player gives up on a class.
**What the checker does.** V4: every great person has `max_claims = 1` (shared) or `null` (personal).

## What the simulator shows (first numbers)

The playground now has a **Simulate** panel (`docs/schema/playground-sim.js`): a small deterministic toy model that plays the example world for 200 turns (cities grow, yields flow, nodes are researched cheapest-first with boosts, a religion spreads by pressure, great people are earned against rivals). **It compares setups against each other; it does not forecast balance.** Every constant is a visible, editable assumption, and the example world is tiny. Defaults give these numbers (all are `[derived]` from the model, not from the game):

| Variable | Result with the model's defaults |
|---|---|
| `late_tail` | Keeping the 2 tail nodes makes the whole tree finish on **turn 102 instead of 71** (31 turns later). The tail is **37.7% of the total cost** and takes **33.3% of research turns** |
| `tree_layout` | Two trees finish on **turn 102**, ending **18 turns apart** (the faster tree sat idle: 837 yield wasted). One shared tree finishes on **turn 85** with 16 wasted |
| `religion_mode` | Pressure alone converts a new city about **11.9 turns** after it is founded; with spread units about **3.4** (19 units bought). Both reach every city. With religion off, no city converts |
| `great_person_pool` | Shared pool: you claim **1 of 4** people, rivals take 3, and you are locked out of 2 of 3 classes. Personal pool: you claim all 4 |

How to read them, honestly:
- **Tail:** the 37.7% is partly an accident of the example, where tail costs follow the era cost ladder (320 and 450). The finding that matters is that **a kept tail is a tuning choice with a real price**: if you keep it, price tail nodes low (a few percent of the tree) or give them effects, otherwise a third of research goes to nodes that unlock nothing.
- **Trees:** most of the gap comes from the culture tree costing more per unit of culture than the science tree does per unit of science. Under two trees, balance the two trees' costs against their yields or accept idle time.
- **Religion:** pressure-only is slower to convert each new city but gets there. Whether 12 turns versus 3 matters is a playtest question, not a model question.
- **Pool:** the lock-out depends on the rival-pace assumption (default 2 points per class per turn, rising). Set rival strength to 0 and the lock-out vanishes; set it low and you can see where it starts. The example pool is only 4 people, so one claim is a quarter of it.

**Use it:** open the playground, choose a variable under Simulate, press Run. The chart shows the series per option (research progress, share of cities following, great people claimed), the table gives the measures, and the sentence under it states the main difference. Change any assumption and run again.

## What the extended example shows

`docs/schema/example-data.json` is one mini-world built on all four decisions: 12 nodes (7 science, 5 culture, including 2 tail nodes) over 3 eras; 3 districts; 6 buildings; 6 cards; 3 governments; 4 beliefs and one religion with no spread units; 4 great people. Every node outside the tail unlocks something, every unboosted node is in era 1 or is a pure tail node, the six boost families are used, and the three governments have 2, 4 and 6 slots. It passes all 20 rules (R1 to R15, V0 to V4).

## Open items

- The simulator measures the research, religion and great-person metrics in a toy model only. Real playtest data still decides; until there is a playable build, treat simulator numbers as a way to compare options, not as results.
- Decide whether `faith_sinks` needs price rules (not in the dataset yet).
- Add catch-up discount settings to the schema if the shared pool is kept.

## Sources

- Religion discussion: [What Do We Think of Religion in Civ VI?](https://forums.civfanatics.com/threads/what-do-we-think-of-religion-in-civ-vi.666703), [Missionaries](https://forums.civfanatics.com/threads/missionaries.695140), [Religious battle and diplomacy](https://forums.civfanatics.com/threads/religious-battle-and-diplomacy.694034) (CivFanatics).
- Tech tree design: [Is the tech/civic tree profound enough?](https://forums.civfanatics.com/threads/is-the-tech-civic-tree-profound-enough.612165/page-2), [Fixing things that weren't broken](https://forums.civfanatics.com/threads/fixing-things-that-werent-broken.400810/page-3), [Will Civilization VII Finally Get the Tech Tree Right?](https://www.superjumpmagazine.com/will-civilization-vii-finally-get-the-tech-tree-right/).
- Everything marked `[sure]`: the owner's game database, via ledger pages 00 to 07.
