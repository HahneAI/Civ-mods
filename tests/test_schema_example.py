"""Checks the example data against the rules in docs/schema/game-data-schema.md.

Not game code: it only proves the written rules can be checked by a machine.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "docs" / "schema"
ENUMS = json.loads((ROOT / "enums.json").read_text(encoding="utf-8"))
DATA = json.loads((ROOT / "example-data.json").read_text(encoding="utf-8"))


def ids(section):
    return {x["id"] for x in DATA[section]}


def test_ids_are_unique_everywhere():
    seen = set()
    for section, rows in DATA.items():
        if section.startswith("_"):
            continue
        for row in rows:
            assert row["id"] not in seen, f"duplicate id {row['id']}"
            seen.add(row["id"])


def test_node_rules():
    era_index = {e["id"]: e["index"] for e in DATA["eras"]}
    nodes = {n["id"]: n for n in DATA["nodes"]}
    for n in nodes.values():
        assert n["tree"] in ENUMS["node_trees"]
        assert n["era"] in era_index
        assert len(n["requires"]) <= 4
        assert n["boost"]["family"] in ENUMS["boost_trigger_families"]
        assert 0 <= n["boost"]["percent"] <= 100
        for r in n["requires"]:
            assert r in nodes, f"{n['id']} requires missing {r}"
            assert nodes[r]["tree"] == n["tree"]
            gap = era_index[n["era"]] - era_index[nodes[r]["era"]]
            assert gap in (0, 1), f"link {r} -> {n['id']} skips an era"


def test_prerequisites_have_no_cycles():
    nodes = {n["id"]: n["requires"] for n in DATA["nodes"]}
    state = {}

    def visit(x):
        assert state.get(x) != 1, f"cycle at {x}"
        if state.get(x) == 2:
            return
        state[x] = 1
        for r in nodes[x]:
            visit(r)
        state[x] = 2

    for n in nodes:
        visit(n)


def test_costs_do_not_fall_with_era():
    index = {e["id"]: e["index"] for e in DATA["eras"]}
    for tree in ENUMS["node_trees"]:
        rows = sorted((index[n["era"]], n["cost"]) for n in DATA["nodes"] if n["tree"] == tree)
        costs = [c for _, c in rows]
        assert costs == sorted(costs)


def test_references_resolve():
    all_ids = set()
    for section, rows in DATA.items():
        if not section.startswith("_"):
            all_ids |= ids(section)
    for n in DATA["nodes"]:
        for u in n["unlocks"]:
            assert u["id"] in all_ids, f"unlock {u['id']} missing"
    for d in DATA["districts"]:
        assert d["requires_node"] in ids("nodes")
        assert d["great_person_class"] in ids("great_person_classes")
    for i in DATA["improvements"]:
        assert i["requires_node"] in ids("nodes")
        assert set(i["yields"]) <= set(ENUMS["yields"])
    for b in DATA["buildings"]:
        assert b["district"] in ids("districts")
        assert set(b["yields"]) <= set(ENUMS["yields"])
        assert set(b["great_person_points"]) <= ids("great_person_classes")
    for e in DATA["effects"]:
        assert e["owner"] in all_ids
        assert e["scope"] in ENUMS["scopes"]
        assert e["kind"] in ENUMS["effect_kinds"]
        assert e["when"] is None or e["when"] in ids("conditions")
    for c in DATA["cards"]:
        assert c["slot"] in ENUMS["slot_types"]
        assert set(c["effects"]) <= ids("effects")
    for g in DATA["governments"]:
        assert set(g["slots"]) == set(ENUMS["slot_types"])


def test_conditions_use_the_closed_list():
    for c in DATA["conditions"]:
        assert c["mode"] in ("all", "any")
        for r in c["requirements"]:
            assert r["kind"] in ENUMS["requirement_kinds"]


def test_meters_and_adjacency_use_known_values():
    for m in DATA["meters"]:
        assert m["fed_by"] in ENUMS["yields"]
        assert m["cost_model"] in ENUMS["cost_models"]
        assert m["on_full"] in ENUMS["meter_resets"]
    for d in DATA["districts"]:
        assert d["cost_model"] in ENUMS["cost_models"]
        for a in d["adjacency"]:
            assert a["yield"] in ENUMS["yields"]
            assert a["per"] in (1, 2, 3)
