"""Check a game-data JSON file against the rules in docs/schema/game-data-schema.md.

Design tool, not game code: it proves the written rules can be checked by a machine,
and it makes the four design variables (docs/schema/variants.json) testable. Flip a
value in the dataset's rules_config and this lists what in the data must change.

Usage:
    python tools/schemacheck.py [docs/schema/example-data.json]

Exit code 0 = no problems, 1 = problems (each printed with its rule code).

Rule codes: R1 to R15 are structural rules. V0 to V4 are the variable checks.

Source: custom (docs/schema).
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

SCHEMA_DIR = Path(__file__).resolve().parent.parent / "docs" / "schema"
SECTIONS_WITH_IDS = [
    "eras", "meters", "terrains", "features", "resource_classes", "unit_classes", "improvements", "units",
    "districts", "buildings", "great_person_classes", "great_person_individuals", "nodes", "governments",
    "cards", "beliefs", "religions", "conditions", "effects",
]


def load(path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_enums() -> dict:
    return load(SCHEMA_DIR / "enums.json")


def load_variants() -> dict:
    return {v["id"]: v for v in load(SCHEMA_DIR / "variants.json")["variables"]}


def check(data: dict, enums: dict | None = None, variants: dict | None = None) -> list[str]:
    enums = enums or load_enums()
    variants = variants or load_variants()
    errs: list[str] = []
    cfg = data.get("rules_config", {})

    def rows(name):
        return data.get(name) or []

    def idset(name):
        return {r["id"] for r in rows(name)}

    # ---- V0 config values valid
    for vid, v in variants.items():
        val = cfg.get(v["config_key"])
        if val not in v["options"]:
            errs.append(f"V0: rules_config.{v['config_key']} = {val!r} is not one of {sorted(v['options'])}")

    # ---- R1 unique ids
    seen = Counter()
    for sec in SECTIONS_WITH_IDS:
        for r in rows(sec):
            seen[r["id"]] += 1
    errs += [f"R1: duplicate id {i}" for i, n in seen.items() if n > 1]
    all_ids = set(seen)

    eras = {e["id"]: e["index"] for e in rows("eras")}
    nodes = {n["id"]: n for n in rows("nodes")}
    trees_allowed = cfg.get("trees") or enums["node_trees"]

    # ---- R2 R3 R4 nodes
    for n in nodes.values():
        if n["era"] not in eras:
            errs.append(f"R2: node {n['id']} has unknown era {n['era']}")
        if len(n["requires"]) > 4:
            errs.append(f"R4: node {n['id']} has more than 4 requirements")
        for r in n["requires"]:
            if r not in nodes:
                errs.append(f"R2: node {n['id']} requires missing node {r}")
                continue
            if nodes[r]["tree"] != n["tree"]:
                errs.append(f"R2: node {n['id']} requires {r} from a different tree")
            if n["era"] in eras and nodes[r]["era"] in eras:
                gap = eras[n["era"]] - eras[nodes[r]["era"]]
                if gap not in (0, 1):
                    errs.append(f"R3: link {r} -> {n['id']} skips an era (gap {gap})")
    state: dict = {}

    def visit(x, path):
        if state.get(x) == 1:
            errs.append(f"R2: cycle through {x}")
            return
        if state.get(x) == 2:
            return
        state[x] = 1
        for r in nodes[x]["requires"]:
            if r in nodes:
                visit(r, path + [x])
        state[x] = 2

    for n in nodes:
        visit(n, [])

    # ---- R5 costs do not fall with era
    for tree in {n["tree"] for n in nodes.values()}:
        seq = sorted((eras.get(n["era"], 0), n["cost"]) for n in nodes.values() if n["tree"] == tree)
        costs = [c for _, c in seq]
        if costs != sorted(costs):
            errs.append(f"R5: costs fall as era rises in tree {tree}")

    # ---- R6 / R15 boosts
    for n in nodes.values():
        b = n["boost"]
        if b["family"] not in enums["boost_trigger_families"]:
            errs.append(f"R6: node {n['id']} boost family {b['family']!r} unknown")
        if not 0 <= b["percent"] <= 100:
            errs.append(f"R6: node {n['id']} boost percent out of range")
        if b["family"] != "none":
            kind = (b.get("trigger") or {}).get("kind")
            fam = enums["boost_trigger_kinds"].get(kind)
            if fam is None:
                errs.append(f"R6: node {n['id']} boost trigger kind {kind!r} unknown")
            elif fam != b["family"]:
                errs.append(f"R6: node {n['id']} trigger {kind!r} belongs to family {fam!r}, not {b['family']!r}")
        elif eras.get(n["era"]) != min(eras.values(), default=1):
            errs.append(f"R15: node {n['id']} has no boost but is not in the first era")

    # ---- R7 references
    for d in rows("districts"):
        if d.get("requires_node") not in nodes:
            errs.append(f"R7: district {d['id']} requires_node missing")
        if d.get("great_person_class") not in idset("great_person_classes"):
            errs.append(f"R7: district {d['id']} great_person_class missing")
    for b in rows("buildings"):
        if b["district"] not in idset("districts"):
            errs.append(f"R7: building {b['id']} district missing")
        if not set(b.get("yields", {})) <= set(enums["yields"]):
            errs.append(f"R7: building {b['id']} uses an unknown yield")
        if not set(b.get("great_person_points", {})) <= idset("great_person_classes"):
            errs.append(f"R7: building {b['id']} points a missing great-person class")
    for i in rows("improvements"):
        if not set(i["yields"]) <= set(enums["yields"]):
            errs.append(f"R7: improvement {i['id']} unknown yield")
    effects = {e["id"]: e for e in rows("effects")}
    conditions = {c["id"]: c for c in rows("conditions")}
    for e in effects.values():
        if e["owner"] not in all_ids:
            errs.append(f"R7: effect {e['id']} owner {e['owner']} missing")
        if e["when"] is not None and e["when"] not in conditions:
            errs.append(f"R7: effect {e['id']} when {e['when']} missing")
        args = e.get("args", {})
        if "yield" in args and args["yield"] not in enums["yields"]:
            errs.append(f"R7: effect {e['id']} unknown yield {args['yield']}")
        if "unit_classes" in args and not set(args["unit_classes"]) <= idset("unit_classes"):
            errs.append(f"R7: effect {e['id']} unknown unit class")
        if "eras" in args and not set(args["eras"]) <= set(eras):
            errs.append(f"R7: effect {e['id']} unknown era")
        # ---- R8 enums
        if e["scope"] not in enums["scopes"]:
            errs.append(f"R8: effect {e['id']} scope {e['scope']!r} not in enums")
        if e["kind"] not in enums["effect_kinds"]:
            errs.append(f"R8: effect {e['id']} kind {e['kind']!r} not in enums")
    for g in rows("great_person_individuals"):
        if g["class"] not in idset("great_person_classes") or g["era"] not in eras:
            errs.append(f"R7: great person {g['id']} has a missing class or era")
        if g.get("effect") and g["effect"] not in effects:
            errs.append(f"R7: great person {g['id']} effect missing")
    for b in rows("beliefs"):
        if b["class"] not in enums["belief_classes"]:
            errs.append(f"R8: belief {b['id']} class unknown")
        if not set(b["effects"]) <= set(effects):
            errs.append(f"R7: belief {b['id']} effect missing")

    # ---- R9 governments
    prev_total = -1
    for g in sorted(rows("governments"), key=lambda x: x["tier"]):
        if set(g["slots"]) != set(enums["slot_types"]):
            errs.append(f"R9: government {g['id']} must list all four slot types")
        total = sum(g["slots"].values())
        if total <= prev_total:
            errs.append(f"R9: government {g['id']} tier {g['tier']} has {total} slots, not more than the tier below")
        prev_total = max(prev_total, total)
        if g.get("fixed_bonus") and g["fixed_bonus"] not in effects:
            errs.append(f"R7: government {g['id']} fixed_bonus effect missing")
        if g.get("requires_node") and g["requires_node"] not in nodes:
            errs.append(f"R7: government {g['id']} requires_node missing")

    # ---- R10 meters and adjacency basics
    for m in rows("meters"):
        if m["fed_by"] not in enums["yields"] or m["cost_model"] not in enums["cost_models"] or m["on_full"] not in enums["meter_resets"]:
            errs.append(f"R10: meter {m['id']} uses an unknown value")
    for d in rows("districts"):
        if d["cost_model"] not in enums["cost_models"]:
            errs.append(f"R10: district {d['id']} cost model unknown")
        for a in d["adjacency"]:
            if a["yield"] not in enums["yields"] or a["per"] not in (1, 2, 3):
                errs.append(f"R10: district {d['id']} adjacency rule invalid")
            # ---- R13 selectors resolve
            for key, val in a["neighbor"].items():
                if key not in enums["adjacency_neighbor_keys"]:
                    errs.append(f"R13: district {d['id']} adjacency selector {key!r} unknown")
                    continue
                sec = enums["adjacency_neighbor_keys"][key]
                if sec and val not in idset(sec):
                    errs.append(f"R13: district {d['id']} adjacency {key}={val!r} not found")

    # ---- R11 unlock consistency (each entity unlocked by exactly the node it names)
    unlocked_by: dict = {}
    for n in nodes.values():
        for u in n["unlocks"]:
            sec = enums["unlock_sections"].get(u["type"])
            if not sec or u["id"] not in idset(sec):
                errs.append(f"R11: node {n['id']} unlocks {u['id']} as {u['type']!r}, which does not exist")
                continue
            if u["id"] in unlocked_by:
                errs.append(f"R11: {u['id']} is unlocked by both {unlocked_by[u['id']]} and {n['id']}")
            unlocked_by[u["id"]] = n["id"]
    for sec in enums["unlock_sections"].values():
        for r in rows(sec):
            req = r.get("requires_node")
            if req and unlocked_by.get(r["id"]) != req:
                errs.append(f"R11: {r['id']} says requires_node {req} but is unlocked by {unlocked_by.get(r['id'])}")
            if not req and r["id"] in unlocked_by:
                errs.append(f"R11: {r['id']} is unlocked by {unlocked_by[r['id']]} but has no requires_node")

    # ---- R12 card effects allowed in slot
    allowed = enums["slot_allowed_effect_kinds"]
    every = {k for v in allowed.values() if v != "any" for k in v}
    for c in rows("cards"):
        if c["slot"] not in enums["slot_types"]:
            errs.append(f"R8: card {c['id']} slot unknown")
            continue
        if not set(c["effects"]) <= set(effects):
            errs.append(f"R7: card {c['id']} effect missing")
            continue
        ok = every if allowed[c["slot"]] == "any" else set(allowed[c["slot"]])
        for eid in c["effects"]:
            if effects[eid]["kind"] not in ok:
                errs.append(f"R12: card {c['id']} ({c['slot']} slot) uses effect kind {effects[eid]['kind']!r}, not allowed there")

    # ---- R14 conditions
    for c in conditions.values():
        if c["mode"] not in ("all", "any"):
            errs.append(f"R14: condition {c['id']} mode {c['mode']!r}")
        for r in c["requirements"]:
            if r["kind"] not in enums["requirement_kinds"]:
                errs.append(f"R8: condition {c['id']} requirement kind {r['kind']!r} not in enums")
                continue
            ref = enums["requirement_arg_refs"].get(r["kind"])
            if ref and r["args"].get(ref[0]) not in idset(ref[1]):
                errs.append(f"R14: condition {c['id']} {r['kind']} references missing {ref[0]} {r['args'].get(ref[0])!r}")
    cstate: dict = {}

    def cvisit(cid):
        if cstate.get(cid) == 1:
            errs.append(f"R14: conditions nest in a loop through {cid}")
            return
        if cstate.get(cid) == 2:
            return
        cstate[cid] = 1
        for r in conditions[cid]["requirements"]:
            if r["kind"] == "set_is_met" and r["args"].get("condition") in conditions:
                cvisit(r["args"]["condition"])
        cstate[cid] = 2

    for cid in conditions:
        cvisit(cid)

    # ================= variable checks =================
    # V1 tree layout
    layout = cfg.get("tree_layout")
    if layout == "two_trees":
        for n in nodes.values():
            if n["tree"] not in enums["node_trees"]:
                errs.append(f"V1: node {n['id']} tree {n['tree']!r} is not science/culture (tree_layout=two_trees)")
            elif n["paid_with"] != n["tree"]:
                errs.append(f"V1: node {n['id']} in the {n['tree']} tree must be paid with {n['tree']}, not {n['paid_with']}")
    elif layout == "one_tree":
        for n in nodes.values():
            if n["tree"] != "main":
                errs.append(f"V1: node {n['id']} tree must be 'main' when tree_layout=one_tree")
            if n["paid_with"] not in ("science", "culture"):
                errs.append(f"V1: node {n['id']} paid_with must be science or culture")

    # V2 religion mode
    mode = cfg.get("religion_mode")
    has_rel = bool(rows("religions")) or bool(rows("beliefs"))
    units = rows("faith_units")
    if mode == "pressure_only":
        if units:
            errs.append("V2: faith_units must be empty when religion_mode=pressure_only")
        if not rows("beliefs") or not rows("religions"):
            errs.append("V2: pressure_only needs at least one belief and one religion")
        if not data.get("religion_pressure"):
            errs.append("V2: pressure_only needs religion_pressure settings")
        if not data.get("faith_sinks"):
            errs.append("V2: pressure_only needs faith_sinks (what faith is spent on)")
    elif mode == "units_and_pressure":
        if not units:
            errs.append("V2: units_and_pressure needs faith_units")
        if not data.get("religion_pressure") or not has_rel:
            errs.append("V2: units_and_pressure needs religion_pressure, beliefs and religions")
    elif mode == "off":
        if has_rel or units:
            errs.append("V2: religion_mode=off must have no beliefs, religions or faith_units")

    # V3 late tail
    if cfg.get("late_tail") == "trim":
        minimum = cfg.get("min_unlocks_per_node", 1)
        for n in nodes.values():
            if len(n["unlocks"]) < minimum:
                errs.append(f"V3: node {n['id']} unlocks {len(n['unlocks'])}, below min_unlocks_per_node={minimum} (late_tail=trim)")

    # V4 great-person pool
    pool = cfg.get("great_person_pool")
    for g in rows("great_person_individuals"):
        if pool == "shared_finite" and g.get("max_claims") != 1:
            errs.append(f"V4: great person {g['id']} must have max_claims=1 when pool is shared_finite")
        if pool == "personal" and g.get("max_claims") is not None:
            errs.append(f"V4: great person {g['id']} must have max_claims=null when pool is personal")
    return errs


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    path = argv[0] if argv else SCHEMA_DIR / "example-data.json"
    errs = check(load(path))
    for e in errs:
        print(e)
    print(f"{len(errs)} problem(s) in {path}" if errs else f"OK: {path}")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
