"""One-click database check: read the debug gameplay database and write every
number the ledger pages are waiting on into one results file.

It only READS. The database is opened read-only, so it cannot be changed.
Nothing here guesses column names: each table is dumped using the columns that
exist, so a wrong guess just means fewer columns, never a crash.

Usage:
    python tools/dbdump.py                      # finds the database itself
    python tools/dbdump.py --db PATH [--out PATH]

Database search order: --db, the CIVLAYER_DEBUG_DB environment variable, then
%LOCALAPPDATA%/Firaxis Games/Sid Meier's Civilization VI/Cache/DebugGameplay.sqlite
(if you do not find it there, search your PC for DebugGameplay.sqlite).

Output: db-results.md in the current folder (ignored by git). Attach that one
file to the chat. Keep it out of the repo: it holds game data, and ledger pages
must not copy game text (hard rule 8).

Source: custom; feeds docs/ledger/db-check.md pages 00 to 06.
"""

from __future__ import annotations

import argparse
import os
import sqlite3
import sys
from datetime import date
from pathlib import Path

ROW_LIMIT = 800  # per table, so the file stays small enough to attach
ALL = ["*"]  # as the column list: dump every column of the table

# GlobalParameters name patterns per page. Matched with LIKE (case-insensitive).
PARAM_PATTERNS = {
    "00 Economy": ["%GROWTH%", "%FOOD%", "%CULTURE_COST%", "%PLOT%", "%HOUSING%", "%AMENIT%", "%CITIZEN%"],
    "01 Combat": ["COMBAT%", "%DAMAGE%", "%HEAL%", "%FORTIF%", "%FLANK%", "%SUPPORT%", "%WALL%", "%HIT_POINTS%"],
    "02 Trade/Diplomacy": ["%TRADE%", "%GRIEVANCE%", "%DIPLO%", "%ENVOY%", "%WARMONGER%", "%FRIEND%", "%ALLIANCE%"],
    "03 Cities/Districts": ["%DISTRICT%", "%CITY_%", "%SETTLER%", "%SPECIALIST%", "%LOYALTY%", "%ADJACEN%"],
    "04 Trees": ["%TECH%", "%CIVIC%", "%BOOST%", "%ERA%"],
    "05 Government/Great people": ["%GREAT_PERSON%", "%GOVERNMENT%", "%POLICY%", "%PATRON%"],
    "06 Religion": ["%RELIGION%", "%FAITH%", "%PANTHEON%", "%PRESSURE%", "%PROPHET%", "%THEOLOG%"],
}

# (page, table, preferred columns, optional WHERE). Missing tables and columns are skipped.
TABLES = [
    ("00 Economy", "Happinesses", [], ""),
    ("00 Economy", "Terrain_YieldChanges", [], ""),
    ("00 Economy", "Feature_YieldChanges", [], ""),
    ("00 Economy", "Resource_YieldChanges", [], ""),
    ("00 Economy", "Improvement_YieldChanges", [], ""),
    ("00 Economy", "GameSpeeds", [], ""),
    ("01 Combat", "Units",
     ["UnitType", "Combat", "RangedCombat", "Bombard", "Range", "BaseMoves", "Cost", "Maintenance",
      "StrategicResource", "PopulationCost", "PromotionClass", "FormationClass"], ""),
    ("01 Combat", "Terrains", [], ""),
    ("01 Combat", "Features", [], ""),
    ("03 Cities/Districts", "Districts", ALL, ""),
    ("03 Cities/Districts", "District_Adjacencies", ALL, ""),
    ("03 Cities/Districts", "Adjacency_YieldChanges", ALL, ""),
    ("03 Cities/Districts", "Buildings",
     ["BuildingType", "PrereqDistrict", "Cost", "Housing", "Entertainment", "CitizenSlots", "Maintenance",
      "PrereqTech", "PrereqCivic", "Capital", "OuterDefenseHitPoints", "OuterDefenseStrength", "Defense"], ""),
    ("03 Cities/Districts", "Building_YieldChanges", ALL, ""),
    ("03 Cities/Districts", "Improvements", ["ImprovementType", "PrereqTech", "PrereqCivic", "Housing", "TilesRequired", "BuildInLine"], ""),
    ("04 Trees", "Technologies", ["TechnologyType", "EraType", "Cost", "Repeatable"], ""),
    ("04 Trees", "TechnologyPrereqs", [], ""),
    ("04 Trees", "Civics", ["CivicType", "EraType", "Cost", "Repeatable"], ""),
    ("04 Trees", "CivicPrereqs", [], ""),
    ("04 Trees", "Boosts",
     ["TechnologyType", "CivicType", "BoostClass", "Boost", "NumItems", "Unit", "ImprovementType",
      "BuildingType", "ResourceType", "DistrictType", "Unit1Type", "Unit2Type"], ""),
    ("04 Trees", "Eras", [], ""),
    ("05 Government/Great people", "Governments", ALL, ""),
    ("05 Government/Great people", "Government_SlotCounts", [], ""),
    ("05 Government/Great people", "Policies", ALL, ""),
    ("05 Government/Great people", "District_GreatPersonPoints", ALL, ""),
    ("05 Government/Great people", "Building_GreatPersonPoints", ALL, ""),
    ("05 Government/Great people", "GreatPersonClasses", [], ""),
    ("05 Government/Great people", "GreatPersonIndividuals", [], ""),
    ("06 Religion", "Beliefs", ["BeliefType", "BeliefClassType"], ""),
    ("06 Religion", "Unit_ReligiousChargesAndStrength", [], ""),
    ("06 Religion", "Religions", ["ReligionType", "Pantheon"], ""),
]

# Words used to list candidate tables when a table name above does not exist.
DISCOVERY_WORDS = ["Trade", "Diplo", "Grievance", "Agenda", "Envoy", "Alliance", "CasusBelli",
                   "Religion", "Boost", "Prereq", "Promotion", "Wall", "Heal", "Specialist", "Loyalty"]


def find_db(arg: str | None) -> Path | None:
    candidates = []
    if arg:
        candidates.append(Path(arg))
    env = os.environ.get("CIVLAYER_DEBUG_DB")
    if env:
        candidates.append(Path(env))
    local = os.environ.get("LOCALAPPDATA")
    if local:
        candidates.append(Path(local) / "Firaxis Games" / "Sid Meier's Civilization VI" / "Cache" / "DebugGameplay.sqlite")
    candidates.append(Path.home() / "Documents" / "My Games" / "Sid Meier's Civilization VI" / "Cache" / "DebugGameplay.sqlite")
    for c in candidates:
        if c.is_file():
            return c
    return None


def connect_readonly(path: Path) -> sqlite3.Connection:
    uri = path.resolve().as_uri() + "?mode=ro&immutable=1"
    con = sqlite3.connect(uri, uri=True)
    con.text_factory = lambda b: b.decode("utf-8", "replace")
    return con


def cell(v) -> str:
    return "" if v is None else str(v).replace("|", "/").replace("\n", " ")


def md_table(cols: list[str], rows: list[tuple]) -> str:
    out = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    out += ["| " + " | ".join(cell(v) for v in r) + " |" for r in rows]
    return "\n".join(out)


def table_names(con) -> dict[str, str]:
    """lower-case name -> real name"""
    return {r[0].lower(): r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type IN ('table','view')")}


def table_columns(con, table: str) -> list[str]:
    return [r[1] for r in con.execute(f'PRAGMA table_info("{table}")')]


def dump_table(con, names: dict[str, str], table: str, prefer: list[str], where: str) -> str:
    real = names.get(table.lower())
    if not real:
        return f"_Table `{table}` does not exist in this database._"
    have = table_columns(con, real)
    lower = {c.lower(): c for c in have}
    if prefer == ALL:
        cols = have
    else:
        cols = [lower[p.lower()] for p in prefer if p.lower() in lower] or have[:12]
    total = con.execute(f'SELECT COUNT(*) FROM "{real}"').fetchone()[0]
    sql = f'SELECT {", ".join(chr(34) + c + chr(34) for c in cols)} FROM "{real}"'
    if where:
        sql += f" WHERE {where}"
    rows = con.execute(sql + f" LIMIT {ROW_LIMIT}").fetchall()
    note = f"{total} rows" + (f", first {ROW_LIMIT} shown" if total > ROW_LIMIT else "")
    extra = ""
    hidden = [c for c in have if c not in cols]
    if hidden and prefer:
        extra = f"\n\n_Other columns not shown:_ {', '.join(hidden)}"
    return f"_{note}._\n\n" + md_table(cols, rows) + extra


def dump_params(con, names, patterns: list[str]) -> str:
    real = names.get("globalparameters")
    if not real:
        return "_Table `GlobalParameters` does not exist._"
    cols = [c.lower() for c in table_columns(con, real)]
    if "name" not in cols or "value" not in cols:
        return f"_GlobalParameters columns are: {', '.join(cols)}_"
    where = " OR ".join(["Name LIKE ?"] * len(patterns))
    rows = con.execute(f"SELECT Name, Value FROM {real} WHERE {where} ORDER BY Name", patterns).fetchall()
    return f"_{len(rows)} rows._\n\n" + md_table(["Name", "Value"], rows)


def discovery(con) -> str:
    rows = []
    for (name,) in con.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"):
        if any(w.lower() in name.lower() for w in DISCOVERY_WORDS):
            cols = table_columns(con, name)
            n = con.execute(f'SELECT COUNT(*) FROM "{name}"').fetchone()[0]
            rows.append((name, n, ", ".join(cols[:10]) + (" ..." if len(cols) > 10 else "")))
    return md_table(["Table", "Rows", "First columns"], rows) if rows else "_No matches._"


def build_report(con) -> str:
    names = table_names(con)
    out = [f"# Database check results ({date.today().isoformat()})",
           "",
           f"Tables in database: {len(names)}. Attach this file to the chat. Do not commit it.",
           ""]
    pages = list(dict.fromkeys(p for p, *_ in TABLES))
    for page in sorted(set(pages) | set(PARAM_PATTERNS)):
        out += [f"## Page {page}", "", "### GlobalParameters", ""]
        out += [dump_params(con, names, PARAM_PATTERNS[page]) if page in PARAM_PATTERNS else "", ""]
        for pg, table, prefer, where in TABLES:
            if pg != page:
                continue
            out += [f"### {table}", ""]
            try:
                out += [dump_table(con, names, table, prefer, where), ""]
            except sqlite3.Error as e:  # one bad table must not stop the run
                out += [f"_Could not read `{table}`: {e}_", ""]
    out += ["## Tables that may hold trade, diplomacy, religion, boost and similar data", "", discovery(con), ""]
    return "\n".join(out)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--db", help="path to DebugGameplay.sqlite")
    ap.add_argument("--out", default="db-results.md", help="results file (default: db-results.md)")
    args = ap.parse_args(argv)

    db = find_db(args.db)
    if not db:
        print("Could not find DebugGameplay.sqlite. Search your PC for it, then run:\n"
              "  python tools/dbdump.py --db \"C:\\path\\to\\DebugGameplay.sqlite\"", file=sys.stderr)
        return 2
    try:
        con = connect_readonly(db)
        report = build_report(con)
    except sqlite3.Error as e:
        print(f"Could not read {db}: {e}", file=sys.stderr)
        return 1
    Path(args.out).write_text(report, encoding="utf-8")
    print(f"Read {db}\nWrote {args.out} ({len(report) // 1024} KB). Attach that file to the chat.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
