# 003 · Group 3 (Workable 4th Ring + Real Strategy on top of the five active mods)

- **Status:** in progress. Logs and check results not received yet.
- **Mods enabled:** the five from 002, plus Workable 4th Ring (3220078106) and Real Strategy (AI) (1617282434).
- **Test script:** see the chat message of 2026-11-11 (6 checks: load and AI turn times, 4th ring work, CQUI citizen view, Movable Districts into ring 4, AI city placement, save/resume). To be copied here when results come in.

## UI bugs reported by the owner during this test (2026-11-13)

| # | Bug | Notes |
|---|---|---|
| 1 | **Great People screen turns transparent** as the owner scrolls right | Cause unknown. |
| 2 | **Top-left tabs** (science, culture and the other menu buttons) **sometimes jump up and sit over the top-left production numbers** | Intermittent. Cause unknown. |

### What we know

- From the 002 logs: CQUI replaces the **TopPanel, LaunchBar, PartialScreenHooks, TechTree and CivicsTree** UI files, and imports its own Great People popup files. Gathering Storm replaces several of the same files, so CQUI's versions win. Bug 2 sits in exactly that area, so CQUI is the first suspect.
- CQUI's build is from March 2021 (`v1.0.11.16`), older than later game updates. That is a guess at a contributing factor, not a finding.
- Neither Real Strategy (AI and Lua only, per its page) nor Workable 4th Ring is expected to touch these screens. Not confirmed for Workable 4th Ring.
- No matching report was found online. The nearest was a base-game fix for the Great People panel on short screens (800 or 768 px tall).

### To isolate

1. Did either bug happen in the UI group or group 2 tests (before 4th Ring and Real Strategy were added)? 
2. Do they happen with **only CQUI** enabled?
3. Screen resolution and UI scale.
4. A screenshot of each bug.
