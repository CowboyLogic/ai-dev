#!/usr/bin/env python3
"""Fetch latest upstream docs for client-config-geminicli skill self-update.

Usage:
    python scripts/update-references.py

Fetches all URLs listed in sources.json and saves raw content to _fetched/
staging directory. Claude then reviews diffs and rewrites reference files.
"""

import json
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent
SOURCES_FILE = SKILL_DIR / "sources.json"
FETCHED_DIR = SKILL_DIR / "_fetched"


def fetch_url(url: str) -> str:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "gemini-cli-skill-updater/1.0"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = resp.read()
        encoding = resp.headers.get_content_charset() or "utf-8"
        return raw.decode(encoding, errors="replace")


def sanitize_filename(url: str) -> str:
    name = url.replace("https://", "").replace("http://", "")
    for ch in "/:.?=&":
        name = name.replace(ch, "_")
    return name.strip("_") + ".txt"


def main():
    if not SOURCES_FILE.exists():
        print(f"ERROR: sources.json not found at {SOURCES_FILE}")
        sys.exit(1)

    with open(SOURCES_FILE, encoding="utf-8") as f:
        sources = json.load(f)

    FETCHED_DIR.mkdir(exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    manifest = {"fetched_at": timestamp, "files": {}}

    # Collect all unique URLs
    urls_to_fetch: dict[str, list[str]] = {}

    # Index URL
    if index_url := sources.get("index"):
        urls_to_fetch.setdefault(index_url, []).append("index")

    # Reference file URLs
    for ref_file, ref_info in sources.get("references", {}).items():
        for url in ref_info.get("urls", []):
            urls_to_fetch.setdefault(url, []).append(ref_file)

    print(f"Fetching {len(urls_to_fetch)} URL(s) to {FETCHED_DIR}/")
    print()

    errors = []
    for url, used_by in sorted(urls_to_fetch.items()):
        fname = sanitize_filename(url)
        out_path = FETCHED_DIR / fname
        print(f"  Fetching: {url}")
        print(f"    Used by: {', '.join(used_by)}")
        try:
            content = fetch_url(url)
            out_path.write_text(content, encoding="utf-8")
            size = len(content)
            print(f"    Saved {size:,} chars -> {out_path.name}")
            manifest["files"][fname] = {"url": url, "used_by": used_by, "size": size}
        except urllib.error.HTTPError as e:
            msg = f"HTTP {e.code}: {url}"
            print(f"    ERROR: {msg}")
            errors.append(msg)
        except Exception as e:
            msg = f"{e}: {url}"
            print(f"    ERROR: {msg}")
            errors.append(msg)
        print()

    manifest_path = FETCHED_DIR / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Manifest written: {manifest_path}")

    if errors:
        print(f"\n{len(errors)} error(s):")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    else:
        print(f"\nAll {len(urls_to_fetch)} URLs fetched successfully.")
        print("\nNext step: Review diffs between _fetched/ content and references/,")
        print("then rewrite any reference files that contain stale information.")


if __name__ == "__main__":
    main()
