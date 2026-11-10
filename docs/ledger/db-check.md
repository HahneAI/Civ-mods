# Database Check: How to Replace Guesses with Real Numbers

Source: custom. Applies to every ledger page. Claude cannot reach the game files from the cloud chat, so the owner runs these once and pastes the rows into the chat.

**Goal:** every `[approx]` / `[verify]` tag on a ledger page becomes a `[sure]` number read from the game's own data.

## Fastest way: one click (recommended)

On your PC, in the repo folder, run:

```
python tools/dbdump.py
```

It finds `DebugGameplay.sqlite` itself, opens it read-only (it cannot change anything), and writes one file, `db-results.md`, covering every section below. Attach that file to the chat. If it cannot find the database, it says so; search your PC for `DebugGameplay.sqlite` and run `python tools/dbdump.py --db "C:\path\to\DebugGameplay.sqlite"`. Do not commit the results file (it is git-ignored): it holds game data.

The manual steps below are the backup way, or for one-off questions.

## Manual setup (about 5 minutes)

1. Copy `DebugGameplay.sqlite` to a safe spot. Path (verify): `%LOCALAPPDATA%\Firaxis Games\Sid Meier's Civilization VI\Cache\DebugGameplay.sqlite` (it moved from Documents in the Leader Pass update, same as the logs). Work on the copy, never the original.
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

## Page 04 · Tech and civic trees (highest value; the owner asked for depth here)

```sql
SELECT TechnologyType, EraType, Cost FROM Technologies ORDER BY Cost;
SELECT CivicType, EraType, Cost FROM Civics ORDER BY Cost;
SELECT * FROM TechnologyPrereqs;
SELECT * FROM CivicPrereqs;
SELECT TechnologyType, BoostClass, Boost, TriggerDescription, Unit, ImprovementType, BuildingType, ResourceType
FROM Boosts;
SELECT CivicType, BoostClass, Boost, TriggerDescription FROM Boosts WHERE CivicType IS NOT NULL;

SELECT Name, Value FROM GlobalParameters
WHERE Name LIKE '%TECH%' OR Name LIKE '%CIVIC%' OR Name LIKE '%BOOST%' OR Name LIKE '%ERA%';
SELECT * FROM GameSpeeds;
```

Boosts may be one table with a TechnologyType and a CivicType column, or two tables. If a query errors, run the `sqlite_master` search from page 02, replacing the words with `%Boost%`, `%Prereq%`, `%Tech%`, `%Civic%`, and paste the list.

## Page 05 · Governments, policy cards, great people

```sql
SELECT GovernmentType, InheritedBonus1, PrereqCivic FROM Governments;
SELECT * FROM Government_SlotCounts;
SELECT PolicyType, GovernmentSlotType, PrereqCivic FROM Policies LIMIT 200;

SELECT GreatPersonClassType, DistrictType FROM GreatPersonClasses;
SELECT * FROM GreatPersonIndividuals LIMIT 60;
SELECT Name, Value FROM GlobalParameters
WHERE Name LIKE '%GREAT_PERSON%' OR Name LIKE '%GOVERNMENT%' OR Name LIKE '%POLICY%' OR Name LIKE '%PATRON%';
```

Column names are guesses; the same fallback applies (`SELECT * FROM <table> LIMIT 1;`).

## Page 06 · Religion and faith

```sql
SELECT Name, Value FROM GlobalParameters
WHERE Name LIKE '%RELIGION%' OR Name LIKE '%FAITH%' OR Name LIKE '%PANTHEON%'
   OR Name LIKE '%PRESSURE%' OR Name LIKE '%PROPHET%' OR Name LIKE '%THEOLOG%';

SELECT BeliefType, BeliefClassType FROM Beliefs ORDER BY BeliefClassType;
SELECT UnitType, Cost, ReligiousStrength, ReligionEvictPercent, SpreadCharges FROM Units WHERE SpreadCharges > 0 OR ReligiousStrength > 0;
SELECT * FROM Religions;
SELECT BuildingType, Cost, ReligiousPressure FROM Buildings WHERE ReligiousPressure IS NOT NULL OR BuildingType LIKE '%SHRINE%' OR BuildingType LIKE '%TEMPLE%';
```

Same fallback as before if a column errors. Also useful: `SELECT * FROM Maps_Religions` or any table from `sqlite_master` with `%Religion%` in the name, since the religion limit per map size is stored there.

## Round 1 result and the follow-up dump

Round 1 (2026-11-10) read pages 00 to 06 from the owner's database. It answered most open numbers and corrected several earlier guesses (tech costs, housing stop point, city-center yield, wounded units, boost size). A few tables were cut to 12 columns, which hid the neighbor-district rows of the adjacency table and the per-building yields.

**Round 2 (2026-11-10) done:** the follow-up dump was read and pages 02, 03, 05 and 06 updated.

`tools/dbdump.py` now dumps those tables in full (adjacency, districts, building yields, great-person points, governments, policies). To fill the remaining gaps, run it again the same way and attach the new `db-results.md`. Expect a larger file (a few hundred KB).

## Keeping this file current

Add a new section here whenever a new ledger page is started. Queries only: no game text or code is copied into the ledger (hard rule 8).
