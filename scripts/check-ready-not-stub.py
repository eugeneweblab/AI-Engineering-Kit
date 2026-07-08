#!/usr/bin/env python3
"""Guardrail: fail if any `status: ready` knowledge doc is actually a stub.

The audit found empty index topics marked `status: ready`, which routed AI agents
(who filter INDEX.json for ready docs) to dead ends. This linter prevents that class
of regression: a doc may only claim `ready` if it has real substance.

A `ready` doc FAILS when any of these hold:
  - its body contains a TODO / placeholder marker
    (e.g. "TODO", "Section overview pending", "FIXME"), or
  - its body (everything after the YAML frontmatter, excluding the H1) has fewer than
    MIN_BODY_CHARS characters of real content, or
  - it is a `type: index` doc whose body is tiny AND whose `related:` list is empty
    (an index that points nowhere).

Exit code 0 = clean, 1 = violations found. Intended for CI / pre-commit.

Usage:
    python3 scripts/check-ready-not-stub.py [knowledge_dir]
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

MIN_BODY_CHARS = 400          # a real `ready` doc has at least this much prose/code
MIN_INDEX_BODY_CHARS = 250    # index docs may be shorter, but not empty

# Match only genuine stub markers, not the words "todo"/"pending" used legitimately
# in prose or code (e.g. a `todos` variable, "avoid leaving TODO comments", the HTML
# `placeholder` attribute). A stub is a line that *starts* with a TODO/FIXME marker
# (optionally as a blockquote/heading), or a known unfinished-section phrase.
STUB_TODO_LINE_RE = re.compile(r"^\s*(?:>+\s*|#+\s*)?(?:TODO|FIXME)\b[:\-\s]", re.MULTILINE)
STUB_PHRASE_RE = re.compile(
    r"section overview pending|content pending|coming soon|to be written|"
    r"documentation pending|draft stub",
    re.IGNORECASE,
)


def has_placeholder(body: str) -> bool:
    return bool(STUB_TODO_LINE_RE.search(body) or STUB_PHRASE_RE.search(body))

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n?(.*)$", re.DOTALL)


def parse(path: Path):
    """Return (frontmatter_dict_lite, body) or (None, None) if no frontmatter."""
    text = path.read_text(encoding="utf-8")
    m = FRONTMATTER_RE.match(text)
    if not m:
        return None, None
    fm_raw, body = m.group(1), m.group(2)
    fm = {}
    for line in fm_raw.splitlines():
        mm = re.match(r"^([A-Za-z_]+):\s*(.*)$", line)
        if mm:
            fm[mm.group(1)] = mm.group(2).strip()
    return fm, body


def body_content_chars(body: str) -> int:
    """Characters of real content: drop the leading H1, headings, and blank lines."""
    chars = 0
    for line in body.splitlines():
        s = line.strip()
        if not s:
            continue
        if s.startswith("#"):        # headings are structure, not substance
            continue
        chars += len(s)
    return chars


def related_is_empty(fm: dict) -> bool:
    rel = fm.get("related", "")
    # matches `related: []` or `related:` (nothing meaningful)
    return rel in ("", "[]")


def main(argv: list[str]) -> int:
    root = Path(argv[1]) if len(argv) > 1 else Path("knowledge")
    if not root.exists():
        print(f"error: {root} not found", file=sys.stderr)
        return 2

    violations: list[tuple[str, str]] = []
    checked = 0

    for path in sorted(root.rglob("*.md")):
        fm, body = parse(path)
        if fm is None:
            continue
        if fm.get("status") != "ready":
            continue
        checked += 1
        rel = str(path)

        if has_placeholder(body):
            violations.append((rel, "contains a TODO/placeholder marker but is marked ready"))
            continue

        chars = body_content_chars(body)
        is_index = fm.get("type") == "index"
        floor = MIN_INDEX_BODY_CHARS if is_index else MIN_BODY_CHARS

        if chars < floor:
            violations.append(
                (rel, f"body has only {chars} chars of content (< {floor}) but is marked ready")
            )
            continue

        if is_index and related_is_empty(fm) and chars < MIN_BODY_CHARS:
            violations.append(
                (rel, "index doc is thin and links nowhere (related: []) but is marked ready")
            )

    if violations:
        print(f"FAIL: {len(violations)} stub doc(s) marked status: ready\n")
        for rel, why in violations:
            print(f"  {rel}\n      {why}")
        print(
            f"\nChecked {checked} ready docs. Fix: add real content, or set status: draft."
        )
        return 1

    print(f"OK: all {checked} ready docs have real content (no stub-as-ready).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
