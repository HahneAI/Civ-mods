# Rule ledger: where we left off

Source: custom. Updated 2026-11-10 (end of the second design push: variables and extended example). The ledger records how Civ 6's systems work, in plain words, as the design reference for the owner's own tile game (CLAUDE.md, "Long-term direction"). No copied text, code, or names (hard rule 8).

## Pages

| Page | System | State |
|---|---|---|
| `00-base-math.md` | tiles, citizens, food, growth, housing, amenities, borders | numbers confirmed from the game database |
| `01-units-combat.md` | units, damage formula, terrain bonuses, healing, cities | confirmed; wounded-unit rule and all 159 units' stats not written up |
| `02-trade-diplomacy.md` | trade routes, relationship ladder, alliances, grievances | confirmed; relationship score per action missing |
| `03-cities-districts.md` | founding, districts, adjacency, buildings, loyalty | confirmed and complete for adjacency |
| `04-tech-civic-trees.md` | both trees: costs, shape, boosts, eras | confirmed; fully analyzed (shape, cost curve, boosts) |
| `05-governments-great-people.md` | governments, slots, cards, great people | confirmed; card effects only partly unpacked |
| `06-religion-faith.md` | pantheon, beliefs, spread, faith units | confirmed; belief effects unpacked on page 07 |
| `07-effects-system.md` | how every effect is stored as data; unlocks; era score | new; beliefs, conditions and moments done |
| `08-design-variables.md` | the four open design questions as switches, with decisions and how to test | new; decisions made, not yet playtested |
| `db-check.md` | how to read the game database (one click) | rounds 1 to 4 done |
| `../schema/playground.html` | interactive page for the four design variables, with rule checks and a toy simulation (open in a browser) | new |

## How the numbers were obtained

The owner ran `tools/dbdump.py` on their PC (read-only, one file out, `db-results.md`, never committed). Four rounds were read: economy and combat, adjacency and buildings, effects, and unwrapped effects. The first draft pages used web numbers; several were wrong and are corrected (tech costs, housing stop point, city-center yield, wounded units, boost size).

## Where we left off

**Done:** pages 00 to 08, the one-click dump tool, and a draft data schema (`../schema/`) with an extended example, a rule checker (`tools/schemacheck.py`), and 53 tests in total for schema and dump.

**Known gaps** (each is tagged `[verify]` or listed under "Open items" on its page):

- Policy card effects after unwrapping (only beliefs were unwrapped).
- Full stat sheet for all 159 units, unit promotions in detail, unit upgrade paths.
- What each moment trigger counts as (era score), commemoration bonus text.
- Relationship score change per action; the full agenda list (112); casus belli.
- Envoy thresholds and city-state bonus effects; espionage and governor details; patronage prices.
- Route capacity sources; tourism and culture victory rules; the other victory types.
- The government table and the effect rows disagree on which tier gets which of two bonuses (page 07, Step 4).
- Housing between -1 and -3, exact aqueduct rule; gold buy price formulas (engine-side).

**Next steps, in order:**

1. Round 5 dump (optional): units in full, promotions, requirements per card, moment triggers. Needs the owner to rerun `tools/dbdump.py` (steps in `db-check.md`).
2. Fill the gaps above, one page at a time.
3. The four owner decisions are now made as switchable variables (page 08): two trees, pressure-only religion, every research node gives something, an unlock or a bonus effect (the owner's call, and the reference game does the same), shared great-person pool. They are starting points; the owner can flip any in `rules_config`. Playtest data will confirm or reverse them.
4. Playtest-based checks: the wounded-unit rule and a few `[approx]` values are quickest confirmed in a game, not in the database.

**Process notes for the next session:**

- The chat has no link to the owner's computer; databases come as attached files.
- Do not commit `db-results*.md` (git-ignored; it holds game data).
- Work on branch `claude/civ6-base-math-formulas-cpkfw7`; the owner merges into `version-control`. The last merge conflict was only the CLAUDE.md changelog.
- The owner's preferences: brief answers, ask before long answers, rate new ideas out of 10, say when unsure.
