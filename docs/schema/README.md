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

Run everything with `pytest` from the repo root (53 passed at the time of writing).

## Status

**v0.2 draft, design only.** No engine code, no real content. Per CLAUDE.md, game-engine work waits for TODO Phase 6; this folder only fixes the shape of the data so the ledger can feed it later.

## Where we left off

1. **The four open questions became switchable variables** in `rules_config`, with decisions made: `two_trees`, `pressure_only`, `trim` (minimum 1), `shared_finite`. Each has a checker rule (V1 to V4) and a metric list for playtests.
2. **The extended example** has 10 nodes, 3 districts, 6 buildings, 6 cards, 3 governments, 4 beliefs, 4 great people, 16 effects and 7 conditions. It passes all rules.
3. **Five new rules** (R11 to R15) replaced the three "not yet checked" ones from v0.1 and added two more found while building the example (a condition-nesting loop check, and "no boost only in the first era").
4. **What the schema still lacks:** full unit stats and promotions, city-states and envoys, governors, espionage, barbarians, victory conditions, price rules for faith spending, catch-up discounts for the shared pool, combat formula as data.

## Next steps, in order

1. Owner reviews the four decisions in `variants.json` and flips any they disagree with (a one-word change in `rules_config`).
2. Extend the example by a fourth era and a second district per class, or add the missing types above. Add a rule whenever a new mistake is found.
3. Write a tiny non-engine simulator (a Python script over the dataset: grow a city, fill the meters, finish nodes) so the variable metrics can be measured without a game. This is the cheapest way to test the four variables before Phase 6.
4. Only at TODO Phase 6: decide where the engine lives and generate typed code (Unity/C# per SPEC section 5) from this schema.

## Rules for editing here

- Names stay generic. No Civ 6 or mod names, text, or art (hard rules 2 and 8).
- Reference numbers come from the ledger; if a ledger number changes, update the schema section that quotes it.
- Add a new effect kind or requirement kind to `enums.json` and the schema doc in the same commit.
