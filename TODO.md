# CivLayer TODO

Work top to bottom. Each phase ends with a test; don't start the next phase until it passes.
Details live in `SPEC.md`. Mod names, DLC needs, and conflicts live in `docs/civ6-mod-list.md`.

Legend: **[You]** needs you at your computer or in the game. **[Claude]** a Claude Code session can do it. **[Both]** Claude prepares, you test.

---

## Phase 0 · Setup

- [ ] **[You]** Check owned DLC in Civ 6 → Additional Content. Record it in `docs/dlc-owned.md`: Rise and Fall, Gathering Storm, New Frontier Pass, Leader Pass, and the six civ packs Civilizations Expanded needs.
- [ ] **[You]** Confirm your OS and the real paths for Workshop mods, Mods folder, Logs, and the debug database (SPEC section 5).
- [ ] **[You]** Get exact names and links for the unnamed mods (candidates in `docs/mod-candidates.md`; confirm against the videos) from each video's description: #7 city-state quests, #8 camera, #9 policy reminder, #10 repeat projects, Reindeer, and Workable 4th Ring.
- [ ] **[Claude]** Update `docs/civ6-mod-list.md` with the confirmed names and drop any mod your DLC can't support.
- [ ] **[You]** Decide: CQUI or Concise UI. Civilizations Expanded or Better Balanced Game. Record in SPEC section 11.
- [ ] **[You]** Create a private GitHub repo and push this starter folder.
- [ ] **[You]** Link this chat to your computer in the Claude desktop app, or plan to zip and attach mod folders.
- [ ] **[You]** Install Python 3.11+, Git, DB Browser for SQLite.

**Test:** `docs/dlc-owned.md` is filled in and every mod in the list has a confirmed Workshop link.

## Phase 1 · Baseline (mods as they are)

- [ ] **[You]** Subscribe to the final mod list. Install in the order in `docs/civ6-mod-list.md` Part 2.
- [ ] **[You]** Run the smoke test (SPEC section 7) after each group. Note what breaks.
  - Group 1 (UI: CQUI, RMT, Enhanced Camera): passed 2026-11-08 (`docs/playtests/001-ui-group.md`). Pinned policy popup check passed in group 2.
  - Group 2 (Repeat Project, Movable Districts): passed 2026-11-09 (`docs/playtests/002-group2.md`). All five mods kept active.
- [ ] **[You]** Attach the four log files from a clean run.
- [ ] **[Claude]** Write `docs/playtests/000-baseline.md`: what works, what breaks, which log errors come from which mod.
- [ ] **[You]** Start a **wall list**: changes you want that no mod makes. Add to it all project long.

**Test:** you know which mods break with which, from real logs, not just research.

## Phase 2 · Tools and inventory

- [ ] **[Claude]** Copy each mod's Workshop folder into `vendor/<workshop-id>-<name>/`. Add `vendor/` to `.gitignore`.
- [ ] **[Claude]** Write `tools/inventory.py` → `docs/inventory.md`.
- [ ] **[Claude]** Write `tools/conflicts.py` → `docs/conflicts.md`.
- [ ] **[Claude]** Write `tools/logtriage.py`, `tools/sqlcheck.py`, `tools/deploy.py`.
  - Early start (owner approved, ahead of phase): `logtriage.py` and `deploy.py` written with tests on sample data. Not yet run on real logs or a real Mods folder. `sqlcheck.py` still to do.
- [ ] **[Claude]** Add `pytest` tests for each tool, plus `luacheck` and XML lint.
- [ ] **[Claude]** Write `CREDITS.md` with author, link, and license status for each mod.
- [ ] **[Both]** Compare `docs/conflicts.md` against the Phase 1 baseline. Every real breakage should appear in the list.

**Test:** `conflicts.md` lists every file replaced by two or more mods, and each Phase 1 breakage maps to an entry.

## Phase 3 · Compatibility patch (patch mode)

- [ ] **[Claude]** Create `mod/CivLayer/CivLayer.modinfo` with one fixed GUID, a high LoadOrder, and DLC Criteria.
- [ ] **[Claude]** Deploy an empty CivLayer. **[You]** Smoke test: game loads with it on.
- [ ] Resolve conflicts one at a time, highest risk first:
  - [ ] **[Both]** Movable Districts + Repeat Project (production panel).
  - [ ] **[Both]** Workable 4th Ring + city panel mods, including CQUI.
  - [ ] **[Both]** Workable 4th Ring + Movable Districts: can a district move into the 4th ring?
  - [ ] **[Both]** Resource mods together, plus Monopolies and Corporations if owned.
  - [ ] **[Both]** Anything else in `docs/conflicts.md`.
- [ ] **[Claude]** After each fix, update `docs/conflicts.md` with the fix and the test result.

**Test:** every mod on the list is enabled at once, a 50-turn game runs with no new log errors, and the save reloads.

## Phase 4 · Absorb mods (merge mode)

Only for mods worth it: abandoned, badly conflicting, or ones you want to customize. One per commit.

- [ ] **[You]** Pick the first mod to absorb.
- [ ] **[Claude]** Copy it under `Data/absorbed/<mod>/` (and `UI/` if needed), credit it, disable the original.
- [ ] **[You]** Smoke test with the original off and CivLayer on.
- [ ] Repeat per mod. Track absorbed mods in `CREDITS.md`.

**Test:** with absorbed originals disabled, the game plays the same as in Phase 3.

## Phase 5 · Your customizations

- [ ] **[You]** Pick the top three items from the wall list.
- [ ] **[Claude]** For each: write a ledger entry first (design decision), then build it in `Data/custom/` or `Scripts/`, with `CL_` prefixes.
- [ ] **[You]** Playtest each one alone before stacking the next.

**Test:** each customization works, and its ledger page explains why it exists.

## Phase 6 · Rule ledger and handoff to your own game

- [ ] **[Claude]** Draft one `docs/ledger/` page per system: world, cities, economy, progress, units, AI, interface.
- [ ] **[You]** Fill in a design decision on every page: keep, change, cut, or replace.
- [ ] **[Both]** Redesign pass: one data schema for your own game, in your own terms.
- [ ] **[Claude]** Write the starter spec for the Unity project (rules engine apart from the view, data-driven content, headless sim). Follow the mastery map's Phase 3.

**Test:** someone could build one system of your game from its ledger page alone, with no Civ 6 code.

---

## Backlog

- Far-future mode: Rebuild-style community turns with first-person missions. Decide permadeath and whether it shares the tile map.
- Extra mods from Part 3 of the mod list: Real Strategy, Detailed Map Tacks, Global Relations Panel, Enhanced Mod Manager.
- Multiplayer: only after the single-player layer is stable.
