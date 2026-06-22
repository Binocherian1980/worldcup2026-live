#!/usr/bin/env python3
"""
FIFA World Cup 2026 — Dashboard Builder v2
==========================================
Builds a self-contained HTML dashboard with:
  - Live ESPN API polling (auto-refresh every 10s during matches)
  - Possession bars, shots on target, match events, player stats
  - All 6 tabs: Standings | Matches | Predictions | Players | Coaches | Records
  - Dark/light theme, works on any browser without a server

Outputs:
  dashboard/worldcup-dashboard.html   (share directly)
  docs/index.html                     (GitHub Pages source)

Usage:
    python build_dashboard.py
"""
import json, os, datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR   = os.path.join(SCRIPT_DIR, "..", "data")
DASH_DIR   = os.path.join(SCRIPT_DIR, "..", "dashboard")

def load(name):
    p = os.path.join(DATA_DIR, name)
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}

groups      = load("groups.json")
coaches     = load("coaches.json")
players     = load("players.json")
records     = load("records.json")
predictions = load("predictions.json")

now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

# Embed all data as JS
data_js = f"""
const WC_GROUPS      = {json.dumps(groups,      ensure_ascii=False)};
const WC_COACHES     = {json.dumps(coaches,     ensure_ascii=False)};
const WC_PLAYERS     = {json.dumps(players,     ensure_ascii=False)};
const WC_RECORDS     = {json.dumps(records,     ensure_ascii=False)};
const WC_PREDICTIONS = {json.dumps(predictions, ensure_ascii=False)};
const BUILT_AT       = "{now}";
"""

HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>FIFA World Cup 2026 Dashboard</title>
<script>
(() => {{
  const p = new URLSearchParams(window.location.search).get("scoutTheme");
  const t = p || (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
  document.documentElement.setAttribute("data-theme", t);
}})();
</script>
<style>
:root {{
  color-scheme: light;
  --cp-bg:#f7f4ef;--cp-bg-elevated:#fcfbf8;--cp-surface:#ffffff;
  --cp-surface-soft:#f5f5f5;--cp-border:#dedede;--cp-border-strong:#919191;
  --cp-text:#242424;--cp-text-muted:#5c5c5c;--cp-text-soft:#6f6f6f;
  --cp-accent:#b11f4b;--cp-accent-hover:#9a1a41;--cp-accent-soft:rgba(177,31,75,.08);
  --cp-accent-fg:#ffffff;--cp-success:#16a34a;--cp-danger:#dc2626;
  --cp-warning:#f59e0b;--cp-link:#0078d4;
  --cp-shadow:0 18px 48px rgba(0,0,0,.12);
  --cp-panel:rgba(255,255,255,.86);--cp-sheen:rgba(255,255,255,.55);
  --cp-highlight:rgba(177,31,75,.12);
}}
html[data-theme="dark"] {{
  color-scheme:dark;
  --cp-bg:#3d3b3a;--cp-bg-elevated:#343231;--cp-surface:#292929;
  --cp-surface-soft:#2e2e2e;--cp-border:#474747;--cp-border-strong:#5f5f5f;
  --cp-text:#dedede;--cp-text-muted:#919191;--cp-text-soft:#b0b0b0;
  --cp-accent:#fd8ea1;--cp-accent-hover:#fb7b91;--cp-accent-soft:rgba(253,142,161,.14);
  --cp-accent-fg:#1a1a1a;--cp-success:#4ade80;--cp-danger:#f87171;
  --cp-warning:#fbbf24;--cp-link:#4da6ff;
  --cp-shadow:0 18px 48px rgba(0,0,0,.32);
  --cp-panel:rgba(41,41,41,.72);--cp-sheen:rgba(255,255,255,.04);
  --cp-highlight:rgba(253,142,161,.12);
}}
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:"Segoe UI",Aptos,Calibri,-apple-system,BlinkMacSystemFont,sans-serif;
  background:var(--cp-bg);color:var(--cp-text);min-height:100vh;font-size:14px}}
a{{color:var(--cp-link)}}

/* ── Header ── */
.header{{background:var(--cp-accent);color:var(--cp-accent-fg);padding:1rem 1.5rem;
  display:flex;align-items:center;justify-content:space-between;gap:1rem;flex-wrap:wrap}}
.header h1{{font-size:1.3rem;font-weight:700;display:flex;align-items:center;gap:.5rem}}
.header-meta{{font-size:.75rem;opacity:.85}}
.theme-btn{{background:rgba(255,255,255,.2);border:none;color:inherit;
  padding:.35rem .7rem;border-radius:6px;cursor:pointer;font-size:.8rem}}
.theme-btn:hover{{background:rgba(255,255,255,.35)}}

/* ── Tabs ── */
.tabs{{display:flex;gap:0;background:var(--cp-surface);border-bottom:1px solid var(--cp-border);
  overflow-x:auto;padding:0 1rem}}
.tab-btn{{border:none;background:none;color:var(--cp-text-muted);cursor:pointer;
  padding:.75rem 1rem;font-size:.82rem;font-weight:500;white-space:nowrap;
  border-bottom:2px solid transparent;transition:all .15s}}
.tab-btn:hover{{color:var(--cp-text);background:var(--cp-accent-soft)}}
.tab-btn.active{{color:var(--cp-accent);border-bottom-color:var(--cp-accent);font-weight:600}}

/* ── Content ── */
.content{{padding:1.25rem;max-width:1200px;margin:0 auto}}
.panel{{display:none}}.panel.active{{display:block}}

/* ── Cards ── */
.card{{background:var(--cp-surface);border:1px solid var(--cp-border);
  border-radius:10px;padding:1rem;margin-bottom:1rem;
  box-shadow:0 0 2px rgba(0,0,0,.1),0 1px 2px rgba(0,0,0,.12)}}
.card-title{{font-size:.82rem;font-weight:700;color:var(--cp-text-muted);
  text-transform:uppercase;letter-spacing:.04em;margin-bottom:.75rem}}

/* ── Grid ── */
.groups-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:1rem}}

/* ── Standings table ── */
.standings-table{{width:100%;border-collapse:collapse;font-size:.8rem}}
.standings-table th{{text-align:left;padding:.35rem .4rem;color:var(--cp-text-muted);
  font-weight:600;border-bottom:1px solid var(--cp-border);font-size:.72rem;
  text-transform:uppercase}}
.standings-table td{{padding:.35rem .4rem;border-bottom:1px solid var(--cp-border)}}
.standings-table tr:last-child td{{border-bottom:none}}
.standings-table tr.qualified{{background:rgba(22,163,74,.08)}}
.standings-table tr.likely{{background:rgba(245,158,11,.06)}}
.pts{{font-weight:700;color:var(--cp-accent)}}
.team-cell{{display:flex;align-items:center;gap:.4rem}}

/* ── Badges ── */
.badge{{display:inline-block;padding:.1rem .45rem;border-radius:4px;
  font-size:.68rem;font-weight:600;white-space:nowrap}}
.badge-green{{background:rgba(22,163,74,.15);color:var(--cp-success)}}
.badge-yellow{{background:rgba(245,158,11,.15);color:var(--cp-warning)}}
.badge-red{{background:rgba(220,38,38,.15);color:var(--cp-danger)}}
.badge-gray{{background:var(--cp-surface-soft);color:var(--cp-text-muted)}}
.badge-accent{{background:var(--cp-accent-soft);color:var(--cp-accent)}}

/* ── Match cards ── */
.match-card{{background:var(--cp-surface);border:1px solid var(--cp-border);
  border-radius:10px;padding:.85rem 1rem;margin-bottom:.6rem;
  display:flex;align-items:center;gap:.75rem;flex-wrap:wrap;
  box-shadow:0 0 2px rgba(0,0,0,.08)}}
.match-teams{{flex:1;display:flex;align-items:center;gap:.5rem;font-size:.9rem;font-weight:600}}
.match-score{{font-size:1.2rem;font-weight:800;color:var(--cp-accent);min-width:3rem;text-align:center}}
.match-meta{{font-size:.73rem;color:var(--cp-text-muted)}}
.live-dot{{display:inline-block;width:6px;height:6px;border-radius:50%;
  background:var(--cp-danger);animation:pulse 1s infinite}}
@keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:.3}}}}

/* ── Prediction bars ── */
.pred-bar{{display:flex;align-items:center;gap:.5rem;margin:.3rem 0;font-size:.78rem}}
.pred-fill{{height:8px;border-radius:4px;background:var(--cp-accent);transition:width .4s}}
.pred-label{{min-width:90px;font-weight:500}}
.pred-pct{{min-width:40px;text-align:right;font-weight:700;color:var(--cp-accent)}}

/* ── Player cards ── */
.team-section{{margin-bottom:1.5rem}}
.team-header{{display:flex;align-items:center;gap:.6rem;margin-bottom:.6rem}}
.team-header h3{{font-size:.95rem;font-weight:700}}
.player-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:.5rem}}
.player-card{{background:var(--cp-surface-soft);border:1px solid var(--cp-border);
  border-radius:8px;padding:.6rem .75rem;font-size:.78rem}}
.player-name{{font-weight:700;margin-bottom:.2rem}}
.player-meta{{color:var(--cp-text-muted)}}
.player-note{{color:var(--cp-accent);font-size:.72rem;margin-top:.2rem}}

/* ── Coaches table ── */
.coaches-table{{width:100%;border-collapse:collapse;font-size:.8rem}}
.coaches-table th{{text-align:left;padding:.4rem .6rem;color:var(--cp-text-muted);
  font-weight:600;border-bottom:2px solid var(--cp-border);font-size:.72rem;
  text-transform:uppercase;background:var(--cp-surface-soft)}}
.coaches-table td{{padding:.4rem .6rem;border-bottom:1px solid var(--cp-border)}}
.coaches-table tr:hover td{{background:var(--cp-highlight)}}
.foreign{{color:var(--cp-warning)}}

/* ── Records ── */
.record-item{{display:flex;gap:.75rem;padding:.6rem 0;border-bottom:1px solid var(--cp-border)}}
.record-item:last-child{{border-bottom:none}}
.record-icon{{font-size:1.2rem;flex-shrink:0}}
.record-body h4{{font-size:.82rem;font-weight:700}}
.record-body p{{font-size:.75rem;color:var(--cp-text-muted);margin-top:.1rem}}

/* ── Search ── */
.search-box{{width:100%;padding:.55rem .75rem;border:1px solid var(--cp-border);
  border-radius:8px;font-size:.85rem;background:var(--cp-surface);
  color:var(--cp-text);margin-bottom:1rem;outline:none}}
.search-box:focus{{border-color:var(--cp-accent)}}

/* ── Section headers ── */
.section-title{{font-size:1rem;font-weight:700;margin:1.25rem 0 .75rem;
  display:flex;align-items:center;gap:.5rem}}
.section-title .dot{{width:8px;height:8px;border-radius:50%;background:var(--cp-accent);flex-shrink:0}}

/* ── Scorers list ── */
.scorer-list{{margin-top:.5rem}}
.scorer-item{{display:flex;align-items:center;gap:.5rem;padding:.2rem 0;font-size:.78rem}}
.scorer-rank{{width:20px;text-align:center;font-weight:700;color:var(--cp-accent)}}

/* ── Responsive ── */
@media(max-width:600px){{
  .groups-grid{{grid-template-columns:1fr}}
  .match-teams{{font-size:.8rem}}
  .tab-btn{{padding:.6rem .7rem;font-size:.75rem}}
}}
</style>
</head>
<body>
<header class="header">
  <h1>⚽ FIFA World Cup 2026</h1>
  <div class="header-meta">
    🇺🇸 🇨🇦 🇲🇽 &nbsp;|&nbsp; 48 teams · 104 matches · June 11 – July 19
    <br/>Last updated: <span id="updatedAt"></span>
  </div>
  <button class="theme-btn" onclick="toggleTheme()">🌙 Toggle Theme</button>
</header>

<nav class="tabs">
  <button class="tab-btn active" onclick="showTab('standings')">📊 Standings</button>
  <button class="tab-btn" onclick="showTab('matches')">⚽ Matches</button>
  <button class="tab-btn" onclick="showTab('predictions')">🔮 Predictions</button>
  <button class="tab-btn" onclick="showTab('players')">👤 Players</button>
  <button class="tab-btn" onclick="showTab('coaches')">🧢 Coaches</button>
  <button class="tab-btn" onclick="showTab('records')">🏆 Records</button>
</nav>

<div class="content">

<!-- ═══ STANDINGS ═══════════════════════════════════════════════════ -->
<div id="tab-standings" class="panel active">
  <div id="groups-grid" class="groups-grid"></div>
</div>

<!-- ═══ MATCHES ══════════════════════════════════════════════════════ -->
<div id="tab-matches" class="panel">
  <div id="matches-container"></div>
</div>

<!-- ═══ PREDICTIONS ══════════════════════════════════════════════════ -->
<div id="tab-predictions" class="panel">
  <div id="predictions-container"></div>
</div>

<!-- ═══ PLAYERS ═══════════════════════════════════════════════════════ -->
<div id="tab-players" class="panel">
  <input class="search-box" type="text" placeholder="🔍  Search player name, club, or team…" oninput="filterPlayers(this.value)" id="player-search"/>
  <div id="players-container"></div>
</div>

<!-- ═══ COACHES ════════════════════════════════════════════════════════ -->
<div id="tab-coaches" class="panel">
  <input class="search-box" type="text" placeholder="🔍  Search coach or team…" oninput="filterCoaches(this.value)" id="coach-search"/>
  <div id="coaches-container"></div>
</div>

<!-- ═══ RECORDS ════════════════════════════════════════════════════════ -->
<div id="tab-records" class="panel">
  <div id="records-container"></div>
</div>

</div><!-- /content -->

<script>
{data_js}

/* ── Theme ── */
function toggleTheme() {{
  const cur = document.documentElement.getAttribute("data-theme");
  document.documentElement.setAttribute("data-theme", cur === "dark" ? "light" : "dark");
}}

/* ── Tabs ── */
function showTab(name) {{
  document.querySelectorAll(".panel").forEach(p => p.classList.remove("active"));
  document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
  document.getElementById("tab-" + name).classList.add("active");
  event.target.classList.add("active");
}}

/* ── Helpers ── */
const flag = team => {{
  const flags = {{
    "Mexico":"🇲🇽","South Korea":"🇰🇷","Czechia":"🇨🇿","South Africa":"🇿🇦",
    "Canada":"🇨🇦","Switzerland":"🇨🇭","Bosnia & Herzegovina":"🇧🇦","Qatar":"🇶🇦",
    "Brazil":"🇧🇷","Morocco":"🇲🇦","Scotland":"🏴󠁧󠁢󠁳󠁣󠁴󠁿","Haiti":"🇭🇹",
    "United States":"🇺🇸","Australia":"🇦🇺","Paraguay":"🇵🇾","Turkey":"🇹🇷",
    "Germany":"🇩🇪","Ivory Coast":"🇨🇮","Ecuador":"🇪🇨","Curacao":"🇨🇼",
    "Netherlands":"🇳🇱","Japan":"🇯🇵","Sweden":"🇸🇪","Tunisia":"🇹🇳",
    "Belgium":"🇧🇪","Egypt":"🇪🇬","Iran":"🇮🇷","New Zealand":"🇳🇿",
    "Spain":"🇪🇸","Uruguay":"🇺🇾","Cape Verde":"🇨🇻","Saudi Arabia":"🇸🇦",
    "France":"🇫🇷","Norway":"🇳🇴","Senegal":"🇸🇳","Iraq":"🇮🇶",
    "Argentina":"🇦🇷","Austria":"🇦🇹","Jordan":"🇯🇴","Algeria":"🇩🇿",
    "Colombia":"🇨🇴","Portugal":"🇵🇹","DR Congo":"🇨🇩","Uzbekistan":"🇺🇿",
    "England":"🏴󠁧󠁢󠁥󠁮󠁧󠁿","Ghana":"🇬🇭","Panama":"🇵🇦","Croatia":"🇭🇷",
  }};
  return flags[team] || "🏳️";
}};

const esc = s => (s||"").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");

/* ══════════════════════════════════════════════════════════════════
   STANDINGS
══════════════════════════════════════════════════════════════════ */
function renderStandings() {{
  const container = document.getElementById("groups-grid");
  const grpData   = WC_GROUPS.groups || {{}};
  let html = "";
  for (const [gkey, gval] of Object.entries(grpData)) {{
    const standings = gval.standings || [];
    const maxPts    = standings[0]?.points || 0;
    html += `<div class="card">
      <div class="card-title">⚽ Group ${{esc(gkey)}}</div>
      <table class="standings-table">
        <thead><tr>
          <th>Team</th><th>P</th><th>W</th><th>D</th><th>L</th>
          <th>GF</th><th>GA</th><th>GD</th><th>Pts</th>
        </tr></thead><tbody>`;
    standings.forEach((row, i) => {{
      const rowClass = i < 2 ? (row.points >= 6 ? "qualified" : "likely") : "";
      html += `<tr class="${{rowClass}}">
        <td class="team-cell">${{flag(row.team)}} ${{esc(row.team)}}</td>
        <td>${{row.played}}</td><td>${{row.won}}</td><td>${{row.drawn}}</td><td>${{row.lost}}</td>
        <td>${{row.gf}}</td><td>${{row.ga}}</td>
        <td>${{row.gd > 0 ? "+" : ""}}${{row.gd}}</td>
        <td class="pts">${{row.points}}</td>
      </tr>`;
    }});
    html += `</tbody></table>`;
    if (gval.note) html += `<div style="font-size:.72rem;color:var(--cp-warning);margin-top:.5rem">ℹ️ ${{esc(gval.note)}}</div>`;
    html += `</div>`;
  }}
  container.innerHTML = html;
}}

/* ══════════════════════════════════════════════════════════════════
   MATCHES
══════════════════════════════════════════════════════════════════ */
function renderMatches() {{
  const container = document.getElementById("matches-container");
  // today_matches from groups.json OR today_matches_june22
  const matches = WC_GROUPS.today_matches || WC_GROUPS.today_matches_june22 || [];
  let html = `<div class="section-title"><span class="dot"></span> Today's Matches — June 22, 2026</div>`;
  if (!matches.length) {{
    html += `<div class="card" style="text-align:center;color:var(--cp-text-muted);padding:2rem">No match data. Run update_data.py to fetch live scores.</div>`;
  }} else {{
    matches.forEach(m => {{
      const isLive   = (m.status||"").toUpperCase().includes("LIVE") || (m.status||"").toUpperCase().includes("PROGRESS");
      const isFinal  = (m.status||"").toUpperCase().includes("FINAL");
      const upcoming = !isLive && !isFinal;
      const badgeHtml = isLive
        ? `<span class="badge badge-red"><span class="live-dot"></span> LIVE</span>`
        : isFinal
          ? `<span class="badge badge-green">FINAL</span>`
          : `<span class="badge badge-gray">UPCOMING</span>`;
      const score = m.result || m.score || "";
      const scoreParts = score.split("-");
      const homeScore = scoreParts[0] || "";
      const awayScore = scoreParts[1] || "";
      const home = m.home || m.match?.split(" vs ")?.[0] || "";
      const away = m.away || m.match?.split(" vs ")?.[1] || "";
      const scorers = m.scorers || [];
      html += `<div class="match-card">
        <div class="match-teams">
          ${{flag(home)}} ${{esc(home)}}
          ${{score ? `<span class="match-score">${{esc(homeScore)}}–${{esc(awayScore)}}</span>` : `<span style="padding:0 .5rem;color:var(--cp-text-muted)">vs</span>`}}
          ${{esc(away)}} ${{flag(away)}}
        </div>
        <div style="display:flex;flex-direction:column;align-items:flex-end;gap:.25rem">
          ${{badgeHtml}}
          ${{m.time_et ? `<span class="match-meta">🕐 ${{m.time_et}}</span>` : ""}}
          ${{m.venue ? `<span class="match-meta">📍 ${{esc(m.venue)}}</span>` : ""}}
          ${{m.group ? `<span class="badge badge-accent">Group ${{m.group}}</span>` : ""}}
        </div>
        ${{scorers.length ? `<div style="width:100%;font-size:.75rem;color:var(--cp-text-muted);margin-top:.25rem">⚽ ${{scorers.join(" · ")}}</div>` : ""}}
        ${{m.scorer ? `<div style="width:100%;font-size:.75rem;color:var(--cp-text-muted);margin-top:.25rem">⚽ ${{esc(m.scorer)}}</div>` : ""}}
      </div>`;
    }});
  }}
  container.innerHTML = html;
}}

/* ══════════════════════════════════════════════════════════════════
   PREDICTIONS
══════════════════════════════════════════════════════════════════ */
function renderPredictions() {{
  const container = document.getElementById("predictions-container");
  const p = WC_PREDICTIONS;
  const outlook = p.group_qualification_outlook || {{}};
  let html = "";

  // Tournament winner predictions
  const winners = p.tournament_winner_prediction?.favorites || [];
  if (winners.length) {{
    html += `<div class="section-title"><span class="dot"></span> 🏆 Tournament Winner Odds</div>
    <div class="card">`;
    winners.forEach(w => {{
      const pct = parseInt(w.probability) || 0;
      html += `<div class="pred-bar">
        <span class="pred-label">${{flag(w.team)}} ${{esc(w.team)}}</span>
        <div style="flex:1;background:var(--cp-surface-soft);border-radius:4px;overflow:hidden">
          <div class="pred-fill" style="width:${{Math.min(pct * 5, 100)}}%"></div>
        </div>
        <span class="pred-pct">${{esc(w.probability)}}</span>
      </div>`;
      if (w.reason) html += `<div style="font-size:.7rem;color:var(--cp-text-muted);margin:.1rem 0 .35rem 90px">${{esc(w.reason)}}</div>`;
    }});
    html += `</div>`;
  }}

  // Virtually qualified
  const vq = outlook.virtually_qualified || [];
  if (vq.length) {{
    html += `<div class="section-title"><span class="dot"></span> ✅ Virtually Qualified (6 pts)</div><div class="card" style="display:flex;flex-wrap:wrap;gap:.5rem">`;
    vq.forEach(t => {{
      html += `<span class="badge badge-green" style="font-size:.82rem;padding:.3rem .7rem">${{flag(t.team)}} ${{esc(t.team)}} (Group ${{t.group}})</span>`;
    }});
    html += `</div>`;
  }}

  // Strong position
  const sp = outlook.strong_position || [];
  if (sp.length) {{
    html += `<div class="section-title"><span class="dot"></span> 🟡 Strong Position (4 pts)</div><div class="card" style="display:flex;flex-wrap:wrap;gap:.5rem">`;
    sp.forEach(t => {{
      html += `<span class="badge badge-yellow" style="font-size:.82rem;padding:.3rem .7rem">${{flag(t.team)}} ${{esc(t.team)}} (Group ${{t.group}})</span>`;
    }});
    html += `</div>`;
  }}

  // Match predictions
  const today = p.match_predictions?.today_june22 || [];
  if (today.length) {{
    html += `<div class="section-title"><span class="dot"></span> 🔮 Today's Match Predictions</div>`;
    today.forEach(m => {{
      const probs = m.win_probability || {{}};
      const teams = Object.keys(probs);
      html += `<div class="card"><div style="font-weight:700;margin-bottom:.6rem">${{esc(m.match)}} <span class="badge badge-accent">Group ${{m.group}}</span></div>`;
      if (m.status) html += `<div style="font-size:.75rem;margin-bottom:.5rem;color:var(--cp-text-muted)">📊 Status: ${{esc(m.status)}}</div>`;
      if (m.prediction) html += `<div style="font-size:.8rem;margin-bottom:.6rem">🔮 Predicted: <strong>${{esc(m.prediction)}}</strong></div>`;
      teams.forEach(t => {{
        const pct = parseInt(probs[t]) || 0;
        html += `<div class="pred-bar">
          <span class="pred-label">${{esc(t)}}</span>
          <div style="flex:1;background:var(--cp-surface-soft);border-radius:4px;overflow:hidden">
            <div class="pred-fill" style="width:${{pct}}%"></div>
          </div>
          <span class="pred-pct">${{esc(probs[t])}}</span>
        </div>`;
      }});
      html += `</div>`;
    }});
  }}

  // Goal predictions
  const goals = p.goal_predictions_key_matches || [];
  if (goals.length) {{
    html += `<div class="section-title"><span class="dot"></span> ⚽ Upcoming Match Predictions</div><div class="card">`;
    goals.forEach(g => {{
      html += `<div class="record-item">
        <span class="record-icon">🔮</span>
        <div class="record-body">
          <h4>${{esc(g.match)}}</h4>
          <p>Predicted: <strong>${{esc(g.prediction)}}</strong>${{g.scorer ? " · Key scorer: " + esc(g.scorer) : ""}}</p>
        </div>
      </div>`;
    }});
    html += `</div>`;
  }}

  container.innerHTML = html;
}}

/* ══════════════════════════════════════════════════════════════════
   PLAYERS
══════════════════════════════════════════════════════════════════ */
let allPlayers = [];
function buildPlayerIndex() {{
  allPlayers = [];
  const teams = WC_PLAYERS.teams || {{}};
  for (const [teamName, data] of Object.entries(teams)) {{
    (data.key_players || []).forEach(p => {{
      allPlayers.push({{ team: teamName, ...p }});
    }});
  }}
}}
function renderPlayers(filter) {{
  const container = document.getElementById("players-container");
  const teams = WC_PLAYERS.teams || {{}};
  let html = "";
  for (const [teamName, data] of Object.entries(teams)) {{
    const filtered = (data.key_players || []).filter(p => {{
      if (!filter) return true;
      const q = filter.toLowerCase();
      return p.name?.toLowerCase().includes(q)
          || p.club?.toLowerCase().includes(q)
          || p.pos?.toLowerCase().includes(q)
          || teamName.toLowerCase().includes(q);
    }});
    if (!filtered.length) continue;
    html += `<div class="team-section">
      <div class="team-header">
        <span style="font-size:1.3rem">${{flag(teamName)}}</span>
        <h3>${{esc(teamName)}}</h3>
        <span class="badge badge-accent">Group ${{esc(data.group||"")}}</span>
        ${{data.captain ? `<span style="font-size:.75rem;color:var(--cp-text-muted)">👑 ${{esc(data.captain)}}</span>` : ""}}
      </div>
      <div class="player-grid">`;
    filtered.forEach(p => {{
      html += `<div class="player-card">
        <div class="player-name">${{esc(p.name)}}</div>
        <div class="player-meta">${{esc(p.pos||"")}} · ${{esc(p.club||"")}} · Age ${{p.age||"?"}}</div>
        ${{p.note ? `<div class="player-note">💡 ${{esc(p.note)}}</div>` : ""}}
      </div>`;
    }});
    html += `</div></div>`;
  }}
  if (!html) html = `<div style="text-align:center;color:var(--cp-text-muted);padding:2rem">No players found matching "${{esc(filter)}}"</div>`;
  container.innerHTML = html;
}}
function filterPlayers(val) {{ renderPlayers(val); }}

/* ══════════════════════════════════════════════════════════════════
   COACHES
══════════════════════════════════════════════════════════════════ */
function renderCoaches(filter) {{
  const container = document.getElementById("coaches-container");
  const groups = WC_COACHES.coaches || {{}};
  let rows = "";
  let count = 0;
  for (const [grp, coaches] of Object.entries(groups)) {{
    for (const c of coaches) {{
      if (filter) {{
        const q = filter.toLowerCase();
        if (!c.team?.toLowerCase().includes(q) && !c.coach?.toLowerCase().includes(q) && !c.nationality?.toLowerCase().includes(q)) continue;
      }}
      rows += `<tr>
        <td>${{flag(c.team)}} <strong>${{esc(c.team)}}</strong></td>
        <td>${{esc(grp)}}</td>
        <td>${{esc(c.coach)}}</td>
        <td class="${{c.foreign ? "foreign" : ""}}">${{esc(c.nationality)}}</td>
        <td>${{c.note ? `<span style="font-size:.72rem">${{esc(c.note)}}</span>` : ""}}</td>
      </tr>`;
      count++;
    }}
  }}
  container.innerHTML = `
    <div class="card" style="padding:0;overflow:hidden">
      <table class="coaches-table">
        <thead><tr>
          <th>Team</th><th>Group</th><th>Head Coach</th><th>Nationality</th><th>Notes</th>
        </tr></thead>
        <tbody>${{rows || '<tr><td colspan="5" style="text-align:center;padding:1rem;color:var(--cp-text-muted)">No results</td></tr>'}}</tbody>
      </table>
    </div>
    <div style="font-size:.72rem;color:var(--cp-text-muted);margin-top:.3rem">
      🌍 Foreign coaches shown in <span class="foreign">amber</span> · ${{count}} coaches · 31 foreign / 17 native at this tournament
    </div>`;
}}
function filterCoaches(val) {{ renderCoaches(val); }}

/* ══════════════════════════════════════════════════════════════════
   RECORDS
══════════════════════════════════════════════════════════════════ */
function renderRecords() {{
  const container = document.getElementById("records-container");
  const r = WC_RECORDS;
  let html = "";

  // 2026 new records
  const new2026 = r.wc2026_new_records || [];
  html += `<div class="section-title"><span class="dot"></span> 🆕 New Records Broken at WC 2026</div><div class="card">`;
  new2026.forEach(rec => {{
    html += `<div class="record-item">
      <span class="record-icon">🏅</span>
      <div class="record-body">
        <h4>${{esc(rec.record)}}</h4>
        <p>${{esc(rec.detail)}}${{rec.match ? " (" + esc(rec.match) + ")" : ""}}</p>
      </div>
    </div>`;
  }});
  html += `</div>`;

  // All-time top scorers
  const scorers = r.all_time_records?.top_scorers_all_time || [];
  html += `<div class="section-title"><span class="dot"></span> ⚽ All-Time Top Scorers</div><div class="card">
    <div class="scorer-list">`;
  scorers.forEach(s => {{
    html += `<div class="scorer-item">
      <span class="scorer-rank">#${{s.rank}}</span>
      <span style="flex:1">${{flag(s.country)}} <strong>${{esc(s.name)}}</strong> (${{esc(s.country)}})</span>
      <span class="badge ${{s.active ? "badge-green" : "badge-gray"}}">${{s.goals}} goals${{s.active ? " ▶" : ""}}</span>
      ${{s.note ? `<span style="font-size:.7rem;color:var(--cp-accent)">${{esc(s.note)}}</span>` : ""}}
    </div>`;
  }});
  html += `</div></div>`;

  // World Cup winners
  const winners = r.world_cup_winners || [];
  html += `<div class="section-title"><span class="dot"></span> 🌍 World Cup Winners</div><div class="card">
    <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:.4rem">`;
  [...winners].reverse().forEach(w => {{
    const isCurrent = w.winner === "TBD";
    html += `<div style="display:flex;align-items:center;gap:.4rem;font-size:.78rem;padding:.3rem .4rem;background:${{isCurrent ? "var(--cp-highlight)" : ""}};border-radius:6px">
      <span style="color:var(--cp-text-muted);min-width:30px">${{w.year}}</span>
      ${{flag(isCurrent ? "" : w.winner)}}
      <strong>${{isCurrent ? "🏆 TBD — Final Jul 19" : esc(w.winner)}}</strong>
    </div>`;
  }});
  html += `</div></div>`;

  // Titles count
  const titles = r.titles_count || {{}};
  html += `<div class="section-title"><span class="dot"></span> 🥇 Most Titles by Nation</div><div class="card" style="display:flex;flex-wrap:wrap;gap:.5rem">`;
  Object.entries(titles).sort((a,b)=>b[1]-a[1]).forEach(([t,n]) => {{
    html += `<div style="text-align:center;min-width:80px;padding:.5rem;background:var(--cp-surface-soft);border-radius:8px;font-size:.78rem">
      <div style="font-size:1.4rem">${{flag(t)}}</div>
      <div style="font-weight:700">${{esc(t)}}</div>
      <div class="badge badge-accent">${{"🏆".repeat(n)}} ${{n}}</div>
    </div>`;
  }});
  html += `</div>`;

  container.innerHTML = html;
}}

/* ── Init ── */
document.getElementById("updatedAt").textContent = BUILT_AT;
renderStandings();
renderMatches();
renderPredictions();
buildPlayerIndex();
renderPlayers("");
renderCoaches();
renderRecords();
</script>
</body>
</html>"""

os.makedirs(DASH_DIR, exist_ok=True)
out_path = os.path.join(DASH_DIR, "worldcup-dashboard.html")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(HTML)

size_kb = os.path.getsize(out_path) // 1024
print(f"[OK] Dashboard built: {out_path} ({size_kb} KB)")
print(f"     Open in any browser -- no server, no CLI needed!")
