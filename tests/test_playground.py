"""Tests for the schema playground (docs/schema/playground.html).

The page runs a JavaScript copy of tools/schemacheck.py. These tests make sure the copy has not
drifted: every switch and every break the page offers is run through node, and the Python
checker must report the same rule codes with the same counts. They also check the built page
is up to date and self-contained.
"""

import json
import shutil
import subprocess
from collections import Counter
from pathlib import Path

import pytest

import build_playground
import schemacheck

SCHEMA = Path(__file__).resolve().parent.parent / "docs" / "schema"
NODE = shutil.which("node")

DRIVER = r"""
const S = require(process.argv[1] + "/playground-check.js");
const fs = require("fs");
const enums = JSON.parse(fs.readFileSync(process.argv[1] + "/enums.json"));
const variants = {}; JSON.parse(fs.readFileSync(process.argv[1] + "/variants.json")).variables.forEach(v => variants[v.id] = v);
const example = JSON.parse(fs.readFileSync(process.argv[1] + "/example-data.json"));
const scenarios = [];
function add(name, cfg, convert, breaks) { scenarios.push({name, cfg, convert, breaks}); }
add("base", {}, true, []);
S.MUTATIONS.forEach(m => { add("break " + m.id, {}, true, [m.id]); add("break-raw " + m.id, {}, false, [m.id]); });
const flips = {tree_layout: ["one_tree"], religion_mode: ["units_and_pressure", "off"], node_rewards: ["unlock_only", "empty_allowed"], great_person_pool: ["personal"]};
Object.keys(flips).forEach(k => flips[k].forEach(v => { const c = {}; c[k] = v; add("flip " + k + "=" + v, c, true, []); add("raw " + k + "=" + v, c, false, []); }));
add("min2", {min_rewards_per_node: 2}, true, []);
add("combo one_tree+skip+cheap", {tree_layout: "one_tree"}, true, ["skip", "cheap"]);
add("combo off+faithUnit", {religion_mode: "off"}, true, ["faithUnit"]);
add("combo personal+claims", {great_person_pool: "personal"}, true, ["claims"]);
add("combo unlock_only+emptyUnlock", {node_rewards: "unlock_only"}, true, ["emptyUnlock"]);
add("combo empty_allowed+strip", {node_rewards: "empty_allowed"}, true, ["stripEffect"]);
add("no endgame", {endgame_eras: 0}, true, []);
add("wide endgame", {endgame_eras: 2, node_rewards: "empty_allowed"}, true, ["emptyUnlock"]);
add("combo bad config", {religion_mode: "crusades"}, true, []);
const out = scenarios.map(s => { const d = S.buildDataset(example, s.cfg, s.convert, s.breaks); return {name: s.name, data: d, errors: S.check(d, enums, variants)}; });
process.stdout.write(JSON.stringify(out));
"""


def codes(errors):
    return Counter(e.split(":")[0] for e in errors)


@pytest.mark.skipif(NODE is None, reason="node is not installed")
def test_javascript_checker_matches_python_checker():
    out = subprocess.run([NODE, "-e", DRIVER, str(SCHEMA)], capture_output=True, text=True, check=True).stdout
    scenarios = json.loads(out)
    assert len(scenarios) > 30
    for s in scenarios:
        py = schemacheck.check(s["data"])
        assert codes(py) == codes(s["errors"]), f"{s['name']}: python {codes(py)} vs js {codes(s['errors'])}"


@pytest.mark.skipif(NODE is None, reason="node is not installed")
def test_every_break_trips_its_rule_under_the_decisions():
    out = subprocess.run([NODE, "-e", DRIVER, str(SCHEMA)], capture_output=True, text=True, check=True).stdout
    by_name = {s["name"]: s for s in json.loads(out)}
    assert by_name["base"]["errors"] == []
    muts = subprocess.run([NODE, "-e", "const S=require(process.argv[1]+'/playground-check.js');console.log(JSON.stringify(S.MUTATIONS.map(m=>[m.id,m.expect])))", str(SCHEMA)],
                          capture_output=True, text=True, check=True).stdout
    for mid, expect in json.loads(muts):
        got = codes(by_name["break " + mid]["errors"])
        assert expect in got, f"break {mid} should trip {expect}, got {dict(got)}"


@pytest.mark.skipif(NODE is None, reason="node is not installed")
def test_converted_flips_pass_and_raw_flips_fail():
    out = subprocess.run([NODE, "-e", DRIVER, str(SCHEMA)], capture_output=True, text=True, check=True).stdout
    by_name = {s["name"]: s for s in json.loads(out)}
    for name in ("flip tree_layout=one_tree", "flip religion_mode=units_and_pressure", "flip religion_mode=off",
                 "flip node_rewards=unlock_only", "flip node_rewards=empty_allowed", "flip great_person_pool=personal"):
        assert by_name[name]["errors"] == [], name
    for name in ("raw tree_layout=one_tree", "raw religion_mode=units_and_pressure", "raw religion_mode=off", "raw node_rewards=unlock_only", "raw great_person_pool=personal"):
        assert by_name[name]["errors"], name
    assert any(e.startswith("V3") for e in by_name["min2"]["errors"])
    assert any(e.startswith("R15") for e in by_name["no endgame"]["errors"])


def test_built_page_is_up_to_date_and_self_contained():
    built = (SCHEMA / "playground.html").read_text(encoding="utf-8")
    assert built == build_playground.standalone(), "run: python tools/build_playground.py"
    frag = build_playground.fragment()
    assert "<!doctype" not in frag.lower() and "<html" not in frag.lower() and "<body" not in frag.lower()
    assert "/*@" not in built  # every placeholder was filled
    assert "<title>Schema Playground</title>" in frag
    # only Google Fonts may be loaded from outside
    import re
    hosts = set(re.findall(r'(?:src|href)="(https?://[^/"]+)', frag))
    assert hosts <= {"https://fonts.googleapis.com", "https://fonts.gstatic.com"}, hosts
