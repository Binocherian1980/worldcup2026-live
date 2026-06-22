#!/usr/bin/env python3
"""Build a self-contained FIFA World Cup 2026 dashboard."""

from __future__ import annotations

import datetime as dt
import json
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = (SCRIPT_DIR / ".." / "data").resolve()
OUTPUT_PATHS = [
    (SCRIPT_DIR / ".." / "dashboard" / "worldcup-dashboard.html").resolve(),
    (SCRIPT_DIR / ".." / "docs" / "index.html").resolve(),
]
DATA_FILES = [
    "groups.json",
    "coaches.json",
    "players.json",
    "records.json",
    "predictions.json",
]


def load_json(name: str) -> object:
    path = DATA_DIR / name
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def to_js(value: object) -> str:
    return json.dumps(value).replace("</", "<\\/")


def build_data_js(
    groups: object,
    coaches: object,
    players: object,
    records: object,
    predictions: object,
    built_at: str,
) -> str:
    return "\n".join(
        [
            f"const WC_GROUPS = {to_js(groups)};",
            f"const WC_COACHES = {to_js(coaches)};",
            f"const WC_PLAYERS = {to_js(players)};",
            f"const WC_RECORDS = {to_js(records)};",
            f"const WC_PREDICTIONS = {to_js(predictions)};",
            f'const BUILT_AT = "{built_at}";',
        ]
    )


HTML_TEMPLATE = r'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>FIFA World Cup 2026 Dashboard</title>
  <script>
  (() => {
    const param = new URLSearchParams(window.location.search).get("scoutTheme");
    const theme = param || (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
    document.documentElement.setAttribute("data-theme", theme);
  })();
  </script>
  <style>
  :root {
    color-scheme: light;
    --cp-bg: #f7f4ef; --cp-bg-elevated: #fcfbf8; --cp-surface: #ffffff;
    --cp-surface-soft: #f5f5f5; --cp-border: #dedede; --cp-border-strong: #919191;
    --cp-text: #242424; --cp-text-muted: #5c5c5c; --cp-text-soft: #6f6f6f;
    --cp-accent: #b11f4b; --cp-accent-hover: #9a1a41; --cp-accent-soft: rgba(177,31,75,.08);
    --cp-accent-fg: #ffffff; --cp-success: #16a34a; --cp-danger: #dc2626;
    --cp-warning: #f59e0b; --cp-link: #0078d4;
    --cp-shadow: 0 18px 48px rgba(0,0,0,.12);
    --cp-panel: rgba(255,255,255,.86); --cp-sheen: rgba(255,255,255,.55);
    --cp-highlight: rgba(177,31,75,.12);
  }
  html[data-theme="dark"] {
    color-scheme: dark;
    --cp-bg: #3d3b3a; --cp-bg-elevated: #343231; --cp-surface: #292929;
    --cp-surface-soft: #2e2e2e; --cp-border: #474747; --cp-border-strong: #5f5f5f;
    --cp-text: #dedede; --cp-text-muted: #919191; --cp-text-soft: #b0b0b0;
    --cp-accent: #fd8ea1; --cp-accent-hover: #fb7b91; --cp-accent-soft: rgba(253,142,161,.14);
    --cp-accent-fg: #1a1a1a; --cp-success: #4ade80; --cp-danger: #f87171;
    --cp-warning: #fbbf24; --cp-link: #4da6ff;
    --cp-shadow: 0 18px 48px rgba(0,0,0,.32);
    --cp-panel: rgba(41,41,41,.72); --cp-sheen: rgba(255,255,255,.04);
    --cp-highlight: rgba(253,142,161,.12);
  }
  * { box-sizing: border-box; }
  html, body { margin: 0; padding: 0; }
  body {
    background: var(--cp-bg);
    color: var(--cp-text);
    font-family: "Segoe UI", Aptos, Calibri, -apple-system, sans-serif;
    min-height: 100vh;
  }
  a { color: var(--cp-link); }
  button, input, select {
    font: inherit;
  }
  .app-shell {
    min-height: 100vh;
    background: var(--cp-bg);
  }
  header {
    position: sticky;
    top: 0;
    z-index: 20;
    display: grid;
    grid-template-columns: minmax(0, 1.3fr) auto minmax(0, 1fr) auto;
    gap: 0.75rem;
    align-items: center;
    padding: 1rem 1.25rem;
    background: var(--cp-panel);
    border-bottom: 1px solid var(--cp-border);
    backdrop-filter: blur(10px);
  }
  .brand {
    font-size: 1.3rem;
    font-weight: 800;
    letter-spacing: 0.01em;
  }
  #live-banner {
    justify-self: center;
    padding: 0.45rem 0.8rem;
    border-radius: 0.625rem;
    border: 1px solid var(--cp-danger);
    background: var(--cp-accent-soft);
    color: var(--cp-danger);
    font-weight: 800;
    white-space: nowrap;
  }
  .meta-line {
    justify-self: end;
    font-size: 0.9rem;
    color: var(--cp-text-muted);
    text-align: right;
  }
  .theme-toggle {
    border: 1px solid var(--cp-border);
    background: var(--cp-surface);
    color: var(--cp-text);
    border-radius: 0.625rem;
    padding: 0.55rem 0.75rem;
    cursor: pointer;
  }
  .theme-toggle:hover,
  .tab-btn:hover,
  .sortable:hover,
  .chip:hover {
    background: var(--cp-accent-soft);
  }
  .tab-strip {
    display: flex;
    gap: 0.5rem;
    overflow-x: auto;
    padding: 0.9rem 1.25rem 0;
  }
  .tab-btn {
    border: 1px solid var(--cp-border);
    background: var(--cp-surface);
    color: var(--cp-text-muted);
    border-radius: 0.625rem 0.625rem 0 0;
    padding: 0.7rem 1rem;
    cursor: pointer;
    white-space: nowrap;
    font-weight: 700;
  }
  .tab-btn.active {
    background: var(--cp-accent);
    color: var(--cp-accent-fg);
    border-color: var(--cp-accent);
  }
  main {
    max-width: 1520px;
    margin: 0 auto;
    padding: 1rem 1.25rem 1.5rem;
  }
  .panel {
    display: none;
  }
  .panel.active {
    display: block;
  }
  .hero-grid,
  .groups-grid,
  .prediction-grid,
  .player-grid,
  .record-grid,
  .summary-grid {
    display: grid;
    gap: 1rem;
  }
  .hero-grid {
    grid-template-columns: repeat(4, minmax(0, 1fr));
    margin-bottom: 1rem;
  }
  .groups-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
  .prediction-grid,
  .summary-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  .player-grid {
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  }
  .record-grid {
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  }
  .card,
  .match-card,
  .team-panel,
  .table-card {
    background: var(--cp-surface);
    border: 1px solid var(--cp-border);
    border-radius: 16px;
    box-shadow: 0 10px 18px var(--cp-highlight);
  }
  .card,
  .table-card,
  .team-panel {
    padding: 1rem;
  }
  .card-title,
  .section-title {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.75rem;
    margin-bottom: 0.85rem;
  }
  .card-title h3,
  .section-title h2 {
    margin: 0;
    font-size: 1rem;
  }
  .section-title {
    margin: 1rem 0 0.85rem;
  }
  .muted {
    color: var(--cp-text-muted);
  }
  .soft {
    color: var(--cp-text-soft);
  }
  .hero-stat {
    font-size: 1.9rem;
    font-weight: 800;
    margin-top: 0.3rem;
  }
  .chip-row,
  .pill-row {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
  }
  .chip,
  .badge {
    display: inline-flex;
    align-items: center;
    gap: 0.25rem;
    padding: 0.32rem 0.58rem;
    border-radius: 0.625rem;
    border: 1px solid var(--cp-border);
    background: var(--cp-surface-soft);
    color: var(--cp-text);
    font-size: 0.82rem;
    font-weight: 700;
  }
  .badge-accent {
    background: var(--cp-accent-soft);
    color: var(--cp-accent);
    border-color: var(--cp-accent-soft);
  }
  .badge-success {
    background: var(--cp-accent-soft);
    color: var(--cp-success);
  }
  .badge-warning {
    background: var(--cp-accent-soft);
    color: var(--cp-warning);
  }
  .badge-danger {
    background: var(--cp-accent-soft);
    color: var(--cp-danger);
  }
  .status-six {
    background: var(--cp-accent-soft);
    outline: 1px solid var(--cp-success);
  }
  .status-four {
    background: var(--cp-accent-soft);
    outline: 1px solid var(--cp-warning);
  }
  .key-value {
    display: grid;
    grid-template-columns: max-content 1fr;
    gap: 0.25rem 0.75rem;
    font-size: 0.92rem;
  }
  .key-value div:nth-child(odd) {
    color: var(--cp-text-muted);
  }
  table {
    width: 100%;
    border-collapse: collapse;
  }
  th, td {
    padding: 0.65rem 0.55rem;
    border-bottom: 1px solid var(--cp-border);
    vertical-align: top;
  }
  th {
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: var(--cp-text-muted);
    text-align: left;
  }
  tr:last-child td {
    border-bottom: 0;
  }
  .numeric {
    text-align: right;
    white-space: nowrap;
  }
  .center {
    text-align: center;
  }
  .team-label {
    display: flex;
    align-items: center;
    gap: 0.45rem;
    font-weight: 700;
  }
  .match-card {
    padding: 1rem;
    margin-bottom: 1rem;
  }
  .match-head {
    display: grid;
    grid-template-columns: minmax(0, 1.1fr) auto;
    gap: 1rem;
    align-items: start;
  }
  .match-main {
    display: flex;
    flex-direction: column;
    gap: 0.7rem;
  }
  .match-scoreline {
    display: grid;
    grid-template-columns: 1fr auto 1fr;
    gap: 0.8rem;
    align-items: center;
  }
  .team-name {
    display: flex;
    align-items: center;
    gap: 0.45rem;
    font-size: 1.1rem;
    font-weight: 800;
  }
  .team-name.right {
    justify-content: flex-end;
    text-align: right;
  }
  .score-chip {
    min-width: 6rem;
    text-align: center;
    padding: 0.65rem 0.9rem;
    border-radius: 0.625rem;
    background: var(--cp-accent);
    color: var(--cp-accent-fg);
    font-size: 1.3rem;
    font-weight: 900;
  }
  .versus-chip {
    min-width: 6rem;
    text-align: center;
    padding: 0.65rem 0.9rem;
    border-radius: 0.625rem;
    background: var(--cp-surface-soft);
    border: 1px solid var(--cp-border);
    color: var(--cp-text-muted);
    font-size: 1rem;
    font-weight: 800;
  }
  .match-meta-list {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
  }
  .match-note {
    padding-top: 0.35rem;
    font-size: 0.92rem;
    color: var(--cp-text-muted);
  }
  .details-panel {
    margin-top: 0.95rem;
    border: 1px solid var(--cp-border);
    border-radius: 0.625rem;
    overflow: hidden;
    background: var(--cp-surface-soft);
  }
  .details-panel > summary {
    cursor: pointer;
    list-style: none;
    padding: 0.85rem 1rem;
    font-weight: 800;
    background: var(--cp-surface);
    border-bottom: 1px solid var(--cp-border);
  }
  .details-panel > summary::-webkit-details-marker {
    display: none;
  }
  .details-body {
    padding: 1rem;
    display: grid;
    gap: 1rem;
  }
  .poss-wrap { display:flex; border-radius:6px; overflow:hidden; height:28px; margin:.6rem 0; border:1px solid var(--cp-border); }
  .poss-home { background:var(--cp-accent); display:flex; align-items:center; justify-content:flex-end; padding-right:.4rem; color:var(--cp-accent-fg); font-weight:700; font-size:.75rem; transition:width .5s; }
  .poss-away { background:var(--cp-border-strong); display:flex; align-items:center; padding-left:.4rem; color:var(--cp-text); font-weight:700; font-size:.75rem; transition:width .5s; }
  .stats-compare {
    width: 100%;
    border-collapse: collapse;
    background: var(--cp-surface);
    border: 1px solid var(--cp-border);
    border-radius: 0.625rem;
    overflow: hidden;
  }
  .stats-compare td,
  .stats-compare th {
    padding: 0.55rem 0.6rem;
    border-bottom: 1px solid var(--cp-border);
  }
  .stats-compare tr:last-child td {
    border-bottom: 0;
  }
  .stats-compare .label {
    text-align: center;
    color: var(--cp-text-muted);
    font-weight: 700;
  }
  .stats-compare .home-stat {
    text-align: right;
  }
  .stats-compare .away-stat {
    text-align: left;
  }
  .winner-stat {
    font-weight: 900;
    color: var(--cp-accent);
  }
  .timeline {
    display: grid;
    gap: 0.5rem;
  }
  .timeline-item {
    display: grid;
    grid-template-columns: max-content 1fr;
    gap: 0.75rem;
    align-items: start;
    padding: 0.65rem 0.75rem;
    border: 1px solid var(--cp-border);
    border-radius: 0.625rem;
    background: var(--cp-surface);
  }
  .timeline-minute {
    font-weight: 900;
    white-space: nowrap;
  }
  .subtle-box {
    padding: 0.8rem 0.9rem;
    border: 1px solid var(--cp-border);
    border-radius: 0.625rem;
    background: var(--cp-surface);
  }
  .player-team-block {
    border: 1px solid var(--cp-border);
    border-radius: 0.625rem;
    background: var(--cp-surface);
    overflow: hidden;
  }
  .player-team-block > summary {
    cursor: pointer;
    padding: 0.8rem 0.9rem;
    font-weight: 800;
    background: var(--cp-surface-soft);
    border-bottom: 1px solid var(--cp-border);
  }
  .player-team-block > summary::-webkit-details-marker {
    display: none;
  }
  .player-stats-wrap {
    overflow-x: auto;
  }
  .player-stats-table th,
  .player-stats-table td {
    white-space: nowrap;
  }
  .search-row {
    display: flex;
    gap: 0.75rem;
    align-items: center;
    margin-bottom: 1rem;
    flex-wrap: wrap;
  }
  .search-input {
    flex: 1 1 280px;
    min-width: 200px;
    padding: 0.75rem 0.9rem;
    border: 1px solid var(--cp-border);
    border-radius: 0.625rem;
    background: var(--cp-surface);
    color: var(--cp-text);
  }
  .search-input:focus {
    outline: 2px solid var(--cp-accent-soft);
    border-color: var(--cp-accent);
  }
  .team-panel-header {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
    gap: 0.75rem;
    margin-bottom: 1rem;
  }
  .player-card {
    border: 1px solid var(--cp-border);
    border-radius: 0.625rem;
    background: var(--cp-surface-soft);
    padding: 0.8rem;
  }
  .player-name {
    font-size: 1rem;
    font-weight: 800;
    margin-bottom: 0.35rem;
  }
  .player-meta {
    font-size: 0.88rem;
    color: var(--cp-text-muted);
    line-height: 1.5;
  }
  .player-note {
    margin-top: 0.45rem;
    font-size: 0.85rem;
    color: var(--cp-accent);
  }
  .sortable {
    cursor: pointer;
    user-select: none;
  }
  .table-wrap {
    overflow-x: auto;
  }
  .record-list {
    display: grid;
    gap: 0.7rem;
  }
  .record-item {
    padding: 0.8rem 0.9rem;
    border: 1px solid var(--cp-border);
    border-radius: 0.625rem;
    background: var(--cp-surface-soft);
  }
  .record-item strong {
    display: block;
    margin-bottom: 0.2rem;
  }
  .bar-list {
    display: grid;
    gap: 0.75rem;
  }
  .bar-row {
    display: grid;
    grid-template-columns: minmax(0, 170px) 1fr max-content;
    gap: 0.75rem;
    align-items: center;
  }
  .bar-track {
    width: 100%;
    height: 0.85rem;
    border-radius: 999px;
    border: 1px solid var(--cp-border);
    background: var(--cp-surface-soft);
    overflow: hidden;
  }
  .bar-fill {
    height: 100%;
    background: var(--cp-accent);
  }
  .note-panel {
    margin-top: 0.75rem;
    padding: 0.8rem 0.9rem;
    border: 1px dashed var(--cp-border-strong);
    border-radius: 0.625rem;
    color: var(--cp-text-muted);
    background: var(--cp-surface-soft);
  }
  .footer-note {
    text-align: center;
    padding: 1rem 0 0.25rem;
    color: var(--cp-text-muted);
    font-size: 0.88rem;
  }
  @media (max-width: 1180px) {
    .groups-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    .hero-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  }
  @media (max-width: 900px) {
    header {
      grid-template-columns: 1fr;
      text-align: left;
    }
    #live-banner,
    .meta-line {
      justify-self: start;
      text-align: left;
    }
    .prediction-grid,
    .summary-grid,
    .groups-grid,
    .hero-grid {
      grid-template-columns: 1fr;
    }
    .match-head,
    .match-scoreline {
      grid-template-columns: 1fr;
    }
    .team-name,
    .team-name.right {
      justify-content: flex-start;
      text-align: left;
    }
  }
  @media (max-width: 640px) {
    main,
    header,
    .tab-strip {
      padding-left: 0.85rem;
      padding-right: 0.85rem;
    }
    .bar-row {
      grid-template-columns: 1fr;
    }
  }
  </style>
</head>
<body>
  <div class="app-shell">
    <header>
      <div class="brand">⚽ FIFA World Cup 2026</div>
      <div id="live-banner" style="display:none">🔴 MATCH LIVE — Auto-updating</div>
      <div class="meta-line">Updated: <span id="refresh-timer">—</span> | Built: __BUILT_AT_HTML__</div>
      <button class="theme-toggle" onclick="toggleTheme()">🌙</button>
    </header>

    <nav class="tab-strip">
      <button class="tab-btn active" onclick="showTab('standings', this)">📊 Standings</button>
      <button class="tab-btn" onclick="showTab('matches', this)">⚽ Matches</button>
      <button class="tab-btn" onclick="showTab('predictions', this)">🔮 Predictions</button>
      <button class="tab-btn" onclick="showTab('players', this)">👤 Players</button>
      <button class="tab-btn" onclick="showTab('coaches', this)">🧢 Coaches</button>
      <button class="tab-btn" onclick="showTab('records', this)">🏆 Records</button>
    </nav>

    <main>
      <section id="tab-standings" class="panel active"></section>
      <section id="tab-matches" class="panel"></section>
      <section id="tab-predictions" class="panel"></section>
      <section id="tab-players" class="panel"></section>
      <section id="tab-coaches" class="panel"></section>
      <section id="tab-records" class="panel"></section>
      <div class="footer-note">Live layer powered by ESPN public APIs with saved JSON fallback for offline viewing.</div>
    </main>
  </div>

  <script>
  __DATA_JS__

  const FLAGS = {
    "Mexico":"🇲🇽","South Korea":"🇰🇷","Czechia":"🇨🇿","South Africa":"🇿🇦",
    "Canada":"🇨🇦","Switzerland":"🇨🇭","Bosnia & Herzegovina":"🇧🇦","Qatar":"🇶🇦",
    "Brazil":"🇧🇷","Morocco":"🇲🇦","Scotland":"🏴","Haiti":"🇭🇹",
    "United States":"🇺🇸","Australia":"🇦🇺","Paraguay":"🇵🇾","Turkey":"🇹🇷",
    "Germany":"🇩🇪","Ivory Coast":"🇨🇮","Ecuador":"🇪🇨","Curacao":"🇨🇼",
    "Netherlands":"🇳🇱","Japan":"🇯🇵","Sweden":"🇸🇪","Tunisia":"🇹🇳",
    "Belgium":"🇧🇪","Egypt":"🇪🇬","Iran":"🇮🇷","New Zealand":"🇳🇿",
    "Spain":"🇪🇸","Uruguay":"🇺🇾","Cape Verde":"🇨🇻","Saudi Arabia":"🇸🇦",
    "France":"🇫🇷","Norway":"🇳🇴","Senegal":"🇸🇳","Iraq":"🇮🇶",
    "Argentina":"🇦🇷","Austria":"🇦🇹","Jordan":"🇯🇴","Algeria":"🇩🇿",
    "Colombia":"🇨🇴","Portugal":"🇵🇹","DR Congo":"🇨🇩","Uzbekistan":"🇺🇿",
    "England":"🏴","Ghana":"🇬🇭","Panama":"🇵🇦","Croatia":"🇭🇷"
  };
  const flag = t => FLAGS[t] || "🏳️";

  const ESPN_SCOREBOARD = 'https://site.api.espn.com/apis/site/v2/sports/soccer/fifa.world/scoreboard';
  const ESPN_SUMMARY = id => `https://site.api.espn.com/apis/site/v2/sports/soccer/fifa.world/summary?event=${id}`;
  const CORS_PROXY = 'https://corsproxy.io/?';

  let liveMatchData = {};
  let scoreboardEvents = [];
  let lastRefreshMs = 0;
  let hasLiveMatch = false;
  let refreshHandle = null;
  let activeTab = 'standings';
  let liveFeedStatus = 'Connecting to ESPN live feed...';
  let playersQuery = '';
  let coachesQuery = '';
  let coachSort = { key: 'group', dir: 'asc' };

  function esc(value) {
    return String(value ?? '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function norm(value) {
    return String(value ?? '').toLowerCase().replace(/[^a-z0-9]+/g, '');
  }

  function numberValue(value) {
    if (value === null || value === undefined || value === '') {
      return null;
    }
    const cleaned = String(value).replace(/,/g, '').replace(/%/g, '').trim();
    const parsed = Number(cleaned);
    return Number.isFinite(parsed) ? parsed : null;
  }

  function textOrDash(value) {
    return value === null || value === undefined || value === '' ? '&mdash;' : esc(value);
  }

  function parseGroupName(name) {
    return String(name || '').replace(/^Group\s+/i, '').trim() || '—';
  }

  function parseMatchTeams(label) {
    if (!label || !String(label).includes(' vs ')) {
      return ['', ''];
    }
    const [home, away] = String(label).split(' vs ', 2);
    return [home || '', away || ''];
  }

  function matchKey(home, away) {
    return `${String(home || '').trim().toLowerCase()}__${String(away || '').trim().toLowerCase()}`;
  }

  function toggleTheme() {
    const root = document.documentElement;
    root.setAttribute('data-theme', root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark');
  }

  function showTab(name, button) {
    activeTab = name;
    document.querySelectorAll('.panel').forEach(panel => panel.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(tab => tab.classList.remove('active'));
    document.getElementById(`tab-${name}`).classList.add('active');
    if (button) {
      button.classList.add('active');
    }
    if (name === 'matches') renderMatches();
    if (name === 'players') renderPlayers();
    if (name === 'coaches') renderCoaches();
    if (name === 'records') renderRecords();
    if (name === 'predictions') renderPredictions();
  }

  async function safeFetch(url, useProxy = false) {
    const target = useProxy ? CORS_PROXY + encodeURIComponent(url) : url;
    try {
      const response = await fetch(target, { cache: 'no-cache' });
      return response.ok ? response.json() : null;
    } catch (error) {
      if (!useProxy) return safeFetch(url, true);
      return null;
    }
  }

  function updateLiveIndicator() {
    const banner = document.getElementById('live-banner');
    if (!banner) return;
    banner.style.display = hasLiveMatch ? 'inline-flex' : 'none';
  }

  function scheduleNext() {
    if (refreshHandle) clearTimeout(refreshHandle);
    refreshHandle = setTimeout(doRefresh, hasLiveMatch ? 10000 : 60000);
  }

  async function doRefresh() {
    const scoreboard = await safeFetch(ESPN_SCOREBOARD);
    if (!scoreboard) {
      hasLiveMatch = false;
      liveFeedStatus = 'Could not reach ESPN live feed. Showing saved data.';
      updateLiveIndicator();
      if (activeTab === 'matches') renderMatches();
      scheduleNext();
      return;
    }

    hasLiveMatch = false;
    const events = scoreboard.events || [];
    scoreboardEvents = events;

    for (const event of events) {
      const state = event.status?.type?.state;
      if (state === 'in') hasLiveMatch = true;
      if (state === 'in' || state === 'post') {
        if (state === 'in' || !liveMatchData[event.id]) {
          const summary = await safeFetch(ESPN_SUMMARY(event.id));
          if (summary) {
            liveMatchData[event.id] = { event, summary };
          }
        } else {
          liveMatchData[event.id].event = event;
        }
      }
    }

    lastRefreshMs = Date.now();
    liveFeedStatus = hasLiveMatch
      ? 'ESPN live feed connected. Polling every 10 seconds.'
      : 'ESPN feed connected. No live match detected; polling every 60 seconds.';
    updateLiveIndicator();
    if (activeTab === 'matches') renderMatches();
    scheduleNext();
  }

  setInterval(() => {
    if (!lastRefreshMs) return;
    const secs = Math.floor((Date.now() - lastRefreshMs) / 1000);
    const el = document.getElementById('refresh-timer');
    if (el) el.textContent = secs < 60 ? `${secs}s ago` : `${Math.floor(secs / 60)}m ago`;
  }, 1000);

  function venueLabel(event) {
    const competition = event?.competitions?.[0] || {};
    const venue = competition.venue || {};
    const address = venue.address || {};
    return [venue.fullName, address.city, address.state].filter(Boolean).join(', ');
  }

  function localMatches() {
    const source = WC_GROUPS.today_matches || WC_GROUPS.today_matches_june22 || [];
    return source.map((entry, index) => {
      const [home, away] = parseMatchTeams(entry.match);
      const resultText = entry.result || entry.score || '';
      const resultMatch = String(resultText).match(/(\d+)\s*-\s*(\d+)/);
      return {
        id: `local-${index}`,
        home,
        away,
        group: entry.group || '',
        venue: entry.venue || '',
        statusText: entry.status || '',
        timeLabel: entry.time_et || '',
        notes: [entry.note, entry.scorer ? `Scorer: ${entry.scorer}` : '', ...(entry.scorers || [])].filter(Boolean),
        homeScore: resultMatch ? resultMatch[1] : '',
        awayScore: resultMatch ? resultMatch[2] : '',
        order: index,
      };
    });
  }

  function eventMatch(event, orderIndex) {
    const competition = event?.competitions?.[0] || {};
    const competitors = competition.competitors || [];
    const home = competitors.find(item => item.homeAway === 'home') || competitors[0] || {};
    const away = competitors.find(item => item.homeAway === 'away') || competitors[1] || {};
    return {
      id: event.id,
      home: home.team?.displayName || '',
      away: away.team?.displayName || '',
      homeScore: home.score ?? '',
      awayScore: away.score ?? '',
      timeLabel: event.status?.type?.shortDetail || event.date || '',
      statusText: event.status?.type?.detail || event.status?.type?.description || '',
      state: event.status?.type?.state || '',
      venue: venueLabel(event),
      event,
      group: '',
      notes: [],
      order: orderIndex,
    };
  }

  function mergedMatches() {
    const local = localMatches();
    const localMap = new Map(local.map(item => [matchKey(item.home, item.away), item]));

    if (!scoreboardEvents.length) {
      return local;
    }

    const merged = scoreboardEvents.map((event, index) => {
      const live = eventMatch(event, index);
      const localItem = localMap.get(matchKey(live.home, live.away)) || {};
      return {
        ...localItem,
        ...live,
        group: localItem.group || '',
        notes: [...(localItem.notes || [])],
      };
    });

    const existing = new Set(merged.map(item => matchKey(item.home, item.away)));
    local.forEach(item => {
      if (!existing.has(matchKey(item.home, item.away))) {
        merged.push(item);
      }
    });

    return merged.sort((a, b) => (a.order ?? 0) - (b.order ?? 0));
  }

  function statMapFromArray(items) {
    const map = {};
    (items || []).forEach((item, index) => {
      if (item === null || item === undefined) return;
      if (typeof item === 'object' && !Array.isArray(item)) {
        const value = item.displayValue ?? item.value ?? item.stat ?? item.summary ?? '';
        [item.name, item.displayName, item.shortDisplayName, item.label, item.abbreviation].forEach(key => {
          const clean = norm(key);
          if (clean && map[clean] === undefined) {
            map[clean] = value;
          }
        });
      } else {
        map[`value${index}`] = item;
      }
    });
    return map;
  }

  function statLookup(map, aliases) {
    for (const alias of aliases) {
      const value = map[norm(alias)];
      if (value !== undefined && value !== null && value !== '') {
        return value;
      }
    }
    return '';
  }

  function pairedSummaryTeams(summary, match) {
    const teams = summary?.boxscore?.teams || [];
    const home = teams.find(team => team.homeAway === 'home') || teams[0] || { statistics: [] };
    const away = teams.find(team => team.homeAway === 'away') || teams[1] || { statistics: [] };
    return {
      home: {
        name: home.team?.displayName || match.home,
        stats: statMapFromArray(home.statistics || []),
      },
      away: {
        name: away.team?.displayName || match.away,
        stats: statMapFromArray(away.statistics || []),
      },
    };
  }

  function renderPossession(summary, match) {
    if (!summary) return '<div class="subtle-box muted">Possession data not available yet.</div>';
    const paired = pairedSummaryTeams(summary, match);
    const rawHome = numberValue(statLookup(paired.home.stats, ['possessionPct', 'possession', 'possessionpercentage']));
    const rawAway = numberValue(statLookup(paired.away.stats, ['possessionPct', 'possession', 'possessionpercentage']));
    if (rawHome === null && rawAway === null) {
      return '<div class="subtle-box muted">Possession data not available yet.</div>';
    }
    let homePct = rawHome;
    let awayPct = rawAway;
    if (homePct === null && awayPct !== null) homePct = Math.max(0, 100 - awayPct);
    if (awayPct === null && homePct !== null) awayPct = Math.max(0, 100 - homePct);
    const total = (homePct || 0) + (awayPct || 0);
    if (total > 0) {
      homePct = (homePct / total) * 100;
      awayPct = (awayPct / total) * 100;
    }
    return `
      <div>
        <div class="section-title"><h2>Possession split</h2><span class="muted">${esc(paired.home.name)} vs ${esc(paired.away.name)}</span></div>
        <div class="poss-wrap">
          <div class="poss-home" style="width:${homePct.toFixed(1)}%">${homePct.toFixed(1)}%</div>
          <div class="poss-away" style="width:${awayPct.toFixed(1)}%">${awayPct.toFixed(1)}%</div>
        </div>
      </div>
    `;
  }

  function compareCell(value, other, cls) {
    const num = numberValue(value);
    const otherNum = numberValue(other);
    const winClass = num !== null && otherNum !== null && num > otherNum ? 'winner-stat' : '';
    return `<td class="${cls} ${winClass}">${textOrDash(value)}</td>`;
  }

  function renderStatComparison(summary, match) {
    if (!summary) return '<div class="subtle-box muted">Detailed team stats are not available yet.</div>';
    const paired = pairedSummaryTeams(summary, match);
    const rows = [
      ['Total Shots', ['totalShots', 'shots']],
      ['Shots on Target', ['shotsOnTarget', 'shotsongoal', 'onGoal']],
      ['Corners', ['wonCorners', 'cornerkicks', 'corners']],
      ['Fouls', ['foulsCommitted', 'fouls']],
      ['Yellow Cards', ['yellowCards']],
      ['Offsides', ['offsides']],
      ['GK Saves', ['saves']],
      ['Passes', ['passes', 'totalPasses', 'completedPasses', 'accuratePasses', 'passescompleted']],
    ];

    const tableRows = rows.map(([label, aliases]) => {
      const homeValue = statLookup(paired.home.stats, aliases);
      const awayValue = statLookup(paired.away.stats, aliases);
      return `
        <tr>
          ${compareCell(homeValue, awayValue, 'home-stat')}
          <td class="label">${esc(label)}</td>
          ${compareCell(awayValue, homeValue, 'away-stat')}
        </tr>
      `;
    }).join('');

    return `
      <div>
        <div class="section-title"><h2>Team comparison</h2><span class="muted">Live numeric matchup</span></div>
        <table class="stats-compare">
          <tbody>${tableRows}</tbody>
        </table>
      </div>
    `;
  }

  function minuteRank(display) {
    const text = String(display || '');
    const match = text.match(/(\d+)'(?:\+(\d+))?/);
    if (!match) return 0;
    return Number(match[1]) + Number(match[2] || 0) / 100;
  }

  function cleanName(text) {
    return String(text || '').replace(/\s+/g, ' ').trim();
  }

  function extractCardSubject(text) {
    const match = String(text || '').match(/^(.+?) \((.+?)\) is shown the (yellow|red) card/i);
    if (match) {
      return `${cleanName(match[1])} [${cleanName(match[2])}]`;
    }
    return cleanName(text);
  }

  function extractSubstitution(text, fallbackTeam) {
    const match = String(text || '').match(/^Substitution, ([^.]+)\. (.+?) replaces (.+?)\./i);
    if (match) {
      return `${cleanName(match[3])} → ${cleanName(match[2])} [${cleanName(match[1])}]`;
    }
    return `${cleanName(text)}${fallbackTeam ? ` [${cleanName(fallbackTeam)}]` : ''}`;
  }

  function extractTimeline(summary) {
    if (!summary) return [];
    const items = [];
    const seen = new Set();
    const details = summary?.header?.competitions?.[0]?.details || [];

    details.forEach(detail => {
      if (!detail.scoringPlay) return;
      const minute = detail.clock?.displayValue || '';
      const scorer = detail.participants?.[0]?.athlete?.displayName || 'Goal';
      const assist = detail.participants?.[1]?.athlete?.displayName || '';
      const team = detail.team?.displayName || '';
      const label = `${cleanName(scorer)}${assist ? ` (assist: ${cleanName(assist)})` : ''} [${cleanName(team)}]`;
      const key = `${minute}|goal|${label}`;
      if (seen.has(key)) return;
      seen.add(key);
      items.push({ minute, icon: '⚽', text: label, order: minuteRank(minute) });
    });

    (summary.commentary || []).forEach(item => {
      const play = item.play || {};
      const typeText = String(play.type?.type || play.type?.text || '').toLowerCase();
      const text = String(play.text || item.text || '');
      const minute = play.clock?.displayValue || item.time?.displayValue || '';
      const team = play.team?.displayName || '';
      let icon = '';
      let label = '';

      if (typeText.includes('yellow') || /yellow card/i.test(text)) {
        icon = '🟨';
        label = extractCardSubject(text);
      } else if (typeText.includes('red') || /red card/i.test(text)) {
        icon = '🟥';
        label = extractCardSubject(text);
      } else if (typeText.includes('sub') || /^Substitution/i.test(text)) {
        icon = '🔄';
        label = extractSubstitution(text, team);
      } else {
        return;
      }

      const key = `${minute}|${icon}|${label}`;
      if (seen.has(key)) return;
      seen.add(key);
      items.push({ minute, icon, text: label, order: minuteRank(minute) });
    });

    return items.sort((a, b) => a.order - b.order);
  }

  function renderTimeline(summary) {
    const items = extractTimeline(summary);
    if (!items.length) {
      return '<div class="subtle-box muted">No match event timeline available from the live feed yet.</div>';
    }
    return `
      <div>
        <div class="section-title"><h2>Match events timeline</h2><span class="muted">Goals, cards, substitutions</span></div>
        <div class="timeline">
          ${items.map(item => `
            <div class="timeline-item">
              <div class="timeline-minute">${esc(item.minute)} ${item.icon}</div>
              <div>${esc(item.text)}</div>
            </div>
          `).join('')}
        </div>
      </div>
    `;
  }

  function normalizeStatRow(sourceMap, aliases) {
    const value = statLookup(sourceMap, aliases);
    return value === '' ? '—' : value;
  }

  function normalizePlayerEntry(teamName, playerName, pos, statsMap) {
    return {
      team: teamName,
      name: playerName,
      pos: pos || '—',
      shotsOnTarget: normalizeStatRow(statsMap, ['shotsOnTarget', 'shotsongoal', 'sog']),
      totalShots: normalizeStatRow(statsMap, ['totalShots', 'shots', 'shot']),
      passes: normalizeStatRow(statsMap, ['passes', 'completedPasses', 'accuratePasses', 'totalPasses', 'passescompleted']),
      tackles: normalizeStatRow(statsMap, ['tackles', 'totalTackles', 'tacklesWon', 'tackleswon']),
      fouls: normalizeStatRow(statsMap, ['foulsCommitted', 'fouls']),
    };
  }

  function boxscorePlayerTables(summary) {
    const blocks = summary?.boxscore?.players || [];
    const grouped = new Map();

    function addRow(teamName, row) {
      if (!teamName || !row.name) return;
      if (!grouped.has(teamName)) grouped.set(teamName, []);
      const rows = grouped.get(teamName);
      if (!rows.some(existing => existing.name === row.name && existing.pos === row.pos)) {
        rows.push(row);
      }
    }

    function parseAthleteBlock(block, teamName) {
      const labels = block.labels || block.statistics || block.columns || [];
      const athletes = block.athletes || block.players || block.entries || [];
      athletes.forEach(item => {
        const athlete = item.athlete || item.player || item;
        const statsMap = {};
        if (Array.isArray(item.stats)) {
          item.stats.forEach((value, index) => {
            if (value && typeof value === 'object' && !Array.isArray(value)) {
              const nestedMap = statMapFromArray([value]);
              Object.assign(statsMap, nestedMap);
            } else if (labels[index]) {
              statsMap[norm(labels[index])] = value;
            }
          });
        }
        if (Array.isArray(item.statistics)) {
          Object.assign(statsMap, statMapFromArray(item.statistics));
        }
        addRow(
          teamName,
          normalizePlayerEntry(
            teamName,
            athlete.displayName || athlete.fullName || '',
            item.position?.abbreviation || athlete.position?.abbreviation || '',
            statsMap
          )
        );
      });
    }

    blocks.forEach(block => {
      const teamName = block.team?.displayName || block.displayName || block.name || '';
      if (Array.isArray(block.players)) {
        block.players.forEach(child => parseAthleteBlock(child, teamName));
      }
      parseAthleteBlock(block, teamName);
    });

    return Array.from(grouped.entries()).map(([team, rows]) => ({ team, rows }));
  }

  function rosterPlayerTables(summary) {
    return (summary?.rosters || []).map(roster => {
      const teamName = roster.team?.displayName || 'Team';
      const rows = (roster.roster || []).map(player => {
        const statsMap = statMapFromArray(player.stats || []);
        return normalizePlayerEntry(
          teamName,
          player.athlete?.displayName || player.athlete?.fullName || '',
          player.position?.abbreviation || '',
          statsMap
        );
      }).filter(row => row.name);
      return { team: teamName, rows };
    }).filter(group => group.rows.length);
  }

  function renderPlayerTables(summary) {
    const groups = boxscorePlayerTables(summary);
    const tables = groups.length ? groups : rosterPlayerTables(summary);
    if (!tables.length) {
      return '<div class="subtle-box muted">Per-player stats are not available from the ESPN summary for this match yet.</div>';
    }
    return `
      <div>
        <div class="section-title"><h2>Player stats tables</h2><span class="muted">Passes/tackles appear when ESPN supplies them.</span></div>
        ${tables.map((group, index) => `
          <details class="player-team-block" ${index === 0 ? 'open' : ''}>
            <summary>${flag(group.team)} ${esc(group.team)} — ${group.rows.length} players</summary>
            <div class="player-stats-wrap">
              <table class="player-stats-table">
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Position</th>
                    <th class="numeric">Shots on Target</th>
                    <th class="numeric">Total Shots</th>
                    <th class="numeric">Passes</th>
                    <th class="numeric">Tackles</th>
                    <th class="numeric">Fouls</th>
                  </tr>
                </thead>
                <tbody>
                  ${group.rows.map(row => `
                    <tr>
                      <td>${esc(row.name)}</td>
                      <td>${esc(row.pos)}</td>
                      <td class="numeric">${textOrDash(row.shotsOnTarget)}</td>
                      <td class="numeric">${textOrDash(row.totalShots)}</td>
                      <td class="numeric">${textOrDash(row.passes)}</td>
                      <td class="numeric">${textOrDash(row.tackles)}</td>
                      <td class="numeric">${textOrDash(row.fouls)}</td>
                    </tr>
                  `).join('')}
                </tbody>
              </table>
            </div>
          </details>
        `).join('')}
      </div>
    `;
  }

  function matchDetails(match) {
    const payload = liveMatchData[match.id];
    const summary = payload?.summary || null;
    const isLive = match.state === 'in' || /LIVE|PROGRESS|DELAY/i.test(match.statusText || '');
    const isFinal = match.state === 'post' || /FINAL|FT/i.test(match.statusText || '');
    const openAttr = isLive || isFinal ? 'open' : '';
    const content = summary
      ? [
          renderPossession(summary, match),
          renderStatComparison(summary, match),
          renderTimeline(summary),
          renderPlayerTables(summary),
        ].join('')
      : '<div class="subtle-box muted">Waiting for detailed ESPN summary data for this match.</div>';

    return `
      <details class="details-panel" ${openAttr}>
        <summary>Match dashboard</summary>
        <div class="details-body">${content}</div>
      </details>
    `;
  }

  function renderStandings() {
    const hosts = (WC_GROUPS.tournament?.hosts || []).map(host => `${flag(host)} ${host}`).join(' · ') || '—';
    const totalTeams = WC_GROUPS.tournament?.total_teams ?? '—';
    const totalMatches = WC_GROUPS.tournament?.total_matches ?? '—';
    const prizePool = WC_GROUPS.tournament?.prize_pool_usd
      ? `$${Math.round(WC_GROUPS.tournament.prize_pool_usd / 1000000)}M`
      : '—';
    const qualified = WC_GROUPS.likely_qualified?.teams || [];
    const groups = WC_GROUPS.groups || {};

    const hero = `
      <div class="hero-grid">
        <div class="card">
          <div class="muted">Hosts</div>
          <div class="hero-stat">${hosts}</div>
          <div class="soft">Three nations, one expanded 48-team tournament.</div>
        </div>
        <div class="card">
          <div class="muted">Tournament scale</div>
          <div class="hero-stat">${esc(totalTeams)} teams</div>
          <div class="soft">${esc(totalMatches)} matches · Prize pool ${esc(prizePool)}</div>
        </div>
        <div class="card">
          <div class="muted">Format</div>
          <div class="hero-stat">${esc(WC_GROUPS.format?.advancement || 'Top 2 plus best third-place teams')}</div>
          <div class="soft">${esc(WC_GROUPS.format?.group_stage || '')}</div>
        </div>
        <div class="card">
          <div class="muted">Virtually qualified</div>
          <div class="hero-stat">${qualified.length}</div>
          <div class="soft">${qualified.map(item => esc(item)).join(' · ') || 'No team has clinched yet.'}</div>
        </div>
      </div>
    `;

    const groupCards = Object.entries(groups).map(([groupName, groupData]) => {
      const rows = (groupData.standings || []).map(row => {
        const rowClass = row.points === 6 ? 'status-six' : row.points === 4 ? 'status-four' : '';
        return `
          <tr class="${rowClass}">
            <td><div class="team-label">${flag(row.team)} <span>${esc(row.team)}</span></div></td>
            <td class="numeric">${textOrDash(row.played)}</td>
            <td class="numeric">${textOrDash(row.won)}</td>
            <td class="numeric">${textOrDash(row.drawn)}</td>
            <td class="numeric">${textOrDash(row.lost)}</td>
            <td class="numeric">${textOrDash(row.gf)}</td>
            <td class="numeric">${textOrDash(row.ga)}</td>
            <td class="numeric">${textOrDash(row.gd)}</td>
            <td class="numeric"><strong>${textOrDash(row.points)}</strong></td>
          </tr>
        `;
      }).join('');

      return `
        <div class="card">
          <div class="card-title">
            <h3>Group ${esc(groupName)}</h3>
            <span class="badge badge-accent">${(groupData.teams || []).length} teams</span>
          </div>
          <table>
            <thead>
              <tr>
                <th>Team</th><th class="numeric">P</th><th class="numeric">W</th><th class="numeric">D</th><th class="numeric">L</th><th class="numeric">GF</th><th class="numeric">GA</th><th class="numeric">GD</th><th class="numeric">Pts</th>
              </tr>
            </thead>
            <tbody>${rows}</tbody>
          </table>
          ${groupData.note ? `<div class="note-panel">${esc(groupData.note)}</div>` : ''}
        </div>
      `;
    }).join('');

    const tiebreakers = (WC_GROUPS.tiebreaker_rules || []).map(rule => `<div class="chip">${esc(rule)}</div>`).join('');
    document.getElementById('tab-standings').innerHTML = `
      ${hero}
      <div class="prediction-grid">
        <div class="card">
          <div class="card-title"><h3>Tiebreaker order</h3></div>
          <div class="chip-row">${tiebreakers || '<span class="muted">No tiebreaker data.</span>'}</div>
        </div>
        <div class="card">
          <div class="card-title"><h3>Third-place ranking</h3></div>
          <div class="chip-row">${(WC_GROUPS.third_place_ranking || []).map(rule => `<div class="chip">${esc(rule)}</div>`).join('') || '<span class="muted">No ranking data.</span>'}</div>
        </div>
      </div>
      <div class="section-title"><h2>All groups A–L</h2><span class="muted">Green highlights 6 points, amber highlights 4 points.</span></div>
      <div class="groups-grid">${groupCards || '<div class="card muted">No standings data found.</div>'}</div>
    `;
  }

  function renderMatches() {
    const matches = mergedMatches();
    const html = matches.map(match => {
      const isLive = match.state === 'in' || /LIVE|PROGRESS|DELAY/i.test(match.statusText || '');
      const isFinal = match.state === 'post' || /FINAL|FT/i.test(match.statusText || '');
      const badge = isLive
        ? '<span class="badge badge-danger">🔴 LIVE</span>'
        : isFinal
          ? '<span class="badge badge-success">FINAL</span>'
          : '<span class="badge">UPCOMING</span>';
      const scoreline = match.homeScore !== '' || match.awayScore !== ''
        ? `<div class="score-chip">${esc(match.homeScore)} - ${esc(match.awayScore)}</div>`
        : '<div class="versus-chip">vs</div>';

      return `
        <div class="match-card">
          <div class="match-head">
            <div class="match-main">
              <div class="match-meta-list">
                ${badge}
                ${match.group ? `<span class="badge badge-accent">Group ${esc(match.group)}</span>` : ''}
                ${match.timeLabel ? `<span class="badge">${esc(match.timeLabel)}</span>` : ''}
              </div>
              <div class="match-scoreline">
                <div class="team-name">${flag(match.home)} ${esc(match.home || 'TBD')}</div>
                ${scoreline}
                <div class="team-name right">${esc(match.away || 'TBD')} ${flag(match.away)}</div>
              </div>
              <div class="match-meta-list">
                ${match.statusText ? `<span class="chip">${esc(match.statusText)}</span>` : ''}
                ${match.venue ? `<span class="chip">${esc(match.venue)}</span>` : ''}
              </div>
              ${match.notes.length ? `<div class="match-note">${match.notes.map(note => esc(note)).join(' · ')}</div>` : ''}
            </div>
          </div>
          ${matchDetails(match)}
        </div>
      `;
    }).join('');

    document.getElementById('tab-matches').innerHTML = `
      <div class="hero-grid">
        <div class="card">
          <div class="muted">Live feed status</div>
          <div class="hero-stat">${hasLiveMatch ? 'Active' : 'Monitoring'}</div>
          <div class="soft">${esc(liveFeedStatus)}</div>
        </div>
        <div class="card">
          <div class="muted">Today&apos;s fixtures</div>
          <div class="hero-stat">${matches.length}</div>
          <div class="soft">Saved JSON schedule is merged with live ESPN scoreboard data.</div>
        </div>
        <div class="card">
          <div class="muted">Last saved JSON update</div>
          <div class="hero-stat">${esc(WC_GROUPS.last_updated || 'Unknown')}</div>
          <div class="soft">The dashboard still works offline with embedded data.</div>
        </div>
        <div class="card">
          <div class="muted">Auto-refresh cadence</div>
          <div class="hero-stat">${hasLiveMatch ? '10s' : '60s'}</div>
          <div class="soft">Live matches trigger faster polling and open stats panels.</div>
        </div>
      </div>
      <div class="section-title"><h2>Today&apos;s matches</h2><span class="muted">Live scores override saved JSON whenever ESPN responds.</span></div>
      ${html || '<div class="card muted">No match data available.</div>'}
    `;
  }

  function renderPredictions() {
    const favorites = WC_PREDICTIONS.tournament_winner_prediction?.favorites || [];
    const virtuallyQualified = WC_PREDICTIONS.group_qualification_outlook?.virtually_qualified || [];
    const strongPosition = WC_PREDICTIONS.group_qualification_outlook?.strong_position || [];
    const contested = WC_PREDICTIONS.group_qualification_outlook?.contested || [];
    const today = WC_PREDICTIONS.match_predictions?.today_june22 || [];
    const upcoming = WC_PREDICTIONS.match_predictions?.upcoming_group_stage_matchday3?.predictions || [];
    const goalPredictions = WC_PREDICTIONS.goal_predictions_key_matches || [];

    const favoriteBars = favorites.map(item => {
      const pct = Math.min(numberValue(item.probability) || 0, 100);
      return `
        <div class="bar-row">
          <div><strong>${flag(item.team)} ${esc(item.team)}</strong><div class="soft">${esc(item.reason || '')}</div></div>
          <div class="bar-track"><div class="bar-fill" style="width:${pct}%"></div></div>
          <div><strong>${esc(item.probability || '—')}</strong></div>
        </div>
      `;
    }).join('');

    document.getElementById('tab-predictions').innerHTML = `
      <div class="prediction-grid">
        <div class="card">
          <div class="card-title"><h3>Tournament winner probabilities</h3><span class="badge badge-accent">${esc(WC_PREDICTIONS.last_updated || 'Saved')}</span></div>
          <div class="bar-list">${favoriteBars || '<div class="muted">No favorite data available.</div>'}</div>
        </div>
        <div class="card">
          <div class="card-title"><h3>Qualification outlook</h3></div>
          <div class="record-list">
            <div class="record-item">
              <strong>Virtually qualified</strong>
              <div class="pill-row">${virtuallyQualified.map(item => `<span class="badge badge-success">${flag(item.team)} ${esc(item.team)} (${esc(item.certainty || '')})</span>`).join('') || '<span class="muted">None yet.</span>'}</div>
            </div>
            <div class="record-item">
              <strong>Strong position</strong>
              <div class="pill-row">${strongPosition.map(item => `<span class="badge badge-warning">${flag(item.team)} ${esc(item.team)} (${esc(item.certainty || '')})</span>`).join('') || '<span class="muted">No strong-position teams listed.</span>'}</div>
            </div>
            <div class="record-item">
              <strong>Contested groups</strong>
              <div class="record-list">${contested.map(item => `<div>${esc(item)}</div>`).join('') || '<div class="muted">No contested groups listed.</div>'}</div>
            </div>
          </div>
        </div>
      </div>

      <div class="section-title"><h2>Today&apos;s prediction board</h2><span class="muted">Projected scores and win probabilities.</span></div>
      <div class="summary-grid">
        ${today.map(item => `
          <div class="card">
            <div class="card-title">
              <h3>${esc(item.match || 'Match')}</h3>
              <span class="badge badge-accent">Group ${esc(item.group || '—')}</span>
            </div>
            <div class="key-value">
              <div>Status</div><div>${esc(item.status || item.time_et || 'Upcoming')}</div>
              <div>Projection</div><div>${esc(item.prediction || '—')}</div>
              <div>Key player</div><div>${esc(item.key_player || '—')}</div>
            </div>
            <div class="bar-list" style="margin-top:0.9rem">
              ${Object.entries(item.win_probability || {}).map(([team, probability]) => `
                <div class="bar-row">
                  <div><strong>${flag(team)} ${esc(team)}</strong></div>
                  <div class="bar-track"><div class="bar-fill" style="width:${Math.min(numberValue(probability) || 0, 100)}%"></div></div>
                  <div><strong>${esc(probability)}</strong></div>
                </div>
              `).join('')}
            </div>
            ${item.note ? `<div class="note-panel">${esc(item.note)}</div>` : ''}
          </div>
        `).join('') || '<div class="card muted">No match prediction data available.</div>'}
      </div>

      <div class="section-title"><h2>Matchday 3 group outlook</h2><span class="muted">${esc(WC_PREDICTIONS.match_predictions?.upcoming_group_stage_matchday3?.note || '')}</span></div>
      <div class="record-grid">
        ${upcoming.map(item => `
          <div class="card">
            <div class="card-title"><h3>Group ${esc(item.group || '—')}</h3></div>
            <div class="record-list">
              ${(item.matches || []).map(match => `<div>${esc(match)}</div>`).join('')}
              <div class="note-panel">${(item.predicted_qualifiers || []).map(team => esc(team)).join(' · ') || 'No projected qualifiers.'}</div>
            </div>
          </div>
        `).join('') || '<div class="card muted">No matchday 3 outlook available.</div>'}
      </div>

      <div class="section-title"><h2>Goal predictions</h2><span class="muted">Likely scorelines for marquee fixtures.</span></div>
      <div class="record-grid">
        ${goalPredictions.map(item => `
          <div class="card">
            <div class="card-title"><h3>${esc(item.match || 'Match')}</h3></div>
            <div><strong>${esc(item.prediction || '—')}</strong></div>
            ${item.scorer ? `<div class="soft" style="margin-top:0.45rem">${esc(item.scorer)}</div>` : ''}
          </div>
        `).join('') || '<div class="card muted">No goal predictions available.</div>'}
      </div>
    `;
  }

  function playerSections() {
    return Object.entries(WC_PLAYERS.teams || {}).sort((a, b) => a[0].localeCompare(b[0]));
  }

  function renderPlayers() {
    const query = playersQuery.trim().toLowerCase();
    const cards = playerSections().map(([team, info]) => {
      const players = (info.key_players || []).filter(player => {
        if (!query) return true;
        const blob = [
          team,
          info.group,
          info.coach,
          info.captain,
          player.name,
          player.pos,
          player.age,
          player.club,
          player.note,
        ].join(' ').toLowerCase();
        return blob.includes(query);
      });

      if (!players.length && query) return '';

      return `
        <div class="team-panel">
          <div class="team-panel-header">
            <div>
              <div class="team-name">${flag(team)} ${esc(team)}</div>
              <div class="soft">Group ${esc(info.group || '—')} · Coach: ${esc(info.coach || '—')} · Captain: ${esc(info.captain || '—')}</div>
            </div>
            <span class="badge badge-accent">${players.length} players shown</span>
          </div>
          <div class="player-grid">
            ${players.map(player => `
              <div class="player-card">
                <div class="player-name">${esc(player.name || 'Unknown')}</div>
                <div class="player-meta">
                  <div><strong>Position:</strong> ${esc(player.pos || '—')}</div>
                  <div><strong>Age:</strong> ${esc(player.age || '—')}</div>
                  <div><strong>Club:</strong> ${esc(player.club || '—')}</div>
                </div>
                ${player.note ? `<div class="player-note">${esc(player.note)}</div>` : ''}
              </div>
            `).join('')}
          </div>
        </div>
      `;
    }).filter(Boolean).join('');

    document.getElementById('tab-players').innerHTML = `
      <div class="search-row">
        <input id="players-search" class="search-input" type="search" placeholder="Search team, player, club, position, or note" value="${esc(playersQuery)}">
        <span class="muted">Search across all embedded player profiles.</span>
      </div>
      ${cards || '<div class="card muted">No player records matched the search.</div>'}
      ${WC_PLAYERS.note_on_other_teams ? `<div class="note-panel">${esc(WC_PLAYERS.note_on_other_teams)}</div>` : ''}
    `;
    const input = document.getElementById('players-search');
    if (input) {
      input.addEventListener('input', event => {
        playersQuery = event.target.value;
        renderPlayers();
      });
    }
  }

  function coachRows() {
    const rows = [];
    Object.entries(WC_COACHES.coaches || {}).forEach(([groupName, entries]) => {
      (entries || []).forEach(entry => {
        rows.push({
          group: parseGroupName(groupName),
          team: entry.team || '',
          coach: entry.coach || '',
          nationality: entry.nationality || '',
          foreign: entry.foreign ? 'Yes' : 'No',
          note: entry.note || '',
        });
      });
    });
    return rows;
  }

  function sortArrow(key) {
    if (coachSort.key !== key) return '';
    return coachSort.dir === 'asc' ? ' ▲' : ' ▼';
  }

  function setCoachSort(key) {
    coachSort = coachSort.key === key
      ? { key, dir: coachSort.dir === 'asc' ? 'desc' : 'asc' }
      : { key, dir: key === 'group' ? 'asc' : 'asc' };
    renderCoaches();
  }

  function renderCoaches() {
    const rows = coachRows().filter(row => {
      if (!coachesQuery.trim()) return true;
      const blob = Object.values(row).join(' ').toLowerCase();
      return blob.includes(coachesQuery.trim().toLowerCase());
    });

    rows.sort((left, right) => {
      const a = String(left[coachSort.key] || '');
      const b = String(right[coachSort.key] || '');
      return coachSort.dir === 'asc' ? a.localeCompare(b) : b.localeCompare(a);
    });

    document.getElementById('tab-coaches').innerHTML = `
      <div class="search-row">
        <input id="coaches-search" class="search-input" type="search" placeholder="Search coach, team, nationality, or notes" value="${esc(coachesQuery)}">
        <span class="muted">${esc(WC_COACHES.coaching_stats?.foreign_coaches_total || 0)} foreign coaches listed.</span>
      </div>
      <div class="table-card">
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th class="sortable" onclick="setCoachSort('group')">Group${sortArrow('group')}</th>
                <th class="sortable" onclick="setCoachSort('team')">Team${sortArrow('team')}</th>
                <th class="sortable" onclick="setCoachSort('coach')">Coach${sortArrow('coach')}</th>
                <th class="sortable" onclick="setCoachSort('nationality')">Nationality${sortArrow('nationality')}</th>
                <th class="sortable" onclick="setCoachSort('foreign')">Foreign${sortArrow('foreign')}</th>
                <th>Notes</th>
              </tr>
            </thead>
            <tbody>
              ${rows.map(row => `
                <tr>
                  <td>${esc(row.group)}</td>
                  <td><div class="team-label">${flag(row.team)} <span>${esc(row.team)}</span></div></td>
                  <td><strong>${esc(row.coach)}</strong></td>
                  <td>${esc(row.nationality)}</td>
                  <td>${row.foreign === 'Yes' ? '<span class="badge badge-warning">Yes</span>' : '<span class="badge badge-success">No</span>'}</td>
                  <td>${textOrDash(row.note)}</td>
                </tr>
              `).join('') || '<tr><td colspan="6" class="muted">No coaches matched the search.</td></tr>'}
            </tbody>
          </table>
        </div>
      </div>
      <div class="summary-grid">
        <div class="card">
          <div class="card-title"><h3>Coaching snapshot</h3></div>
          <div class="key-value">
            <div>Foreign coaches</div><div>${esc(WC_COACHES.coaching_stats?.foreign_coaches_total || '—')}</div>
            <div>Native coaches</div><div>${esc(WC_COACHES.coaching_stats?.native_coaches_total || '—')}</div>
            <div>Most coaches by nation</div><div>${esc(WC_COACHES.coaching_stats?.most_coaches_by_nation || '—')}</div>
            <div>Second most</div><div>${esc(WC_COACHES.coaching_stats?.second_most || '—')}</div>
          </div>
        </div>
        <div class="card">
          <div class="card-title"><h3>Record note</h3></div>
          <div>${esc(WC_COACHES.coaching_stats?.oldest_coach_record || 'No coaching record note available.')}</div>
        </div>
      </div>
    `;

    const input = document.getElementById('coaches-search');
    if (input) {
      input.addEventListener('input', event => {
        coachesQuery = event.target.value;
        renderCoaches();
      });
    }
  }

  function renderRecords() {
    const newRecords = WC_RECORDS.wc2026_new_records || [];
    const allTime = WC_RECORDS.all_time_records || {};
    const winners = WC_RECORDS.world_cup_winners || [];
    const titles = Object.entries(WC_RECORDS.titles_count || {});
    const topScorers = allTime.top_scorers_all_time || [];
    const quirky = [
      ['Fastest goal', `${allTime.fastest_goal?.player || '—'} (${allTime.fastest_goal?.country || '—'}) — ${allTime.fastest_goal?.seconds || '—'} seconds`],
      ['Biggest win', `${allTime.biggest_win?.match || '—'} (${allTime.biggest_win?.year || '—'})`],
      ['Most goals in one match', `${allTime.most_goals_in_one_match?.match || '—'} — ${allTime.most_goals_in_one_match?.goals || '—'} goals`],
      ['Youngest scorer', `${allTime.youngest_scorer?.player || '—'} — ${allTime.youngest_scorer?.age || '—'} (${allTime.youngest_scorer?.year || '—'})`],
      ['Oldest scorer', `${allTime.oldest_scorer?.player || '—'} — ${allTime.oldest_scorer?.age || '—'} (${allTime.oldest_scorer?.year || '—'})`],
      ['Single-tournament scoring record', `${allTime.most_goals_single_tournament?.player || '—'} — ${allTime.most_goals_single_tournament?.goals || '—'} goals`],
    ];

    document.getElementById('tab-records').innerHTML = `
      <div class="record-grid">
        <div class="card">
          <div class="card-title"><h3>2026 new records</h3><span class="badge badge-accent">${esc(WC_RECORDS.last_updated || 'Saved')}</span></div>
          <div class="record-list">
            ${newRecords.map(item => `
              <div class="record-item">
                <strong>${esc(item.record || 'Record')}</strong>
                <div>${esc(item.detail || '—')}</div>
                ${item.match ? `<div class="soft">${esc(item.match)}</div>` : ''}
                ${item.note ? `<div class="soft">${esc(item.note)}</div>` : ''}
                ${item.goals ? `<div class="soft">${esc(item.goals)}</div>` : ''}
              </div>
            `).join('') || '<div class="muted">No 2026 record items available.</div>'}
          </div>
        </div>
        <div class="card">
          <div class="card-title"><h3>All-time milestones</h3></div>
          <div class="key-value">
            <div>Most titles</div><div>${esc(allTime.most_titles?.team || '—')} (${esc(allTime.most_titles?.titles || '—')})</div>
            <div>Most finals</div><div>${esc(allTime.most_finals_appearances?.team || '—')} (${esc(allTime.most_finals_appearances?.finals || '—')})</div>
            <div>Most matches</div><div>${esc(allTime.most_matches_played?.team || '—')} (${esc(allTime.most_matches_played?.matches || '—')})</div>
            <div>Most wins</div><div>${esc(allTime.most_wins?.team || '—')} (${esc(allTime.most_wins?.wins || '—')})</div>
          </div>
        </div>
      </div>

      <div class="section-title"><h2>Top scorers in World Cup history</h2><span class="muted">Including new 2026 marks.</span></div>
      <div class="table-card">
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Rank</th>
                <th>Player</th>
                <th>Country</th>
                <th class="numeric">Goals</th>
                <th class="numeric">Matches</th>
                <th>Active</th>
                <th>Note</th>
              </tr>
            </thead>
            <tbody>
              ${topScorers.map(item => `
                <tr>
                  <td>${esc(item.rank)}</td>
                  <td><strong>${esc(item.player)}</strong></td>
                  <td>${flag(item.country)} ${esc(item.country)}</td>
                  <td class="numeric">${esc(item.goals)}</td>
                  <td class="numeric">${esc(item.matches)}</td>
                  <td>${item.active ? '<span class="badge badge-success">Active</span>' : '<span class="badge">Retired</span>'}</td>
                  <td>${textOrDash(item.note)}</td>
                </tr>
              `).join('') || '<tr><td colspan="7" class="muted">No scorer records available.</td></tr>'}
            </tbody>
          </table>
        </div>
      </div>

      <div class="section-title"><h2>World Cup winners list</h2><span class="muted">Champions from 1930 through the 2026 final placeholder.</span></div>
      <div class="table-card">
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Year</th>
                <th>Winner</th>
                <th>Host</th>
                <th>Final score</th>
              </tr>
            </thead>
            <tbody>
              ${winners.map(item => `
                <tr>
                  <td>${esc(item.year)}</td>
                  <td>${flag(item.winner)} ${esc(item.winner)}</td>
                  <td>${esc(item.host || '—')}</td>
                  <td>${textOrDash(item.final_score || item.final_date)}</td>
                </tr>
              `).join('') || '<tr><td colspan="4" class="muted">No winners list available.</td></tr>'}
            </tbody>
          </table>
        </div>
      </div>

      <div class="record-grid">
        <div class="card">
          <div class="card-title"><h3>Titles by nation</h3></div>
          <div class="bar-list">
            ${titles.map(([team, count]) => `
              <div class="bar-row">
                <div><strong>${flag(team)} ${esc(team)}</strong></div>
                <div class="bar-track"><div class="bar-fill" style="width:${Math.min((Number(count) || 0) * 20, 100)}%"></div></div>
                <div><strong>${esc(count)}</strong></div>
              </div>
            `).join('') || '<div class="muted">No title counts available.</div>'}
          </div>
        </div>
        <div class="card">
          <div class="card-title"><h3>Bizarre and iconic records</h3></div>
          <div class="record-list">
            ${quirky.map(([label, value]) => `
              <div class="record-item">
                <strong>${esc(label)}</strong>
                <div>${esc(value)}</div>
              </div>
            `).join('')}
          </div>
        </div>
      </div>
    `;
  }

  function initialize() {
    renderStandings();
    renderMatches();
    renderPredictions();
    renderPlayers();
    renderCoaches();
    renderRecords();
    updateLiveIndicator();
    doRefresh();
  }

  initialize();
  </script>
</body>
</html>
'''


def build_html(data_js: str, built_at: str) -> str:
    return (
        HTML_TEMPLATE.replace("__DATA_JS__", data_js)
        .replace("__BUILT_AT_HTML__", built_at)
    )


def write_outputs(html: str) -> None:
    encoded = html.encode("utf-8")
    size_kb = len(encoded) / 1024
    for path in OUTPUT_PATHS:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(html, encoding="utf-8", newline="\n")
        print(f"[OK] Dashboard built at: {path} ({size_kb:.1f} KB)")


def main() -> None:
    missing = [name for name in DATA_FILES if not (DATA_DIR / name).exists()]
    if missing:
        raise FileNotFoundError(f"Missing JSON data files: {', '.join(missing)}")

    groups = load_json("groups.json")
    coaches = load_json("coaches.json")
    players = load_json("players.json")
    records = load_json("records.json")
    predictions = load_json("predictions.json")

    built_at = dt.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
    data_js = build_data_js(groups, coaches, players, records, predictions, built_at)
    html = build_html(data_js, built_at)
    write_outputs(html)


if __name__ == "__main__":
    main()
