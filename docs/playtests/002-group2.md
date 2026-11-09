# 002 · Group 2 (Repeat Project + Movable Districts on top of the UI group)

- **Date:** 2026-11-09
- **Mods enabled:** CQUI (2115302648), Radial Measuring Tool (1628605090), Enhanced Camera (2484412297), Repeat Project (1505351262), Movable Districts (2683624437)
- **Setup:** Gathering Storm rules. Played as owner (Washington city, Encampment built).
- **Logs:** not received yet. Triage pending.

## Owner-reported results (in progress)

| # | Check | Result |
|---|---|---|
| 1 | Production panel opens, CQUI layout intact | Looks fine (screenshot). |
| 2 | Repeat Project | **Works.** A 3-turn Encampment project auto-restarted when it finished. No button; the mod is automatic. |
| 3 | Movable Districts: Move button | **Present.** It is a gear icon on the district tile, shown only while the city's production panel is open. A red "!" badge showed on it; tooltip text not yet reported. The move itself is not tested yet. |
| 4 | Both mods at once | Both active in the same game. Move gear still shows with Repeat Project installed. |
| 5 | CQUI policy popup (pinned from 001) | Not tested yet. |
| 6 | Save, reload, one turn, exit | Not done yet. |

## Open issues

- **CQUI Options button.** The owner saw a blank, unlabeled bar in the Options menu that did nothing on click. Not yet reproduced or explained. Possible workaround: the CQUI icon above the minimap. Need the logs and to know whether this also happens with only the UI group enabled (it was not reported in 001, but 001 did not look for it).
- **Red "!" on the Move gear.** Probably "can't afford" but unconfirmed. Need the tooltip text and gold balance.
- **Move not yet tested,** and "buildings stay intact" needs a district that has a building.

## Notes

- Earlier guess that the Move button was missing from the production panel was wrong: the mod's button is the gear on the tile.
- Earlier test script said Repeat Project "has a repeat option." It has no option; it repeats automatically.
