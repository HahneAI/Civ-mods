# CLAUDE.md

Instructions for Claude Code sessions in this repo.

## What this project is

CivLayer is one Civilization VI mod layer that combines community mods, adds the owner's own customizations, and records every rule in a ledger. The ledger later becomes the design spec for the owner's own tile-based civ game.

## Long-term direction (far down the line)

This repo will shift over time. Civ 6 modding is the first stage only. The real goal is the owner's own **tile-rendered civilization and community-building game**. The modded Civ 6 setup is the testbed for the owner's ideal design: play it, find what works, record it in the ledger.

- Phase 6 (TODO.md) is where the shift starts. The standalone game (Unity/C#, SPEC section 5) will live in this repo next to the mod, or move to its own repo. The owner decides when.
- "Reverse engineering" here means studying Civ 6's **rules and behavior** through the mod system and play, then rebuilding them in the owner's own terms. It does **not** mean decompiling or copying Civ 6 or mod code, art, text, or names (hard rules 2 and 8, SPEC section 9). The ledger is the clean-room wall between the two.
- Until Phase 6, write every ledger page and design note so it can later feed the new game: describe rules as ideas, flag the owner's design decisions, and note what to keep, change, cut, or replace.
- Don't start game-engine work early. Raise it only when the TODO reaches Phase 6 or the owner asks.

**Read before any work:**
1. `SPEC.md` — architecture, layers, rules, tech stack.
2. `TODO.md` — find the first unchecked item in the current phase.
3. `docs/civ6-mod-list.md` — the mods, DLC needs, and known conflicts.
4. `docs/dlc-owned.md` — what the owner actually has. If it's empty, ask before writing DLC-dependent code.

## How to work

- **Branch workflow:** work only on your chat's feature branch → owner merges it into `version-control` → once tests pass there, owner merges into `main`. Never push to `version-control` or `main` yourself. Each chat keeps its own feature branch unless told otherwise.
- Work the first unchecked TODO item in the current phase. Don't skip phases.
- One logical change per commit. Absorb at most one mod per commit.
- Check items off in `TODO.md` only after the owner confirms the playtest passed.
- When a session ends, update `TODO.md` and add one line to the changelog at the bottom of this file.

## Hard rules

1. **Never edit `vendor/`.** It holds read-only copies of Workshop mods.
2. **Never decompile or copy Civ 6 engine code.** Only use the mod system: XML, SQL, Lua, `.modinfo`.
3. **Every new type uses the `CL_` prefix.**
4. **Never change the mod GUID** in `CivLayer.modinfo`.
5. **Gate DLC content with Criteria** so the mod loads without that DLC.
6. **Cite the source of every change** in a file header or commit message: mod name + Workshop ID, ledger page, or "custom".
7. **Merged UI files** start with a header listing the combined mods and which lines came from which.
8. **No copied code, art, or text in `docs/ledger/`.** Describe rules in plain words.
9. **Don't publish** anything or push to a public repo. Publishing needs each author's permission (SPEC section 9).

## You can't run the game

The owner is the tester. For every change that needs testing:

1. Run lint, `tools/sqlcheck.py`, and the tests.
2. Deploy with `tools/deploy.py`.
3. Give the owner a short test script: civ, map size, speed, turns to play, and exactly what to check.
4. Ask for these logs afterward: `Database.log`, `Modding.log`, `Lua.log`, `GameEffects.log`.
5. Run `tools/logtriage.py`, file the result in `docs/playtests/`, and fix what broke.

Never say a change works until the owner confirms it in game.

## Commands

```
python tools/inventory.py           # rebuild docs/inventory.md from vendor/
python tools/conflicts.py           # rebuild docs/conflicts.md
python tools/sqlcheck.py            # test CivLayer SQL against the debug DB copy
python tools/logtriage.py <logdir>  # summarize game logs by mod
python tools/deploy.py              # copy mod/CivLayer into the game's Mods folder
python tools/dbdump.py              # read the debug DB, write db-results.md for the ledger
pytest                              # tool tests
luacheck mod/CivLayer               # Lua lint
```

These tools don't exist until TODO Phase 2 builds them.

## Reaching the owner's computer

- If this chat is linked to the owner's computer, use those tools to read Workshop folders and logs, and to deploy.
- If not, ask the owner to zip and attach the folders. Paths are in SPEC section 5.

## How the owner wants answers

- Brief and direct. Ask clarifying questions before long answers.
- Say "you're wrong" and explain when an assumption is weak.
- Rate new ideas out of 10, backed by a quick web search of what others have done.
- Say when you're unsure instead of guessing.
- Don't create large files unless asked.

## Changelog

- Repo created from starter: SPEC.md, TODO.md, CLAUDE.md.
- Added "Long-term direction" section: repo will later shift to the owner's own tile-rendered civ game.
- Added `docs/civ6-mod-list.md` (the 10 mods, DLC needs, conflicts, extras).
- Added `docs/dlc-owned.md` (from memory) and `docs/mod-candidates.md` (unconfirmed links for the unnamed mods).
- Built `tools/logtriage.py` and `tools/deploy.py` early, with pytest tests (owner approved bending the phase order for these two).
- Added branch workflow: feature branch → `version-control` → `main`; created `main` and `version-control`.
- Added from starter zip: `CREDITS.md` and empty folders (`docs/ledger`, `docs/playtests`, `mod/CivLayer/{Data,Scripts,Text,UI}`).
- Confirmed DLC from screenshots in `docs/dlc-owned.md`: both expansions, all six Civilizations Expanded packs, most of New Frontier Pass, full Leader Pass.
- Owner confirmed the DLC list is complete; Vietnam and Kublai Khan Pack not owned.
- Confirmed mod #4: Workable 4th Ring by PhantomJ_M (Workshop ID still TBD).
- UI group installed: CQUI (decided as UI base), Radial Measuring Tool, Enhanced Camera. #7 and #9 on hold (CQUI covers them). CREDITS.md started.
- First real logs (UI group): clean. Filed `docs/playtests/001-ui-group.md`; fixed logtriage attribution (look-ahead, Firaxis noise).
- UI group playtest passed; CQUI policy popup check pinned for a later run.
- Group 2 IDs confirmed from Workshop pages: Repeat Project (yamada, 1505351262), Movable Districts (wltk, 2683624437). Test pending.
- Group 2 partial results filed (`docs/playtests/002-group2.md`): Repeat Project works; Move gear present; logs pending; CQUI blank Options button open.
- Group 2 playtest PASSED (logs clean; Movable Districts and Repeat Project use AddUserInterfaces so no production panel clash). Five mods now active. Next: Workable 4th Ring (ID needed).
- Plan change: Real Strategy (AI) replaces Deity++; group 3 = Workable 4th Ring + Real Strategy. Deity++ on hold.
- Added ledger pages 00 (base math) and 01 (units and combat) plus `docs/ledger/db-check.md` (queries the owner runs to confirm numbers).
- Added ledger page 02 (trade and diplomacy).
- Added ledger page 03 (cities and districts).
- Added ledger pages 04 (tech and civic trees) and 05 (governments and great people).
- Added ledger page 06 (religion and faith) with a master map of all systems.
- Merged `version-control` into the feature branch (conflict was only the CLAUDE.md changelog; kept both sets).
- Built `tools/dbdump.py` (one-click read-only database check, output `db-results.md`, git-ignored) with tests; `docs/ledger/db-check.md` now leads with it.
- Round 1 database read (owner ran `dbdump.py`): ledger pages 00 to 06 updated with confirmed numbers; page 04 rewritten from real tree data; `dbdump.py` extended for a follow-up dump (adjacency, buildings, policies, great-person points).
- Round 2 database read: complete adjacency, building ladders, trade yields by district, diplomacy ladder, alliances, government bonuses, great-person points and religious units added to ledger pages 02, 03, 05, 06.
- `tools/dbdump.py` round 3: modifier digest (what policies, beliefs, buildings etc. do), all GlobalParameters, table catalog, extra systems.
- Round 3 database read: new ledger page 07 (effects system), unlock counts and era thresholds on page 04, resources and improvements on page 00; `dbdump.py` now resolves attach-modifier wrappers.
- `dbdump.py` round 4: condition-set digest, moments, era data, city-state bonuses, projects, unit upgrades and unit unlocks.
- Round 4 database read: page 07 extended (unlocks including units, resolved belief effects, condition sets, era-score moments, era data); corrected earlier claim that late techs unlock nothing.
