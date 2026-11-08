# 001 · UI group smoke test

- **Date:** 2026-11-08
- **Mods enabled:** CQUI (2115302648), Radial Measuring Tool (1628605090), Enhanced Camera (2484412297)
- **Setup:** Gathering Storm rules, 6 players, Continents map. Played, saved, reloaded.
- **Logs received:** Database.log, Modding.log, Lua.log. GameEffects.log was not written (it seems to need logging turned on; not needed yet).
- **Triage:** `python tools/logtriage.py <logdir>` run on 2026-11-08.

## Result from the logs: clean

| Source | Errors | Warnings | Verdict |
|---|---|---|---|
| CQUI | 1 | 0 | Harmless. Its manifest points to a Chinese text file that isn't shipped. Doesn't affect English. |
| Base game / DLC | 100 | 180 | Harmless Firaxis noise: duplicate text tags in promo and Hall of Fame files, missing Chinese translation files, two expansion gossip text files. None come from a mod. |
| Radial Measuring Tool | 0 | 0 | Loads on new game and on reload. |
| Enhanced Camera | 0 | 0 | Loads (no Lua; it's a data-only mod). |

- **Lua.log:** no runtime errors. CQUI and RMT both start up on the new game and again after the save reload, so the reload worked.
- **Mod load order:** all three mods are installed and enabled per Modding.log; the game reported they can run together.

## Owner's in-game checks

_Waiting for the owner's notes._

- [ ] CQUI city panel (Civ 5-style layout)
- [ ] CQUI city-state quests in the city-state panel
- [ ] CQUI policy popup after a civic
- [ ] RMT button and radius display
- [ ] Enhanced Camera: zoom range wider than normal
- [ ] Save, reload, one more turn

## Tool fixes from this run

`logtriage.py` first put 96 base-game errors under "unknown source". Two fixes:
1. Database.log names the file a few lines **after** the error, so the tool now looks ahead as well as back.
2. Known Firaxis noise (promo text, Hall of Fame text, gossip text, missing Chinese translations, "Service missing") is now labeled base game.
