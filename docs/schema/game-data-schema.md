# Game Data Schema (draft v0.2)

Source: custom design note, built from ledger pages 00 to 07 (which were read from the owner's Civ 6 database). **This is a design document, not engine code.** It describes the *shape* of the data for the owner's own tile game, in the owner's own terms. Names in it are generic placeholders. Numbers marked "reference" are what Civ 6 used (from the ledger) and are starting points to tune, not rules. No Civ 6 names, text, or code are copied (hard rule 8, SPEC section 9).

Machine-checkable parts: `enums.json` (closed lists), `variants.json` (the four design variables, the decisions made, and who made them), `example-data.json` (an extended mini-world: 10 nodes, 3 districts, 6 buildings, 6 cards), `tools/schemacheck.py` (checks any dataset against the rules in section 5), and `tests/test_schema_example.py` (53 tests: the example passes, and every rule and variable fails when broken).

**v0.2 change:** the four open questions from v0.1 are now **switchable variables** with decisions (section 3.11, ledger page 08). Flip a value in `rules_config` and `python tools/schemacheck.py` lists what in the data must change.

## 1. Principles (from the master map, ledger page 06)

1. **Data, not code.** Every card, building, belief, and government is rows of data. No special code per item. (Ledger 07: 2,219 effect rows, none special-cased.)
2. **One meter system.** Food basket, science, culture, great-person points, faith, borders: all are "a meter fills, then something happens, then the next one costs more." Build it once.
3. **Caps force tradeoffs.** Housing vs. citizens, districts vs. population, slots vs. government tier, route capacity vs. civics. Every cap is a data field.
4. **The map feeds the tree.** Terrain feeds adjacency; boosts reward acts on the map. Keep both links.
5. **Closed lists.** Effect kinds, requirement kinds, scopes, and trigger families are fixed lists (`enums.json`). A new kind needs a design decision, not just a new row.
6. **Say it once.** A card that repeats one effect per class per era is stored once with a list of classes and eras (ledger 07, Step 3).
7. **IDs are stable strings** with a type prefix (`node.`, `dist.`, `bld.`, `card.`, `eff.`, `cond.`, `gov.`, `gp.`, `imp.`). Unique across the whole dataset.

## 2. Core types

### 2.1 Yield

One of: `food, production, gold, science, culture, faith` (`enums.json`). Whole numbers per turn.

### 2.2 Era

| Field | Type | Meaning |
|---|---|---|
| `id` | string | `era_1` ... |
| `index` | int | order, starting at 1 |
| `great_person_base_cost` | int | points needed for a great person of this era |

Reference: 8 eras plus a future era; great-person base cost **30, 60, 120, 240, 420, 660, 960, 1320** (each step up is 60 more than the last, ledger 05). Era length 40 to 60 turns before it can end (ledger 07).

### 2.3 Meter (the one reusable idea)

| Field | Type | Meaning |
|---|---|---|
| `id` | string | `meter_food` ... |
| `fed_by` | yield | which yield fills it |
| `cost_model` | enum | `flat`, `per_count_over_average`, `game_progress`, `per_size` |
| `cost_params` | object | numbers for that model |
| `on_full` | enum | `reset` or `carry_over` |

Meters in the reference game, all expressible as above:

| Meter | Fed by | Reference cost rule |
|---|---|---|
| City growth | food | start 15, +8 per size step, exponent 1.5 (ledger 00) |
| Tech tree | science | node cost (see 3.4) |
| Civic tree | culture | node cost |
| Border growth | culture | first tile 10, then 10 + (6 x (tiles-1))^1.3 (ledger 00) |
| Great person | great-person points | era base cost (2.2) |
| Faith purchases | faith | unit price rises per unit bought |

## 3. Entity tables

### 3.1 Map layer

| Entity | Fields |
|---|---|
| `terrain` | `id`, `yields`, `move_cost`, `defense_bonus`, `passable`, `is_water`, `is_highland` |
| `feature` | `id`, `yields_added`, `move_cost_added`, `valid_terrain` |
| `resource` | `id`, `class` (`bonus, luxury, strategic, artifact`), `yields`, `amenities` (luxury only) |
| `improvement` | `id`, `requires_node`, `valid_on`, `yields`, `housing_per_tiles {housing, tiles}` |

Reference values (ledger 00, 01): flat land costs 1 to move, highland 2, forest and jungle +1; highland gives +3 defense; a river edge +5; a luxury gives 4 amenities; a farm-type improvement gives 1 housing per 2 improved tiles.

### 3.2 City rules (one global settings object)

| Group | Fields (reference value) |
|---|---|
| Food | `food_per_citizen` (2) |
| Growth | meter `meter_food` (start 15, +8, exp 1.5) |
| Housing steps | headroom >=2: 100%; 1: 50%; 0: 25%; <= -4: 0% (ledger 00); base housing by water: none 2, coast 3, river or lake 5 |
| Amenities | `citizens_per_amenity` (2); mood table: score -> growth %, non-food yield %, rebellion points |
| Reach | `work_radius` (3), `buy_radius` (3), `min_city_distance` (3), `tile_worker_capacity` (1) |
| Founding | `settler_cost` (80 production, 1 citizen) |
| Loyalty | start/max 100; bands 0-25, 26-50, 51-75, 76-100 with yield change -1, -0.5, -0.25, 0 and growth change 0, +0.25, +0.75, +1 |

Mood table (reference, ledger 00): score >=5 +20% growth and yields; 3 to 4 +10%; 0 to 2 none; -1 to -2 -15% growth, -10% yields; -3 to -4 -30%, -20%; -5 to -6 growth stops, -30%; <= -7 growth stops, -40%.

### 3.3 District, adjacency, building

`district`:

| Field | Meaning |
|---|---|
| `id`, `cost`, `cost_model`, `cost_params` | cost model: `per_count_over_average` (specialty), `game_progress` (housing/utility), `flat` |
| `one_per_city` | false for housing-type districts |
| `housing`, `amenities`, `city_strength_mod` | numbers |
| `requires_node` | unlock |
| `great_person_class`, `gp_points_per_turn` | each specialty district gives 1 point per turn of its class |
| `adjacency` | list of `adjacency_rule` |

`adjacency_rule`: `{yield, amount, per, neighbor}` where `neighbor` is a selector (a terrain, feature, improvement, resource class, river, wonder, natural wonder, a district id, or "any other district"). Reference: +1 or +2 per 1 matching neighbor, +1 per 2 for "any other district".

District cap (reference): **1 specialty district per 3 citizens** (`districts_per_citizens = 3`, global).

`building`: `id`, `district`, `cost`, `housing`, `amenities`, `citizen_slots` (reference: 1 per specialty-district building), `upkeep_gold`, `yields`, `great_person_points {class: points}`, `requires_node`. Reference ladder inside a district: costs about 90 to 150, then 250 to 330, then 440; yields about +2, +4, then +3 to +6.

### 3.4 Node (tech or civic), boost, unlock

`node`:

| Field | Type | Meaning |
|---|---|---|
| `id` | string | `node.` prefix |
| `tree` | `science` or `culture` (or `main` when `tree_layout = one_tree`) | which tree the node sits in |
| `paid_with` | yield | which yield pays for it; must equal the tree in `two_trees`, either `science` or `culture` in `one_tree` |
| `era` | era id | |
| `cost` | int | before modifiers |
| `requires` | list of node ids | same tree only; 0 to 4 |
| `boost` | object | `{family, trigger, percent}` |
| `unlocks` | list of `{type, id}` | type in `district, building, improvement, unit, project, card, government` |

`boost`: `family` in `build_or_own, chain_node, combat, diplomacy_trade, explore, religion, none`; `trigger` is `{kind, ...}` with arguments such as `count` or a target id; `percent` 0 to 100 (reference 40; one late civic 90).

Cost modifiers (global): game speed multiplier (reference marathon 3.0, epic 1.5, standard 1.0, quick 0.67, online 0.5) and an era shift (reference -20% for a node older than the game era, +20% for newer).

### 3.5 Units (light)

`unit`: `id`, `class`, `melee`, `ranged`, `range`, `moves`, `cost`, `upkeep`, `needs_resource`, `population_cost`, `requires_node`. `unit_class` is the grouping effects use (melee, ranged, light cavalry, and so on). Combat rule (global): damage = base (24) + random up to 12, times e^(gap x 0.04), min 1, max HP 100; bonuses are flat strength additions (reference ledger 01).

### 3.6 Government and cards

`government`: `id`, `tier`, `requires_node`, `slots {military, economic, diplomatic, wildcard}`, `fixed_bonus` (an effect id or null), `influence_per_turn`, `points_per_envoy`. Reference slot totals: starter 2, then 4, 6, 8, 10 by tier (tier 4 has 5 wildcards).

`card`: `id`, `slot`, `requires_node`, `effects` (list of effect ids). Reference: 157 cards; 118 gated by a civic.

### 3.7 Effects, scopes, conditions (the core of the design)

`effect`:

| Field | Meaning |
|---|---|
| `id`, `owner` | the card, building, belief, government, great person, or promotion that carries it |
| `scope` | who gets it (`scopes` in `enums.json`) |
| `kind` | what changes (closed list of 24, `effect_kinds`) |
| `args` | numbers and ids for that kind (`yield`, `amount`, `unit_classes`, `eras`, ...) |
| `when` | id of a `condition` or null |

`condition`: `{id, mode: all|any, requirements: [{kind, args, negate}]}`. `kind` from the closed list of 15 `requirement_kinds`; `set_is_met` lets one condition use another. Conditions are shared between effects.

`attach_effect` is a wrapper ("when X, also apply effect Y"); in the reference game 64 of 88 belief rows were wrappers. In this schema, prefer putting the condition on the inner effect and drop the wrapper, unless a belief must attach to many objects.

Effect kinds, in plain words:

| Kind | Meaning |
|---|---|
| `yield_pct`, `yield_flat`, `yield_per_citizen` | change a yield in the scope |
| `tile_yield` | change a tile's yield (filtered by improvement or terrain through `when`) |
| `adjacency_yield` | extra adjacency bonus for a district |
| `production_pct_by_unit_class` | % production of unit classes in given eras |
| `cost_mod` | cheaper or dearer unit, building or purchase |
| `strength_mod`, `experience_mod`, `healing_mod`, `movement_mod` | unit changes |
| `grant_ability` | give a named ability defined in `abilities` |
| `growth_pct`, `border_expansion_pct` | city meters |
| `housing`, `amenity` | city caps |
| `great_person_points` | extra points |
| `trade_capacity`, `trade_route_yield` | trade |
| `influence_points` | envoy meter |
| `grant_unit` | free unit |
| `loyalty` | loyalty change |
| `era_score` | era score |
| `attach_effect` | wrapper |

### 3.8 Religion

`belief`: `id`, `class` (`pantheon, follower, worship, founder, enhancer`), `effects`. A belief is one sentence: condition (the city follows it) + tile or building filter + yield bonus. `religion`: `{id, beliefs, holy_city}`. Reference: religion starts with 2 beliefs; pantheon costs 25 faith; pressure within 10 tiles, 1 point per turn, holy city x4, holy-site district x2; trade routes carry 1.0 (destination) and 0.5 (origin) pressure. `faith_unit`: charges (reference 3), strength (100, 110, 75), evict percent (10, 25, 75), cost (75, 200, 75).

Religion data in the dataset (variable `religion_mode`, section 3.11): `beliefs`, `religions`, `religion_pressure {radius, per_turn_adjacent_city, holy_city_multiplier, shrine_district_multiplier, route_destination, route_origin, pantheon_cost_faith}`, `faith_sinks` (what faith can be spent on: `great_person_patronage`, `building_purchase`), and `faith_units` (empty unless `units_and_pressure`).

### 3.9 Trade and diplomacy

- `route_yield_rule`: `{district, domestic_dest: yields, international_dest: yields}`. Reference: the route pays by the destination's districts (domestic: +1 food or production; international: +3 gold from commerce-type, +1 science, culture or faith from the matching district). Range 15 land / 30 water, duration 20 turns, builds roads.
- `diplomatic_state`: `{id, level, yield_bonus}`. Reference: allied 100 (+50), declared friend 83 (+25), friendly 66 (+25), neutral 50 (0), unfriendly 33 (-25), denounced 16 (-75), war 0 (-100).
- `promise`: `{id, favor_cost, grievances_if_refused}`. Reference: 30 favor, 25 grievances.
- `alliance_type`: five types, levels 1 to 3 at 0, 320, 960 points, each level a list of effects.

### 3.10 Era score and moments

`moment`: `{id, era_score 0..5, scope: first_time | first_in_world, category}`. Golden age threshold 25, dark age below 25; past dark age -10, past golden age +5. Reference: 162 moment types; the world-first version of a moment is worth about 1 more. `commemoration`: 12 categories, each with a golden, a normal, and a dark age effect.

## 4. Reference numbers in one place

All listed in ledger pages 00 to 07. The most important are summarised in the sections above. The reference numbers are a *starting point*; the owner's design decisions (section 6) override them.

### 3.11 Rules config: the four design variables

The dataset carries a `rules_config` object. Each key is one design variable (full text in `variants.json` and ledger page 08):

| Variable (`rules_config` key) | Options | Current decision | What the checker enforces |
|---|---|---|---|
| `tree_layout` | `two_trees`, `one_tree` | `two_trees` | V1: in `two_trees` a node's `paid_with` equals its tree; in `one_tree` every node is tree `main` |
| `religion_mode` | `pressure_only`, `units_and_pressure`, `off` | `pressure_only` | V2: `pressure_only` needs beliefs, a religion, pressure settings, faith sinks and **no** faith units; `units_and_pressure` needs faith units; `off` needs none of it |
| `late_tail` | `keep`, `trim` (+ `min_unlocks_per_node`, `tail_eras`) | **`keep`**, minimum 1, tail of 1 era (owner decision, 2026-11-11) | V3: under `trim` every node unlocks at least the minimum; under `keep` the same holds **outside the last `tail_eras` eras**, so thin nodes can trail the tree but never appear in the middle |
| `great_person_pool` | `shared_finite`, `personal` | `shared_finite` | V4: each great person has `max_claims = 1` (shared) or `null` (personal) |

How to play with a variable: change its value in a copy of the dataset, run `python tools/schemacheck.py <file>`, read what must change, change it, then playtest and compare the metrics listed in `variants.json`.

## 5. Validation rules (these are tested)

Structural rules (codes R1 to R15), run by `tools/schemacheck.py`:

| Code | Rule |
|---|---|
| R1 | Every `id` is unique across the dataset |
| R2 | Node `requires` exist, stay inside one tree, and have no cycles |
| R3 | A node requires only nodes in the **same or the previous era** (no link skips an era). Reference: 0 of 95 tech links and 0 of 78 civic links skip |
| R4 | A node has at most 4 requirements (reference: techs up to 4, civics up to 2) |
| R5 | Costs never fall as era rises, inside a tree |
| R6 | `boost.percent` is 0 to 100; the family is from the closed list; the trigger kind exists and belongs to that family |
| R7 | Every reference (`requires_node`, `district`, `owner`, `when`, effect ids, classes, eras) resolves |
| R8 | Every effect kind, scope, requirement kind, belief class, card slot is in `enums.json` |
| R9 | Every government lists all four slot types; total slots strictly rise with tier |
| R10 | Meters and adjacency rules use known yields and cost models |
| R11 | **Unlock consistency:** each unlocked id exists in the section its type names; each entity is unlocked by exactly one node; that node equals the entity's `requires_node` (and the reverse) |
| R12 | **Card fits slot:** a card's effect kinds must be allowed in its slot (`slot_allowed_effect_kinds`; wildcard allows any) |
| R13 | **Adjacency selectors resolve:** terrain, feature, improvement, resource class, district named in a neighbor selector exist |
| R14 | Condition requirements reference real ids; conditions that nest (`set_is_met`) do not loop |
| R15 | A node with no boost is only allowed in the first era, or, under `late_tail = keep`, as a pure tail node (no unlocks, in the last `tail_eras` eras). The reference game left 11 late nodes without one; this keeps that to the tail |

Variable rules: V0 (config values are valid options) and V1 to V4 (section 3.11).

R11 to R15 are new in v0.2: R11, R12 and R13 were the three "not yet checked" rules from v0.1, and R14 and R15 were added while building the extended example.

## 6. Design decisions, in the ledger's keep / change / cut language

| Decision | Status | Why |
|---|---|---|
| One meter system | **Keep** | Same shape on five pages |
| Districts spend land, adjacency pays | **Keep** (9/10) | The placement puzzle |
| Boosts reward map acts | **Keep, widen triggers** (9/10) | Two thirds of reference triggers are "build or own"; the example uses six families: own, chain, combat, diplomacy and trade, explore, religion |
| Two trees vs. one | **Decided: `two_trees`** (8/10) | Contrast in shape is a strength; one tree is a config switch |
| 24 effect kinds, 15 requirement kinds | **Keep as the closed list** | Covers the reference game |
| Policy cards repeated per class per era | **Change**: store once | Example: one card, one effect row with a class list and an era list |
| Belief wrappers | **Change**: condition on the inner effect | Example beliefs have no wrapper rows |
| Government = fixed bonus + slots | **Keep** (8/10) | Editable ruleset layer; slots rise with tier (R9) |
| Great-person pool | **Decided: `shared_finite`** (7/10) | Rival communities exist; `personal` is one switch away |
| Religion | **Decided: `pressure_only`** (7/10) | Keep the belief sentence and spread by pressure; drop the unit layer |
| Thin late tail | **Decided by the owner: `keep`** (6/10; my pick was `trim`, 8/10) | Thin nodes trail the tree (V3, R15) and may carry their own effect; trim is one switch away |
| Unit unlocks in tech nodes | **Keep** | 45 of 77 reference techs unlock units |

## 7. What this draft does not cover

Per-unit stat sheet and promotions in detail; city-state and envoy rules; governors; espionage; barbarians; climate; victory conditions; combat formula as data (only the constants are listed); a few `faith_sinks` details (price rules); save-game format; anything about rendering or the engine (Phase 6).
