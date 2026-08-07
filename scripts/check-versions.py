#!/usr/bin/env python3
"""Guardrail: no document may recommend a runtime that has reached end of life.

This is the one defect class that appears without anyone editing the file. Three
separate audits of this base each found the same thing by hand — "Redis 7.x is the
current stable line as of 2026" after 8.x shipped, "target PHP 8.1+" after 8.1 died,
`node:20` and `golang:1.23` in the examples an agent copies. Structure checks cannot
see it, because nothing about the document is malformed. Only the calendar moved.

Version data comes from a committed snapshot (`scripts/data/eol.json`) rather than
the network, so a run is deterministic and works offline. `--refresh` updates it; the
check fails if the snapshot itself has gone stale, since old data would quietly stop
finding anything.

Intentionally-dated references — a `node:18` that exists to show a broken dev/prod
pair, a `FROM node:latest` in a "Bad Example" — are exempted by content hash in
`scripts/data/eol-baseline.json`, the same mechanism `check-knowledge.py` uses for
code fragments. Exempting by hash means editing the line brings it back for review.

Exit code 0 = clean, 1 = a document recommends something dead.

Usage:
    python3 scripts/check-versions.py
    python3 scripts/check-versions.py --refresh          # re-fetch the snapshot
    python3 scripts/check-versions.py --update-baseline  # accept current exemptions
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KB = ROOT / "knowledge"
DATA = ROOT / "scripts" / "data" / "eol.json"
BASELINE = ROOT / "scripts" / "data" / "eol-baseline.json"

# The snapshot is only useful while it resembles reality.
MAX_SNAPSHOT_AGE_DAYS = 120

PRODUCTS = [
    "nodejs", "php", "python", "go", "postgresql", "mysql", "redis", "mariadb",
    "ruby", "dotnet", "nginx", "wordpress", "django", "laravel", "rails",
]

# Each pattern captures a version an author is telling the reader to use. Anything
# that reads as "this feature arrived in X" is deliberately not matched: `PHP 8.0+`
# in "named arguments (PHP 8.0+)" is a fact about history, not a recommendation.
CLAIMS: list[tuple[str, str]] = [
    (r"FROM\s+node:(\d+(?:\.\d+)*)", "nodejs"),
    (r"image:\s*node:(\d+(?:\.\d+)*)", "nodejs"),
    (r'"node":\s*">=\s*(\d+(?:\.\d+)*)', "nodejs"),
    (r"node-version(?:-file)?:\s*['\"]?(\d+(?:\.\d+)*)", "nodejs"),
    (r"FROM\s+php:(\d+(?:\.\d+)*)", "php"),
    (r"php-version:\s*['\"]?(\d+(?:\.\d+)*)", "php"),
    (r"(?:target|run|use)\s+PHP\s+(\d+\.\d+)\+", "php"),
    (r"FROM\s+python:(\d+(?:\.\d+)*)", "python"),
    (r"python-version:\s*['\"]?(\d+(?:\.\d+)*)", "python"),
    (r"FROM\s+golang:(\d+(?:\.\d+)*)", "go"),
    (r"go-version:\s*['\"]?(\d+(?:\.\d+)*)", "go"),
    (r"FROM\s+postgres:(\d+(?:\.\d+)*)", "postgresql"),
    (r"image:\s*postgres:(\d+(?:\.\d+)*)", "postgresql"),
    (r"FROM\s+mysql:(\d+(?:\.\d+)*)", "mysql"),
    (r"image:\s*mysql:(\d+(?:\.\d+)*)", "mysql"),
    (r"FROM\s+redis:(\d+(?:\.\d+)*)", "redis"),
    (r"image:\s*redis:(\d+(?:\.\d+)*)", "redis"),
]


def refresh() -> int:
    import urllib.request

    products: dict[str, dict[str, object]] = {}
    for name in PRODUCTS:
        try:
            with urllib.request.urlopen(
                f"https://endoflife.date/api/{name}.json", timeout=30
            ) as response:
                cycles = json.load(response)
        except Exception as exc:                      # noqa: BLE001 - reported, not raised
            print(f"  could not fetch {name}: {exc}")
            continue
        products[name] = {str(c["cycle"]): c.get("eol") for c in cycles}

    if not products:
        print("error: fetched nothing; refusing to overwrite the snapshot")
        return 1
    DATA.write_text(
        json.dumps(
            {
                "fetched": date.today().isoformat(),
                "source": "https://endoflife.date",
                "products": products,
            },
            indent=1,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"snapshot updated: {len(products)} products, "
          f"{sum(len(v) for v in products.values())} cycles.")
    return 0


def eol_date(cycles: dict[str, object], version: str) -> str | None:
    """The cycle a version belongs to, longest match first: 8.1.2 -> 8.1, then 8."""
    parts = version.split(".")
    for width in range(len(parts), 0, -1):
        cycle = ".".join(parts[:width])
        if cycle in cycles:
            value = cycles[cycle]
            return value if isinstance(value, str) else None
    return None


def main(argv: list[str]) -> int:
    if "--refresh" in argv:
        return refresh()

    if not DATA.exists():
        print(f"error: {DATA.relative_to(ROOT)} is missing; run with --refresh")
        return 1
    snapshot = json.loads(DATA.read_text(encoding="utf-8"))
    today = date.today()
    age = (today - datetime.strptime(snapshot["fetched"], "%Y-%m-%d").date()).days
    if age > MAX_SNAPSHOT_AGE_DAYS:
        print(f"FAIL: the end-of-life snapshot is {age} days old. Stale data finds "
              f"nothing and reads as clean.\n  Run: python3 scripts/check-versions.py "
              f"--refresh")
        return 1

    baseline: dict[str, str] = (
        json.loads(BASELINE.read_text(encoding="utf-8")) if BASELINE.exists() else {}
    )
    compiled = [(re.compile(pattern), product) for pattern, product in CLAIMS]

    found: dict[str, str] = {}
    problems: list[str] = []
    for path in sorted(KB.rglob("*.md")):
        rel = path.relative_to(KB).as_posix()
        for number, line in enumerate(
            path.read_text(encoding="utf-8", errors="replace").split("\n"), start=1
        ):
            for pattern, product in compiled:
                match = pattern.search(line)
                if not match:
                    continue
                cycles = snapshot["products"].get(product)
                if not cycles:
                    continue
                eol = eol_date(cycles, match.group(1))
                if not eol or eol >= today.isoformat():
                    continue
                key = hashlib.sha1(f"{rel}:{line.strip()}".encode()).hexdigest()[:10]
                found[key] = f"{rel}:{number}"
                if key in baseline:
                    continue
                problems.append(
                    f"{rel}:{number}: {product} {match.group(1)} reached end of life "
                    f"on {eol}\n      {line.strip()}"
                )

    if "--update-baseline" in argv:
        BASELINE.write_text(
            json.dumps(found, indent=1, sort_keys=True) + "\n", encoding="utf-8"
        )
        print(f"baseline updated: {len(found)} intentional references recorded.")
        return 0

    stale = sorted(set(baseline) - set(found))
    for key in stale:
        problems.append(
            f"baseline: {baseline[key]} is exempted but no longer matches. "
            f"Run --update-baseline."
        )

    if problems:
        print(f"FAIL: {len(problems)} version claim(s) point at something unsupported\n")
        for problem in problems:
            print(f"  {problem}")
        print("\nA line that has gone end of life still installs and still runs. It "
              "just stops\nreceiving security fixes, silently. Update it, or record a "
              "deliberate one with\n--update-baseline.")
        return 1

    print(f"OK: every runtime version the base recommends is still supported "
          f"({len(baseline)} deliberate exceptions, data from {snapshot['fetched']}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
