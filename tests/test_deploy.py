"""Tests for tools/deploy.py."""

import pytest

import deploy
from deploy import DeployError


@pytest.fixture
def source(tmp_path):
    src = tmp_path / "src" / "CivLayer"
    (src / "Data").mkdir(parents=True)
    (src / "CivLayer.modinfo").write_text("<Mod/>")
    (src / "Data" / "a.sql").write_text("-- a")
    (src / "Data" / "junk.bak").write_text("x")
    (src / ".DS_Store").write_text("x")
    return src


@pytest.fixture
def mods(tmp_path):
    d = tmp_path / "Mods"
    d.mkdir()
    return d


def test_copies_and_skips_junk(source, mods):
    deploy.deploy(source, mods)
    target = mods / "CivLayer"
    assert (target / "CivLayer.modinfo").is_file()
    assert (target / "Data" / "a.sql").is_file()
    assert not (target / "Data" / "junk.bak").exists()
    assert not (target / ".DS_Store").exists()


def test_replaces_previous_deploy(source, mods):
    deploy.deploy(source, mods)
    (mods / "CivLayer" / "stale.sql").write_text("old")
    deploy.deploy(source, mods)
    assert not (mods / "CivLayer" / "stale.sql").exists()


def test_refuses_to_replace_foreign_folder(source, mods):
    foreign = mods / "CivLayer"
    foreign.mkdir()
    (foreign / "keep.txt").write_text("mine")
    with pytest.raises(DeployError, match="Refusing"):
        deploy.deploy(source, mods)
    assert (foreign / "keep.txt").is_file()


def test_dry_run_changes_nothing(source, mods):
    files = deploy.deploy(source, mods, dry_run=True)
    assert {str(f).replace("\\", "/") for f in files} == {"CivLayer.modinfo", "Data/a.sql"}
    assert not (mods / "CivLayer").exists()


def test_missing_source_or_modinfo(tmp_path, mods):
    with pytest.raises(DeployError, match="Phase 3"):
        deploy.deploy(tmp_path / "nope", mods)
    empty = tmp_path / "empty"
    empty.mkdir()
    with pytest.raises(DeployError, match="modinfo"):
        deploy.deploy(empty, mods)


def test_missing_mods_dir(source, tmp_path):
    with pytest.raises(DeployError, match="does not exist"):
        deploy.deploy(source, tmp_path / "no-mods")


def test_resolve_order(tmp_path, monkeypatch):
    cli = tmp_path / "cli"
    assert deploy.resolve_mods_dir(cli, env={"CIVLAYER_MODS_DIR": "x"}) == cli
    assert str(deploy.resolve_mods_dir(None, env={"CIVLAYER_MODS_DIR": "x"})) == "x"
    monkeypatch.setattr(deploy.sys, "platform", "linux")
    with pytest.raises(DeployError, match="--mods-dir"):
        deploy.resolve_mods_dir(None, env={})


def test_cli_dry_run(source, mods, capsys):
    assert deploy.main(["--source", str(source), "--mods-dir", str(mods), "--dry-run"]) == 0
    assert "would copy 2 files" in capsys.readouterr().out
