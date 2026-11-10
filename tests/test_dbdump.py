"""Tests for tools/dbdump.py using a tiny synthetic database."""

import sqlite3

import dbdump


def make_db(path):
    con = sqlite3.connect(path)
    con.executescript(
        """
        CREATE TABLE GlobalParameters (Name TEXT, Value TEXT);
        INSERT INTO GlobalParameters VALUES ('CITY_GROWTH_MULTIPLIER','8'), ('OTHER_THING','1');
        CREATE TABLE Technologies (TechnologyType TEXT, EraType TEXT, Cost INT, Extra TEXT);
        INSERT INTO Technologies VALUES ('T_A','ERA_1',25,'x'), ('T_B','ERA_1',50,'y');
        CREATE TABLE Units (UnitType TEXT, Combat INT);
        INSERT INTO Units VALUES ('U_A', 20);
        CREATE TABLE TradeThing (A INT);
        """
    )
    con.commit()
    con.close()


def test_report_has_values_and_survives_missing_tables(tmp_path):
    db = tmp_path / "d.sqlite"
    make_db(db)
    out = tmp_path / "out.md"
    assert dbdump.main(["--db", str(db), "--out", str(out)]) == 0
    text = out.read_text(encoding="utf-8")
    assert "CITY_GROWTH_MULTIPLIER" in text and "OTHER_THING" not in text.split("## Page 01")[0].split("Page 00")[1]
    assert "T_B" in text and "| 50 |" in text
    assert "Table `Civics` does not exist" in text  # missing table does not crash
    assert "TradeThing" in text  # discovery list


def test_database_is_not_modified(tmp_path):
    db = tmp_path / "d.sqlite"
    make_db(db)
    before = db.read_bytes()
    dbdump.main(["--db", str(db), "--out", str(tmp_path / "o.md")])
    assert db.read_bytes() == before


def test_missing_db_returns_error(tmp_path, monkeypatch):
    monkeypatch.delenv("CIVLAYER_DEBUG_DB", raising=False)
    monkeypatch.delenv("LOCALAPPDATA", raising=False)
    monkeypatch.setenv("HOME", str(tmp_path))
    assert dbdump.main(["--db", str(tmp_path / "nope.sqlite"), "--out", str(tmp_path / "o.md")]) == 2


def test_all_columns_marker_dumps_every_column(tmp_path):
    db = tmp_path / "d.sqlite"
    con = sqlite3.connect(db)
    con.executescript("CREATE TABLE Districts (DistrictType TEXT, A INT, B INT, C INT, D INT, E INT, F INT, G INT, H INT, I INT, J INT, K INT, L INT, M INT, N INT);"
                      "INSERT INTO Districts VALUES ('D_X',1,2,3,4,5,6,7,8,9,10,11,12,13,14);")
    con.commit(); con.close()
    out = tmp_path / "o.md"
    dbdump.main(["--db", str(db), "--out", str(out)])
    text = out.read_text(encoding="utf-8")
    assert "| N |" in text.split("### Districts")[1].split("###")[0]  # 14th column present


def test_modifier_digest_and_catalog(tmp_path):
    db = tmp_path / "m.sqlite"
    con = sqlite3.connect(db)
    con.executescript(
        """
        CREATE TABLE Modifiers (ModifierId TEXT, ModifierType TEXT, SubjectRequirementSetId TEXT);
        CREATE TABLE ModifierArguments (ModifierId TEXT, Name TEXT, Type TEXT, Value TEXT);
        CREATE TABLE DynamicModifiers (ModifierType TEXT, CollectionType TEXT, EffectType TEXT);
        CREATE TABLE PolicyModifiers (PolicyType TEXT, ModifierId TEXT);
        CREATE TABLE TraitModifiers (TraitType TEXT, ModifierId TEXT);
        CREATE TABLE GlobalParameters (Name TEXT, Value TEXT);
        INSERT INTO GlobalParameters VALUES ('A_PARAM','1');
        INSERT INTO DynamicModifiers VALUES ('MT_YIELD','COLLECTION_OWNER','EFFECT_ADJUST_YIELD');
        INSERT INTO Modifiers VALUES ('M1','MT_YIELD','REQ1'), ('M2','MT_YIELD',NULL);
        INSERT INTO ModifierArguments VALUES ('M1','Amount','ARGTYPE_IDENTITY','2'), ('M1','YieldType','ARGTYPE_IDENTITY','YIELD_GOLD');
        INSERT INTO PolicyModifiers VALUES ('POLICY_X','M1');
        INSERT INTO TraitModifiers VALUES ('TRAIT_Y','M2');
        """
    )
    con.commit(); con.close()
    out = tmp_path / "o.md"
    assert dbdump.main(["--db", str(db), "--out", str(out)]) == 0
    text = out.read_text(encoding="utf-8")
    assert "POLICY_X | COLLECTION_OWNER>EFFECT_ADJUST_YIELD | Amount=2; YieldType=YIELD_GOLD | when REQ1" in text
    assert "TRAIT_Y" not in text                  # civilization/leader content is skipped
    assert "## All GlobalParameters" in text and "A_PARAM" in text
    assert "## Table catalog" in text and "| PolicyModifiers | 1 |" in text


def test_attach_wrapper_is_resolved_one_level(tmp_path):
    db = tmp_path / "w.sqlite"
    con = sqlite3.connect(db)
    con.executescript(
        """
        CREATE TABLE Modifiers (ModifierId TEXT, ModifierType TEXT, SubjectRequirementSetId TEXT);
        CREATE TABLE ModifierArguments (ModifierId TEXT, Name TEXT, Type TEXT, Value TEXT);
        CREATE TABLE DynamicModifiers (ModifierType TEXT, CollectionType TEXT, EffectType TEXT);
        CREATE TABLE BeliefModifiers (BeliefType TEXT, ModifierId TEXT);
        INSERT INTO DynamicModifiers VALUES ('MT_ATTACH','COLLECTION_ALL_CITIES','EFFECT_ATTACH_MODIFIER'), ('MT_YIELD','COLLECTION_OWNER','EFFECT_ADJUST_PLOT_YIELD');
        INSERT INTO Modifiers VALUES ('OUTER','MT_ATTACH',NULL), ('INNER','MT_YIELD','REQ_FARM');
        INSERT INTO ModifierArguments VALUES ('OUTER','ModifierId','ARGTYPE_IDENTITY','INNER'), ('INNER','Amount','ARGTYPE_IDENTITY','1');
        INSERT INTO BeliefModifiers VALUES ('BELIEF_Z','OUTER');
        """
    )
    con.commit(); con.close()
    out = tmp_path / "o.md"
    dbdump.main(["--db", str(db), "--out", str(out)])
    assert "==> COLLECTION_OWNER>EFFECT_ADJUST_PLOT_YIELD | Amount=1 | when REQ_FARM" in out.read_text(encoding="utf-8")


def test_requirement_digest(tmp_path):
    db = tmp_path / "r.sqlite"
    con = sqlite3.connect(db)
    con.executescript(
        """
        CREATE TABLE RequirementSets (RequirementSetId TEXT, RequirementSetType TEXT);
        CREATE TABLE RequirementSetRequirements (RequirementSetId TEXT, RequirementId TEXT);
        CREATE TABLE Requirements (RequirementId TEXT, RequirementType TEXT, Inverse INT);
        CREATE TABLE RequirementArguments (RequirementId TEXT, Name TEXT, Type TEXT, Value TEXT);
        INSERT INTO RequirementSets VALUES ('SET_A','REQUIREMENTSET_ALL');
        INSERT INTO RequirementSetRequirements VALUES ('SET_A','R1'), ('SET_A','R2');
        INSERT INTO Requirements VALUES ('R1','REQUIREMENT_CITY_HAS_BUILDING',0), ('R2','REQUIREMENT_PLOT_HAS_FEATURE',1);
        INSERT INTO RequirementArguments VALUES ('R1','BuildingType','ARGTYPE_IDENTITY','BUILDING_X'), ('R2','FeatureType','ARGTYPE_IDENTITY','FEATURE_Y');
        """
    )
    con.commit(); con.close()
    out = tmp_path / "o.md"
    dbdump.main(["--db", str(db), "--out", str(out)])
    assert "SET_A | REQUIREMENT_CITY_HAS_BUILDING: BuildingType=BUILDING_X ; REQUIREMENT_PLOT_HAS_FEATURE (NOT): FeatureType=FEATURE_Y" in out.read_text(encoding="utf-8")
