# FIFA World Cup 2026 Dashboard 🏆

> Live-updated group standings, match results, player profiles, coach info, predictions, and historical records — in a single HTML file that works on any machine.

## Quick Start

```
1. Open  dashboard/worldcup-dashboard.html  in any browser   ← no install needed
2. After a matchday, run:  python scripts/update_data.py --build
3. Refresh the browser  ← dashboard is updated
```

---

## What's Included

| Tab | Contents |
|---|---|
| 📊 Standings | All 12 groups, live points tables, qualification status |
| ⚽ Matches | Today's schedule with scores, scorers, venues |
| 🔮 Predictions | Tournament winner odds, group winners, Round of 32 |
| 👤 Players | Key players for all top teams (age, club, position) |
| 🧢 Coaches | All 48 head coaches with nationality and notes |
| 🏆 Records | WC 2026 new records + all-time history |

---

## File Structure

```
WorldCup2026/
├── data/
│   ├── groups.json        ← standings, group tables, today's matches
│   ├── coaches.json       ← all 48 coaches
│   ├── players.json       ← squad key players
│   ├── records.json       ← all-time + 2026 records
│   └── predictions.json   ← win probabilities, group predictions
├── dashboard/
│   └── worldcup-dashboard.html   ← THE FILE TO SHARE / OPEN
├── scripts/
│   ├── update_data.py     ← fetches live data from ESPN API
│   └── build_dashboard.py ← regenerates the HTML from JSON files
└── README.md
```

---

## Keeping Data Fresh

### After every matchday (recommended):
```bash
# 1. Fetch live standings + scores from ESPN + rebuild HTML
python scripts/update_data.py --build

# 2. Or step by step:
python scripts/update_data.py       # update JSON data files
python scripts/build_dashboard.py   # regenerate HTML from JSON
```

### Options:
```
python scripts/update_data.py --standings   # standings only
python scripts/update_data.py --matches     # match results only
python scripts/update_data.py --build       # update all + rebuild HTML
```

### Automate with Windows Task Scheduler:
1. Open Task Scheduler → Create Basic Task
2. Trigger: Daily or "On log on"
3. Action: `python C:\Users\<you>\WorldCup2026\scripts\update_data.py --build`
4. Done — dashboard auto-refreshes before you open it

---

## Sharing With Your Team

### Option A: Share the HTML file directly
- Run `python scripts/update_data.py --build`
- Send `dashboard/worldcup-dashboard.html` via Teams, email, or SharePoint
- Recipient opens it in any browser — **no install, no Python, no CLI needed**
- Works on Windows, Mac, Linux, even mobile browsers

### Option B: GitHub Pages (always-live link)
```bash
cd C:\Users\<you>\WorldCup2026
git init
git add .
git commit -m "FIFA WC 2026 dashboard"
git branch -M main
git remote add origin https://github.com/<you>/worldcup2026.git
git push -u origin main
# Then enable GitHub Pages → Settings → Pages → branch: main / folder: /dashboard
# Share link: https://<you>.github.io/worldcup2026/worldcup-dashboard.html
```

### Option C: SharePoint / OneDrive
- Upload `WorldCup2026/` folder to SharePoint
- Share the URL to `dashboard/worldcup-dashboard.html`
- Team members can open it directly from their browser

### Option D: Azure Static Web Apps (advanced, always live)
```bash
# Install Azure Static Web Apps CLI
npm install -g @azure/static-web-apps-cli
# Deploy
swa deploy dashboard/ --deployment-token <your-token>
```

---

## Using with Copilot CLI (ask me live questions)

When using GitHub Copilot CLI in a new session, I can reload the knowledge base:
```
"Load the World Cup 2026 data from C:\Users\<you>\WorldCup2026\data\ and answer questions"
```

I'll read the JSON files and combine with live web search for real-time answers.

---

## Requirements (for update script only)

- Python 3.8+ (standard library only — no pip installs needed)
- Internet connection (for `update_data.py`)

The **dashboard HTML requires nothing** — just a browser.

---

## Tournament Info

| | |
|---|---|
| Dates | June 11 – July 19, 2026 |
| Hosts | 🇺🇸 USA · 🇨🇦 Canada · 🇲🇽 Mexico |
| Teams | 48 teams in 12 groups |
| Format | Top 2 per group + 8 best 3rd-place → Round of 32 |
| Prize pool | $727 million |
| Final | July 19, 2026 |

---

*Dashboard built with GitHub Copilot CLI · Data sources: ESPN public API, FIFA.com, web search*
