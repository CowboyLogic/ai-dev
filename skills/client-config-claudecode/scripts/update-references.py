#!/usr/bin/env python3
"""
update-references.py — Fetch latest Claude Code docs and save raw content
for Claude to use when refreshing the skill's reference files.

Usage:
    python update-references.py [--ref references/permissions.md] [--all]

This script fetches the upstream docs and saves them to a _fetched/ staging
directory. Claude then reads the fetched content and rewrites the reference
files to reflect any changes in the official documentation.

Workflow (for Claude):
    1. Run this script to fetch raw docs → saved to _fetched/
    2. For each fetched file, compare against the current reference file
    3. Update reference files to reflect new fields, removed fields, or changed behavior
    4. Run scripts/validate-settings.py to confirm no breakage
    5. Remove _fetched/ directory when done
"""
import json
import sys
import urllib.request
import urllib.error
from pathlib import Path

SKILL_ROOT = Path(__file__).parent.parent
SOURCES_FILE = SKILL_ROOT / "assets" / "sources.json"
FETCHED_DIR = SKILL_ROOT / "_fetched"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; claude-skill-updater/1.0)",
    "Accept": "text/html,text/markdown,text/plain,*/*",
}

def fetch_url(url: str) -> str:
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            content = resp.read()
            charset = "utf-8"
            ct = resp.headers.get("Content-Type", "")
            if "charset=" in ct:
                charset = ct.split("charset=")[-1].split(";")[0].strip()
            return content.decode(charset, errors="replace")
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code} fetching {url}: {e.reason}")
    except urllib.error.URLError as e:
        raise RuntimeError(f"Network error fetching {url}: {e.reason}")

def save_fetched(ref_path: str, content: str, url: str) -> Path:
    # Convert "references/hooks.md" → "_fetched/hooks.md"
    name = Path(ref_path).name
    out_path = FETCHED_DIR / name
    FETCHED_DIR.mkdir(exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(f"<!-- SOURCE: {url} -->\n")
        f.write(f"<!-- FETCHED: {__import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat()} -->\n\n")
        f.write(content)
    return out_path

def main():
    if not SOURCES_FILE.exists():
        print(f"ERROR: assets/sources.json not found at {SOURCES_FILE}")
        sys.exit(1)

    with open(SOURCES_FILE) as f:
        sources = json.load(f)

    refs = sources.get("references", {})

    # Filter to specific ref if requested
    target = None
    if "--ref" in sys.argv:
        idx = sys.argv.index("--ref")
        if idx + 1 < len(sys.argv):
            target = sys.argv[idx + 1]

    fetch_all = "--all" in sys.argv or target is None

    results = []
    for ref_path, meta in refs.items():
        if target and ref_path != target:
            continue

        url = meta["url"]
        covers = meta.get("covers", "")
        print(f"\nFetching: {ref_path}")
        print(f"  URL: {url}")
        print(f"  Covers: {covers[:80]}...")

        try:
            content = fetch_url(url)
            out_path = save_fetched(ref_path, content, url)
            size = len(content)
            print(f"  Saved {size:,} chars -> {out_path.relative_to(SKILL_ROOT)}")
            results.append({"ref": ref_path, "fetched": str(out_path), "url": url, "ok": True})
        except RuntimeError as e:
            print(f"  FAILED: {e}")
            results.append({"ref": ref_path, "url": url, "ok": False, "error": str(e)})

    success = sum(1 for r in results if r["ok"])
    failed = len(results) - success

    print(f"\n{'='*50}")
    print(f"Fetched {success}/{len(results)} sources")
    if failed:
        print(f"  {failed} failed — check network/URL changes")
    if success:
        print(f"\nNext steps for Claude:")
        print(f"  1. Read each file in _fetched/")
        print(f"  2. Read the corresponding file in references/")
        print(f"  3. Update references/ to reflect documentation changes")
        print(f"  4. Run: python scripts/validate-settings.py")
        print(f"  5. Remove _fetched/ when complete")
        print(f"\nFetched files:")
        for r in results:
            if r["ok"]:
                print(f"  {r['fetched']}")

if __name__ == "__main__":
    main()
