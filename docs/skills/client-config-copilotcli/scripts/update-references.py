#!/usr/bin/env python3
"""
update-references.py — Fetch latest GitHub Copilot CLI docs and save raw content
for Claude to use when refreshing the skill's reference files.

Usage:
    python update-references.py [--ref references/mcp.md] [--all]

Fetches upstream docs -> saves to _fetched/ staging directory.
Claude then reads _fetched/ content and updates references/ files accordingly.

Workflow (for Claude):
    1. Run this script -> content saved to _fetched/
    2. For each fetched file, compare against the current reference file
    3. Update reference files to reflect new/changed/removed info
    4. Remove _fetched/ when done
"""
import json
import sys
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime, timezone

SKILL_ROOT = Path(__file__).parent.parent
SOURCES_FILE = SKILL_ROOT / "sources.json"
FETCHED_DIR = SKILL_ROOT / "_fetched"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; copilot-skill-updater/1.0)",
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

def save_fetched(ref_path: str, contents: list, urls: list) -> Path:
    name = Path(ref_path).name
    out_path = FETCHED_DIR / name
    FETCHED_DIR.mkdir(exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(f"<!-- FETCHED: {datetime.now(timezone.utc).isoformat()} -->\n\n")
        for url, content in zip(urls, contents):
            f.write(f"<!-- SOURCE: {url} -->\n\n")
            f.write(content)
            f.write("\n\n---\n\n")
    return out_path

def main():
    if not SOURCES_FILE.exists():
        print(f"ERROR: sources.json not found at {SOURCES_FILE}")
        sys.exit(1)

    with open(SOURCES_FILE) as f:
        sources = json.load(f)

    refs = sources.get("references", {})

    target = None
    if "--ref" in sys.argv:
        idx = sys.argv.index("--ref")
        if idx + 1 < len(sys.argv):
            target = sys.argv[idx + 1]

    results = []
    for ref_path, meta in refs.items():
        if target and ref_path != target:
            continue

        # Support both single url and urls array
        urls = meta.get("urls", [meta["url"]] if "url" in meta else [])
        covers = meta.get("covers", "")
        print(f"\nFetching: {ref_path}  ({len(urls)} source(s))")
        print(f"  Covers: {covers[:80]}...")

        fetched_contents = []
        fetched_urls = []
        all_ok = True
        for url in urls:
            print(f"  -> {url}")
            try:
                content = fetch_url(url)
                fetched_contents.append(content)
                fetched_urls.append(url)
                print(f"     {len(content):,} chars")
            except RuntimeError as e:
                print(f"     FAILED: {e}")
                all_ok = False

        if fetched_contents:
            out_path = save_fetched(ref_path, fetched_contents, fetched_urls)
            total = sum(len(c) for c in fetched_contents)
            print(f"  Saved {total:,} chars -> {out_path.relative_to(SKILL_ROOT)}")
            results.append({"ref": ref_path, "fetched": str(out_path), "ok": all_ok})
        else:
            results.append({"ref": ref_path, "ok": False, "error": "all sources failed"})

    success = sum(1 for r in results if r["ok"])
    print(f"\n{'='*50}")
    print(f"Fetched {success}/{len(results)} reference(s)")
    if success:
        print(f"\nNext steps for Claude:")
        print(f"  1. Read each file in _fetched/")
        print(f"  2. Read the corresponding file in references/")
        print(f"  3. Update references/ to reflect documentation changes")
        print(f"  4. Remove _fetched/ when complete")
        print(f"\nFetched files:")
        for r in results:
            if r.get("fetched"):
                print(f"  {r['fetched']}")

if __name__ == "__main__":
    main()
