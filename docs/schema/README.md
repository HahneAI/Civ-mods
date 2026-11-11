# Schema folder: where we left off

Source: custom. Updated 2026-11-10 (end of the first long design session).

## What is here

| File | What it is |
|---|---|
| `game-data-schema.md` | Draft v0.2: types, fields, reference values, 20 rules, decisions |
| `enums.json` | The closed lists (yields, effect kinds, requirement kinds, scopes, slot rules, trigger kinds, ...). Edit here first |
| `variants.json` | The four design variables: options, current decision, rating, how to test, metrics |
| `example-data.json` | Extended mini-world following all four decisions (placeholder names) |
| `../../tools/schemacheck.py` | Checks a dataset against the rules; `python tools/schemacheck.py [file]` |
| `../../tests/test_schema_example.py` | 27 tests: the example passes and every rule and variable fails when broken |
| `../ledger/08-design-variables.md` | The same four variables in plain words, with evidence |
| `playground.html` | **Interactive playground**: open it in a browser (double-click). Left: the four variable switches, 15 "break it" switches, the node tree. Right: the 20 rules answering live. Also published as a private artifact |
| `playground.template.html`, `playground-check.js` | The parts the playground is built from (page, and a JavaScript copy of the checker plus the switch and break definitions) |
| `../../tools/build_playground.py` | Rebuilds `playground.html` from its parts: `python tools/build_playground.py` |
| `../../tests/test_playground.py` | Runs every switch and break through node and checks the JavaScript checker gives the same rule codes as the Python one |

Run everything with `pytest` from the repo root (61 passed at the time of writing; the playground parity tests need node and skip without it).

## Status

**v0.2 draft, design only.** No engine code, no real content. Per CLAUDE.md, game-engine work waits for TODO Phase 6; this folder only fixes the shape of the data so the ledger can feed it later.

## Where we left off

1. **The four open questions became switchable variables** in `rules_config`, with decisions made: `two_trees`, `pressure_only`, `keep` (the thin tail, **owner decision of 2026-11-11**, overriding my first pick of `trim`), `shared_finite`. Each has a checker rule (V1 to V4) and a metric list for playtests.
2. **The extended example** has 12 nodes (10 working nodes plus 2 tail nodes), 3 districts, 6 buildings, 6 cards, 3 governments, 4 beliefs, 4 great people, 17 effects and 7 conditions. It passes all rules. Of the two tail nodes, one is a pure prerequisite (culture) and one carries a small direct effect (science), to show both ways of ending a tree.
3. **Five new rules** (R11 to R15) replaced the three "not yet checked" ones from v0.1 and added two more found while building the example (a condition-nesting loop check, and "no boost only in the first era").
4. **What the schema still lacks:** full unit stats and promotions, city-states and envoys, governors, espionage, barbarians, victory conditions, price rules for faith spending, catch-up discounts for the shared pool, combat formula as data.

## The playground (how to use it)

1. Open `docs/schema/playground.html`, or the published artifact (private link: https://claude.ai/artifact/2wrH8dvTdMVQ2fTddPd7vK).
2. **Design variables** (top left): pick another option. With "Convert the data" on, the page rewrites the example to match, so only your breaks can fail. Turn it off to see the raw flip: what you would have to fix by hand.
3. **Break it**: switch on a damage. The switch says whether the expected rule caught it ("caught by R3") or stayed quiet (for example a faith unit is fine once religion uses units).
4. **The tree**: nodes are boxed by era; a red node is named by a failing rule. Click one for its cost, requirements, unlocks, boost and the rules naming it.
5. **Check your own dataset**: paste an edited `example-data.json` to check it as it stands.
6. Edit the page's parts (`playground.template.html`, `playground-check.js`, or the JSON files), then run `python tools/build_playground.py`. A test fails if the built page is stale.

When a rule changes in `tools/schemacheck.py`, change the same rule in `playground-check.js`; `tests/test_playground.py` will tell you if they drift.

## Next steps, in order

1. Owner reviews the four decisions in `variants.json` and flips any they disagree with (a one-word change in `rules_config`).
2. Extend the example by a fourth era and a second district per class, or add the missing types above. Add a rule whenever a new mistake is found.
3. Write a tiny non-engine simulator (a Python script over the dataset: grow a city, fill the meters, finish nodes) so the variable metrics can be measured without a game. This is the cheapest way to test the four variables before Phase 6.
4. Only at TODO Phase 6: decide where the engine lives and generate typed code (Unity/C# per SPEC section 5) from this schema.

## Rules for editing here

- Names stay generic. No Civ 6 or mod names, text, or art (hard rules 2 and 8).
- Reference numbers come from the ledger; if a ledger number changes, update the schema section that quotes it.
- Add a new effect kind or requirement kind to `enums.json` and the schema doc in the same commit.
