# CivLayer: Spec and Tech Stack

**Working name:** CivLayer (rename any time; see "Naming" below).
**Companion files:** `CLAUDE.md` (how Claude Code works in this repo), `TODO.md` (the checklist), `docs/civ6-mod-list.md` (the mods, their DLC needs, and known conflicts).

---

## 1. Goal

Build one mod layer on top of Civilization VI that:

1. Combines the best community mods into a single setup that loads cleanly together.
2. Adds your own customizations on top.
3. Records every rule it touches in your own words, so the layer becomes the design spec for your own tile-based civ game later.

The end goal is the third point. The first two are how you learn the rules well enough to rebuild them.

## 2. Non-goals (for now)

- Editing or decompiling the Civ 6 game engine (the C++ binaries). The layer only uses the official mod system: XML, SQL, Lua and `.modinfo`.
- Publishing the combined mod. It stays private until every included mod's author has given permission (see section 9).
- Multiplayer support. Single-player first; Movable Districts already has reported multiplayer desyncs.
- Building the standalone game. That starts only after the ledger (section 8) is complete enough, and it follows the clean-room rule.

## 3. Layer architecture

The game loads in stacked layers. Each layer may only depend on the ones beneath it.

| Layer | What it is | Who edits it |
|---|---|---|
| **L0 · Base game + DLC** | Civ 6 plus whichever expansions and packs you own. | Nobody. Read-only reference. |
| **L1 · Community mods** | The original mods, unchanged, as installed from Steam Workshop. Copies live in `vendor/` for reading only. | Nobody. Never edit `vendor/`. |
| **L2 · Compatibility patch** | `mod/CivLayer/` in patch mode: loads last and fixes only the conflicts between L1 mods. | Claude Code, with your review. |
| **L3 · Absorbed mods** | L1 mods whose features have been merged into CivLayer, so the original can be turned off. | Claude Code, one mod at a time. |
| **L4 · Your customizations** | Your own rules, units, and tweaks. Lives in its own folders inside CivLayer. | You and Claude Code. |

### Two operating modes

- **Patch mode (start here, rated 8/10):** keep every L1 mod enabled and installed from Workshop. CivLayer loads last and only fixes conflicts. You keep the mods' own updates.
- **Merge mode (later, rated 5/10 as a first step):** absorb a mod into CivLayer, then disable the original. Do this only for mods that are abandoned, conflict badly, or that you want to customize deeply.

Move from patch to merge one mod at a time. Never merge more than one mod per change.

## 4. Repo layout

```
civ-layer/
  CLAUDE.md               Claude Code instructions
  SPEC.md                 This file
  TODO.md                 Phased checklist
  CREDITS.md              Every mod used or absorbed, with author and link
  docs/
    civ6-mod-list.md      The 10 mods, extras, DLC needs, conflicts
    dlc-owned.md          What you actually own (filled in after checking)
    inventory.md          Generated: every file each mod adds or replaces
    conflicts.md          Generated + hand notes: every clash and its fix
    ledger/               Rule ledger, one page per game system
    playtests/            One note per playtest session
  vendor/                 Read-only copies of Workshop mods (gitignored)
    <workshop-id>-<name>/
  mod/CivLayer/           The mod the game loads
    CivLayer.modinfo
    Data/                 SQL and XML gameplay changes
      patch/              Conflict fixes (patch mode)
      absorbed/<mod>/     Merged mods (merge mode)
      custom/             Your own changes (L4)
    Text/                 Display text (XML), en_US
    UI/                   Merged or replaced UI Lua and XML
    Scripts/              Gameplay Lua scripts
  tools/                  Python helpers (section 6)
  tests/                  Tests for the tools and data checks
```

## 5. Tech stack

### Inside the game (what the mod is made of)

| Piece | Use | Notes |
|---|---|---|
| **SQLite** | The gameplay database the game builds at load time. | Every unit, building, yield and modifier is a table row. |
| **SQL** | Preferred way to change gameplay data. | Can be checked against the debug database before you launch the game. |
| **XML** | Alternative data format; required for text and `.modinfo`. | Same effect as SQL for data. |
| **Lua** | Live rules (gameplay scripts) and all UI screens. | Civ 6 uses a Lua 5.1-based runtime. Verify before using newer syntax. |
| **`.modinfo`** | The manifest: what files load, in what order, under what conditions. | Uses action types such as `UpdateDatabase`, `UpdateText`, `ImportFiles`, `ReplaceUIScript`, `AddUserInterfaces`, `AddGameplayScripts`. |
| **Criteria** | Load a file only when a condition is true. | Used to gate DLC content, e.g. load Gathering Storm pieces only when the `RULESET_EXPANSION_2` ruleset is in use. |
| **LoadOrder** | Property that controls which file loads later and wins. | CivLayer's patch files use a high LoadOrder so they load after every L1 mod. |

### On your computer

| Tool | Use |
|---|---|
| Civ 6 (Steam) | The test harness. Only you can run it. |
| DB Browser for SQLite | Inspect the debug gameplay database by hand. |
| VS Code (or any editor) | Read and edit files. |
| Git + GitHub (private repo) | History, one change per commit, easy rollback. |
| Civ 6 SDK / ModBuddy | Optional. Not needed: the mod folder works when copied into the Mods folder. |

### Claude Code tooling (in `tools/`)

| Tool | Language | What it does |
|---|---|---|
| `inventory.py` | Python 3.11+, `lxml` | Reads every `.modinfo` in `vendor/` and lists what each mod adds, replaces, and in what order. Writes `docs/inventory.md`. |
| `conflicts.py` | Python | Finds files replaced by more than one mod, rows edited by more than one mod, and duplicate type names. Writes `docs/conflicts.md`. |
| `sqlcheck.py` | Python `sqlite3` | Runs CivLayer's SQL against a copy of the debug database to catch errors before launch. |
| `logtriage.py` | Python | Reads `Database.log`, `Modding.log`, `Lua.log`, and `GameEffects.log`, and summarizes errors by mod. |
| `deploy.py` | Python | Copies `mod/CivLayer/` into the game's Mods folder. |
| Lint | `luacheck` (Lua), `xmllint` (XML) | Syntax checks before every deploy. |
| Tests | `pytest` | Tests for the tools themselves and for data rules (e.g. no duplicate types). |

### Key paths (Windows defaults, confirm on your machine)

| What | Path |
|---|---|
| Workshop mods | `C:\Program Files (x86)\Steam\steamapps\workshop\content\289070\<workshop-id>\` |
| Local Mods folder | `Documents\My Games\Sid Meier's Civilization VI\Mods\` |
| Logs | `Documents\My Games\Sid Meier's Civilization VI\Logs\` |
| Debug gameplay DB | `Documents\My Games\Sid Meier's Civilization VI\Cache\DebugGameplay.sqlite` (verify location) |
| Base game data | `...\steamapps\common\Sid Meier's Civilization VI\Base\Assets\Gameplay\Data\` |
| DLC data | `...\Sid Meier's Civilization VI\DLC\<pack>\` |

Claude Code reaches these through a chat linked to your computer, or you zip and attach the folders.

### Later: your own game (Phase 6)

| Piece | Choice |
|---|---|
| Engine | Unity (C#). Godot is the fallback. |
| Rules engine | Plain C# with no Unity objects, so it runs headless and can swap engines. |
| Content data | JSON or SQLite tables, designed from the ledger, not copied from Civ 6. |
| Tests | Headless 100-turn simulations, deterministic seeds. |

## 6. Merge rules

1. **Never edit `vendor/`.** It is read-only reference.
2. **Data conflicts:** when two mods change the same row, the patch file picks one value (or a new one) and states why in `docs/conflicts.md`.
3. **UI conflicts:** when two mods replace the same UI file, the merged version goes in `mod/CivLayer/UI/`, with a header comment listing which mods it combines, which lines came from which mod, and the base file version.
4. **New types:** every new type CivLayer creates uses the `CL_` prefix (e.g. `UNIT_CL_SCOUT_RIDER`), so it can never collide with a game or mod type.
5. **Absorbing a mod:** copy its files under `Data/absorbed/<mod>/`, remove the original from the enabled list, and run the full smoke test. One mod per commit.
6. **DLC gating:** anything that needs an expansion or pack gets a Criteria entry, so the layer still loads if you don't own that DLC.
7. **Every change cites its source:** a mod name and Workshop ID, the ledger page, or "custom".

## 7. Testing protocol

Claude Code can't run Civ 6. You are the tester; Claude does everything before and after.

**Before each playtest (Claude):** lint, run `sqlcheck.py`, deploy, and write a short test script: which civ, map, speed, and what to check.

**Smoke test (you, 10 to 15 minutes):**
1. The game reaches the main menu with CivLayer and all L1 mods enabled.
2. A new game starts without bouncing to the menu.
3. Play 10 turns: found a city, build something, open each changed screen.
4. Check every feature listed in the test script.
5. Save, quit to menu, reload the save.

**After each playtest (you, then Claude):** you attach the four log files and a note on what you saw. Claude runs `logtriage.py`, files the note in `docs/playtests/`, and fixes what broke.

**Done means:** no new errors in any log, every listed feature works, and the save reloads.

## 8. Rule ledger (the bridge to your own game)

One Markdown page per system in `docs/ledger/`: world and tiles, cities, economy, progress, units and combat, AI, interface. Each page records:

- **What the rule does**, in your own words.
- **Where it lives** (table names, Lua file names), for reference only.
- **What the mods changed** and why players wanted that change.
- **Your design decision:** keep, change, cut, or replace, and the reason.
- **Open questions.**

The ledger describes rules as ideas. It never contains copied game code, art, or text. That is the clean-room line your own game is built from.

## 9. Legal and credit rules

- This is not legal advice.
- Mods have no license unless the author attaches one. Using combined mods privately is the normal community practice. **Publishing requires each included author's permission and credit.**
- CQUI is MIT-licensed and can be included with its license and attribution.
- `CREDITS.md` lists every mod used in patch mode or absorbed, with its author, Workshop link, and license or permission status.
- The standalone game (Phase 6) uses none of Civ 6's or any mod's code, art, text, or names.

## 10. Naming

- **Mod name:** CivLayer (placeholder).
- **Type prefix:** `CL_`.
- **Mod ID:** a single GUID generated once in `CivLayer.modinfo`. Never change it, or saved games lose the mod.

## 11. Open decisions

| Decision | Options | Default until you decide |
|---|---|---|
| Which DLC you own | Fill in `docs/dlc-owned.md` | Assume base game + Gathering Storm |
| CQUI or Concise UI | **Decided: CQUI** (installed). #7 and #9 on hold: CQUI covers them. | CQUI |
| Civilizations Expanded or Better Balanced Game | Pick one civ rework | Civilizations Expanded, if DLC allows |
| Your first customizations | From your Phase 1 wall list | None yet |
| Permadeath and map questions for the far-future mode | See the mastery map | Deferred |
