#!/usr/bin/env python3
"""Guardrail: run each language's real linter over the examples, not just its parser.

`check-knowledge.py` proves a shell block parses with `bash -n`. That is a low bar:
`for f in $(ls *.log)` parses, and breaks on the first filename with a space. The
base teaches exactly that as an antipattern, which is the point — a document can
state a rule and then break it two hundred lines away, and nothing notices.

Two defects here were of that shape, both in Good Examples:

  playbooks/02-failed-deployment.md picked the rollback target with
  `ls -1dt … | sed -n 2p`, while linux/01, linux/28 and snippets/03 all say "never
  parse `ls` output". A rollback playbook is the worst place to reach for the wrong
  release.

  linux/19-debugging.md took `pid=$(pgrep -f my-service)` and then used `$pid`
  unquoted in six commands. `pgrep` matches more than one process whenever it
  matches at all ambiguously, and every one of those commands then breaks.

A third finding was about the rule, not the code: linux/03 said "Quote everything"
without qualification, while twenty-five Good Examples across the base are command
transcripts that nobody quotes. The rule now says where it binds.

Nothing is filtered by severity or code. Every current diagnostic is recorded in
`scripts/data/lint-baseline.json` keyed by document, code and message shape, and
only unreviewed ones fail — the same contract as check-types.py and
check-dangerous-sinks.py. A missing linter is reported, never silently skipped.

The baseline stores a *count* per key, not just the key. Keying alone let a second
`SC2086` in a document that already had one pass unseen, which is how the first
version of this check reported success on an injected `for f in $(ls …)`.

Exit code 0 = clean, 1 = an unreviewed diagnostic.

Usage:
    python3 scripts/check-lint.py
    python3 scripts/check-lint.py --require-tools
    python3 scripts/check-lint.py --update-baseline
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KB = ROOT / "knowledge"
BASELINE = ROOT / "scripts" / "data" / "lint-baseline.json"

SKIPPED: dict[str, str] = {}


def lint_shell(source: str) -> list[tuple[str, str]]:
    # A block that is a fragment of a script still deserves script rules; the shebang
    # only tells shellcheck which dialect to assume.
    body = source if source.lstrip().startswith("#!") else "#!/usr/bin/env bash\n" + source
    proc = subprocess.run(
        ["shellcheck", "--format=json", "-s", "bash", "-"],
        input=body, capture_output=True, text=True,
    )
    try:
        report = json.loads(proc.stdout or "[]")
    except json.JSONDecodeError:
        return [("SC0000", (proc.stderr or "shellcheck produced no report")[:200])]
    return [(f"SC{item['code']}", item["message"]) for item in report]


# language tags -> (tool that must be on PATH, function returning [(code, message)])
LINTERS: dict[str, tuple[str, object]] = {
    "bash": ("shellcheck", lint_shell),
    "sh": ("shellcheck", lint_shell),
    "shell": ("shellcheck", lint_shell),
    "zsh": ("shellcheck", lint_shell),
}

FENCE = re.compile(
    r"^```(" + "|".join(sorted(LINTERS)) + r")\s*$\n(.*?)^```\s*$",
    re.DOTALL | re.MULTILINE,
)


def main(argv: list[str]) -> int:
    baseline: dict[str, str] = (
        json.loads(BASELINE.read_text(encoding="utf-8")) if BASELINE.exists() else {}
    )
    found: dict[str, int] = {}
    where: dict[str, str] = {}
    sample: dict[str, str] = {}
    problems: list[str] = []
    counted = 0

    for path in sorted(KB.rglob("*.md")):
        rel = path.relative_to(KB).as_posix()
        for tag, source in FENCE.findall(path.read_text(encoding="utf-8", errors="replace")):
            tool, linter = LINTERS[tag]
            if not shutil.which(tool):
                SKIPPED[tag] = tool
                continue
            counted += 1
            for code, message in linter(source):
                shape = re.sub(r"'[^']*'", "'…'", message)[:150]
                key = f"{rel}|{code}|{shape}"
                found[key] = found.get(key, 0) + 1
                where[key] = rel
                sample.setdefault(key, message)

    if "--update-baseline" in argv:
        BASELINE.write_text(json.dumps(found, indent=1, sort_keys=True) + "\n", encoding="utf-8")
        print(f"baseline updated: {sum(found.values())} diagnostics across "
              f"{len(set(where.values()))} documents.")
        return 0

    for key, count in sorted(found.items()):
        known = baseline.get(key, 0)
        if count > known:
            document, code, _ = key.split("|", 2)
            problems.append(
                f"{document}: {code} {sample.get(key, '')[:180]}"
                + (f"  ({count - known} more than the {known} reviewed)" if known else "")
            )
    for key in sorted(set(baseline) - set(found)):
        problems.append(
            f"baseline: {key.split('|')[0]} no longer produces {key.split('|')[1]}. "
            f"Run --update-baseline."
        )

    for tag, tool in sorted(SKIPPED.items()):
        message = f"```{tag} blocks were not linted: `{tool}` is unavailable."
        if "--require-tools" in argv:
            problems.append(message)
        else:
            print(f"  note: {message}")

    if problems:
        print(f"\nFAIL: {len(problems)} lint diagnostic(s) not previously reviewed\n")
        for problem in sorted(problems)[:50]:
            print(f"  {problem}")
        if len(problems) > 50:
            print(f"  … and {len(problems) - 50} more")
        print("\nThese blocks parse. A linter that knows the language still rejects "
              "them.\nFix the example, or record a reviewed one with --update-baseline.")
        return 1

    print(f"OK: {counted} blocks pass their language's linter "
          f"({sum(baseline.values())} reviewed diagnostics).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
