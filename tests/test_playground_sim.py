"""Tests for the toy simulation (docs/schema/playground-sim.js), run through node.

The simulation is a model, not the game, so these tests check properties that must hold for any
sensible version of it: it is deterministic, every variable option runs, and the comparisons it is
built to show (pooled vs split trees, trim vs keep, units vs pressure, shared vs personal pools) point
the way the design reasoning says. They also check it survives broken data and respects its inputs.
"""

import json
import shutil
import subprocess
from pathlib import Path

import pytest

SCHEMA = Path(__file__).resolve().parent.parent / "docs" / "schema"
NODE = shutil.which("node")
pytestmark = pytest.mark.skipif(NODE is None, reason="node is not installed")

DRIVER = r"""
const dir = process.argv[1];
const S = require(dir + "/playground-check.js"), Sim = require(dir + "/playground-sim.js"), fs = require("fs");
const v = {}; JSON.parse(fs.readFileSync(dir + "/variants.json")).variables.forEach(x => v[x.id] = x);
const ex = JSON.parse(fs.readFileSync(dir + "/example-data.json"));
const cfg = {}; Object.values(v).forEach(x => cfg[x.config_key] = x.decision); cfg.min_rewards_per_node = 1; cfg.endgame_eras = 1;
const out = {};
Object.keys(v).forEach(id => {
  out[id] = Sim.compare(S, ex, cfg, id, v, {}).map(r => ({option: r.option, isDecision: r.isDecision, m: r.result.metrics}));
});
const a = Sim.simulate(S.buildDataset(ex, cfg, true, []), {}), b = Sim.simulate(S.buildDataset(ex, cfg, true, []), {});
out.deterministic = JSON.stringify(a) === JSON.stringify(b);
out.shortRun = Sim.simulate(S.buildDataset(ex, cfg, true, []), {turns: 20});
const broken = S.buildDataset(ex, cfg, true, ["cycle"]);
out.broken = Sim.simulate(broken, {}).metrics;
out.fastRivals = Sim.simulate(S.buildDataset(ex, cfg, true, []), {rival_strength: 0}).metrics;
out.defaults = Sim.DEFAULTS;
process.stdout.write(JSON.stringify(out));
"""


@pytest.fixture(scope="module")
def out():
    res = subprocess.run([NODE, "-e", DRIVER, str(SCHEMA)], capture_output=True, text=True, check=True)
    return json.loads(res.stdout)


def pick(rows, option):
    return next(r["m"] for r in rows if r["option"] == option)


def test_deterministic_and_respects_turn_count(out):
    assert out["deterministic"] is True
    assert len(out["shortRun"]["series"]["turn"]) == 20


def test_every_option_of_every_variable_runs(out):
    for vid in ("tree_layout", "religion_mode", "node_rewards", "great_person_pool"):
        assert len(out[vid]) >= 2
        for row in out[vid]:
            assert row["m"]["nodes_total"] >= 10


def test_one_shared_tree_finishes_no_later_and_wastes_less(out):
    two, one = pick(out["tree_layout"], "two_trees"), pick(out["tree_layout"], "one_tree")
    assert one["finish_all"] <= two["finish_all"]
    assert one["wasted_while_blocked"] <= two["wasted_while_blocked"]
    assert one["blocked_gap"] == 0 and two["blocked_gap"] >= 0


def test_requiring_a_real_unlock_drops_the_effect_only_nodes(out):
    both, strict = pick(out["node_rewards"], "unlock_or_effect"), pick(out["node_rewards"], "unlock_only")
    assert both["effect_only_nodes"] == 1 and strict["effect_only_nodes"] == 0
    assert strict["nodes_total"] == both["nodes_total"] - 1
    assert strict["finish_all"] < both["finish_all"]
    assert 0 < both["effect_only_cost_share"] < 100 and strict["effect_only_turn_share"] == 0


def test_allowing_empty_nodes_changes_nothing_when_the_data_has_none(out):
    both, empty = pick(out["node_rewards"], "unlock_or_effect"), pick(out["node_rewards"], "empty_allowed")
    assert empty["finish_all"] == both["finish_all"]


def test_religion_modes(out):
    pressure = pick(out["religion_mode"], "pressure_only")
    units = pick(out["religion_mode"], "units_and_pressure")
    off = pick(out["religion_mode"], "off")
    assert pressure["faith_units_bought"] == 0 and units["faith_units_bought"] > 0
    assert units["religion_lag"] <= pressure["religion_lag"]
    assert off["religion_on"] is False and off["religion_turn"] is None and off["religion_unconverted"] >= 1


def test_great_person_pools(out):
    shared, personal = pick(out["great_person_pool"], "shared_finite"), pick(out["great_person_pool"], "personal")
    assert personal["gp_rival"] == 0
    assert personal["gp_player"] == personal["gp_total"]
    assert shared["gp_player"] + shared["gp_rival"] <= shared["gp_total"]
    assert shared["gp_player"] <= personal["gp_player"]


def test_no_rivals_means_no_losses(out):
    assert out["fastRivals"]["gp_rival"] == 0


def test_broken_data_does_not_crash_the_simulation(out):
    # the loop in the tree means some nodes can never be researched, and that is reported, not thrown
    assert out["broken"]["nodes_done"] < out["broken"]["nodes_total"]


def test_assumptions_are_exposed(out):
    assert out["defaults"]["turns"] == 200 and out["defaults"]["rival_strength"] == 1.0
