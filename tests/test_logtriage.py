"""Tests for tools/logtriage.py. Log lines are synthetic samples in the game's format."""

import logtriage
from logtriage import BASE, UNKNOWN

WS = r"C:\Program Files (x86)\Steam\steamapps\workshop\content\289070"
LOCAL = r"C:\Users\me\Documents\My Games\Sid Meier's Civilization VI\Mods"


def write_logs(tmp_path, **logs):
    for name, text in logs.items():
        (tmp_path / f"{name}.log").write_text(text, encoding="utf-8")
    return tmp_path


def sources(report):
    return {i.source for i in report.issues.values()}


def test_lua_error_attributed_by_path(tmp_path):
    write_logs(tmp_path, Lua=(
        "[1.000] InGame: Loaded fine\n"
        f"[2.000] InGame: Runtime Error: {WS}\\2683624437\\UI\\ProductionPanel.lua:120: attempt to index a nil value\n"
    ))
    report = logtriage.triage_dir(tmp_path)
    assert sources(report) == {"2683624437"}
    assert len(report.issues) == 1


def test_database_error_uses_context_lines(tmp_path):
    write_logs(tmp_path, Database=(
        f"[5.0] Loading {LOCAL}\\SomeMod\\Data\\Units.sql\n"
        "[5.1] [Gameplay] ERROR: UNIQUE constraint failed: Types.Type\n"
    ))
    report = logtriage.triage_dir(tmp_path)
    assert sources(report) == {"SomeMod"}


def test_modding_log_falls_back_to_last_named_mod(tmp_path):
    lines = [f"[1.0] UpdateDatabase - Loading {LOCAL}\\CivLayer\\Data\\patch\\a.sql"]
    lines += ["[1.1] Applying component"] * 5
    lines += ["[1.2] Failed to apply component"]
    write_logs(tmp_path, Modding="\n".join(lines) + "\n")
    report = logtriage.triage_dir(tmp_path)
    assert sources(report) == {"CivLayer"}


def test_repeats_are_grouped_and_timestamps_ignored(tmp_path):
    line = "[{t}] [Gameplay] ERROR: no such table: Foo\n"
    write_logs(tmp_path, Database=line.format(t="1.0") + line.format(t="9.5"))
    report = logtriage.triage_dir(tmp_path)
    (issue,) = report.issues.values()
    assert issue.count == 2
    assert issue.source == UNKNOWN


def test_base_game_paths_and_warnings(tmp_path):
    write_logs(tmp_path, GameEffects=(
        "[1.0] Warning: modifier MODIFIER_X has no requirement set "
        "(..\\Base\\Assets\\Gameplay\\Data\\Modifiers.xml)\n"
    ))
    report = logtriage.triage_dir(tmp_path)
    (issue,) = report.issues.values()
    assert issue.severity == "warning"
    assert issue.source == BASE


def test_ignores_non_errors(tmp_path):
    write_logs(tmp_path, Modding="[1.0] Finished: 0 errors\n[1.1] Mod loaded\n")
    report = logtriage.triage_dir(tmp_path)
    assert not report.issues


def test_missing_logs_reported(tmp_path):
    write_logs(tmp_path, Lua="[1.0] ok\n")
    report = logtriage.triage_dir(tmp_path)
    assert set(report.missing_logs) == {"Database.log", "Modding.log", "GameEffects.log"}


def test_cli_writes_report(tmp_path):
    logs = tmp_path / "logs"
    logs.mkdir()
    write_logs(logs, Lua=f"[1.0] Runtime Error: {WS}\\123\\x.lua:1: boom\n")
    out = tmp_path / "out" / "triage.md"
    assert logtriage.main([str(logs), "--out", str(out)]) == 0
    text = out.read_text()
    assert "| 123 | 1 | 0 |" in text
    assert "Missing: Database.log" in text


def test_cli_rejects_empty_folder(tmp_path):
    assert logtriage.main([str(tmp_path)]) == 2
