#!/usr/bin/env python3
"""
build_dashboard.py — theme JSON → self-contained teardown dashboard (docs/index.html).

usage: build_dashboard.py [themes/some-theme.json]
"""

import json
import sys
from pathlib import Path

HERE = Path(__file__).parent

TEMPLATE = r"""<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__NAME__ — decoded</title>
<style>
:root {
  --bg: #0B0F1C; --bg2: #0E1424;
  --panel: rgba(255,255,255,0.045); --panel-line: rgba(255,255,255,0.09);
  --ink: #E9EDF6; --muted: #9AA3B8; --faint: #6B7488;
  --c-sound: #B8842B; --c-light: #2E9BBF; --c-mod: #C9709E; --c-aux: #5E9E44;
  --c-sound-hi: #E8C87A; --band-fill: rgba(255,255,255,0.03);
  --grid: rgba(255,255,255,0.07); --tip-bg: rgba(14,20,36,0.92);
  --chip: rgba(255,255,255,0.07);
  --display: "Avenir Next", Seravek, system-ui, sans-serif;
  --body: system-ui, -apple-system, sans-serif;
  --mono: ui-monospace, "SF Mono", Menlo, monospace;
}
@media (prefers-color-scheme: light) { :root {
  --bg: #F4F2EC; --bg2: #ECE9E0;
  --panel: rgba(255,255,255,0.72); --panel-line: rgba(28,34,48,0.10);
  --ink: #1C2230; --muted: #5A6274; --faint: #8A92A4;
  --c-sound: #96660F; --c-light: #0E7FA6; --c-mod: #B04A80; --c-aux: #3F8228;
  --c-sound-hi: #7A5410; --band-fill: rgba(28,34,48,0.035);
  --grid: rgba(28,34,48,0.09); --tip-bg: rgba(255,255,255,0.95);
  --chip: rgba(28,34,48,0.06);
}}
:root[data-theme="dark"] {
  --bg: #0B0F1C; --bg2: #0E1424;
  --panel: rgba(255,255,255,0.045); --panel-line: rgba(255,255,255,0.09);
  --ink: #E9EDF6; --muted: #9AA3B8; --faint: #6B7488;
  --c-sound: #B8842B; --c-light: #2E9BBF; --c-mod: #C9709E; --c-aux: #5E9E44;
  --c-sound-hi: #E8C87A; --band-fill: rgba(255,255,255,0.03);
  --grid: rgba(255,255,255,0.07); --tip-bg: rgba(14,20,36,0.92);
  --chip: rgba(255,255,255,0.07);
}
:root[data-theme="light"] {
  --bg: #F4F2EC; --bg2: #ECE9E0;
  --panel: rgba(255,255,255,0.72); --panel-line: rgba(28,34,48,0.10);
  --ink: #1C2230; --muted: #5A6274; --faint: #8A92A4;
  --c-sound: #96660F; --c-light: #0E7FA6; --c-mod: #B04A80; --c-aux: #3F8228;
  --c-sound-hi: #7A5410; --band-fill: rgba(28,34,48,0.035);
  --grid: rgba(28,34,48,0.09); --tip-bg: rgba(255,255,255,0.95);
  --chip: rgba(28,34,48,0.06);
}
html { background: var(--bg); }
body {
  margin: 0; color: var(--ink); font-family: var(--body);
  font-size: 17px; line-height: 1.55;
  background:
    radial-gradient(1100px 500px at 70% -10%, rgba(46,155,191,0.10), transparent 60%),
    radial-gradient(900px 480px at 10% 8%, rgba(184,132,43,0.09), transparent 55%),
    var(--bg);
  min-height: 100vh;
}
.wrap { max-width: 1100px; margin: 0 auto; padding: 40px 22px 90px; }
.eyebrow {
  font-family: var(--mono); font-size: 12.5px; letter-spacing: 0.14em;
  text-transform: uppercase; color: var(--faint); display: flex; gap: 12px; align-items: center;
}
.demo-chip {
  font-family: var(--mono); font-size: 11.5px; letter-spacing: 0.06em;
  background: var(--chip); border: 1px solid var(--panel-line);
  border-radius: 999px; padding: 3px 11px; color: var(--muted);
}
h1 {
  font-family: var(--display); font-weight: 600; font-size: clamp(34px, 5.4vw, 54px);
  line-height: 1.06; margin: 14px 0 10px; text-wrap: balance; letter-spacing: -0.015em;
}
h1 .accent { color: var(--c-sound-hi); }
.lede { color: var(--muted); max-width: 62ch; margin: 0 0 8px; font-size: 18px; }
h2 { font-family: var(--display); font-weight: 600; font-size: 24px; margin: 0 0 4px; letter-spacing: -0.01em; }
.sub { color: var(--muted); font-size: 15px; margin: 0 0 18px; max-width: 70ch; }
.tiles { display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); gap: 14px; margin: 30px 0 34px; }
.tile {
  background: var(--panel); border: 1px solid var(--panel-line); border-radius: 16px;
  padding: 16px 18px 14px; backdrop-filter: blur(14px); -webkit-backdrop-filter: blur(14px);
  transition: transform .22s cubic-bezier(.2,.9,.3,1.4), border-color .22s;
}
.tile:hover { transform: translateY(-3px); border-color: var(--c-light); }
.tile .k { font-family: var(--mono); font-size: 12px; letter-spacing: 0.1em; text-transform: uppercase; color: var(--faint); }
.tile .v { font-family: var(--display); font-size: 30px; font-weight: 600; margin-top: 4px; font-variant-numeric: tabular-nums; }
.tile .d { color: var(--muted); font-size: 13.5px; margin-top: 2px; }
.panel {
  background: var(--panel); border: 1px solid var(--panel-line); border-radius: 20px;
  padding: 24px 26px 20px; margin: 26px 0; backdrop-filter: blur(14px); -webkit-backdrop-filter: blur(14px);
  position: relative;
}
.legend { display: flex; flex-wrap: wrap; gap: 16px; margin: 6px 0 4px; font-size: 14px; color: var(--muted); }
.legend .item { display: inline-flex; align-items: center; gap: 7px; }
.swatch { width: 14px; height: 4px; border-radius: 2px; display: inline-block; }
.chart-box { position: relative; }
.chart-box svg { display: block; width: 100%; height: auto; }
.tip {
  position: absolute; pointer-events: none; display: none; z-index: 5;
  background: var(--tip-bg); border: 1px solid var(--panel-line); border-radius: 12px;
  padding: 9px 12px; font-family: var(--mono); font-size: 12.5px; line-height: 1.6;
  backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px);
  box-shadow: 0 10px 30px rgba(0,0,0,0.25); white-space: nowrap;
}
.tip b { font-weight: 600; }
canvas { display: block; width: 100%; border-radius: 10px; }
.two { display: grid; grid-template-columns: 1fr 1fr; gap: 26px; }
@media (max-width: 860px) { .two { grid-template-columns: 1fr; } }
.seg-strip { display: flex; gap: 12px; overflow-x: auto; padding: 4px 2px 10px; }
.seg-card {
  min-width: 200px; flex: 1; background: var(--panel); border: 1px solid var(--panel-line);
  border-radius: 16px; padding: 15px 17px; backdrop-filter: blur(14px); -webkit-backdrop-filter: blur(14px);
  transition: transform .2s ease, border-color .2s;
}
.seg-card:hover { transform: translateY(-3px); }
.seg-card .time { font-family: var(--mono); font-size: 12px; color: var(--faint); }
.seg-card .band { font-family: var(--display); font-weight: 600; font-size: 21px; margin: 3px 0 1px; text-transform: capitalize; }
.seg-card .tech { font-size: 13.5px; color: var(--muted); }
.band-pill { display: inline-block; width: 9px; height: 9px; border-radius: 50%; margin-right: 7px; }
table { border-collapse: collapse; width: 100%; font-size: 14.5px; }
th { font-family: var(--mono); font-size: 12px; letter-spacing: 0.08em; text-transform: uppercase;
     color: var(--faint); text-align: left; padding: 9px 12px; border-bottom: 1px solid var(--panel-line); }
td { padding: 10px 12px; border-bottom: 1px solid var(--panel-line); vertical-align: top; }
td.num { font-family: var(--mono); font-variant-numeric: tabular-nums; }
.tag { font-family: var(--mono); font-size: 10.5px; letter-spacing: 0.07em; text-transform: uppercase;
       padding: 2px 8px; border-radius: 999px; background: var(--chip); color: var(--muted);
       border: 1px solid var(--panel-line); white-space: nowrap; }
.tag.measured { color: var(--c-sound-hi); border-color: var(--c-sound); }
.tbl-wrap { overflow-x: auto; }
details { margin-top: 12px; }
summary { cursor: pointer; color: var(--muted); font-size: 14px; }
summary:focus-visible, .tile:focus-visible { outline: 2px solid var(--c-light); outline-offset: 3px; }
.note { color: var(--muted); font-size: 14px; border-left: 2px solid var(--panel-line); padding-left: 14px; margin: 14px 0; }
.method p { color: var(--muted); font-size: 15px; max-width: 74ch; }
.method code { font-family: var(--mono); font-size: 13px; background: var(--chip); padding: 1px 6px; border-radius: 6px; }
footer { margin-top: 50px; color: var(--faint); font-size: 13.5px; font-family: var(--mono); }
@media (prefers-reduced-motion: reduce) { .tile, .seg-card { transition: none; } }
</style>

<div class="wrap">
  <div class="eyebrow"><span>NeuroVIZR · theme teardown</span>__DEMO_CHIP__</div>
  <h1>__NAME_HTML__ <span class="accent">decoded</span></h1>
  <p class="lede">What does this journey actually contain? Every number below is measured
  from the session itself — the audio channels, the light, and how tightly the two move together.</p>

  <div class="tiles" id="tiles"></div>

  <div class="panel">
    <h2>The protocol</h2>
    <p class="sub">Stimulation frequency over the journey — sound and light on one axis.
    Shaded lanes are the brainwave bands each frequency targets. Where the amber and cyan
    lines travel together, light and sound are working the same rhythm.</p>
    <div class="legend" id="protocol-legend"></div>
    <div class="chart-box" id="protocol"></div>
    <details><summary>View as table</summary><div class="tbl-wrap" id="protocol-table"></div></details>
  </div>

  <div class="panel">
    <h2>Journey phases</h2>
    <p class="sub">Auto-segmented from the frequency timeline — no liner notes required.</p>
    <div class="seg-strip" id="segments"></div>
  </div>

  <div class="two">
    <div class="panel">
      <h2>Inside the sound</h2>
      <p class="sub">Spectrogram, 40–1000&nbsp;Hz. The bright line is the carrier tone;
      its slow drift is part of the composition.</p>
      <canvas id="spec" height="240"></canvas>
      <div class="legend"><span class="item"><span class="swatch" style="background:var(--c-sound)"></span>loudness</span></div>
      <div class="chart-box" id="loudness"></div>
    </div>
    <div class="panel">
      <h2>Inside the light</h2>
      <p class="sub">The colour ribbon is the show itself, second by second.
      Below it, measured brightness.</p>
      <canvas id="hue" height="64"></canvas>
      <div class="legend"><span class="item"><span class="swatch" style="background:var(--c-light)"></span>brightness</span></div>
      <div class="chart-box" id="luma"></div>
    </div>
  </div>

  <div class="panel">
    <h2>How this compares</h2>
    <p class="sub">The question every buyer quietly asks: “isn’t this just binaural beats
    on YouTube?” Measured rows come from this decode; context rows describe the alternatives.</p>
    <div class="tbl-wrap" id="compare"></div>
    <p class="note">This page measures what the theme <em>contains</em>. Whether it changes how you
    feel is the next instrument: a session journal + before/after self-report across many
    listeners — the placebo comparison lives there, in the open.</p>
  </div>

  <div class="panel method">
    <h2>Method</h2>
    <p><b>Sound.</b> The stereo file is decoded and each ear is tracked separately with a
    windowed FFT (~2&nbsp;s windows, sub-bin peak interpolation). A <em>binaural beat</em> is the
    difference between the two carrier tones; an <em>isochronic pulse</em> is found by measuring the
    loudness envelope’s own rhythm. Offsets under ~0.8&nbsp;Hz read as a single carrier.</p>
    <p><b>Light.</b> Video of the show is reduced to one average colour per frame; flicker rate
    is the dominant rhythm of the brightness signal. A phone filming at 60&nbsp;fps can only see
    flicker up to 30&nbsp;Hz — film at 240&nbsp;fps (slo-mo) to resolve gamma-rate light.</p>
    <p><b>Lock score.</b> Per second, the light’s flicker is compared to the sound’s stimulation
    frequency, counting half/double harmonics as a lock (the demo’s gamma phase drives light at
    20&nbsp;Hz against a 40&nbsp;Hz pulse — deliberate half-harmonic).</p>
    <p>Pipeline: <code>analyzer.py</code>, pure Python + ffmpeg, no dependencies. Point it at any
    session capture: <code>python3 analyzer.py session.wav lightshow.mov "Theme name"</code>.</p>
  </div>

  <footer id="foot"></footer>
</div>

<script>
const THEME = __THEME_JSON__;
const BANDS = [
  ["delta", 0.5, 4], ["theta", 4, 8], ["alpha", 8, 13], ["beta", 13, 30], ["gamma", 30, 46]
];
const css = n => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
const fmtT = s => Math.floor(s/60) + ":" + String(Math.floor(s%60)).padStart(2,"0");

/* ---------------- tiles ---------------- */
(function tiles(){
  const a = THEME.audio, c = THEME.coupling || {};
  const bands = [...new Set(THEME.segments.map(s => s.band).filter(b => b !== "—"))];
  const techs = [...new Set(THEME.segments.map(s => s.technique))];
  const items = [
    ["Journey", fmtT(a.duration_s), "minutes:seconds"],
    ["Phases", THEME.segments.length, bands.join(" · ")],
    ["Techniques", techs.length, techs.join(" + ")],
    ["Light–sound lock", (c.pct_locked != null ? c.pct_locked + "%" : "—"),
      c.r != null ? "correlation r = " + c.r : "no light capture"],
  ];
  document.getElementById("tiles").innerHTML = items.map(([k,v,d]) =>
    `<div class="tile" tabindex="0"><div class="k">${k}</div><div class="v">${v}</div><div class="d">${d}</div></div>`).join("");
})();

/* ---------------- shared chart helpers ---------------- */
function makeSVG(w, h){ const s = document.createElementNS("http://www.w3.org/2000/svg","svg");
  s.setAttribute("viewBox", `0 0 ${w} ${h}`); s.setAttribute("width", w); s.setAttribute("height", h);
  s.style.width = "100%"; s.style.height = "auto"; return s; }
function el(n, at){ const e = document.createElementNS("http://www.w3.org/2000/svg", n);
  for (const k in at) e.setAttribute(k, at[k]); return e; }
function linePath(pts){ let d = "", pen = false;
  for (const p of pts){ if (p == null){ pen = false; continue; }
    d += (pen ? "L" : "M") + p[0].toFixed(1) + " " + p[1].toFixed(1); pen = true; } return d; }

/* ---------------- protocol chart ---------------- */
function drawProtocol(){
  const box = document.getElementById("protocol");
  box.innerHTML = "";
  const W = Math.max(560, box.clientWidth || 900), H = 380;
  const M = {l: 56, r: 118, t: 14, b: 34};
  const a = THEME.audio, l = THEME.light;
  const dur = a.duration_s;
  const yLo = 2, yHi = 46;
  const yOf = hz => M.t + (1 - (Math.log2(hz) - Math.log2(yLo)) / (Math.log2(yHi) - Math.log2(yLo))) * (H - M.t - M.b);
  const xOf = t => M.l + (t / dur) * (W - M.l - M.r);
  const svg = makeSVG(W, H);
  svg.setAttribute("role","img");
  svg.setAttribute("aria-label","Stimulation frequency over time for sound and light");

  for (const [name, lo, hi] of BANDS){
    const y1 = yOf(Math.min(hi, yHi)), y2 = yOf(Math.max(lo, yLo));
    if (y2 <= M.t) continue;
    svg.appendChild(el("rect", {x: M.l, y: y1, width: W - M.l - M.r, height: y2 - y1,
      fill: name === "alpha" || name === "gamma" ? "var(--band-fill)" : "transparent"}));
    const lab = el("text", {x: W - M.r + 10, y: (y1 + y2) / 2 + 4, "font-size": 12.5,
      fill: "var(--faint)", "font-family": "var(--mono)"});
    lab.textContent = name + " " + lo + "–" + hi;
    svg.appendChild(lab);
    svg.appendChild(el("line", {x1: M.l, y1: y2, x2: W - M.r, y2: y2, stroke: "var(--grid)", "stroke-width": 1}));
  }
  for (let m = 0; m <= dur; m += 60){
    const x = xOf(m);
    svg.appendChild(el("line", {x1: x, y1: M.t, x2: x, y2: H - M.b, stroke: "var(--grid)", "stroke-width": 1}));
    const t = el("text", {x, y: H - 12, "text-anchor": "middle", "font-size": 12, fill: "var(--faint)", "font-family": "var(--mono)"});
    t.textContent = fmtT(m); svg.appendChild(t);
  }
  const yt = el("text", {x: 16, y: M.t + 12, "font-size": 12, fill: "var(--faint)", "font-family": "var(--mono)"});
  yt.textContent = "Hz"; svg.appendChild(yt);

  const series = [
    {key: "beat",   t: a.t,     v: a.beat,    color: "var(--c-sound)", name: "binaural beat (sound)"},
    {key: "mod",    t: a.mod_t, v: a.mod_hz,  color: "var(--c-mod)",   name: "isochronic pulse (sound)"},
  ];
  if (l) series.push({key: "flick", t: l.t, v: l.flicker, color: "var(--c-light)", name: "light flicker"});
  for (const s of series){
    const pts = s.t.map((tt, i) => (s.v[i] != null && s.v[i] >= yLo) ? [xOf(tt), yOf(Math.min(s.v[i], yHi))] : null);
    svg.appendChild(el("path", {d: linePath(pts), fill: "none", stroke: s.color,
      "stroke-width": s.key === "flick" ? 2 : 2.5, "stroke-linecap": "round",
      "stroke-dasharray": s.key === "flick" ? "1 6" : "none"}));
    let last = null;
    for (let i = pts.length - 1; i >= 0; i--) if (pts[i]) { last = pts[i]; break; }
    if (last) s.endPt = last;
  }
  // end labels, nudged apart when two lines finish at the same height
  const labelled = series.filter(s => s.endPt).sort((p, q) => p.endPt[1] - q.endPt[1]);
  let prevY = -99;
  for (const s of labelled){
    let y = s.endPt[1] + 4;
    if (y - prevY < 15) y = prevY + 15;
    prevY = y;
    const lb = el("text", {x: s.endPt[0] + 6, y, "font-size": 12, fill: s.color, "font-family": "var(--mono)"});
    lb.textContent = s.key === "flick" ? "light" : (s.key === "beat" ? "sound" : "pulse");
    svg.appendChild(lb);
  }
  const cross = el("line", {x1: 0, y1: M.t, x2: 0, y2: H - M.b, stroke: "var(--faint)", "stroke-width": 1, opacity: 0});
  svg.appendChild(cross);
  box.appendChild(svg);

  const tip = document.createElement("div"); tip.className = "tip"; box.appendChild(tip);
  const near = (arr, t) => { let bi = 0, bd = 1e9;
    for (let i = 0; i < arr.length; i++){ const d = Math.abs(arr[i] - t); if (d < bd){ bd = d; bi = i; } } return bi; };
  box.addEventListener("mousemove", ev => {
    const r = box.getBoundingClientRect();
    const scale = W / r.width;
    const x = (ev.clientX - r.left) * scale;
    if (x < M.l || x > W - M.r){ tip.style.display = "none"; cross.setAttribute("opacity", 0); return; }
    const t = (x - M.l) / (W - M.l - M.r) * dur;
    cross.setAttribute("x1", x); cross.setAttribute("x2", x); cross.setAttribute("opacity", 0.5);
    const ib = near(a.t, t), im = near(a.mod_t, t);
    const rows = [`<b>${fmtT(t)}</b>`];
    if (a.beat[ib] != null) rows.push(`sound &nbsp;<b>${a.beat[ib].toFixed(1)} Hz</b>`);
    if (a.mod_hz[im] != null) rows.push(`pulse &nbsp;<b>${a.mod_hz[im].toFixed(1)} Hz</b>`);
    if (l){ const il = near(l.t, t); if (l.flicker[il] != null) rows.push(`light &nbsp;<b>${l.flicker[il].toFixed(1)} Hz</b>`); }
    tip.innerHTML = rows.join("<br>");
    tip.style.display = "block";
    const px = (x / scale), flip = px > r.width - 150;
    tip.style.left = (flip ? px - tip.offsetWidth - 14 : px + 14) + "px";
    tip.style.top = Math.min((ev.clientY - r.top) + 8, r.height - 90) + "px";
  });
  box.addEventListener("mouseleave", () => { tip.style.display = "none"; cross.setAttribute("opacity", 0); });

  document.getElementById("protocol-legend").innerHTML = series.map(s =>
    `<span class="item"><span class="swatch" style="background:${s.color}"></span>${s.name}</span>`).join("");

  const rows = THEME.segments.map(s =>
    `<tr><td class="num">${fmtT(s.start)}–${fmtT(s.end)}</td><td>${s.technique}</td><td>${s.band}</td>
     <td class="num">${s.hz_from != null ? (s.hz_from === s.hz_to ? s.hz_from : s.hz_from + "→" + s.hz_to) + " Hz" : "—"}</td></tr>`).join("");
  document.getElementById("protocol-table").innerHTML =
    `<table><thead><tr><th>Time</th><th>Technique</th><th>Band</th><th>Rate</th></tr></thead><tbody>${rows}</tbody></table>`;
}

/* ---------------- segments ---------------- */
(function segments(){
  const BC = {delta: "var(--c-aux)", theta: "var(--c-mod)", alpha: "var(--c-sound)", beta: "var(--c-light)", gamma: "var(--c-mod)"};
  document.getElementById("segments").innerHTML = THEME.segments.map(s => `
    <div class="seg-card" tabindex="0">
      <div class="time">${fmtT(s.start)} – ${fmtT(s.end)}</div>
      <div class="band"><span class="band-pill" style="background:${BC[s.band] || "var(--faint)"}"></span>${s.band}</div>
      <div class="tech">${s.technique}${s.hz_from != null ? " · " + (s.hz_from === s.hz_to ? s.hz_from : s.hz_from + "→" + s.hz_to) + " Hz" : ""}</div>
    </div>`).join("");
})();

/* ---------------- spectrogram ---------------- */
function drawSpec(){
  const cv = document.getElementById("spec");
  const a = THEME.audio, S = a.spec;
  const w = cv.clientWidth || 480; cv.width = w * 2; cv.height = 480;
  const ctx = cv.getContext("2d");
  const nT = S.length, nB = S[0].length;
  let mx = 0; for (const row of S) for (const v of row) mx = Math.max(mx, v);
  const dark = !document.documentElement.matches('[data-theme="light"]') &&
    !(window.matchMedia("(prefers-color-scheme: light)").matches && !document.documentElement.matches('[data-theme="dark"]'));
  const cw = cv.width / nT, ch = cv.height / nB;
  for (let i = 0; i < nT; i++){
    for (let j = 0; j < nB; j++){
      const v = Math.pow(S[i][j] / mx, 0.35);
      if (v < 0.03) continue;
      const l = dark ? 8 + v * 72 : 96 - v * 62;
      ctx.fillStyle = `hsl(38 ${30 + v * 45}% ${l}%)`;
      ctx.fillRect(i * cw, cv.height - (j + 1) * ch, Math.ceil(cw), Math.ceil(ch));
    }
  }
}

/* ---------------- small line charts ---------------- */
function smallLine(elId, ts, vs, color, dur, fmt){
  const box = document.getElementById(elId); box.innerHTML = "";
  const W = Math.max(300, box.clientWidth || 480), H = 90, M = {l: 6, r: 6, t: 8, b: 6};
  let mx = 0; for (const v of vs) if (v != null) mx = Math.max(mx, v);
  const svg = makeSVG(W, H);
  const pts = ts.map((t, i) => vs[i] != null ? [M.l + t / dur * (W - M.l - M.r), M.t + (1 - vs[i] / mx) * (H - M.t - M.b)] : null);
  svg.appendChild(el("path", {d: linePath(pts) + ` L ${W - M.r} ${H - M.b} L ${M.l} ${H - M.b} Z`,
    fill: color, opacity: 0.12, stroke: "none"}));
  svg.appendChild(el("path", {d: linePath(pts), fill: "none", stroke: color, "stroke-width": 2}));
  box.appendChild(svg);
  const tip = document.createElement("div"); tip.className = "tip"; box.appendChild(tip);
  box.addEventListener("mousemove", ev => {
    const r = box.getBoundingClientRect();
    const t = (ev.clientX - r.left) / r.width * dur;
    let bi = 0, bd = 1e9;
    for (let i = 0; i < ts.length; i++){ const d = Math.abs(ts[i] - t); if (d < bd){ bd = d; bi = i; } }
    if (vs[bi] == null){ tip.style.display = "none"; return; }
    tip.innerHTML = `<b>${fmtT(ts[bi])}</b><br>${fmt(vs[bi])}`;
    tip.style.display = "block";
    const px = ev.clientX - r.left;
    tip.style.left = (px > r.width - 120 ? px - tip.offsetWidth - 12 : px + 12) + "px";
    tip.style.top = "0px";
  });
  box.addEventListener("mouseleave", () => tip.style.display = "none");
}

/* ---------------- hue ribbon ---------------- */
function drawHue(){
  if (!THEME.light) return;
  const cv = document.getElementById("hue");
  const hues = THEME.light.hue;
  const w = cv.clientWidth || 480; cv.width = w * 2; cv.height = 128;
  const ctx = cv.getContext("2d");
  const cw = cv.width / hues.length;
  for (let i = 0; i < hues.length; i++){
    ctx.fillStyle = hues[i];
    ctx.fillRect(i * cw, 0, Math.ceil(cw) + 1, cv.height);
  }
}

/* ---------------- comparison ---------------- */
(function compare(){
  const a = THEME.audio, c = THEME.coupling || {};
  const techs = [...new Set(THEME.segments.map(s => s.technique))].join(" + ");
  const bandsVisited = [...new Set(THEME.segments.map(s => s.band).filter(b => b !== "—"))].join(" → ");
  const rows = [
    ["<b>This theme</b> <span class='tag measured'>measured</span>",
      techs, bandsVisited || "—",
      "coupled light, " + (c.pct_locked != null ? c.pct_locked + "% locked" : "—"),
      "programmed arc, " + THEME.segments.length + " phases"],
    ["YouTube binaural loop <span class='tag'>context</span>",
      "binaural only", "one fixed band", "no light channel", "static — one frequency for an hour"],
    ["Dreamachine <span class='tag'>context</span>",
      "light only", "alpha (~8–13 Hz)", "flicker yes, no audio coupling", "static — one rate, eyes closed"],
    ["Lucia N°03 / clinic strobes <span class='tag'>context</span>",
      "light-first", "programmable", "practitioner-operated, $$$", "session design varies by operator"],
    ["Sham / placebo <span class='tag'>open question</span>",
      "—", "—", "—", "the n-of-1 journal program is how we test this — join it"],
  ];
  document.getElementById("compare").innerHTML =
    `<table><thead><tr><th>What</th><th>Technique</th><th>Bands</th><th>Light</th><th>Protocol</th></tr></thead>
    <tbody>${rows.map(r => `<tr>${r.map(cell => `<td>${cell}</td>`).join("")}</tr>`).join("")}</tbody></table>`;
})();

/* ---------------- footer + render ---------------- */
document.getElementById("foot").textContent =
  (THEME.is_demo ? "Demo journey — synthesized to exercise the instrument. Hand it a real session next. · " : "") +
  "Decoded with analyzer.py — stdlib Python + ffmpeg, zero dependencies.";

function renderAll(){
  drawProtocol(); drawSpec(); drawHue();
  const a = THEME.audio;
  smallLine("loudness", a.t, a.rms, css("--c-sound") || "#B8842B", a.duration_s, v => "level " + v.toFixed(3));
  if (THEME.light) smallLine("luma", THEME.light.luma.map((_, i) => i + 0.5), THEME.light.luma,
    css("--c-light") || "#2E9BBF", a.duration_s, v => "brightness " + Math.round(v));
}
renderAll();
let rT; addEventListener("resize", () => { clearTimeout(rT); rT = setTimeout(renderAll, 180); });
new MutationObserver(renderAll).observe(document.documentElement, {attributes: true, attributeFilter: ["data-theme"]});
</script>
"""


def build(theme_path, out_path=None):
    theme = json.loads(Path(theme_path).read_text())
    name = theme["name"].replace(" demo", "").replace(" (demo)", "")
    html = (TEMPLATE
            .replace("__NAME__", name)
            .replace("__NAME_HTML__", name + ",")
            .replace("__DEMO_CHIP__",
                     '<span class="demo-chip">demo data — synthesized session</span>'
                     if theme.get("is_demo") else "")
            .replace("__THEME_JSON__", json.dumps(theme)))
    out = Path(out_path) if out_path else HERE / "docs" / "index.html"
    out.parent.mkdir(exist_ok=True)
    out.write_text(html)
    print("wrote", out, "(%.0f KB)" % (out.stat().st_size / 1024))
    return out


if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else str(HERE / "themes" / "first-flight-demo.json")
    build(src)
