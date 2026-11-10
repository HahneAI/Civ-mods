# Schema folder: where we left off

Source: custom. Updated 2026-11-10 (end of the first long design session).

## What is here

| File | What it is |
|---|---|
| `game-data-schema.md` | Draft v0.1 of the data shape for the owner's own game: types, fields, reference values, rules, keep/change/cut decisions |
| `enums.json` | The closed lists (yields, effect kinds, requirement kinds, scopes, ...). Edit here first |
| `example-data.json` | A tiny made-up dataset that follows the schema (placeholder names) |
| `../../tests/test_schema_example.py` | Checks the example against the validation rules (10 rules, section 5) |

Run the check with `pytest` from the repo root. `33 passed` at the time of writing.

## Status

**v0.1 draft, design only.** No engine code, no real content. Per CLAUDE.md, game-engine work waits for TODO Phase 6; this folder only fixes the shape of the data so the ledger can feed it later.

## Where we left off

1. The schema covers the economy, map, districts, trees, governments, cards, effects, religion, trade, diplomacy, and era score. It was drawn from ledger pages 00 to 07.
2. The example dataset has 4 nodes, 1 district, 1 building, 1 improvement, 1 government, 1 card, 2 effects, 1 condition. It is a skeleton, not a game.
3. **Open design questions for the owner** (details in section 6 of the schema):
   - one node type with a `tree` field (kept) or really two trees;
   - whether religion is a unit system or a cultural-influence layer;
   - whether to keep the thin late-game tail of nodes;
   - whether the great-person pool is shared (needs multiplayer).
4. **Next steps, in order:**
   1. Owner reviews section 6 and answers the open questions.
   2. Extend `example-data.json` to one full mini-era (about 10 nodes, 3 districts, 6 buildings, 6 cards) and add checks for the three "not yet checked" rules (schema section 5).
   3. Finish the ledger gaps (see `../ledger/README.md`), then add the missing types (units in full, city-states, governors, espionage, victory).
   4. Only at TODO Phase 6: decide where the engine lives and generate typed code (Unity/C# per SPEC section 5) from this schema.

## Rules for editing here

- Names stay generic. No Civ 6 or mod names, text, or art (hard rules 2 and 8).
- Reference numbers come from the ledger; if a ledger number changes, update the schema section that quotes it.
- Add a new effect kind or requirement kind to `enums.json` and the schema doc in the same commit.
