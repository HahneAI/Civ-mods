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
