#!/usr/bin/env python3
"""
update-references.py — Fetch latest OpenAI Codex docs and save raw content
for Claude to use when refreshing the skill's reference files.

Usage:
    python update-references.py [--ref references/mcp.md] [--all]

Fetches upstream docs -> saves to a staging directory: <repo>/.agent-output/client-config-codex/_fetched/
when the skill is in a git checkout, otherwise _fetched/ inside the skill folder.
Claude then reads the staged content and updates references/ files accordingly.

Workflow (for Claude):
    1. Run this script -> content saved to _fetched/
    2. For each fetched file, compare against the current reference file
    3. Update reference files to reflect new/changed/removed info
    4. Remove the staging directory when done
"""
import json
import sys
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime, timezone

SKILL_ROOT = Path(__file__).parent.parent
SOURCES_FILE = SKILL_ROOT / "sources.json"


def staging_dir() -> Path:
    """Stage downloads under the repo-root .agent-output/ (gitignored scratch space) when this
    skill sits in a git checkout; otherwise fall back to _fetched/ inside the skill folder."""
    for parent in SKILL_ROOT.parents:
        if (parent / ".git").exists():
            return parent / ".agent-output" / SKILL_ROOT.name / "_fetched"
    return SKILL_ROOT / "_fetched"


FETCHED_DIR = staging_dir()

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; codex-skill-updater/1.0)",
    "Accept": "text/markdown,text/plain,*/*",
}

def fetch_url(url: str) -> str:
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            content = resp.read()
            # get_content_charset() strips quotes (charset="utf-8") that a manual split would keep.
            charset = resp.headers.get_content_charset() or "utf-8"
            try:
                return content.decode(charset, errors="replace")
            except LookupError:
                raise RuntimeError(f"Unknown charset {charset!r} fetching {url}")
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code} fetching {url}: {e.reason}")
    except urllib.error.URLError as e:
        raise RuntimeError(f"Network error fetching {url}: {e.reason}")
    except OSError as e:  # includes TimeoutError raised while reading the response body
        raise RuntimeError(f"Network error fetching {url}: {e}")

def save_fetched(ref_path: str, contents: list, urls: list) -> Path:
    name = Path(ref_path).name
    out_path = FETCHED_DIR / name
    FETCHED_DIR.mkdir(parents=True, exist_ok=True)
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
        return 1

    with open(SOURCES_FILE) as f:
        sources = json.load(f)

    refs = dict(sources.get("references", {}))
    if sources.get("index") and "--ref" not in sys.argv:
        # A full refresh also stages the upstream docs index so new pages can be spotted.
        refs = {"index/llms-index.md": {
            "urls": [sources["index"]],
            "covers": "upstream docs index; compare against sources.json for pages not yet covered",
        }, **refs}

    args = sys.argv[1:]
    target = None
    if "--ref" in args:
        idx = args.index("--ref")
        if idx + 1 >= len(args):
            print("ERROR: --ref requires a reference path")
            return 2
        target = args[idx + 1]
        del args[idx:idx + 2]
    if any(arg != "--all" for arg in args):
        print("ERROR: usage: python scripts/update-references.py [--ref references/file.md] [--all]")
        return 2
    if target and target not in refs:
        print(f"ERROR: unknown reference: {target}")
        return 2

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

        if all_ok:
            try:
                out_path = save_fetched(ref_path, fetched_contents, fetched_urls)
            except OSError as e:  # full disk, permissions: fail this ref so cleanup discards the run
                print(f"     FAILED: could not write staged file: {e}")
                all_ok = False

        if all_ok:
            total = sum(len(c) for c in fetched_contents)
            print(f"  Saved {total:,} chars -> {out_path}")
            results.append({"ref": ref_path, "fetched": str(out_path), "ok": True})
        else:
            stale_path = FETCHED_DIR / Path(ref_path).name
            if stale_path.exists():
                stale_path.unlink()
            results.append({"ref": ref_path, "ok": False, "error": "one or more sources failed"})

    success = sum(1 for r in results if r["ok"])
    failed = len(results) - success
    if failed:
        # A partial set must not be usable: discard everything this run staged.
        for r in results:
            if r.get("fetched"):
                Path(r["fetched"]).unlink(missing_ok=True)
                r["ok"] = False
        if FETCHED_DIR.exists() and not any(FETCHED_DIR.iterdir()):
            FETCHED_DIR.rmdir()
        success = 0
    print(f"\n{'='*50}")
    print(f"Fetched {success}/{len(results)} reference(s)")
    if failed:
        print(f"  {failed} incomplete — staged files from this run were discarded")
    if success and not failed:
        print(f"\nNext steps for Claude:")
        print(f"  1. Read each file in {FETCHED_DIR}")
        print(f"  2. Read the corresponding file in references/")
        print(f"  3. Update references/ to reflect documentation changes")
        print(f"  4. Remove {FETCHED_DIR} when complete")
        print(f"\nFetched files:")
        for r in results:
            if r.get("fetched"):
                print(f"  {r['fetched']}")
    return 1 if failed else 0

if __name__ == "__main__":
    sys.exit(main())
