#!/usr/bin/env python3
"""Find installed skills in a library kept outside every harness's discovery path.

The library is one directory holding any number of skills, at any depth: a skill is
a directory that contains SKILL.md. Clones of skill repositories can sit in it as they
are. This script ranks the library against a query and prints the directory of each
match, so an agent loads the one skill it needs instead of carrying every description.

Standard-library Python only, so it runs wherever Python 3.9+ does.
"""

from __future__ import annotations

import argparse
from collections import Counter
import json
import math
import os
from pathlib import Path
import re
import sys
import tempfile

LIBRARY_ENV = "SKILL_ROUTER_LIBRARY"
DEFAULT_LIBRARY = "~/.skill-library"
INDEX_NAME = ".skill-router-index.json"
INDEX_VERSION = 1

# Directories that never hold skills and can be large.
PRUNED_DIRS = {".git", ".hg", ".svn", "node_modules", "__pycache__", ".venv", "venv"}

# Text a harness substitutes when it loads a skill itself. Read as a plain file, the
# text stays literal, so a skill that depends on it needs the agent to fill it in.
HARNESS_VARIABLE = re.compile(r"\$ARGUMENTS\b|\$\{CLAUDE_[A-Z_]+\}")

DESCRIPTION_LIMIT = 1024
TOPICS_SENTENCE = re.compile(r"\s*Library topics include [^.]*\.\s*$")
SNIPPET_CHARS = 300

# BM25 parameters, and how many times a name counts relative to description text.
BM25_K1 = 1.5
BM25_B = 0.75
NAME_WEIGHT = 3
# Results scoring below this share of the best result are dropped as passing mentions.
RELATIVE_FLOOR = 0.35

STOPWORDS = frozenset(
    """a an and any are as at be before by can do does for from how i if in into is it its
    me my need of on or that the their them then this to up use used uses using want
    what when where which who why will with you your""".split()
)
# Words too common in skill names to say what a library covers.
GENERIC_NAME_WORDS = frozenset("skill skills helper helpers tool tools util utils".split())

FRONTMATTER_KEY = re.compile(r"^([A-Za-z_][\w-]*):(.*)$")
BLOCK_SCALAR = re.compile(r"^[|>][+-]?\d*\s*(#.*)?$")
DOUBLE_QUOTED = re.compile(r'"((?:[^"\\]|\\.)*)"')
SINGLE_QUOTED = re.compile(r"'((?:[^']|'')*)'")
DOUBLE_QUOTE_ESCAPE = re.compile(r"\\(x[0-9a-fA-F]{2}|u[0-9a-fA-F]{4}|U[0-9a-fA-F]{8}|.)")
# Values are kept on one line, so escapes for whitespace become a space and escapes for
# control characters are dropped. Any other escaped character stands for itself.
WHITESPACE_ESCAPES = frozenset("nrtvfN_LP")
CONTROL_ESCAPES = frozenset("0abe")


class RouterError(Exception):
    """A problem to report to the caller, without a traceback."""


def warn(message: str) -> None:
    """Report a problem that does not stop the command. Stdout stays clean for results."""
    print(f"skill-router: {message}", file=sys.stderr)


def read_frontmatter(text: str) -> dict[str, str]:
    """Return the top-level scalar fields of a SKILL.md frontmatter block.

    This reads the subset of YAML that frontmatter uses: plain, quoted, folded, and
    literal scalars. Whitespace in a value is collapsed, which is all a search needs.
    """
    lines = text.lstrip("﻿").splitlines()
    if not lines or lines[0].rstrip() != "---":
        return {}
    block: list[str] = []
    for line in lines[1:]:
        if line.rstrip() in ("---", "..."):
            break
        block.append(line)
    else:
        return {}

    fields: dict[str, str] = {}
    key: str | None = None
    parts: list[str] = []
    is_block = False

    def flush() -> None:
        if key is None:
            return
        value = " ".join(" ".join(parts).split())
        fields[key] = value if is_block else _flow_scalar(value)

    for line in block:
        match = FRONTMATTER_KEY.match(line)
        if match:
            flush()
            key = match.group(1)
            value = match.group(2).strip()
            is_block = bool(BLOCK_SCALAR.match(value))
            parts = [] if is_block or not value else [value]
        elif key is not None and (line[:1] in (" ", "\t") or not line.strip()):
            parts.append(line.strip())
    flush()
    return fields


def _flow_scalar(value: str) -> str:
    """Decode a plain or quoted scalar, dropping a trailing comment."""
    if value.startswith('"'):
        match = DOUBLE_QUOTED.match(value)
        if match:
            # Anything after the closing quote is a comment.
            return " ".join(DOUBLE_QUOTE_ESCAPE.sub(_decode_escape, match.group(1)).split())
    elif value.startswith("'"):
        match = SINGLE_QUOTED.match(value)
        if match:
            return match.group(1).replace("''", "'")
    if value.startswith("#"):
        return ""
    # In a plain scalar, " #" starts a comment.
    return re.split(r"\s#", value, maxsplit=1)[0].rstrip()


def _decode_escape(match: re.Match) -> str:
    code = match.group(1)
    if len(code) > 1:
        point = int(code[1:], 16)
        # Surrogates and out-of-range values are not characters.
        return chr(point) if point <= 0x10FFFF and not 0xD800 <= point <= 0xDFFF else ""
    if code in WHITESPACE_ESCAPES:
        return " "
    return "" if code in CONTROL_ESCAPES else code


def find_skill_dirs(root: Path) -> list[Path]:
    """Return every directory under root that holds a SKILL.md, in a stable order."""
    found: list[Path] = []
    seen: set[str] = set()

    def unreadable(error: OSError) -> None:
        warn(f"cannot read {error.filename}: {error.strerror or error}")

    for current, dirnames, filenames in os.walk(root, followlinks=True, onerror=unreadable):
        real = os.path.realpath(current)
        if real in seen:
            # A symlink loop, or two links to one place.
            dirnames[:] = []
            continue
        seen.add(real)
        if "SKILL.md" in filenames:
            found.append(Path(current))
            # A skill's own subdirectories are its files, not more skills.
            dirnames[:] = []
            continue
        dirnames[:] = sorted(d for d in dirnames if d not in PRUNED_DIRS)
    return found


def build_entry(root: Path, skill_dir: Path, stat: os.stat_result) -> dict:
    text = (skill_dir / "SKILL.md").read_text(encoding="utf-8", errors="replace")
    fields = read_frontmatter(text)
    return {
        "name": fields.get("name") or skill_dir.resolve().name,
        "description": fields.get("description", ""),
        "dir": skill_dir.relative_to(root).as_posix(),
        "harness_variables": sorted(set(HARNESS_VARIABLE.findall(text))),
        "mtime_ns": stat.st_mtime_ns,
        "size": stat.st_size,
    }


def load_index(index_path: Path) -> list[dict]:
    try:
        data = json.loads(index_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    if not isinstance(data, dict) or data.get("version") != INDEX_VERSION:
        return []
    skills = data.get("skills")
    if not isinstance(skills, list):
        return []
    # The cache is disposable: a record that is not well formed is read again from source.
    return [entry for entry in skills if valid_entry(entry)]


def valid_entry(entry: object) -> bool:
    def is_int(value: object) -> bool:
        return isinstance(value, int) and not isinstance(value, bool)

    return (
        isinstance(entry, dict)
        and isinstance(entry.get("name"), str)
        and bool(entry["name"])
        and isinstance(entry.get("description"), str)
        and isinstance(entry.get("dir"), str)
        and isinstance(entry.get("harness_variables"), list)
        and all(isinstance(variable, str) for variable in entry["harness_variables"])
        and is_int(entry.get("mtime_ns"))
        and is_int(entry.get("size"))
    )


def refresh_index(root: Path, rebuild: bool = False) -> list[dict]:
    """Return the library's skills, re-reading only SKILL.md files that changed.

    The index file is a cache keyed on each SKILL.md's size and modification time, so
    it cannot go stale: every call walks the library and repairs what differs.
    """
    index_path = root / INDEX_NAME
    previous = [] if rebuild else load_index(index_path)
    cached = {entry["dir"]: entry for entry in previous}
    skills: list[dict] = []
    for skill_dir in find_skill_dirs(root):
        relative = skill_dir.relative_to(root).as_posix()
        try:
            stat = (skill_dir / "SKILL.md").stat()
            entry = cached.get(relative)
            if entry is None or entry["mtime_ns"] != stat.st_mtime_ns or entry["size"] != stat.st_size:
                entry = build_entry(root, skill_dir, stat)
        except OSError as error:
            # One unreadable or vanished skill must not hide the rest of the library.
            warn(f"skipped {relative}/SKILL.md: {error.strerror or error}")
            continue
        skills.append(entry)
    skills.sort(key=lambda entry: (entry["name"], entry["dir"]))
    if rebuild or skills != previous:
        write_index(index_path, skills)
    return skills


def write_index(index_path: Path, skills: list[dict]) -> None:
    payload = json.dumps({"version": INDEX_VERSION, "skills": skills}, indent=1)
    # A read-only library still searches; it just re-reads every file each time.
    try:
        # A new, uniquely named file: a fixed name could be a planted symlink, and two
        # commands running at once would write through each other.
        descriptor, temporary = tempfile.mkstemp(
            dir=index_path.parent, prefix=index_path.name + ".", suffix=".tmp"
        )
    except OSError as error:
        warn(f"could not write {index_path}: {error}")
        return
    try:
        try:
            handle = os.fdopen(descriptor, "w", encoding="utf-8")
        except OSError:
            # Windows cannot delete a file that still has an open descriptor.
            try:
                os.close(descriptor)
            except OSError:
                pass
            raise
        with handle:
            handle.write(payload + "\n")
        os.replace(temporary, index_path)
    except OSError as error:
        warn(f"could not write {index_path}: {error}")
        try:
            os.unlink(temporary)
        except OSError:
            pass


def tokenize(text: str) -> list[str]:
    tokens = []
    for token in re.findall(r"[a-z0-9]+", text.lower()):
        if len(token) < 2 or token in STOPWORDS:
            continue
        if len(token) > 3 and token.endswith("s") and not token.endswith("ss"):
            token = token[:-1]
        tokens.append(token)
    return tokens


def search(skills: list[dict], query: str, limit: int) -> list[tuple[float, dict]]:
    """Rank skills against the query with BM25, names weighted above descriptions.

    A skill whose name is the query comes first, with an infinite score, ahead of
    anything ranked by relevance.
    """
    wanted = {query.strip().lower(), "-".join(query.lower().split())}
    exact = [skill for skill in skills if skill["name"].lower() in wanted]
    terms = set(tokenize(query))
    if not terms and not exact:
        raise RouterError("the query has no searchable words; name the task or the tool")
    documents = [
        Counter(tokenize(skill["name"]) * NAME_WEIGHT + tokenize(skill["description"]))
        for skill in skills
    ]
    lengths = [sum(document.values()) for document in documents]
    average = (sum(lengths) / len(lengths)) if lengths else 0.0
    ranked: list[tuple[float, dict]] = []
    containing = {term: sum(1 for d in documents if term in d) for term in terms}
    for skill, document, length in zip(skills, documents, lengths):
        score = 0.0
        for term in terms:
            frequency = document.get(term, 0)
            if not frequency:
                continue
            count = containing[term]
            idf = math.log(1 + (len(documents) - count + 0.5) / (count + 0.5))
            norm = BM25_K1 * (1 - BM25_B + BM25_B * length / average)
            score += idf * frequency * (BM25_K1 + 1) / (frequency + norm)
        if score > 0:
            ranked.append((score, skill))
    ranked.sort(key=lambda item: (-item[0], item[1]["name"], item[1]["dir"]))
    if ranked:
        floor = ranked[0][0] * RELATIVE_FLOOR
        ranked = [item for item in ranked if item[0] >= floor]
    # The floor is set before named skills move up, so it still measures the best match.
    ranked = [item for item in ranked if not any(item[1] is skill for skill in exact)]
    return ([(math.inf, skill) for skill in exact] + ranked)[:limit]


def snippet(text: str) -> str:
    if len(text) <= SNIPPET_CHARS:
        return text
    return text[:SNIPPET_CHARS].rsplit(" ", 1)[0] + " ..."


def library_topics(skills: list[dict], max_chars: int) -> list[str]:
    """Return the words most common across skill names, most frequent first."""
    counts: Counter[str] = Counter()
    for skill in skills:
        words = set(re.findall(r"[a-z0-9]+", skill["name"].lower()))
        counts.update(
            word
            for word in words
            if len(word) > 1 and word not in STOPWORDS and word not in GENERIC_NAME_WORDS
        )
    chosen: list[str] = []
    used = 0
    for word in sorted(counts, key=lambda word: (-counts[word], word)):
        cost = len(word) + (2 if chosen else 0)
        if used + cost > max_chars:
            break
        chosen.append(word)
        used += cost
    return chosen


def write_topics(skill_md: Path, topics: list[str]) -> str:
    """Set the topics sentence at the end of a SKILL.md description. Return the description."""
    with open(skill_md, encoding="utf-8", newline="") as handle:
        text = handle.read()
    match = re.search(r"^description:[ \t]*(\S.*?)[ \t]*(\r?)$", text, re.MULTILINE)
    if not match or match.group(1)[0] in "|>\"'":
        raise RouterError(f"{skill_md} has no single-line plain description to update")
    description = TOPICS_SENTENCE.sub("", match.group(1))
    if topics:
        description += f" Library topics include {', '.join(topics)}."
    if len(description) > DESCRIPTION_LIMIT:
        raise RouterError(
            f"the description would be {len(description)} characters; the limit is "
            f"{DESCRIPTION_LIMIT}. Lower --max-chars."
        )
    updated = text[: match.start(1)] + description + text[match.end(1) :]
    with open(skill_md, "w", encoding="utf-8", newline="") as handle:
        handle.write(updated)
    return description


def positive_int(value: str) -> int:
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError("must be 1 or more")
    return number


def resolve_library(option: str | None) -> Path:
    raw = option or os.environ.get(LIBRARY_ENV) or DEFAULT_LIBRARY
    root = Path(raw).expanduser()
    if not root.is_dir():
        raise RouterError(
            f"no skill library at {root.as_posix()}. Create that directory and put skills "
            f"in it, or set {LIBRARY_ENV} to the library's path."
        )
    return root.resolve()


def command_search(args: argparse.Namespace) -> int:
    root = resolve_library(args.library)
    skills = refresh_index(root)
    query = " ".join(args.query)
    ranked = search(skills, query, args.limit)
    if args.json:
        results = [
            {
                "name": skill["name"],
                "dir": (root / skill["dir"]).as_posix(),
                "description": skill["description"],
                "harness_variables": skill["harness_variables"],
                "exact_name": math.isinf(score),
                "score": None if math.isinf(score) else round(score, 3),
            }
            for score, skill in ranked
        ]
        print(
            json.dumps(
                {"library": root.as_posix(), "indexed": len(skills), "query": query, "results": results},
                indent=2,
            )
        )
        return 0
    if not ranked:
        print(
            f'No skill in the library matches "{query}" ({len(skills)} indexed, '
            f"library: {root.as_posix()}). Search once more with different words: the tool, "
            "the file type, or the kind of task."
        )
        return 0
    print(f'Top {len(ranked)} of {len(skills)} skills for "{query}":')
    for position, (score, skill) in enumerate(ranked, start=1):
        print()
        print(f"{position}. {skill['name']}" + (" (exact name)" if math.isinf(score) else ""))
        print(f"   dir:  {(root / skill['dir']).as_posix()}")
        print(f"   desc: {snippet(skill['description']) or '(no description)'}")
        if skill["harness_variables"]:
            variables = ", ".join(skill["harness_variables"])
            print(f"   note: uses {variables}, which only a harness fills in; supply the value yourself")
    return 0


def command_index(args: argparse.Namespace) -> int:
    root = resolve_library(args.library)
    skills = refresh_index(root, rebuild=args.rebuild)
    print(f"{len(skills)} skills indexed in {root.as_posix()}")
    undescribed = [skill["dir"] for skill in skills if not skill["description"]]
    if undescribed:
        print(f"\n{len(undescribed)} with no description (found by name only):")
        for path in undescribed:
            print(f"  {path}")
    names = Counter(skill["name"] for skill in skills)
    duplicates = sorted(name for name, count in names.items() if count > 1)
    if duplicates:
        print(f"\n{len(duplicates)} names used by more than one skill:")
        for name in duplicates:
            paths = ", ".join(skill["dir"] for skill in skills if skill["name"] == name)
            print(f"  {name}: {paths}")
    dependent = [skill for skill in skills if skill["harness_variables"]]
    if dependent:
        print(f"\n{len(dependent)} use harness-only variables:")
        for skill in dependent:
            print(f"  {skill['dir']}: {', '.join(skill['harness_variables'])}")
    return 0


def command_topics(args: argparse.Namespace) -> int:
    root = resolve_library(args.library)
    topics = library_topics(refresh_index(root), args.max_chars)
    if args.write:
        skill_md = Path(__file__).resolve().parent.parent / "SKILL.md"
        description = write_topics(skill_md, topics)
        print(f"Updated {skill_md.as_posix()} ({len(description)} characters):")
        print(description)
        return 0
    print(", ".join(topics) if topics else "(the library is empty)")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="skill_router.py",
        description="Find installed skills in a library kept outside the harness's discovery path.",
    )
    parser.add_argument(
        "--library",
        help=f"library directory (default: ${LIBRARY_ENV}, then {DEFAULT_LIBRARY})",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    find = commands.add_parser("search", help="rank the library against a query")
    find.add_argument("query", nargs="+", help="words describing the task")
    find.add_argument("-n", "--limit", type=positive_int, default=5, help="most results to print (default: 5)")
    find.add_argument("--json", action="store_true", help="print results as JSON, with full descriptions")
    find.set_defaults(run=command_search)

    index = commands.add_parser("index", help="refresh the index and report on the library")
    index.add_argument("--rebuild", action="store_true", help="discard the cached index and re-read every skill")
    index.set_defaults(run=command_index)

    topics = commands.add_parser("topics", help="print the words most common across skill names")
    topics.add_argument("--max-chars", type=positive_int, default=300, help="length budget for the list (default: 300)")
    topics.add_argument(
        "--write",
        action="store_true",
        help="put the list in this skill's own SKILL.md description",
    )
    topics.set_defaults(run=command_topics)
    return parser


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    args = build_parser().parse_args(argv)
    try:
        return args.run(args)
    except RouterError as error:
        print(f"skill-router: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
