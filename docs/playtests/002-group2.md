# 002 · Group 2 (Repeat Project + Movable Districts on top of the UI group)

- **Date:** 2026-11-09
- **Mods enabled:** CQUI (2115302648), Radial Measuring Tool (1628605090), Enhanced Camera (2484412297), Repeat Project (1505351262), Movable Districts (2683624437)
- **Setup:** Gathering Storm rules, 6 players, Continents map. Heroes and Legends game mode was ON in this game (it was off in 001). Played, saved, quit to menu, resumed.
- **Logs:** Database.log, Modding.log, Lua.log. GameEffects.log is not written.
- **Result: PASSED. Keep all five mods enabled.**

## Owner-confirmed in game

| # | Check | Result |
|---|---|---|
| 1 | Production panel opens, CQUI layout intact | Pass |
| 2 | Repeat Project | Pass. A 3-turn Encampment project restarted by itself. No button; the mod is automatic. |
| 3 | Movable Districts | Pass. The Move button is a gear icon on the district tile, shown while the city's production panel is open. An Encampment was moved "flawlessly". |
| 4 | Both mods at once | Pass |
| 5 | CQUI policy popup (pinned from 001) | Pass |
| 6 | Save, reload, one turn, exit | Pass |

## What the logs show

- All five mods are installed and enabled; the game loaded the same set on the new game and again on resume.
- **Why the production-panel conflict did not happen:** Movable Districts (`md_interface`) and Repeat Project (`CMR_RepeatProject_UI`) both use `AddUserInterfaces`, which adds their own UI contexts. They do not replace the production panel file. Only the game's own Heroes mode and CQUI replace it. So there is nothing for the three to fight over.
- Movable Districts registers one gameplay script (`md_helper.lua`) that loads cleanly on both loads.
- No Lua errors from Movable Districts, Repeat Project, Radial Measuring Tool or Enhanced Camera.

## Errors and warnings (all minor)

| Item | Count | Source | Verdict |
|---|---|---|---|
| Duplicate text tags, missing Chinese files, Gossip text | ~100 errors, ~180 warnings | Firaxis files | Same as 001; harmless. |
| `MinimapPanel: ERROR: SetModLens - Given lens 'NONE' has no entry` | 6 | Lua.log, right after opening the resource lens | Almost certainly CQUI's minimap lens code (the resource lens comes from CQUI). Cosmetic, no visible effect reported. Not confirmed. |
| `UpdateDatabase - Error Loading SQL` for `../cqui_settings_local.sql` | 1 per load | CQUI | Expected. That optional file doesn't exist. It is where personal CQUI defaults would go. |
| `Error Loading XML` in Rulers of the Sahara and Catherine de Medici data files | 3 per load | Firaxis DLC | Harmless; appears without mods. |

## Still open

- **CQUI blank Options button** (owner report, 2026-11-09): not explained by the logs. Need to know whether the CQUI icon above the minimap opens a settings screen. Low priority while CQUI works.
- **`SetModLens 'NONE'` error:** watch whether it grows or shows visible symptoms.

## Tool note

`logtriage.py` lists the `SetModLens` error under "unknown source". Lua.log lines carry no path, so the tool can only guess by the log prefix. Possible later improvement: map the `MinimapPanel:` and `ModLens_` prefixes to CQUI.
