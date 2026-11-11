/* Schema rule checker, JavaScript port of tools/schemacheck.py.
 * Used by playground.html in the browser and by node in the parity test.
 * Keep the two in step: tests/test_playground.py compares their results.
 * Source: custom (docs/schema). */
(function (root) {
  "use strict";

  var SECTIONS_WITH_IDS = [
    "eras", "meters", "terrains", "features", "resource_classes", "unit_classes", "improvements", "units",
    "districts", "buildings", "great_person_classes", "great_person_individuals", "nodes", "governments",
    "cards", "beliefs", "religions", "conditions", "effects", "projects"
  ];

  function subset(a, b) { // every element of a is in b
    var set = new Set(b);
    return a.every(function (x) { return set.has(x); });
  }
  function sameSet(a, b) {
    return a.length === b.length && subset(a, b) && subset(b, a);
  }
  function sum(obj) { return Object.keys(obj).reduce(function (t, k) { return t + obj[k]; }, 0); }

  function check(data, enums, variants) {
    var errs = [];
    var cfg = data.rules_config || {};
    function rows(name) { return data[name] || []; }
    function idset(name) { return new Set(rows(name).map(function (r) { return r.id; })); }
    function has(setLike, v) { return setLike.has(v); }

    // V0 config values valid
    Object.keys(variants).forEach(function (vid) {
      var v = variants[vid];
      var val = cfg[v.config_key];
      if (!Object.prototype.hasOwnProperty.call(v.options, val)) {
        errs.push("V0: rules_config." + v.config_key + " = '" + val + "' is not one of " + JSON.stringify(Object.keys(v.options).sort()));
      }
    });

    // R1 unique ids
    var seen = {};
    SECTIONS_WITH_IDS.forEach(function (sec) {
      rows(sec).forEach(function (r) { seen[r.id] = (seen[r.id] || 0) + 1; });
    });
    Object.keys(seen).forEach(function (id) { if (seen[id] > 1) errs.push("R1: duplicate id " + id); });
    var allIds = new Set(Object.keys(seen));

    var eras = {};
    rows("eras").forEach(function (e) { eras[e.id] = e.index; });
    var nodes = {};
    rows("nodes").forEach(function (n) { nodes[n.id] = n; });
    var nodeList = rows("nodes");
    var eraValues = Object.keys(eras).map(function (k) { return eras[k]; });
    var minEra = eraValues.length ? Math.min.apply(null, eraValues) : 1;
    var endgameEras = cfg.endgame_eras === undefined ? 1 : cfg.endgame_eras;
    var lastEras = endgameEras > 0 ? eraValues.slice().sort(function (a, b) { return a - b; }).slice(-endgameEras) : [];

    // R2 R3 R4
    nodeList.forEach(function (n) {
      if (!(n.era in eras)) errs.push("R2: node " + n.id + " has unknown era " + n.era);
      if (n.requires.length > 4) errs.push("R4: node " + n.id + " has more than 4 requirements");
      n.requires.forEach(function (r) {
        if (!(r in nodes)) { errs.push("R2: node " + n.id + " requires missing node " + r); return; }
        if (nodes[r].tree !== n.tree) errs.push("R2: node " + n.id + " requires " + r + " from a different tree");
        if ((n.era in eras) && (nodes[r].era in eras)) {
          var gap = eras[n.era] - eras[nodes[r].era];
          if (gap !== 0 && gap !== 1) errs.push("R3: link " + r + " -> " + n.id + " skips an era (gap " + gap + ")");
        }
      });
    });
    var state = {};
    function visit(x) {
      if (state[x] === 1) { errs.push("R2: cycle through " + x); return; }
      if (state[x] === 2) return;
      state[x] = 1;
      nodes[x].requires.forEach(function (r) { if (r in nodes) visit(r); });
      state[x] = 2;
    }
    Object.keys(nodes).forEach(function (n) { visit(n); });

    // R5 costs do not fall with era
    var trees = {};
    nodeList.forEach(function (n) { trees[n.tree] = true; });
    Object.keys(trees).forEach(function (tree) {
      var seq = nodeList.filter(function (n) { return n.tree === tree; })
        .map(function (n) { return [eras[n.era] || 0, n.cost]; })
        .sort(function (a, b) { return a[0] - b[0] || a[1] - b[1]; });
      var costs = seq.map(function (p) { return p[1]; });
      var sorted = costs.slice().sort(function (a, b) { return a - b; });
      if (costs.some(function (c, i) { return c !== sorted[i]; })) errs.push("R5: costs fall as era rises in tree " + tree);
    });

    // R6 / R15 boosts
    nodeList.forEach(function (n) {
      var b = n.boost;
      if (enums.boost_trigger_families.indexOf(b.family) < 0) errs.push("R6: node " + n.id + " boost family '" + b.family + "' unknown");
      if (!(b.percent >= 0 && b.percent <= 100)) errs.push("R6: node " + n.id + " boost percent out of range");
      if (b.family !== "none") {
        var kind = (b.trigger || {}).kind;
        var fam = enums.boost_trigger_kinds[kind];
        if (fam === undefined) errs.push("R6: node " + n.id + " boost trigger kind '" + kind + "' unknown");
        else if (fam !== b.family) errs.push("R6: node " + n.id + " trigger '" + kind + "' belongs to family '" + fam + "', not '" + b.family + "'");
      } else if (eras[n.era] !== minEra && lastEras.indexOf(eras[n.era]) < 0) {
        errs.push("R15: node " + n.id + " has no boost but is not in the first era or an endgame era");
      }
    });

    // R7 references
    var gpClasses = idset("great_person_classes");
    var districtsSet = idset("districts");
    rows("districts").forEach(function (d) {
      if (!(d.requires_node in nodes)) errs.push("R7: district " + d.id + " requires_node missing");
      if (!gpClasses.has(d.great_person_class)) errs.push("R7: district " + d.id + " great_person_class missing");
    });
    rows("buildings").forEach(function (b) {
      if (!districtsSet.has(b.district)) errs.push("R7: building " + b.id + " district missing");
      if (!subset(Object.keys(b.yields || {}), enums.yields)) errs.push("R7: building " + b.id + " uses an unknown yield");
      if (!subset(Object.keys(b.great_person_points || {}), Array.from(gpClasses))) errs.push("R7: building " + b.id + " points a missing great-person class");
    });
    rows("improvements").forEach(function (i) {
      if (!subset(Object.keys(i.yields), enums.yields)) errs.push("R7: improvement " + i.id + " unknown yield");
    });
    var effects = {};
    rows("effects").forEach(function (e) { effects[e.id] = e; });
    var conditions = {};
    rows("conditions").forEach(function (c) { conditions[c.id] = c; });
    var unitClasses = Array.from(idset("unit_classes"));
    Object.keys(effects).forEach(function (k) {
      var e = effects[k];
      if (!allIds.has(e.owner)) errs.push("R7: effect " + e.id + " owner " + e.owner + " missing");
      if (e.when !== null && e.when !== undefined && !(e.when in conditions)) errs.push("R7: effect " + e.id + " when " + e.when + " missing");
      var args = e.args || {};
      if ("yield" in args && enums.yields.indexOf(args["yield"]) < 0) errs.push("R7: effect " + e.id + " unknown yield " + args["yield"]);
      if ("unit_classes" in args && !subset(args.unit_classes, unitClasses)) errs.push("R7: effect " + e.id + " unknown unit class");
      if ("eras" in args && !subset(args.eras, Object.keys(eras))) errs.push("R7: effect " + e.id + " unknown era");
      if (enums.scopes.indexOf(e.scope) < 0) errs.push("R8: effect " + e.id + " scope '" + e.scope + "' not in enums");
      if (enums.effect_kinds.indexOf(e.kind) < 0) errs.push("R8: effect " + e.id + " kind '" + e.kind + "' not in enums");
    });
    rows("great_person_individuals").forEach(function (g) {
      if (!gpClasses.has(g["class"]) || !(g.era in eras)) errs.push("R7: great person " + g.id + " has a missing class or era");
      if (g.effect && !(g.effect in effects)) errs.push("R7: great person " + g.id + " effect missing");
    });
    rows("beliefs").forEach(function (b) {
      if (enums.belief_classes.indexOf(b["class"]) < 0) errs.push("R8: belief " + b.id + " class unknown");
      if (!subset(b.effects, Object.keys(effects))) errs.push("R7: belief " + b.id + " effect missing");
    });

    // R9 governments
    var prevTotal = -1;
    rows("governments").slice().sort(function (a, b) { return a.tier - b.tier; }).forEach(function (g) {
      if (!sameSet(Object.keys(g.slots), enums.slot_types)) errs.push("R9: government " + g.id + " must list all four slot types");
      var total = sum(g.slots);
      if (total <= prevTotal) errs.push("R9: government " + g.id + " tier " + g.tier + " has " + total + " slots, not more than the tier below");
      prevTotal = Math.max(prevTotal, total);
      if (g.fixed_bonus && !(g.fixed_bonus in effects)) errs.push("R7: government " + g.id + " fixed_bonus effect missing");
      if (g.requires_node && !(g.requires_node in nodes)) errs.push("R7: government " + g.id + " requires_node missing");
    });

    // R10 meters and adjacency basics, R13 selectors
    rows("meters").forEach(function (m) {
      if (enums.yields.indexOf(m.fed_by) < 0 || enums.cost_models.indexOf(m.cost_model) < 0 || enums.meter_resets.indexOf(m.on_full) < 0) {
        errs.push("R10: meter " + m.id + " uses an unknown value");
      }
    });
    rows("districts").forEach(function (d) {
      if (enums.cost_models.indexOf(d.cost_model) < 0) errs.push("R10: district " + d.id + " cost model unknown");
      d.adjacency.forEach(function (a) {
        if (enums.yields.indexOf(a["yield"]) < 0 || [1, 2, 3].indexOf(a.per) < 0) errs.push("R10: district " + d.id + " adjacency rule invalid");
        Object.keys(a.neighbor).forEach(function (key) {
          var val = a.neighbor[key];
          if (!(key in enums.adjacency_neighbor_keys)) { errs.push("R13: district " + d.id + " adjacency selector '" + key + "' unknown"); return; }
          var sec = enums.adjacency_neighbor_keys[key];
          if (sec && !idset(sec).has(val)) errs.push("R13: district " + d.id + " adjacency " + key + "='" + val + "' not found");
        });
      });
    });

    // R11 unlock consistency
    var unlockedBy = {};
    nodeList.forEach(function (n) {
      n.unlocks.forEach(function (u) {
        var sec = enums.unlock_sections[u.type];
        if (!sec || !idset(sec).has(u.id)) {
          errs.push("R11: node " + n.id + " unlocks " + u.id + " as '" + u.type + "', which does not exist");
          return;
        }
        if (u.id in unlockedBy) errs.push("R11: " + u.id + " is unlocked by both " + unlockedBy[u.id] + " and " + n.id);
        unlockedBy[u.id] = n.id;
      });
    });
    Object.keys(enums.unlock_sections).forEach(function (t) {
      rows(enums.unlock_sections[t]).forEach(function (r) {
        var req = r.requires_node;
        if (req && unlockedBy[r.id] !== req) errs.push("R11: " + r.id + " says requires_node " + req + " but is unlocked by " + unlockedBy[r.id]);
        if (!req && r.id in unlockedBy) errs.push("R11: " + r.id + " is unlocked by " + unlockedBy[r.id] + " but has no requires_node");
      });
    });

    // R12 card effects allowed in slot
    var allowed = enums.slot_allowed_effect_kinds;
    var every = new Set();
    Object.keys(allowed).forEach(function (k) { if (allowed[k] !== "any") allowed[k].forEach(function (x) { every.add(x); }); });
    rows("cards").forEach(function (c) {
      if (enums.slot_types.indexOf(c.slot) < 0) { errs.push("R8: card " + c.id + " slot unknown"); return; }
      if (!subset(c.effects, Object.keys(effects))) { errs.push("R7: card " + c.id + " effect missing"); return; }
      var ok = allowed[c.slot] === "any" ? every : new Set(allowed[c.slot]);
      c.effects.forEach(function (eid) {
        if (!ok.has(effects[eid].kind)) errs.push("R12: card " + c.id + " (" + c.slot + " slot) uses effect kind '" + effects[eid].kind + "', not allowed there");
      });
    });

    // R14 conditions
    Object.keys(conditions).forEach(function (cid) {
      var c = conditions[cid];
      if (c.mode !== "all" && c.mode !== "any") errs.push("R14: condition " + c.id + " mode '" + c.mode + "'");
      c.requirements.forEach(function (r) {
        if (enums.requirement_kinds.indexOf(r.kind) < 0) { errs.push("R8: condition " + c.id + " requirement kind '" + r.kind + "' not in enums"); return; }
        var ref = enums.requirement_arg_refs[r.kind];
        if (ref && !idset(ref[1]).has(r.args[ref[0]])) errs.push("R14: condition " + c.id + " " + r.kind + " references missing " + ref[0] + " '" + r.args[ref[0]] + "'");
      });
    });
    var cstate = {};
    function cvisit(cid) {
      if (cstate[cid] === 1) { errs.push("R14: conditions nest in a loop through " + cid); return; }
      if (cstate[cid] === 2) return;
      cstate[cid] = 1;
      conditions[cid].requirements.forEach(function (r) {
        if (r.kind === "set_is_met" && (r.args.condition in conditions)) cvisit(r.args.condition);
      });
      cstate[cid] = 2;
    }
    Object.keys(conditions).forEach(cvisit);

    // ---- variable checks
    var layout = cfg.tree_layout;
    if (layout === "two_trees") {
      nodeList.forEach(function (n) {
        if (enums.node_trees.indexOf(n.tree) < 0) errs.push("V1: node " + n.id + " tree '" + n.tree + "' is not science/culture (tree_layout=two_trees)");
        else if (n.paid_with !== n.tree) errs.push("V1: node " + n.id + " in the " + n.tree + " tree must be paid with " + n.tree + ", not " + n.paid_with);
      });
    } else if (layout === "one_tree") {
      nodeList.forEach(function (n) {
        if (n.tree !== "main") errs.push("V1: node " + n.id + " tree must be 'main' when tree_layout=one_tree");
        if (n.paid_with !== "science" && n.paid_with !== "culture") errs.push("V1: node " + n.id + " paid_with must be science or culture");
      });
    }

    var mode = cfg.religion_mode;
    var hasRel = rows("religions").length > 0 || rows("beliefs").length > 0;
    var units = rows("faith_units");
    var pressure = data.religion_pressure;
    var sinks = data.faith_sinks;
    if (mode === "pressure_only") {
      if (units.length) errs.push("V2: faith_units must be empty when religion_mode=pressure_only");
      if (!rows("beliefs").length || !rows("religions").length) errs.push("V2: pressure_only needs at least one belief and one religion");
      if (!pressure || !Object.keys(pressure).length) errs.push("V2: pressure_only needs religion_pressure settings");
      if (!sinks || !sinks.length) errs.push("V2: pressure_only needs faith_sinks (what faith is spent on)");
    } else if (mode === "units_and_pressure") {
      if (!units.length) errs.push("V2: units_and_pressure needs faith_units");
      if (!pressure || !Object.keys(pressure).length || !hasRel) errs.push("V2: units_and_pressure needs religion_pressure, beliefs and religions");
    } else if (mode === "off") {
      if (hasRel || units.length) errs.push("V2: religion_mode=off must have no beliefs, religions or faith_units");
    }

    var rewardMode = cfg.node_rewards;
    var minimum = cfg.min_rewards_per_node === undefined ? 1 : cfg.min_rewards_per_node;
    var owned = {};
    Object.keys(effects).forEach(function (k) { owned[effects[k].owner] = (owned[effects[k].owner] || 0) + 1; });
    nodeList.forEach(function (n) {
      var unlocks = n.unlocks.length;
      var endgame = lastEras.indexOf(eras[n.era]) >= 0;
      if (rewardMode === "unlock_or_effect") {
        var total = unlocks + (owned[n.id] || 0);
        if (total < minimum) errs.push("V3: node " + n.id + " gives " + total + " rewards (unlocks plus own effects), below min_rewards_per_node=" + minimum);
      } else if (rewardMode === "unlock_only" || (rewardMode === "empty_allowed" && !endgame)) {
        if (unlocks < minimum) {
          var where = rewardMode === "unlock_only" ? "" : " outside the endgame eras";
          errs.push("V3: node " + n.id + " unlocks " + unlocks + ", below min_rewards_per_node=" + minimum + where + " (node_rewards=" + rewardMode + ")");
        }
      }
    });

    var pool = cfg.great_person_pool;
    rows("great_person_individuals").forEach(function (g) {
      if (pool === "shared_finite" && g.max_claims !== 1) errs.push("V4: great person " + g.id + " must have max_claims=1 when pool is shared_finite");
      if (pool === "personal" && g.max_claims !== null && g.max_claims !== undefined) errs.push("V4: great person " + g.id + " must have max_claims=null when pool is personal");
    });
    return errs;
  }


  // ------------------------------------------------------------------
  // Shared by the playground UI and the parity test: converting the data to
  // match a variable's option, and the "break it" mutations.
  // ------------------------------------------------------------------
  function clone(x) { return JSON.parse(JSON.stringify(x)); }
  function nodeById(d, id) { return d.nodes.filter(function (n) { return n.id === id; })[0]; }

  function convertData(d) {
    var cfg = d.rules_config;
    // tree layout
    if (cfg.tree_layout === "one_tree") {
      cfg.trees = ["main"];
      d.nodes.forEach(function (n) { n.paid_with = n.paid_with || n.tree; n.tree = "main"; });
    }
    // religion mode
    if (cfg.religion_mode === "units_and_pressure") {
      d.faith_units = [{ id: "fu.messenger", charges: 3, strength: 100, evict_percent: 10, cost: 75 }];
    } else if (cfg.religion_mode === "off") {
      d.beliefs = []; d.religions = []; d.faith_units = [];
      d.effects = d.effects.filter(function (e) { return e.id.indexOf("eff.bel_") !== 0; });
      var dropped = { "cond.hearth_on_field": 1, "cond.stone_on_quarry": 1, "cond.chapter_with_chapel": 1, "cond.accord_after_contact": 1 };
      d.conditions = d.conditions.filter(function (c) { return !dropped[c.id]; });
      var c3 = nodeById(d, "node.c3");
      if (c3) c3.boost = { family: "chain_node", trigger: { kind: "have_node", node: "node.s2" }, percent: 40 };
    }
    // node rewards: unlock_only removes nodes that give nothing by unlocking (and what they own)
    if (cfg.node_rewards === "unlock_only") {
      var thin = {};
      d.nodes.forEach(function (n) { if (!n.unlocks.length) thin[n.id] = true; });
      d.nodes = d.nodes.filter(function (n) { return !thin[n.id]; });
      d.effects = d.effects.filter(function (e) { return !thin[e.owner]; });
    }
    // great-person pool
    if (cfg.great_person_pool === "personal") {
      d.great_person_individuals.forEach(function (g) { g.max_claims = null; });
    }
    return d;
  }

  // Each break: id, label, what it does, the rule code expected to fire, and the change.
  var MUTATIONS = [
    { id: "dup", label: "Duplicate an id", expect: "R1", note: "Add a second copy of a card.",
      apply: function (d) { d.cards.push(clone(d.cards[0])); } },
    { id: "cycle", label: "Make a loop in the tree", expect: "R2", note: "The first node now requires one that requires it.",
      apply: function (d) { nodeById(d, "node.s1").requires = ["node.s2"]; } },
    { id: "skip", label: "Skip an era", expect: "R3", note: "A third-era node requires a first-era node directly.",
      apply: function (d) { nodeById(d, "node.s6").requires = ["node.s1"]; } },
    { id: "cheap", label: "Make a late node cheap", expect: "R5", note: "A third-era node costs 10.",
      apply: function (d) { nodeById(d, "node.s6").cost = 10; } },
    { id: "family", label: "Mislabel a boost", expect: "R6", note: "A build-trigger boost is filed under combat.",
      apply: function (d) { nodeById(d, "node.s2").boost.family = "combat"; } },
    { id: "lateNone", label: "Remove a late boost", expect: "R15", note: "A second-era node gets no boost.",
      apply: function (d) { nodeById(d, "node.s4").boost = { family: "none", percent: 0 }; } },
    { id: "enumKind", label: "Invent an effect kind", expect: "R8", note: "An effect uses a kind that is not on the closed list.",
      apply: function (d) { d.effects[0].kind = "make_it_rain"; } },
    { id: "unlockType", label: "Unlock the wrong type", expect: "R11", note: "A node says it unlocks a building but names a district.",
      apply: function (d) { nodeById(d, "node.s2").unlocks = [{ type: "building", id: "dist.study" }]; } },
    { id: "cardSlot", label: "Put a trade effect on a military card", expect: "R12", note: "The drill card now carries the caravan effect.",
      apply: function (d) { d.cards.filter(function (c) { return c.id === "card.drill"; })[0].effects = ["eff.caravan"]; } },
    { id: "adjacency", label: "Point adjacency at a missing terrain", expect: "R13", note: "A district likes a terrain that does not exist.",
      apply: function (d) { d.districts[0].adjacency[0].neighbor = { terrain: "terrain.moon" }; } },
    { id: "cond", label: "Break a condition", expect: "R14", note: "A condition names a building that does not exist.",
      apply: function (d) { d.conditions[0].requirements[0].args.building = "bld.nope"; } },
    { id: "slots", label: "Flatten the government slots", expect: "R9", note: "Every government gets the same slots.",
      apply: function (d) { d.governments.forEach(function (g) { g.slots = { military: 1, economic: 1, diplomatic: 0, wildcard: 0 }; }); } },
    { id: "emptyUnlock", label: "Give a middle node nothing", expect: "V3", note: "A second-era node unlocks nothing and has no effect of its own, so it gives you nothing.",
      apply: function (d) { nodeById(d, "node.s4").unlocks = []; d.effects = d.effects.filter(function (e) { return e.owner !== "node.s4"; }); } },
    { id: "stripEffect", label: "Strip the bonus from the last node", expect: "V3", note: "The final culture node unlocks nothing; remove its bonus effect and it gives nothing (fails unless empty nodes are allowed).",
      apply: function (d) { d.effects = d.effects.filter(function (e) { return e.owner !== "node.c5"; }); } },
    { id: "faithUnit", label: "Add a faith unit", expect: "V2", note: "Fails when religion is pressure-only or off.",
      apply: function (d) { d.faith_units = (d.faith_units || []).concat([{ id: "fu.extra", charges: 3 }]); } },
    { id: "claims", label: "Make one great person claimable by all", expect: "V4", note: "Fails when the pool is shared.",
      apply: function (d) { d.great_person_individuals[0].max_claims = null; } }
  ];

  // pristine data + config + options -> the dataset the checker sees
  function buildDataset(pristine, config, convert, breaks) {
    var d = clone(pristine);
    Object.keys(config).forEach(function (k) { d.rules_config[k] = config[k]; });
    if (convert) convertData(d);
    (breaks || []).forEach(function (id) {
      var m = MUTATIONS.filter(function (x) { return x.id === id; })[0];
      if (m) m.apply(d);
    });
    return d;
  }

  var api = { check: check, SECTIONS_WITH_IDS: SECTIONS_WITH_IDS, MUTATIONS: MUTATIONS, buildDataset: buildDataset, convertData: convertData };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  root.SchemaCheck = api;
})(typeof globalThis !== "undefined" ? globalThis : this);
