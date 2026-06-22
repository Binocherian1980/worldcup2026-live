"""
FIFA World Cup 2026 - Live Data Updater
=======================================
Fetches live standings, scores, and match data from the ESPN public API
(no API key required) and updates the local JSON data files.

Usage:
    python update_data.py                  # Update all data
    python update_data.py --standings      # Update standings only
    python update_data.py --matches        # Update today's matches only
    python update_data.py --build          # Also rebuild the HTML dashboard

Run this script after every matchday to keep your dashboard fresh.
Schedule it with Windows Task Scheduler for automatic updates.
"""

import json
import os
import sys
import datetime
import argparse
import urllib.request
import urllib.error

# ── Paths ──────────────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR   = os.path.join(SCRIPT_DIR, "..", "data")
DASH_DIR   = os.path.join(SCRIPT_DIR, "..", "dashboard")

# ── ESPN Public API (no auth required) ────────────────────────────────────
ESPN_SCOREBOARD = "https://site.api.espn.com/apis/site/v2/sports/soccer/fifa.world/scoreboard"
ESPN_STANDINGS  = "https://site.api.espn.com/apis/v2/sports/soccer/fifa.world/standings"
ESPN_SCHEDULE   = "https://site.api.espn.com/apis/site/v2/sports/soccer/fifa.world/scoreboard"

GROUP_FLAG_MAP = {
    "Mexico": "🇲🇽", "South Korea": "🇰🇷", "Korea Republic": "🇰🇷",
    "Czechia": "🇨🇿", "Czech Republic": "🇨🇿", "South Africa": "🇿🇦",
    "Canada": "🇨🇦", "Switzerland": "🇨🇭", "Bosnia & Herzegovina": "🇧🇦",
    "Bosnia and Herzegovina": "🇧🇦", "Qatar": "🇶🇦",
    "Brazil": "🇧🇷", "Morocco": "🇲🇦", "Scotland": "🏴󠁧󠁢󠁳󠁣󠁴󠁿", "Haiti": "🇭🇹",
    "United States": "🇺🇸", "USA": "🇺🇸", "Australia": "🇦🇺",
    "Paraguay": "🇵🇾", "Turkey": "🇹🇷", "Türkiye": "🇹🇷",
    "Germany": "🇩🇪", "Ivory Coast": "🇨🇮", "Côte d'Ivoire": "🇨🇮",
    "Ecuador": "🇪🇨", "Curacao": "🇨🇼", "Curaçao": "🇨🇼",
    "Netherlands": "🇳🇱", "Japan": "🇯🇵", "Sweden": "🇸🇪", "Tunisia": "🇹🇳",
    "Belgium": "🇧🇪", "Egypt": "🇪🇬", "Iran": "🇮🇷", "New Zealand": "🇳🇿",
    "Spain": "🇪🇸", "Uruguay": "🇺🇾", "Cape Verde": "🇨🇻", "Saudi Arabia": "🇸🇦",
    "France": "🇫🇷", "Norway": "🇳🇴", "Senegal": "🇸🇳", "Iraq": "🇮🇶",
    "Argentina": "🇦🇷", "Austria": "🇦🇹", "Jordan": "🇯🇴", "Algeria": "🇩🇿",
    "Colombia": "🇨🇴", "Portugal": "🇵🇹", "DR Congo": "🇨🇩", "Congo DR": "🇨🇩",
    "Uzbekistan": "🇺🇿", "England": "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "Ghana": "🇬🇭",
    "Panama": "🇵🇦", "Croatia": "🇭🇷",
}


def fetch_json(url: str) -> dict | None:
    """Fetch JSON from a URL with a browser-like User-Agent."""
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode())
    except Exception as exc:
        print(f"  ⚠️  Failed to fetch {url}: {exc}")
        return None


def load_json(filename: str) -> dict:
    path = os.path.join(DATA_DIR, filename)
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_json(filename: str, data: dict) -> None:
    path = os.path.join(DATA_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"  ✅ Saved {filename}")


def flag(team: str) -> str:
    return GROUP_FLAG_MAP.get(team, "🏳️")


# ── Update: Scoreboard / Today's Matches ──────────────────────────────────
def update_matches() -> None:
    print("\n📡 Fetching live scoreboard from ESPN...")
    data = fetch_json(ESPN_SCOREBOARD)
    if not data:
        print("  Falling back to cached data.")
        return

    groups_data = load_json("groups.json")
    today = datetime.date.today().isoformat()
    today_matches = []

    events = data.get("events", [])
    print(f"  Found {len(events)} events")

    for event in events:
        competitions = event.get("competitions", [{}])
        comp = competitions[0] if competitions else {}
        competitors = comp.get("competitors", [])

        home = next((c for c in competitors if c.get("homeAway") == "home"), {})
        away = next((c for c in competitors if c.get("homeAway") == "away"), {})

        home_team = home.get("team", {}).get("displayName", "?")
        away_team = away.get("team", {}).get("displayName", "?")
        home_score = home.get("score", "")
        away_score = away.get("score", "")

        status_type = event.get("status", {}).get("type", {})
        state      = status_type.get("state", "pre")   # pre / in / post
        detail     = status_type.get("description", "")

        match_entry = {
            "home": home_team,
            "away": away_team,
            "home_flag": flag(home_team),
            "away_flag": flag(away_team),
            "date": event.get("date", today)[:10],
            "venue": comp.get("venue", {}).get("fullName", ""),
            "status": "FINAL" if state == "post" else ("LIVE" if state == "in" else "UPCOMING"),
            "detail": detail,
        }
        if state != "pre":
            match_entry["score"] = f"{home_score}-{away_score}"

        today_matches.append(match_entry)

    # Update today's matches in groups.json
    groups_data["today_matches"] = today_matches
    groups_data["last_updated"] = datetime.datetime.now().isoformat()
    save_json("groups.json", groups_data)
    print(f"  Updated {len(today_matches)} match(es)")


# ── Update: Standings ──────────────────────────────────────────────────────
def update_standings() -> None:
    print("\n📊 Fetching standings from ESPN...")
    data = fetch_json(ESPN_STANDINGS)
    if not data:
        print("  Falling back to cached standings.")
        return

    groups_data = load_json("groups.json")
    existing_groups = groups_data.get("groups", {})

    standings_data = data.get("standings", [])
    print(f"  Found {len(standings_data)} group(s) in API response")

    for group in standings_data:
        group_name = group.get("name", "")  # e.g. "Group A"
        group_key  = group_name.replace("Group ", "").strip()
        if not group_key or group_key not in existing_groups:
            continue

        entries = group.get("standings", {}).get("entries", [])
        new_standings = []
        for entry in entries:
            team_name = entry.get("team", {}).get("displayName", "?")
            stats = {s["name"]: s.get("value", 0) for s in entry.get("stats", [])}
            new_standings.append({
                "team": team_name,
                "flag": flag(team_name),
                "played": int(stats.get("gamesPlayed", 0)),
                "won":    int(stats.get("wins", 0)),
                "drawn":  int(stats.get("ties", 0)),
                "lost":   int(stats.get("losses", 0)),
                "gf":     int(stats.get("pointsFor", 0)),
                "ga":     int(stats.get("pointsAgainst", 0)),
                "gd":     int(stats.get("pointDifferential", 0)),
                "points": int(stats.get("points", 0)),
            })

        if new_standings:
            existing_groups[group_key]["standings"] = new_standings
            print(f"  Updated Group {group_key}")

    groups_data["groups"] = existing_groups
    groups_data["last_updated"] = datetime.datetime.now().isoformat()
    save_json("groups.json", groups_data)


# ── Update: Predictions (recalculate from current standings) ───────────────
def update_predictions() -> None:
    print("\n🔮 Recalculating predictions from current standings...")
    groups_data  = load_json("groups.json")
    predictions  = load_json("predictions.json")

    virtually_qualified = []
    strong_position     = []

    for gkey, gval in groups_data.get("groups", {}).items():
        standings = gval.get("standings", [])
        if not standings:
            continue
        leader = standings[0]
        if leader.get("points", 0) >= 6:
            virtually_qualified.append({
                "team": leader["team"],
                "group": gkey,
                "points": leader["points"],
                "certainty": "99%"
            })
        elif leader.get("points", 0) >= 4:
            strong_position.append({
                "team": leader["team"],
                "group": gkey,
                "points": leader["points"],
                "certainty": "85%"
            })

    predictions["group_qualification_outlook"]["virtually_qualified"] = virtually_qualified
    predictions["group_qualification_outlook"]["strong_position"]     = strong_position
    predictions["last_updated"] = datetime.datetime.now().isoformat()
    save_json("predictions.json", predictions)


# ── Main ───────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Update FIFA WC 2026 data")
    parser.add_argument("--standings", action="store_true", help="Update standings only")
    parser.add_argument("--matches",   action="store_true", help="Update match results only")
    parser.add_argument("--build",     action="store_true", help="Also rebuild HTML dashboard")
    args = parser.parse_args()

    print("=" * 56)
    print("  FIFA World Cup 2026 — Data Updater")
    print(f"  {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 56)

    if args.standings:
        update_standings()
    elif args.matches:
        update_matches()
    else:
        update_standings()
        update_matches()
        update_predictions()

    if args.build:
        import subprocess
        build_script = os.path.join(SCRIPT_DIR, "build_dashboard.py")
        subprocess.run([sys.executable, build_script], check=True)

    print("\n✅ Done! Run build_dashboard.py to regenerate the HTML.")


if __name__ == "__main__":
    main()
