"""Tests for the draft game-data schema (docs/schema) and tools/schemacheck.py.

Two jobs: prove the extended example passes every rule, and prove each rule and each of the
four design variables actually bites (flip a value or break the data, the right code appears).
"""

import copy
import json
from pathlib import Path

import schemacheck

ROOT = Path(__file__).resolve().parent.parent / "docs" / "schema"
BASE = json.loads((ROOT / "example-data.json").read_text(encoding="utf-8"))
ENUMS = schemacheck.load_enums()
VARIANTS = schemacheck.load_variants()


def run(mutate=None):
    data = copy.deepcopy(BASE)
    if mutate:
        mutate(data)
    return schemacheck.check(data, ENUMS, VARIANTS)


def codes(errs):
    return {e.split(":")[0] for e in errs}


def node(d, nid):
    return next(n for n in d["nodes"] if n["id"] == nid)


# ---------- the example and the decisions

def test_example_passes_every_rule():
    assert run() == []


def test_example_follows_the_four_decisions():
    cfg = BASE["rules_config"]
    for vid, v in VARIANTS.items():
        assert cfg[v["config_key"]] == v["decision"], vid


def test_example_size_matches_the_plan():
    assert len(BASE["nodes"]) == 10
    assert len(BASE["districts"]) == 3
    assert len(BASE["buildings"]) == 6
    assert len(BASE["cards"]) == 6
    assert {n["tree"] for n in BASE["nodes"]} == {"science", "culture"}


def test_variants_file_is_consistent():
    for v in VARIANTS.values():
        assert v["decision"] in v["options"]
        assert v["checks"]


# ---------- structural rules bite

def test_r1_duplicate_id():
    assert "R1" in codes(run(lambda d: d["cards"].append(copy.deepcopy(d["cards"][0]))))


def test_r2_cycle_and_cross_tree_and_missing():
    def cyc(d):
        node(d, "node.s1")["requires"] = ["node.s2"]
    assert "R2" in codes(run(cyc))

    def cross(d):
        node(d, "node.c2")["requires"] = ["node.s1"]
    assert "R2" in codes(run(cross))


def test_r3_era_skip():
    def skip(d):
        node(d, "node.s6")["requires"] = ["node.s1"]
    assert "R3" in codes(run(skip))


def test_r4_too_many_requirements():
    def many(d):
        node(d, "node.s6")["requires"] = ["node.s1", "node.s2", "node.s3", "node.s4", "node.s5"]
    assert "R4" in codes(run(many))


def test_r5_cost_falls_with_era():
    def cheap(d):
        node(d, "node.s6")["cost"] = 10
    assert "R5" in codes(run(cheap))


def test_r6_boost_rules():
    def percent(d):
        node(d, "node.s2")["boost"]["percent"] = 150
    assert "R6" in codes(run(percent))

    def family(d):
        node(d, "node.s2")["boost"]["family"] = "combat"
    assert "R6" in codes(run(family))


def test_r15_no_boost_only_in_first_era():
    def late_none(d):
        node(d, "node.s4")["boost"] = {"family": "none", "percent": 0}
    assert "R15" in codes(run(late_none))


def test_r7_reference_missing():
    def bad(d):
        d["buildings"][0]["district"] = "dist.nowhere"
    assert "R7" in codes(run(bad))


def test_r8_enum_violations():
    def kind(d):
        d["effects"][0]["kind"] = "make_it_rain"
    assert "R8" in codes(run(kind))


def test_r9_government_slots():
    def flat(d):
        for g in d["governments"]:
            g["slots"] = {"military": 1, "economic": 1, "diplomatic": 0, "wildcard": 0}
    assert "R9" in codes(run(flat))


def test_r10_unknown_values():
    def meter(d):
        d["meters"][0]["fed_by"] = "mana"
    assert "R10" in codes(run(meter))


def test_r11_unlock_consistency():
    def wrong_type(d):
        node(d, "node.s2")["unlocks"] = [{"type": "building", "id": "dist.study"}]
    assert "R11" in codes(run(wrong_type))

    def wrong_node(d):
        d["buildings"][0]["requires_node"] = "node.s1"
    assert "R11" in codes(run(wrong_node))

    def double(d):
        node(d, "node.s1")["unlocks"].append({"type": "district", "id": "dist.study"})
    assert "R11" in codes(run(double))


def test_r12_card_effect_must_fit_slot():
    def bad(d):
        next(c for c in d["cards"] if c["id"] == "card.drill")["effects"] = ["eff.caravan"]
    errs = run(bad)
    assert "R12" in codes(errs)


def test_r12_wildcard_accepts_other_kinds():
    def wild(d):
        next(c for c in d["cards"] if c["id"] == "card.devotion")["effects"] = ["eff.drill"]
    assert "R12" not in codes(run(wild))


def test_r13_adjacency_selector_must_exist():
    def bad(d):
        d["districts"][0]["adjacency"][0]["neighbor"] = {"terrain": "terrain.moon"}
    assert "R13" in codes(run(bad))


def test_r14_condition_references_and_loops():
    def missing(d):
        d["conditions"][0]["requirements"][0]["args"]["building"] = "bld.nope"
    assert "R14" in codes(run(missing))

    def loop(d):
        cond = {c["id"]: c for c in d["conditions"]}
        cond["cond.city_has_academy"]["requirements"] = [
            {"kind": "set_is_met", "args": {"condition": "cond.academy_or_shrine"}, "negate": False}]
    assert "R14" in codes(run(loop))


# ---------- the four variables bite

def test_v0_config_value_must_be_an_option():
    def bad(d):
        d["rules_config"]["religion_mode"] = "crusades"
    assert "V0" in codes(run(bad))


def test_v1_tree_layout():
    # two_trees: a node paid with the wrong yield fails
    def wrong(d):
        node(d, "node.c1")["paid_with"] = "science"
    assert "V1" in codes(run(wrong))

    # one_tree: all nodes must be tree 'main'
    def to_one(d):
        d["rules_config"]["tree_layout"] = "one_tree"
    assert "V1" in codes(run(to_one))

    def to_one_fixed(d):
        d["rules_config"]["tree_layout"] = "one_tree"
        d["rules_config"]["trees"] = ["main"]
        for n in d["nodes"]:
            n["tree"] = "main"
    assert run(to_one_fixed) == []


def test_v2_religion_mode():
    # pressure_only with a faith unit fails
    def unit(d):
        d["faith_units"] = [{"id": "fu.x", "charges": 3}]
    assert "V2" in codes(run(unit))

    # units_and_pressure without units fails, with units passes
    def need_units(d):
        d["rules_config"]["religion_mode"] = "units_and_pressure"
    assert "V2" in codes(run(need_units))

    def with_units(d):
        d["rules_config"]["religion_mode"] = "units_and_pressure"
        d["faith_units"] = [{"id": "fu.x", "charges": 3}]
    assert "V2" not in codes(run(with_units))

    # off must have no religion data
    def off(d):
        d["rules_config"]["religion_mode"] = "off"
    assert "V2" in codes(run(off))

    def off_clean(d):
        d["rules_config"]["religion_mode"] = "off"
        d["beliefs"], d["religions"] = [], []
        d["effects"] = [e for e in d["effects"] if not e["id"].startswith("eff.bel_")]
        d["conditions"] = [c for c in d["conditions"] if c["id"] in ("cond.city_has_academy", "cond.city_has_shrine", "cond.academy_or_shrine")]
        d["nodes"][8]["boost"] = {"family": "chain_node", "trigger": {"kind": "have_node", "node": "node.s5"}, "percent": 40}
    assert "V2" not in codes(run(off_clean))


def test_v3_late_tail():
    def empty(d):
        node(d, "node.s6")["unlocks"] = []
    assert "V3" in codes(run(empty))

    def keep(d):
        d["rules_config"]["late_tail"] = "keep"
        node(d, "node.s6")["unlocks"] = []
        for u in ("bld.academy", "bld.exchange", "bld.sanctum"):
            next(b for b in d["buildings"] if b["id"] == u)["requires_node"] = None
    assert "V3" not in codes(run(keep))


def test_v3_minimum_is_adjustable():
    def two(d):
        d["rules_config"]["min_unlocks_per_node"] = 2
    errs = run(two)
    assert "V3" in codes(errs)  # single-unlock nodes now fail


def test_v4_great_person_pool():
    def personal_wrong(d):
        d["rules_config"]["great_person_pool"] = "personal"
    assert "V4" in codes(run(personal_wrong))

    def personal(d):
        d["rules_config"]["great_person_pool"] = "personal"
        for g in d["great_person_individuals"]:
            g["max_claims"] = None
    assert run(personal) == []

    def shared_wrong(d):
        d["great_person_individuals"][0]["max_claims"] = None
    assert "V4" in codes(run(shared_wrong))


# ---------- the tool itself

def test_cli_ok_and_failure(tmp_path, capsys):
    assert schemacheck.main([str(ROOT / "example-data.json")]) == 0
    bad = copy.deepcopy(BASE)
    bad["rules_config"]["late_tail"] = "nonsense"
    p = tmp_path / "bad.json"
    p.write_text(json.dumps(bad), encoding="utf-8")
    assert schemacheck.main([str(p)]) == 1
    assert "V0" in capsys.readouterr().out
