<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>CDA Runtime Control Plane - Decision Ledger & Attested Path</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
/* CSS Styles & Theme Setup */
:root {
  --bg: #EDEFF1;
  --s: #F8F9FA;
  --l: #D5D9DE;
  --t: #14181D;
  --m: #5F6B7A;
  --ok: #3B6E8C; /* PERMIT */
  --rm: #2B8A8A; /* REMEDIATE */
  --rv: #B08A2E; /* ESCALATE */
  --dn: #A23A3F; /* BLOCK */
  --in: #6B5B95; /* INDETERMINATE */
  box-sizing: border-box;
  padding-top: env(safe-area-inset-top, 0px);
  padding-bottom: env(safe-area-inset-bottom, 0px);
}

@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --bg: #0B0E12;
    --s: #10141A;
    --l: #222932;
    --t: #E4E7EB;
    --m: #8993A0;
    --ok: #5F86A6;
    --rm: #3FA8A8;
    --rv: #C9A25B;
    --dn: #C4585D;
    --in: #8B7BB5;
  }
}

:root[data-theme="dark"] {
  --bg: #0B0E12;
  --s: #10141A;
  --l: #222932;
  --t: #E4E7EB;
  --m: #8993A0;
  --ok: #5F86A6;
  --rm: #3FA8A8;
  --rv: #C9A25B;
  --dn: #C4585D;
  --in: #8B7BB5;
}

html { scroll-padding-top: env(safe-area-inset-top, 0px); }
* { box-sizing: border-box; margin: 0; }
body { background: var(--bg); color: var(--t); font: 400 13px/1.5 "IBM Plex Sans", system-ui, sans-serif; }
.n { font-family: "IBM Plex Mono", ui-monospace, monospace; font-variant-numeric: tabular-nums; }
.m { color: var(--m); }
.lab { font-size: 12px; color: var(--m); }

/* Layout Structure */
header { display: flex; justify-content: space-between; align-items: center; gap: 16px; flex-wrap: wrap; padding: 16px 24px; border-bottom: 1px solid var(--l); }
.brand { font-weight: 600; font-size: 15px; letter-spacing: .04em; }
.st { display: flex; gap: 20px; align-items: center; flex-wrap: wrap; font-size: 12px; }
.dot { display: inline-block; width: 7px; height: 7px; border-radius: 50%; margin-right: 6px; background: var(--ok); }

.grid { display: grid; grid-template-columns: 240px minmax(0,1fr) 340px; gap: 1px; background: var(--l); border-bottom: 1px solid var(--l); }
.g2 { grid-template-columns: minmax(0,1fr) 320px 320px; }

.p { background: var(--bg); padding: 20px 22px; min-width: 0; position: relative; }
.p::before { content: ""; position: absolute; inset: 0; pointer-events: none; opacity: 0; transition: opacity .4s; background: radial-gradient(340px circle at var(--x,50%) var(--y,50%), color-mix(in srgb, var(--t) 6%, transparent), transparent 70%); }
.p:hover::before { opacity: 1; }

/* KPI Cards */
.k { padding: 10px 0; border-bottom: 1px solid var(--l); }
.k:first-of-type { padding-top: 0; }
.k:last-child { border: 0; }
.k b { display: block; font: 300 32px/1 "IBM Plex Sans"; letter-spacing: -.02em; margin: 6px 0 4px; }
.k svg { display: block; margin-top: 4px; }

h2 { font-size: 12px; font-weight: 500; color: var(--m); text-transform: uppercase; letter-spacing: .05em; }
.bar { display: flex; justify-content: space-between; align-items: center; gap: 12px; flex-wrap: wrap; margin-bottom: 10px; }
.seg { display: flex; }
.seg button { border-radius: 0; }
.seg button + button { border-left: 0; }
.seg button[aria-pressed="true"] { border-color: var(--t); background: var(--s); }

.alert { display: flex; justify-content: space-between; align-items: center; gap: 12px; flex-wrap: wrap; border: 1px solid var(--rv); padding: 10px 14px; margin-bottom: 14px; background: color-mix(in srgb, var(--rv) 8%, transparent); }
.alert.h { display: none; }

button { font: 500 12px "IBM Plex Sans", sans-serif; color: var(--t); background: none; border: 1px solid var(--l); padding: 6px 12px; cursor: pointer; transition: all .15s ease; }
button:hover { border-color: var(--t); }
button:focus-visible { outline: 2px solid var(--ok); outline-offset: 2px; }

/* Map & Graph Elements */
#mp { display: block; }
#mp .bg { fill: color-mix(in srgb, var(--t) 16%, var(--bg)); stroke: var(--bg); stroke-width: .4; }
#mp .ag { fill: color-mix(in srgb, var(--t) 16%, var(--bg)); stroke: var(--bg); stroke-width: .6; cursor: pointer; transition: fill .9s; }
#mp .ag.hv, #mp .ag.sel { stroke: var(--t); stroke-width: 1.3; }
#gr line { stroke: var(--m); stroke-opacity: .35; stroke-width: .5; stroke-dasharray: 1 4; }
#hb circle { fill: var(--t); opacity: .75; pointer-events: none; }
.rip { fill: none; stroke-width: 1.2; vector-effect: non-scaling-stroke; transform-box: fill-box; transform-origin: center; }

.lg { display: flex; align-items: center; gap: 12px; margin-top: 10px; font-size: 12px; color: var(--m); }
.lg i { flex: 1; max-width: 260px; height: 6px; background: linear-gradient(90deg, var(--ok) 0%, var(--rm) 25%, var(--rv) 50%, var(--dn) 75%, var(--in) 100%); }

/* Focus & Stochastic Metrics */
.dl { display: grid; grid-template-columns: 110px 1fr; gap: 6px 10px; margin-top: 10px; font-size: 12px; }
.dl dt { color: var(--m); }
.dl dd { word-break: break-all; }

button.rw { display: grid; grid-template-columns: 1fr 64px 40px 44px; gap: 8px; align-items: center; width: 100%; text-align: left; border: 0; border-bottom: 1px solid var(--l); padding: 7px 0; font-weight: 400; }
.rw .b2 { height: 5px; background: var(--l); display: block; }
.rw .b2 i { display: block; height: 100%; }

/* Queue & Tables */
.q { padding: 12px 0; border-bottom: 1px solid var(--l); cursor: pointer; }
.q .r { display: flex; justify-content: space-between; gap: 8px; }
.q .a { display: flex; gap: 8px; margin-top: 10px; }

.tw { overflow-x: auto; background: var(--s); margin-top: 12px; border: 1px solid var(--l); }
table { width: 100%; border-collapse: collapse; min-width: 620px; }
th { font-weight: 500; font-size: 11.5px; color: var(--m); text-align: left; padding: 8px 12px; border-bottom: 1px solid var(--l); background: var(--bg); }
td { padding: 8px 12px; border-bottom: 1px solid var(--l); font-size: 12px; }
tbody tr { cursor: pointer; }
tbody tr:hover, tbody tr.on { background: color-mix(in srgb, var(--t) 4%, var(--bg)); }

.badge { display: inline-flex; align-items: center; gap: 5px; padding: 2px 6px; border-radius: 2px; font-size: 11px; font-weight: 500; }

.tok { margin-top: 12px; padding-top: 10px; border-top: 1px solid var(--l); font-size: 11px; color: var(--m); word-break: break-all; }
.chain { display: flex; align-items: center; overflow-x: auto; padding: 14px 24px; background: var(--s); border-bottom: 1px solid var(--l); }
.blk { border: 1px solid var(--l); padding: 5px 9px; font-size: 11px; white-space: nowrap; background: var(--bg); }
.ln { width: 16px; height: 1px; background: var(--l); flex: none; }

footer { padding: 14px 24px; font-size: 11.5px; color: var(--m); }

@media (max-width: 1080px) { .grid, .g2 { grid-template-columns: 1fr; } }
@media (prefers-reduced-motion: no-preference) {
  .new { animation: nw 1.8s ease-out; }
  @keyframes nw { from { background: color-mix(in srgb, var(--rv) 24%, transparent); } to { background: transparent; } }
  .live { animation: br 2.6s ease-in-out infinite; }
  @keyframes br { 50% { opacity: .3; } }
  .rip { animation: rp 1.6s ease-out forwards; }
  @keyframes rp { from { transform: scale(1); opacity: 1; } to { transform: scale(11); opacity: 0; } }
}
</style>
</head>
<body>

<header>
  <div class="brand">CDA <span class="m" style="font-weight:400">Decision Ledger & Attested Control Plane</span></div>
  <div class="st">
    <span id="ha" class="m"></span>
    <span><span class="dot live"></span>Verified Chain, Block <span class="n" id="bn">14,203</span></span>
    <span class="n" id="clk">UTC 00:00:00</span>
  </div>
</header>

<!-- Top Panel Grid -->
<div class="grid">
  <!-- 5-State Verdict KPI Panel -->
  <section class="p" aria-label="24h Verdict Summary">
    <h2 style="margin-bottom:12px">24h Verdict Distribution</h2>
    <div class="k"><span class="lab"><span class="dot"></span>PERMIT</span><b class="n" id="k0">0</b><span class="lab" id="p0"></span><svg id="s0" width="190" height="20"></svg></div>
    <div class="k"><span class="lab"><span class="dot" style="background:var(--rm)"></span>REMEDIATE</span><b class="n" id="k1">0</b><span class="lab" id="p1"></span><svg id="s1" width="190" height="20"></svg></div>
    <div class="k"><span class="lab"><span class="dot" style="background:var(--rv)"></span>ESCALATE (HITL)</span><b class="n" id="k2">0</b><span class="lab" id="p2"></span><svg id="s2" width="190" height="20"></svg></div>
    <div class="k"><span class="lab"><span class="dot" style="background:var(--dn)"></span>BLOCK</span><b class="n" id="k3">0</b><span class="lab" id="p3"></span><svg id="s3" width="190" height="20"></svg></div>
    <div class="k"><span class="lab"><span class="dot" style="background:var(--in)"></span>INDETERMINATE</span><b class="n" id="k4">0</b><span class="lab" id="p4"></span><svg id="s4" width="190" height="20"></svg></div>
  </section>

  <!-- Risk Map & Monte Carlo Simulation -->
  <section class="p" aria-label="Geographic Risk Map">
    <div class="alert h" id="al"><div id="at"></div><div><button id="dm">Dismiss</button> <button id="go" style="border-color:var(--rv)">View Prediction</button></div></div>
    <div class="bar"><h2>Jurisdiction Risk Map</h2>
      <div class="seg"><button id="l0" aria-pressed="true">Current</button><button id="l1" aria-pressed="false">30-Day Monte Carlo</button></div></div>
    <svg id="mp" viewBox="0 0 900 441" width="100%" role="img" aria-label="World map displaying risk distribution"><g id="gr"></g><g id="pg"></g><g id="hb"></g><g id="rp"></g></svg>
    <p id="nm" class="lab" hidden>Map projection library unavailable. Showing simplified spatial nodes.</p>
    <div class="lg"><span>Stable</span><i></i><span>High Risk</span><span style="margin-left:auto">Gray: No active agents</span></div>
  </section>

  <!-- Stochastic Semantic Risk & Focus Panel -->
  <section class="p" aria-label="Stochastic Semantic Risk & Focus">
    <h2>Stochastic Semantic Risk Index</h2>
    <div style="margin-top:8px; padding:10px; border:1px solid var(--l); background:var(--s)">
      <div style="display:flex; justify-content:space-between; align-items:baseline">
        <span class="lab">Raw Drift vs Enforced Boundary</span>
        <span class="n" id="sri_val" style="font-weight:600; font-size:14px; color:var(--rv)">0.42 Drift</span>
      </div>
      <!-- Comparative SVG Chart: Raw LLM Variance vs Enforced Cutoff -->
      <svg id="drift_chart" viewBox="0 0 280 60" width="100%" style="margin-top:6px; display:block">
        <!-- Background Grid -->
        <line x1="0" y1="50" x2="280" y2="50" stroke="var(--l)" stroke-dasharray="2 2" />
        <!-- Raw Stochastic Output Variance (Unfiltered LLM) -->
        <path id="raw_drift_path" d="M 0,35 Q 40,10 80,42 T 160,15 T 240,48 T 280,20" fill="none" stroke="var(--m)" stroke-width="1.2" stroke-dasharray="3 3" opacity="0.75" />
        <!-- CDA Enforced Bounded Line (Zero-Variance Deterministic Execution) -->
        <path id="cda_bound_path" d="M 0,35 L 120,35 L 120,50 L 280,50" fill="none" stroke="var(--ok)" stroke-width="2" />
        <!-- Enforcement Boundary Cutoff Marker -->
        <line x1="120" y1="5" x2="120" y2="55" stroke="var(--dn)" stroke-width="1.2" stroke-dasharray="2 2" />
        <text x="124" y="14" font-size="9" fill="var(--dn)" font-family="IBM Plex Mono">Enforcement Cutoff</text>
      </svg>
      <div style="display:flex; justify-content:space-between; font-size:10px; color:var(--m); margin-top:4px">
        <span>--- Raw LLM Drift</span>
        <span style="color:var(--ok)">— CDA Enforced (Zero Drift)</span>
      </div>
    </div>

    <div id="dt" style="margin-top:14px"></div>
    <h2 style="margin:16px 0 4px">High Risk Jurisdictions</h2>
    <div id="rk"></div>
  </section>
</div>

<!-- Bottom Panel Grid -->
<div class="grid g2">
  <!-- Decision Ledger Table -->
  <section class="p" aria-label="Decision Ledger">
    <h2>Recent Attested Decisions</h2>
    <div class="tw"><table>
      <thead><tr><th>Time</th><th>Jurisdiction</th><th>Agent ID</th><th>Regime</th><th>Action</th><th>Verdict</th></tr></thead>
      <tbody id="tb"></tbody>
    </table></div>
  </section>

  <!-- Escalation Queue (HITL / ESCALATE) -->
  <section class="p" aria-label="Human Escalation Queue">
    <h2>Human-In-The-Loop Queue (<span id="qc">0</span>)</h2>
    <div id="ql"></div>
  </section>

  <!-- Attested Path & PASETO Inspection -->
  <section class="p" aria-label="Attested Evaluation Path Detail">
    <h2>Attested Path & PASETO v4 Detail</h2>
    <div id="in"></div>
  </section>
</div>

<!-- Blockchain Ledger Bar -->
<div class="chain" id="ch" aria-label="Blockchain Block Ledger"></div>

<footer>
  CDA Reference Architecture for ITU-T FG-TIDA. Aligned with UC #14 (Zhao - Attested Evaluation Path), UC #17 (Gorlla - 5-State Taxonomy), and UC #9 (Lineage & Governance). Monte Carlo simulation based on 2,000 runs per jurisdiction.
</footer>

<script>
// Helper utilities
const $ = id => document.getElementById(id);
const fmt = v => v.toLocaleString('en-US');
const hx = n => Array.from({length: n}, () => Math.floor(Math.random() * 16).toString(16)).join('');
const RM = matchMedia('(prefers-reduced-motion:reduce)').matches;

// 5-State Verdict Mapping: [Name, CSS Variable]
const OC = [
  ['PERMIT', '--ok'],
  ['REMEDIATE', '--rm'],
  ['ESCALATE', '--rv'],
  ['BLOCK', '--dn'],
  ['INDETERMINATE', '--in']
];

const TH = 0.65, N = 2000, BINS = 16;

// Regulatory Regimes mapping
const REGIMES = ['FINRA_US', 'EU_AI_ACT_HIGH_RISK', 'ISO_42001', 'ICAO_ANNEX_9', 'GDPR_ART_22'];

// Country Jurisdictions setup
const C = {};
[
  ['US','United States',42,500,80,40,60,10,.01,.05],
  ['CA','Canada',18,200,20,15,15,5,0,.04],
  ['MX','Mexico',26,240,30,35,80,10,.05,.07],
  ['BR','Brazil',38,350,50,55,130,15,.07,.08],
  ['AR','Argentina',12,85,20,20,50,5,.04,.09],
  ['CL','Chile',14,150,20,20,30,4,-.03,.05],
  ['CO','Colombia',16,110,20,25,50,5,.06,.08],
  ['PE','Peru',9,55,10,12,35,3,.05,.10],
  ['GB','United Kingdom',22,290,30,15,20,5,-.01,.03],
  ['DE','Germany',24,320,35,20,15,5,0,.03],
  ['NG','Nigeria',10,50,12,18,50,10,.03,.10],
  ['ZA','South Africa',8,65,10,12,20,3,-.02,.07],
  ['IN','India',34,310,40,45,85,15,.12,.10],
  ['CN','China',28,290,30,25,40,10,.02,.05],
  ['JP','Japan',16,200,15,10,8,2,0,.03],
  ['AU','Australia',12,145,15,10,15,3,-.02,.04]
].forEach(([k,n,ag,p,rm,es,bl,ind,mu,sg]) => {
  const t = p + rm + es + bl + ind;
  C[k] = {
    n, ag, c: [p, rm, es, bl, ind],
    pd: (bl + ind) / t,
    pr: (es + rm) / t,
    b: [bl/t, ind/t, es/t, rm/t, p/t],
    mu, sg
  };
});

const risk = o => Math.min(1, 1.5 * o.pd + 0.8 * o.pr);

// Monte Carlo simulation
function gauss() {
  let u = 0, v = 0;
  while (!u) u = Math.random();
  while (!v) v = Math.random();
  return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v);
}

function mc(k) {
  const o = C[k], r0 = risk(o), out = new Float32Array(N), S = 30;
  for (let i = 0; i < N; i++) {
    let r = r0;
    for (let t = 0; t < S; t++) {
      r += o.mu / S + o.sg * gauss() / Math.sqrt(S);
      r = r < 0 ? 0 : r > 1 ? 1 : r;
    }
    out[i] = r;
  }
  out.sort();
  const h = new Array(BINS).fill(0);
  let s = 0, pc = 0;
  out.forEach(v => {
    h[Math.min(BINS - 1, Math.floor(v * BINS))]++;
    s += v;
    if (v > TH) pc++;
  });
  o.mc = { mean: s / N, p10: out[Math.floor(N * .1)], p90: out[Math.floor(N * .9)], pc: pc / N, h };
}

function col(r) {
  if (r <= .25) return 'var(--ok)';
  if (r < .45) return `color-mix(in srgb, var(--rv) ${Math.round((r - .25) / .2 * 100)}%, var(--ok))`;
  if (r < .65) return `color-mix(in srgb, var(--dn) ${Math.round((r - .45) / .2 * 100)}%, var(--rv))`;
  return 'var(--dn)';
}

let LY = 0, PIN = 'NG', HV = null, AL = null;
const DIS = new Set(), CT = {};

// Map Coordinates
const LL = {
  US:[-98,39], CA:[-100,58], MX:[-102,23], BR:[-52,-10], AR:[-64,-34], CL:[-71,-30], CO:[-74,4],
  PE:[-75,-10], GB:[-2,54], DE:[10,51], NG:[8,9], ZA:[25,-29], IN:[79,22], CN:[103,35], JP:[138,37], AU:[134,-25]
};
let M = null;

const ld = s => new Promise(r => {
  const e = document.createElement('script');
  e.src = s; e.onload = () => r(1); e.onerror = () => r(0);
  document.head.appendChild(e);
});

async function geo() {
  for (const v of ['1.6.0', '1.5.3']) {
    const b = `https://cdn.jsdelivr.net/npm/jsvectormap@${v}/dist/`;
    if (await ld(b + 'js/jsvectormap.min.js') && await ld(b + 'maps/world.js')) {
      const m = window.jsVectorMap && jsVectorMap.maps && jsVectorMap.maps.world;
      if (m && m.paths) return m;
    }
  }
  return null;
}

function grid(W, H) {
  let g = '';
  for (let i = 1; i < 12; i++) g += `<line x1="${i * W / 12}" x2="${i * W / 12}" y1="0" y2="${H}"/>`;
  for (let i = 1; i < 6; i++) g += `<line x1="0" x2="${W}" y1="${i * H / 6}" y2="${i * H / 6}"/>`;
  $('gr').innerHTML = g;
}

function build() {
  const W = M ? (M.width || 900) : 900, H = M ? (M.height || 441) : 441;
  $('mp').setAttribute('viewBox', `0 0 ${W} ${H}`);
  grid(W, H);
  let s = '', i = 0;
  if (M) {
    for (const k in M.paths) { if (k != 'AQ') s += `<path id="c-${k}" data-c="${k}" class="${C[k] ? 'ag' : 'bg'}" d="${M.paths[k].path}"/>`; }
    $('pg').innerHTML = s;
    for (const k in C) {
      const e = $('c-' + k); if (!e) continue;
      const b = e.getBBox();
      CT[k] = [b.x + b.width / 2, b.y + b.height / 2];
      e.style.transitionDelay = (i++ * 70) + 'ms';
    }
  } else {
    for (const k in C) {
      CT[k] = [(LL[k][0] + 180) / 360 * W, (90 - LL[k][1]) / 180 * H];
      s += `<circle id="c-${k}" data-c="${k}" class="ag" cx="${CT[k][0]}" cy="${CT[k][1]}" r="${(4 + Math.sqrt(C[k].ag) * .9).toFixed(1)}"/>`;
    }
    $('pg').innerHTML = s;
  }
  let hb = '';
  if (M) for (const k in C) if (CT[k]) hb += `<circle cx="${CT[k][0]}" cy="${CT[k][1]}" r="${(1.2 + Math.sqrt(C[k].ag) * .28).toFixed(1)}"/>`;
  $('hb').innerHTML = hb;
  mark(); paint();
  setTimeout(() => document.querySelectorAll('.ag').forEach(e => e.style.transitionDelay = ''), 2500);
}

$('pg').onmouseover = e => { const k = e.target.dataset.c; if (k && C[k]) { HV = k; mark(); det(k); } };$('pg').onmouseout = () => { HV = null; mark(); det(PIN); };
$('pg').onclick = e => { const k = e.target.dataset.c; if (k && C[k]) { PIN = k; mark(); det(k); } };$('rk').onclick = e => { const b = e.target.closest('[data-c]'); if (b) { PIN = b.dataset.c; mark(); det(PIN); } };

function mark() { document.querySelectorAll('.ag').forEach(e => { e.classList.toggle('sel', e.dataset.c == PIN); e.classList.toggle('hv', e.dataset.c == HV); }); }
function paint() { for (const k in C) { const e = $('c-' + k); if (e) e.style.fill = col(LY ? C[k].mc.mean : risk(C[k])); } }
function lay() { [0, 1].forEach(i => $('l' + i).setAttribute('aria-pressed', LY == i)); }
$('l0').onclick = () => { LY = 0; lay(); ui(); };$('l1').onclick = () => { LY = 1; lay(); ui(); };

// Jurisdiction Detail Panel
function det(k) {
  const o = C[k], r = risk(o), m = o.mc, n = o.c.reduce((a, b) => a + b, 0), W = 250, Hh = 50, mx = Math.max(...m.h);
  const bars = m.h.map((v, i) => `<rect x="${i * W / BINS + 1}" y="${10 + Hh - v / mx * Hh}" width="${W / BINS - 2}" height="${v / mx * Hh}" style="fill:${col((i + .5) / BINS)}"/>`).join('');
  
  $('dt').innerHTML = `<div style="font-size:16px;font-weight:600">${o.n}</div>
  <div class="m">${o.ag} Agents, ${fmt(n)} Decisions (24h)</div>
  <dl class="dl">
    <dt>Block / Indet.</dt><dd class="n">${Math.round(o.pd * 100)}%</dd>
    <dt>HITL / Remed.</dt><dd class="n">${Math.round(o.pr * 100)}%</dd>
    <dt>Current Risk</dt><dd class="n">${r.toFixed(2)}</dd>
    <dt>30-Day Mean</dt><dd class="n">${m.mean.toFixed(2)} <span class="m">(${m.p10.toFixed(2)} to ${m.p90.toFixed(2)})</span></dd>
    <dt>Critical Threshold</dt><dd class="n">${Math.round(m.pc * 100)}% scenarios</dd>
  </dl>
  <svg viewBox="0 0 ${W} ${Hh + 24}" width="100%" style="margin-top:10px;display:block">
    ${bars}
    <line x1="${r * W}" x2="${r * W}" y1="10" y2="${Hh + 10}" stroke-width="1.5" style="stroke:var(--t)"/>
    <line x1="${TH * W}" x2="${TH * W}" y1="10" y2="${Hh + 10}" stroke-dasharray="3 3" style="stroke:var(--m)"/>
    <text x="${r * W}" y="8" font-size="9" text-anchor="${r > .85 ? 'end' : r < .1 ? 'start' : 'middle'}" style="fill:var(--t)">now</text>
    <text x="${TH * W}" y="${Hh + 22}" font-size="9" text-anchor="middle" style="fill:var(--m)">critical</text>
  </svg>`;
}

function rank() {
  const v = k => LY ? C[k].mc.mean : risk(C[k]);
  $('rk').innerHTML = Object.keys(C).sort((a, b) => v(b) - v(a)).slice(0, 5).map(k => {
    const x = v(k), d = x - risk(C[k]);
    return `<button class="rw" data-c="${k}"><span>${C[k].n}</span><span class="b2"><i style="width:${Math.round(x * 100)}%;background:${col(x)}"></i></span><span class="n">${x.toFixed(2)}</span><span class="n m">${LY ? (d >= 0 ? '+' : '') + d.toFixed(2) : ''}</span></button>`;
  }).join('');
}

function alertUp() {
  let b = null;
  for (const k in C) { if (DIS.has(k) || risk(C[k]) >= TH) continue; if (!b || C[k].mc.pc > C[b].mc.pc) b = k; }
  const a = $('al');
  if (!b || C[b].mc.pc < .15) { a.classList.add('h'); AL = null; return; }
  AL = b; a.classList.remove('h');
  $('at').innerHTML = `<strong>${C[b].n} Risk Threshold Projection Alert</strong><br><span class="m">Exceeds boundary in ${Math.round(C[b].mc.pc * 100)}% of 30-day Monte Carlo runs.</span>`;
}

$('dm').onclick = () => { DIS.add(AL); alertUp(); };$('go').onclick = () => { LY = 1; lay(); PIN = AL; ui(); };

// KPI Counter Animation
function tw(el, to) {
  const from = +el.dataset.v || 0; el.dataset.v = to;
  if (RM) { el.textContent = fmt(to); return; }
  const t0 = performance.now();
  (function f(t) {
    const k = Math.min(1, (t - t0) / 1000), e = 1 - Math.pow(1 - k, 3);
    el.textContent = fmt(Math.round(from + (to - from) * e));
    if (k < 1) requestAnimationFrame(f);
  })(t0);
}

function kpi() {
  const t = [0, 1, 2, 3, 4].map(j => Object.values(C).reduce((a, o) => a + o.c[j], 0));
  const T = t.reduce((a, b) => a + b, 0);
  t.forEach((v, j) => {
    tw($('k' + j), v);$('p' + j).textContent = Math.round(v / T * 100) + '% of total';
  });
}

const SP = [
  [148, 152, 139, 160, 155, 158, 163, 151, 157, 150],
  [22, 25, 21, 28, 24, 26, 29, 23, 27, 25],
  [19, 22, 18, 24, 20, 21, 23, 19, 25, 21],
  [31, 38, 35, 42, 36, 33, 40, 45, 44, 38],
  [5, 8, 4, 9, 6, 5, 10, 7, 8, 6]
];

function spark() {
  SP.forEach((d, i) => {
    const lo = Math.min(...d) - 2, hi = Math.max(...d) + 2;
    const p = d.map((v, k) => `${k * 20},${20 - (v - lo) / (hi - lo) * 18}`).join(' ');
    const el = $('s' + i);
    if (el) el.innerHTML = `<polyline points="${p}" fill="none" stroke-width="1.5" style="stroke:var(${OC[i][1]})"/>`;
  });
}

// Sample Initial Decisions Log (Attested Evaluation Path Enabled)
const R = [
  ['22:41:08', 'AR', 'ar-agent-07', 'FINRA_US', 'USER_ELEVATION', 2, '675e3ccc-7113'],
  ['22:31:38', 'NG', 'ng-agent-03', 'EU_AI_ACT_HIGH_RISK', 'DB_DROP', 3, '51b26356-0ba4'],
  ['22:25:12', 'DE', 'de-agent-12', 'ISO_42001', 'PROMPT_INJECTION', 1, '43a91bf2-8cc1'],
  ['22:22:08', 'PE', 'pe-agent-05', 'GDPR_ART_22', 'PII_EXFILTRATION', 3, '6463a0d6-3021'],
  ['22:15:00', 'US', 'us-agent-02', 'FINRA_US', 'API_TIMEOUT_FAIL', 4, '11e892ba-00f4'],
  ['22:03:08', 'CO', 'co-agent-11', 'ICAO_ANNEX_9', 'POLICY_OVERRIDE', 2, '9711a539-d235'],
  ['21:53:38', 'IN', 'in-agent-21', 'ISO_42001', 'BATCH_PROCESS', 0, '86f6af21-1250']
];

let SEL = R[0][6];

function table(fresh) {
  $('tb').innerHTML = R.map((r, i) => `
    <tr data-i="${i}" class="${fresh && i == 0 ? 'new' : ''}">
      <td class="n">${r[0]}</td>
      <td class="n">${r[1]}</td>
      <td class="n">${r[2]}</td>
      <td class="n m" style="font-size:11px">${r[3]}</td>
      <td class="n">${r[4]}</td>
      <td><span class="badge" style="background:color-mix(in srgb, var(${OC[r[5]][1]}) 18%, transparent); color:var(${OC[r[5]][1]})"><span class="dot" style="background:var(${OC[r[5]][1]})"></span>${OC[r[5]][0]}</span></td>
    </tr>`).join('');
  const k = R.findIndex(r => r[6] == SEL);
  show(k < 0 ? 0 : k);
}

// Show Detailed Attested Path & PASETO Inspection
function show(i) {
  const r = R[i]; SEL = r[6];
  document.querySelectorAll('#tb tr').forEach((e, k) => e.classList.toggle('on', k == i));
  
  const principal_id = `usr_${hx(5)} -> tenant_${r[1].toLowerCase()} -> ${r[2]}`;
  const eval_hash = hx(16);
  
  $('in').innerHTML = `
    <div class="n" style="font-size:14px; font-weight:500; margin-top:6px">${r[6]}</div>
    <dl class="dl" style="grid-template-columns:100px 1fr">
      <dt>Verdict</dt><dd><span class="badge" style="background:color-mix(in srgb, var(${OC[r[5]][1]}) 18%, transparent); color:var(${OC[r[5]][1]})">${OC[r[5]][0]}</span></dd>
      <dt>Agent ID</dt><dd class="n">${r[2]}</dd>
      <dt>Jurisdiction</dt><dd>${C[r[1]].n}</dd>
      <dt>Regime Context</dt><dd class="n">${r[3]}</dd>
      <dt>Principal Authority</dt><dd class="n" style="font-size:11px">${principal_id}</dd>
      <dt>Action Evaluated</dt><dd class="n">${r[4]}</dd>
      <dt>Attested Path</dt>
      <dd class="n" style="font-size:11px; color:var(--m)">
        [VAL] POL-SEC-01 (v2.1.0, #${eval_hash.slice(0,6)})<br>
        [VAL] POL-ALIGN-09 (v1.0.4, #${eval_hash.slice(6,12)})<br>
        [BYPASS] POL-GEO-04 (Reason: Local override)
      </dd>
      <dt>Execution Hash</dt><dd class="n" style="font-size:11px">${eval_hash}</dd>
      <dt>PASETO v4 Signature</dt><dd><span class="dot"></span>Valid (k4.public.2026-09)</dd>
    </dl>
    <div class="tok n">v4.public.eyJyZWYiOiI${btoa(r[6]).replace(/=/g, '')}…N8kQ2vH0rTz</div>`;
}

$('tb').onclick = e => { const t = e.target.closest('tr'); if (t) show(+t.dataset.i); };

// Human Escalation Queue (HITL / ESCALATE)
const cnt = () => { $('qc').textContent = document.querySelectorAll('.q').length; };
const WHAT = {
  USER_ELEVATION: ['Elevate user permissions to Admin for 30m', 'Admin privileges mandate explicit human authorization.'],
  DB_DROP: ['Drop production database table', 'Destructive operation without verified backup snapshot.'],
  ASSET_TRANSFER: ['Transfer funds to external account', 'Exceeds autonomous threshold of USD 25,000.'],
  BATCH_PROCESS: ['Execute mass batch operation', 'Affects over 10,000 customer records.'],
  POLICY_OVERRIDE: ['Bypass active regulatory policy', 'Requires human compliance override seal.'],
  PROMPT_INJECTION: ['Potential prompt injection detected', 'LLM output drifted into non-enforced boundary.'],
  PII_EXFILTRATION: ['Exfiltration of sensitive customer data', 'Hard compliance boundary violation.']
};

const Q0 = [
  ['AR', 'ar-agent-07', 'ASSET_TRANSFER', '06:12', 'Transfer USD 48,200 to external party', 'Exceeds autonomous threshold of USD 25,000.'],
  ['NG', 'ng-agent-03', 'USER_ELEVATION', '02:41', 'Grant root DB access', 'Elevated permission request.'],
  ['CO', 'co-agent-11', 'POLICY_OVERRIDE', '01:05', 'Export customer table', 'Bypasses export restriction policy.']
];

function qi(k, ag, ac, t, what, why, cls) {
  const w = WHAT[ac] || ['Action required', 'Human review needed'];
  const principal = `usr_${hx(4)} -> ${ag}`;
  return `<div class="q ${cls || ''}" data-c="${k}">
    <div class="r"><strong>${what || w[0]}</strong><span class="n m">${t}</span></div>
    <div class="m" style="margin-top:2px">${why || w[1]}</div>
    <div class="lab n" style="margin-top:4px">${ag} | ${C[k].n} | Auth: ${principal}</div>
    <div class="a"><button data-a>Approve</button><button data-a>Reject</button></div>
  </div>`;
}

$('ql').innerHTML = Q0.map(q => qi(...q)).join('');$('ql').onclick = e => {
  if (e.target.dataset.a !== undefined) { e.target.closest('.q').remove(); cnt(); return; }
  const q = e.target.closest('.q'); if (q) { PIN = q.dataset.c; mark(); det(PIN); }
};

function addQ(k, ag, ac) {
  $('ql').insertAdjacentHTML('afterbegin', qi(k, ag, ac, 'now', null, null, 'new'));
  const q = document.querySelectorAll('.q'); if (q.length > 5) q[q.length - 1].remove(); cnt();
}

// Blockchain Block Feed
const H = ['9f3a', 'c41e', '7b02', 'e8d5', '1a6c', '5f90', 'b3d7', '2e48'];
let BN = 14203;

function chain(fresh) {
  $('ch').innerHTML = H.map((h, i) => `<div class="blk n ${fresh && i == 0 ? 'new' : ''}">#${BN - i} ${h}…</div>`).join('<div class="ln"></div>');
  $('bn').textContent = fmt(BN);
}

// Ripple Effect on Map
function ripple(k, j) {
  if (RM || !CT[k]) return;
  const c = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
  c.setAttribute('class', 'rip');
  c.setAttribute('cx', CT[k][0]);
  c.setAttribute('cy', CT[k][1]);
  c.setAttribute('r', 2);
  c.style.stroke = `var(${OC[j][1]})`;
  $('rp').appendChild(c);
  setTimeout(() => c.remove(), 1700);
}

// Simulated Real-Time Evaluation Event
const POOL = Object.keys(C).flatMap(k => Array(C[k].ag).fill(k));
const ACT = ['USER_ELEVATION', 'DB_DROP', 'ASSET_TRANSFER', 'BATCH_PROCESS', 'POLICY_OVERRIDE', 'PROMPT_INJECTION', 'API_TIMEOUT_FAIL'];

function ev() {
  if (document.hidden) return;
  const k = POOL[Math.floor(Math.random() * POOL.length)], o = C[k], u = Math.random();
  // Veredict Index: 0: PERMIT, 1: REMEDIATE, 2: ESCALATE, 3: BLOCK, 4: INDETERMINATE
  const j = u < o.b[0] ? 3 : u < o.b[0] + o.b[1] ? 4 : u < o.b[0] + o.b[1] + o.b[2] ? 2 : u < o.b[0] + o.b[1] + o.b[2] + o.b[3] ? 1 : 0;
  
  const al = .03;
  o.c[j]++;
  o.pd += al * ((j >= 3 ? 1 : 0) - o.pd);
  o.pr += al * ((j == 1 || j == 2 ? 1 : 0) - o.pr);
  mc(k);

  const ac = ACT[Math.floor(Math.random() * ACT.length)];
  const ag = `${k.toLowerCase()}-agent-${String(1 + Math.floor(Math.random() * o.ag)).padStart(2, '0')}`;
  const regime = REGIMES[Math.floor(Math.random() * REGIMES.length)];

  // Update Stochastic Drift Visual
  const drift_val = (0.2 + Math.random() * 0.6).toFixed(2);
  $('sri_val').textContent = `${drift_val} Drift`;
  if (drift_val > 0.5) $('sri_val').style.color = 'var(--dn)';
  else $('sri_val').style.color = 'var(--rv)';

  R.unshift([new Date().toISOString().slice(11, 19), k, ag, regime, ac, j, hx(8) + '-' + hx(4)]);
  R.pop();
  
  H.unshift(hx(4)); H.pop(); BN++;
  
  ui(); table(true); chain(true); ripple(k, j);
  if (j == 2) addQ(k, ag, ac);
}

function ui() { paint(); rank(); mark(); det(HV || PIN); kpi(); alertUp(); cnt(); }

// Initialization
Object.keys(C).forEach(mc);
$('ha').textContent = `${Object.values(C).reduce((a, o) => a + o.ag, 0)} agents active across ${Object.keys(C).length} jurisdictions`;
lay(); spark(); table(false); chain(false); build(); ui();
geo().then(m => { M = m; build(); $('nm').hidden = !!m; });

// Live Loop Execution
setTimeout(function loop() { ev(); setTimeout(loop, 1600 + Math.random() * 1800); }, 2800);

const tick = () => { $('clk').textContent = 'UTC ' + new Date().toISOString().slice(11, 19); };
tick(); setInterval(tick, 1000);

document.querySelectorAll('.p').forEach(p => p.addEventListener('pointermove', e => {
  const r = p.getBoundingClientRect();
  p.style.setProperty('--x', (e.clientX - r.left) + 'px');
  p.style.setProperty('--y', (e.clientY - r.top) + 'px');
}));
</script>
</body>
</html>