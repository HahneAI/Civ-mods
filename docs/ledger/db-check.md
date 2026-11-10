# Database Check: How to Replace Guesses with Real Numbers

Source: custom. Applies to every ledger page. Claude cannot reach the game files from the cloud chat, so the owner runs these once and pastes the rows into the chat.

**Goal:** every `[approx]` / `[verify]` tag on a ledger page becomes a `[sure]` number read from the game's own data.

## Setup (once, about 5 minutes)

1. Copy `DebugGameplay.sqlite` to a safe spot. Path (verify): `Documents\My Games\Sid Meier's Civilization VI\Cache\DebugGameplay.sqlite`. Work on the copy, never the original.
2. Open the copy in DB Browser for SQLite. Open the "Execute SQL" tab.
3. Run one query at a time. Click the grid, select all, copy, and paste the rows into the chat. A screenshot also works.
4. Claude updates the page and changes the tag.

If a query errors with "no such table/column", paste the error. Table and column names below are best guesses.

## Page 00 · Base math (economy)

```sql
SELECT Name, Value FROM GlobalParameters
WHERE Name LIKE '%GROWTH%' OR Name LIKE '%FOOD%' OR Name LIKE '%CULTURE_COST%'
   OR Name LIKE '%PLOT%' OR Name LIKE '%HOUSING%' OR Name LIKE '%AMENIT%';

SELECT * FROM Happinesses;
SELECT TerrainType, YieldType, YieldChange FROM Terrain_YieldChanges;
SELECT FeatureType, YieldType, YieldChange FROM Feature_YieldChanges;
```

## Page 01 · Units and combat

```sql
SELECT Name, Value FROM GlobalParameters
WHERE Name LIKE 'COMBAT%' OR Name LIKE '%DAMAGE%' OR Name LIKE '%HEAL%'
   OR Name LIKE '%FORTIF%' OR Name LIKE '%FLANK%' OR Name LIKE '%SUPPORT%'
   OR Name LIKE '%WALL%' OR Name LIKE '%CITY_%STRENGTH%' OR Name LIKE '%HIT_POINTS%';

SELECT UnitType, Combat, RangedCombat, Bombard, Range, BaseMoves, Cost, Maintenance, StrategicResource
FROM Units;

SELECT TerrainType, MovementCost, DefenseModifier FROM Terrains;
SELECT FeatureType, MovementCost, DefenseModifier FROM Features;
```

If the two terrain queries error, run `SELECT * FROM Terrains LIMIT 1;` and paste the column names.

## Page 02 · Trade and diplomacy

Table names are the least certain here, so start by listing what exists:

```sql
SELECT name FROM sqlite_master WHERE type='table'
AND (name LIKE '%Trade%' OR name LIKE '%Diplo%' OR name LIKE '%Grievance%'
  OR name LIKE '%Agenda%' OR name LIKE '%Envoy%' OR name LIKE '%Alliance%' OR name LIKE '%CasusBelli%');

SELECT Name, Value FROM GlobalParameters
WHERE Name LIKE '%TRADE%' OR Name LIKE '%GRIEVANCE%' OR Name LIKE '%DIPLO%'
   OR Name LIKE '%ENVOY%' OR Name LIKE '%WARMONGER%' OR Name LIKE '%FRIEND%' OR Name LIKE '%ALLIANCE%';
```

Paste both results. Based on the table list, Claude will write the follow-up queries.

## Page 03 · Cities and districts

```sql
SELECT Name, Value FROM GlobalParameters
WHERE Name LIKE '%DISTRICT%' OR Name LIKE '%CITY_%' OR Name LIKE '%SETTLER%'
   OR Name LIKE '%SPECIALIST%' OR Name LIKE '%LOYALTY%' OR Name LIKE '%MIN_CITY%' OR Name LIKE '%ADJACEN%';

SELECT DistrictType, Cost, CostProgressionModel, CostProgressionParam1, Housing, Entertainment,
       CityStrengthModifier, PlunderType, OnePerCity, RequiresPlacement
FROM Districts;

SELECT * FROM District_Adjacencies LIMIT 80;
SELECT * FROM Adjacency_YieldChanges LIMIT 80;
```

If a column errors, run `SELECT * FROM Districts LIMIT 1;` and paste the column names. Also paste `SELECT UnitType, Cost, PopulationCost FROM Units WHERE UnitType LIKE '%SETTLER%';`.

## Keeping this file current

Add a new section here whenever a new ledger page is started. Queries only: no game text or code is copied into the ledger (hard rule 8).
