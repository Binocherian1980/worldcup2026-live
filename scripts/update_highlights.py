"""
update_highlights.py — Auto-update docs/data/highlights.json from FIFA YouTube playlist.
Runs every 30 minutes via GitHub Actions cron.
The static site JS fetches this same-origin JSON to discover new match highlights
without needing a full site rebuild.
"""

import json
import os
import re
import sys
import unicodedata
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────
YT_PLAYLIST   = 'PLBRLtDhTHh5o'
RSS_URL       = f'https://www.youtube.com/feeds/videos.xml?playlist_id={YT_PLAYLIST}'
OEMBED_URL    = 'https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={vid}&format=json'
OUTPUT_PATH   = Path(__file__).parent.parent / 'docs' / 'data' / 'highlights.json'

# ── Team name normalisation (mirrors JS _normTeam + Python _norm) ─────────────
_ALIASES = {
    "côte d'ivoire": 'ivory',  "cote d'ivoire": 'ivory',  'ivory coast': 'ivory',
    'dr congo': 'drcong',      'congo dr': 'drcong',       'democratic republic of congo': 'drcong',
    'korea republic': 'skorea','south korea': 'skorea',
    'usa': 'unitedst',         'united states': 'unitedst',
    'cape verde': 'capeverd',  'cabo verde': 'capeverd',
    'new zealand': 'newzeal',  'saudi arabia': 'saudiarb',
    'ir iran': 'iran',
    'turkiye': 'turkey',       'türkiye': 'turkey',
    'bosnia and herzegovina': 'bosniah', 'bosnia & herzegovina': 'bosniah',
    'czechia': 'czechia',
}

def _norm(t: str) -> str:
    s = t.lower().strip()
    if s in _ALIASES:
        return _ALIASES[s]
    s = unicodedata.normalize('NFD', s)
    s = re.sub(r'[^a-z]', '', s)
    return s[:8]

def _hkey(t1: str, t2: str) -> str:
    a, b = _norm(t1), _norm(t2)
    return f'{a}/{b}' if a < b else f'{b}/{a}'

# ── Fetch helpers ─────────────────────────────────────────────────────────────
def _get(url: str) -> str:
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 Chrome/120'})
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.read().decode('utf-8', errors='replace')
    except Exception as e:
        print(f'  [WARN] fetch {url[:60]}: {e}', file=sys.stderr)
        return ''

def _oembed_ok(vid: str) -> bool:
    """Return True if YouTube video is publicly available."""
    try:
        req = urllib.request.Request(
            OEMBED_URL.format(vid=vid),
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req, timeout=8):
            return True
    except Exception:
        return False

# ── RSS playlist parser ───────────────────────────────────────────────────────
def fetch_playlist() -> dict:
    """
    Fetch FIFA YouTube highlights playlist RSS and return {key: {yt, title}} dict.
    RSS only returns last 15 entries — the most recently uploaded highlights.
    """
    xml = _get(RSS_URL)
    if not xml:
        return {}

    result = {}
    for entry in re.findall(r'<entry>(.*?)</entry>', xml, re.DOTALL):
        vid_m   = re.search(r'<yt:videoId>([^<]+)</yt:videoId>', entry)
        title_m = re.search(r'<title>([^<]+)</title>', entry)
        pub_m   = re.search(r'<published>([^<]+)</published>', entry)
        if not vid_m or not title_m:
            continue
        vid   = vid_m.group(1).strip()
        title = title_m.group(1).strip()
        pub   = pub_m.group(1).strip() if pub_m else ''

        # "Highlights | Team1 N-N Team2 | FIFA World Cup 2026™"
        m = re.search(
            r'Highlights[^|:]*[|:]\s*(.+?)\s+\d+[-:]\d+\s+(.+?)\s*\|', title, re.I
        )
        if not m:
            # "Alt Cast Highlights: Team1 v Team2 | FIFA World Cup 2026™"
            m = re.search(
                r'Alt Cast Highlights:\s*(.+?)\s+v(?:s\.?)?\s+(.+?)\s*\|', title, re.I
            )
        if m:
            t1  = m.group(1).strip()
            t2  = m.group(2).strip()
            key = _hkey(t1, t2)
            result[key] = {'yt': vid, 'title': title, 'published': pub}

    print(f'  RSS: found {len(result)} highlights')
    return result

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    # Load existing data (to merge with, not overwrite)
    existing: dict = {}
    if OUTPUT_PATH.exists():
        try:
            existing = json.loads(OUTPUT_PATH.read_text(encoding='utf-8'))
        except Exception:
            pass

    existing_highlights: dict = existing.get('highlights', {})
    existing_unavailable: list = existing.get('unavailable', [])

    # Fetch latest from RSS
    fresh = fetch_playlist()

    # Merge: RSS wins (official source) — but keep previous entries not in RSS
    merged = dict(existing_highlights)
    new_count = 0
    for key, data in fresh.items():
        if key not in merged or merged[key].get('yt') != data['yt']:
            merged[key] = data
            new_count += 1

    print(f'  Merged: {len(merged)} total ({new_count} new/updated)')

    # Check availability of every video (fast: oEmbed 404 = unavailable)
    all_ids = {v['yt'] for v in merged.values() if 'yt' in v}
    unavailable = set(existing_unavailable)  # carry forward known-unavailable

    # Only check videos we haven't confirmed unavailable yet
    to_check = all_ids - unavailable
    print(f'  Checking {len(to_check)} video IDs...')
    newly_unavailable = []
    for vid in to_check:
        if not _oembed_ok(vid):
            unavailable.add(vid)
            newly_unavailable.append(vid)

    if newly_unavailable:
        print(f'  Newly unavailable: {newly_unavailable}')
    else:
        print(f'  All videos available')

    # Build output
    output = {
        'playlist': YT_PLAYLIST,
        'updated_at': datetime.now(timezone.utc).isoformat(),
        'highlights': merged,
        'unavailable': sorted(unavailable),
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f'  Written: {OUTPUT_PATH}  ({len(merged)} highlights, {len(unavailable)} unavailable)')


if __name__ == '__main__':
    main()
