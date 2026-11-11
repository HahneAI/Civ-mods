/* Toy simulation over a schema dataset. Source: custom (docs/schema).
 *
 * What it is: a small, deterministic model that plays the example dataset forward turn by turn
 * (city growth, yields, research, religion spread, great people) so the four design variables can be
 * compared with numbers. What it is NOT: a balance forecast. Every constant is a visible assumption
 * (DEFAULTS), tuned for plausible shapes, not calibrated to any game. Use it to compare setups
 * against each other, never to read an absolute turn count.
 *
 * Deliberate simplifications: one yield pool per tree, greedy cheapest-first research, every city
 * builds every unlocked district and building after a fixed delay, a straight line of cities,
 * policy cards ignored, rivals are a smooth points-per-turn curve.
 */
(function (root) {
  "use strict";

  var DEFAULTS = {
    turns: 200,
    city_interval: 25, max_cities: 8,
    food_surplus: 4, size_cap: 12,
    base_sci: 2, base_cul: 1.5, base_faith: 1, sci_per_citizen: 0.5, cul_per_citizen: 0.35,
    building_delay: 15,
    boost_delay_own: 6, boost_delay_combat: 30, boost_delay_trade: 20, boost_delay_explore: 18,
    religion_found_turn: 40, convert_threshold: 60, city_spacing: 5, unit_push: 40, unit_cost_step: 25,
    rival_strength: 1.0, rival_start: 30, rival_rate: 2, rival_growth: 150
  };
  var DESCRIPTIONS = {
    turns: "Turns to simulate", city_interval: "Turns between new cities", max_cities: "Maximum cities", food_surplus: "Food surplus per city per turn",
    size_cap: "City size cap", base_sci: "Base science per city", base_cul: "Base culture per city", sci_per_citizen: "Science per citizen", cul_per_citizen: "Culture per citizen",
    building_delay: "Turns to build each district or building", religion_found_turn: "Turn the religion is adopted", convert_threshold: "Pressure a city needs to convert",
    unit_push: "Pressure per missionary charge", rival_strength: "Rival great-people pace (1 = default)", rival_start: "Turn rivals start earning points"
  };

  function clone(x) { return JSON.parse(JSON.stringify(x)); }
  function by(list) { var m = {}; (list || []).forEach(function (x) { m[x.id] = x; }); return m; }

  function simulate(data, userParams) {
    var P = {}; Object.keys(DEFAULTS).forEach(function (k) { P[k] = DEFAULTS[k]; });
    Object.keys(userParams || {}).forEach(function (k) { if (userParams[k] !== undefined && userParams[k] !== null && !isNaN(userParams[k])) P[k] = Number(userParams[k]); });
    var cfg = data.rules_config || {};
    var nodes = clone(data.nodes || []);
    var nodeMap = by(nodes);
    var eraIdx = {}; (data.eras || []).forEach(function (e) { eraIdx[e.id] = e; });
    var layout = cfg.tree_layout;
    var pooled = layout === "one_tree";

    // ----- helpers from the data
    var foodMeter = (data.meters || []).filter(function (m) { return m.id === "meter_food"; })[0];
    var fm = foodMeter ? foodMeter.cost_params : { start: 15, per_step: 8, exponent: 1.5 };
    function foodNeeded(size) { return fm.start + fm.per_step * (size - 1) + Math.pow(size - 1, fm.exponent); }
    var buildings = data.buildings || [], districts = data.districts || [];
    var gov = data.governments || [];
    var effects = data.effects || [];

    // ----- state
    var done = {}, doneTurn = {}, avail = {}, progress = {}, boosted = {}, boostAt = {};
    var unlockTurn = {};
    nodes.forEach(function (n) { progress[n.id] = 0; });
    var religionOn = cfg.religion_mode !== "off" && (data.beliefs || []).length > 0;
    var religionTurn = religionOn ? P.religion_found_turn : null;
    var cities = [], pressure = [], follows = [];
    var faith = 0, unitCost = 75, unitsBought = 0;
    var wasted = { science: 0, culture: 0, pooled: 0 }, wastedBlocked = 0;
    var tailTurns = 0, researchTurns = 0;
    var series = { turn: [], nodes_total: [], nodes_science: [], nodes_culture: [], religion_share: [], cities: [], gp_claims: [], gp_rival: [] };

    // ----- great people
    var gpClasses = (data.great_person_classes || []).map(function (c) { return c.id; });
    var individuals = (data.great_person_individuals || []).slice().sort(function (a, b) { return ((eraIdx[a.era] || {}).index || 0) - ((eraIdx[b.era] || {}).index || 0); });
    var shared = cfg.great_person_pool === "shared_finite";
    var pools = {}, playerPts = {}, rivalPts = {}, claims = [], rivalClaims = 0, gpWasted = 0;
    gpClasses.forEach(function (c) { pools[c] = individuals.filter(function (i) { return i["class"] === c; }); playerPts[c] = 0; rivalPts[c] = 0; });
    var classTotal = {}; gpClasses.forEach(function (c) { classTotal[c] = pools[c].length; });

    function nodeAvailable(n) { return !done[n.id] && n.requires.every(function (r) { return done[r]; }); }
    function activeTurn(entityId, requiresNode) { // turn the thing starts producing, or null
      var u = unlockTurn[entityId];
      return u === undefined ? null : u + P.building_delay;
    }

    function completeNode(n, t) {
      done[n.id] = true; doneTurn[n.id] = t;
      (n.unlocks || []).forEach(function (u) { unlockTurn[u.id] = t; });
      nodes.forEach(function (m) { if (avail[m.id] === undefined && nodeAvailable(m)) avail[m.id] = t; });
    }
    nodes.forEach(function (n) { if (!n.requires.length) avail[n.id] = 0; });

    function boostFireTurn(n) {
      var b = n.boost || {};
      if (!b.family || b.family === "none" || avail[n.id] === undefined) return null;
      var trig = b.trigger || {}, count = trig.count || 1;
      switch (b.family) {
        case "build_or_own": return avail[n.id] + P.boost_delay_own * count;
        case "chain_node": return done[trig.node] ? Math.max(avail[n.id], doneTurn[trig.node]) : null;
        case "combat": return avail[n.id] + P.boost_delay_combat * count;
        case "diplomacy_trade": return avail[n.id] + P.boost_delay_trade * count;
        case "explore": return avail[n.id] + P.boost_delay_explore;
        case "religion": return religionTurn === null ? null : Math.max(avail[n.id], religionTurn);
      }
      return null;
    }

    function govFactor(yieldName, t) {
      // highest-tier unlocked government's fixed bonus, plus effects owned by finished nodes; only unconditional yield_pct
      var f = 1, best = null;
      gov.forEach(function (g) { if ((!g.requires_node || done[g.requires_node]) && (best === null || g.tier > best.tier)) best = g; });
      effects.forEach(function (e) {
        if (e.kind !== "yield_pct" || (e.when !== null && e.when !== undefined) || !e.args || e.args["yield"] !== yieldName) return;
        var active = (best && best.fixed_bonus === e.id) || (done[e.owner] === true);
        if (active) f *= 1 + e.args.amount / 100;
      });
      return f;
    }

    var tailIds = {}; nodes.forEach(function (n) { if (!(n.unlocks || []).length) tailIds[n.id] = true; });
    var religionHit50 = null, religionAt100 = null;

    for (var t = 1; t <= P.turns; t++) {
      // ---- cities and growth
      var target = Math.min(P.max_cities, 1 + Math.floor((t - 1) / P.city_interval));
      while (cities.length < target) { cities.push({ size: 1, food: 0, x: cities.length * P.city_spacing, founded: t, converted: null }); pressure.push(0); follows.push(false); }
      var citizens = 0;
      cities.forEach(function (c) {
        c.food += P.food_surplus;
        var need = foodNeeded(c.size);
        if (c.food >= need && c.size < P.size_cap) { c.food -= need; c.size += 1; }
        citizens += c.size;
      });
      var n = cities.length;

      // ---- yields from buildings
      var bY = { science: 0, culture: 0, faith: 0 };
      var districtActive = {};
      districts.forEach(function (d) { var a = activeTurn(d.id); districtActive[d.id] = a !== null && t >= a; });
      buildings.forEach(function (b) {
        var a = activeTurn(b.id);
        if (a === null || t < a || !districtActive[b.district]) return;
        Object.keys(b.yields || {}).forEach(function (y) { if (bY[y] !== undefined) bY[y] += b.yields[y] * n; });
      });
      var sci = (P.base_sci * n + P.sci_per_citizen * citizens + bY.science) * govFactor("science", t);
      var cul = (P.base_cul * n + P.cul_per_citizen * citizens + bY.culture) * govFactor("culture", t);
      var fai = (P.base_faith * n + bY.faith) * govFactor("faith", t);

      // ---- boosts
      nodes.forEach(function (nd) {
        if (done[nd.id] || boosted[nd.id]) return;
        var at = boostFireTurn(nd);
        if (at !== null && t >= at) {
          boosted[nd.id] = true;
          progress[nd.id] = Math.min(nd.cost - 1, progress[nd.id] + nd.cost * nd.boost.percent / 100);
        }
      });

      // ---- research
      var rpools = pooled ? [{ name: "pooled", amount: sci + cul, filter: function () { return true; } }]
                         : [{ name: "science", amount: sci, filter: function (nd) { return nd.tree === "science"; } },
                            { name: "culture", amount: cul, filter: function (nd) { return nd.tree === "culture"; } }];
      var spentAny = false, spentTail = false, incompleteAtStart = Object.keys(done).length < nodes.length;
      rpools.forEach(function (pl) {
        var budget = pl.amount, guard = 0;
        while (budget > 1e-9 && guard++ < nodes.length + 2) {
          var cands = nodes.filter(function (nd) { return pl.filter(nd) && nodeAvailable(nd); });
          if (!cands.length) { wasted[pl.name] += budget; if (incompleteAtStart) wastedBlocked += budget; break; }
          cands.sort(function (a, b) { return (a.cost - progress[a.id]) - (b.cost - progress[b.id]); });
          var cur = cands[0], need = cur.cost - progress[cur.id];
          spentAny = true; if (tailIds[cur.id]) spentTail = true;
          if (budget >= need) { budget -= need; progress[cur.id] = cur.cost; completeNode(cur, t); }
          else { progress[cur.id] += budget; budget = 0; }
        }
      });
      if (spentAny) researchTurns++;
      if (spentTail) tailTurns++;

      // ---- religion
      if (religionOn && t >= religionTurn) {
        if (t === religionTurn) { follows[0] = true; cities[0].converted = t; }
        var shrine = !!districtActive["dist.shrine"];
        var rp = data.religion_pressure || {};
        var radius = rp.radius || 10, per = rp.per_turn_adjacent_city || 1, holy = rp.holy_city_multiplier || 4, shrineMult = rp.shrine_district_multiplier || 2;
        for (var j = 0; j < n; j++) {
          if (follows[j]) continue;
          for (var k = 0; k < n; k++) {
            if (!follows[k] || Math.abs(cities[j].x - cities[k].x) > radius) continue;
            pressure[j] += per * (k === 0 ? holy : 1) * (shrine ? shrineMult : 1);
          }
        }
        if (cfg.religion_mode === "units_and_pressure") {
          faith += fai;
          while (faith >= unitCost) {
            faith -= unitCost; unitCost += P.unit_cost_step; unitsBought++;
            var charges = ((data.faith_units && data.faith_units[0] && data.faith_units[0].charges) || 3);
            for (var ch = 0; ch < charges; ch++) {
              var tgt = -1;
              for (var q = 0; q < n; q++) if (!follows[q]) { tgt = q; break; }
              if (tgt >= 0) pressure[tgt] += P.unit_push;
            }
          }
        }
        for (var m2 = 0; m2 < n; m2++) if (!follows[m2] && pressure[m2] >= P.convert_threshold) { follows[m2] = true; cities[m2].converted = t; }
      }
      var fcount = follows.filter(Boolean).length, share = n ? fcount / n : 0;
      if (religionOn && religionHit50 === null && share >= 0.5 && t >= religionTurn) religionHit50 = t;
      if (religionOn && t === 100) religionAt100 = Math.round(share * 1000) / 10;

      // ---- great people
      var rivalRate = P.rival_strength * P.rival_rate * (1 + t / P.rival_growth);
      gpClasses.forEach(function (c) {
        var rate = 0;
        districts.forEach(function (d) { if (d.great_person_class === c && districtActive[d.id]) rate += (d.gp_points_per_turn || 0) * n; });
        buildings.forEach(function (b) {
          var a = activeTurn(b.id);
          if (a !== null && t >= a && districtActive[b.district] && b.great_person_points && b.great_person_points[c]) rate += b.great_person_points[c] * n;
        });
        if (!pools[c].length) { gpWasted += rate; return; }
        playerPts[c] += rate;
        if (shared && t >= P.rival_start) rivalPts[c] += rivalRate;
        var loop = 0;
        while (pools[c].length && loop++ < 20) {
          var next = pools[c][0], cost = (eraIdx[next.era] || { great_person_base_cost: 60 }).great_person_base_cost;
          var pOk = playerPts[c] >= cost, rOk = shared && rivalPts[c] >= cost;
          if (!pOk && !rOk) break;
          var playerWins = pOk && (!rOk || (playerPts[c] / cost) >= (rivalPts[c] / cost));
          if (playerWins) { playerPts[c] -= cost; claims.push({ id: next.id, turn: t }); } else { rivalPts[c] -= cost; rivalClaims++; }
          pools[c].shift();
        }
      });

      series.turn.push(t); series.nodes_total.push(Object.keys(done).length);
      series.nodes_science.push(nodes.filter(function (x) { return done[x.id] && x.tree === "science"; }).length);
      series.nodes_culture.push(nodes.filter(function (x) { return done[x.id] && x.tree === "culture"; }).length);
      series.religion_share.push(religionOn ? Math.round(share * 1000) / 10 : 0);
      series.cities.push(n); series.gp_claims.push(claims.length); series.gp_rival.push(rivalClaims);
    }

    function lastDone(filter) {
      var ts = nodes.filter(filter).map(function (x) { return doneTurn[x.id]; });
      return ts.length && ts.every(function (v) { return v !== undefined; }) ? Math.max.apply(null, ts) : null;
    }
    function metricsGap() {
      var a = lastDone(function (x) { return x.tree === "science"; }), b = lastDone(function (x) { return x.tree === "culture"; });
      return a === null || b === null ? null : Math.abs(a - b);
    }
    var lags = cities.filter(function (c, i) { return i > 0 && c.converted !== null; }).map(function (c) { return c.converted - Math.max(c.founded, religionTurn || 0); });
    var lagAvg = lags.length ? Math.round(lags.reduce(function (a, b) { return a + b; }, 0) / lags.length * 10) / 10 : null;
    var unconverted = cities.filter(function (c) { return c.converted === null; }).length;
    var totalCost = nodes.reduce(function (s, x) { return s + x.cost; }, 0);
    var tailCost = nodes.filter(function (x) { return tailIds[x.id]; }).reduce(function (s, x) { return s + x.cost; }, 0);
    var lockedOut = gpClasses.filter(function (c) { return !claims.some(function (cl) { return cl.id && individuals.filter(function (i) { return i.id === cl.id; })[0]["class"] === c; }) && classTotal[c] > 0; }).length;
    var metrics = {
      nodes_done: Object.keys(done).length, nodes_total: nodes.length,
      finish_all: lastDone(function () { return true; }),
      finish_science: pooled ? null : lastDone(function (x) { return x.tree === "science"; }),
      finish_culture: pooled ? null : lastDone(function (x) { return x.tree === "culture"; }),
      wasted_yield: Math.round(wasted.science + wasted.culture + wasted.pooled),
      wasted_while_blocked: Math.round(wastedBlocked),
      blocked_gap: (pooled || metricsGap() === null) ? 0 : metricsGap(),
      tail_nodes: Object.keys(tailIds).length, tail_cost_share: totalCost ? Math.round(tailCost / totalCost * 1000) / 10 : 0,
      tail_turns: tailTurns, tail_turn_share: researchTurns ? Math.round(tailTurns / researchTurns * 1000) / 10 : 0,
      total_cost: totalCost,
      religion_on: religionOn, religion_turn: religionTurn, religion_half: religionHit50, religion_at_100: religionAt100, religion_lag: lagAvg, religion_unconverted: unconverted,
      religion_end_share: series.religion_share[series.religion_share.length - 1], faith_units_bought: unitsBought,
      gp_player: claims.length, gp_rival: rivalClaims, gp_wasted: Math.round(gpWasted), gp_locked_classes: lockedOut, gp_total: individuals.length
    };
    return { metrics: metrics, series: series, params: P, doneTurn: doneTurn };
  }

  // Run the sim for each option of one variable, with everything else as given.
  function compare(S, pristine, config, variableId, variants, params) {
    var v = variants[variableId];
    return Object.keys(v.options).map(function (opt) {
      var cfg = {}; Object.keys(config).forEach(function (k) { cfg[k] = config[k]; });
      cfg[v.config_key] = opt;
      var d = S.buildDataset(pristine, cfg, true, []);
      var r = simulate(d, params);
      return { option: opt, isDecision: opt === v.decision, result: r };
    });
  }

  var api = { simulate: simulate, compare: compare, DEFAULTS: DEFAULTS, DESCRIPTIONS: DESCRIPTIONS };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  root.SchemaSim = api;
})(typeof globalThis !== "undefined" ? globalThis : this);
