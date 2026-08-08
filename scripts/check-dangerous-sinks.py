#!/usr/bin/env python3
"""Guardrail: a construct that can execute or inject must be reviewed once.

An agent copies from this base. A `dangerouslySetInnerHTML` in a document labelled
"Good Example" ships as production code, so the ones that are there deliberately —
after a sanitizer, or inside a "never do this" — have to be told apart from the ones
nobody looked at.

This does not try to judge. Judgement is what produced the two findings that prompted
it, and the judging heuristic was right twice out of twenty-eight:

  * `nextjs/19-seo.md` fed `JSON.stringify(jsonLd)` straight into a `<script>` via
    `dangerouslySetInnerHTML` and called it Good. `JSON.stringify` escapes neither `<`
    nor `/`, and script content is raw text, so a title containing `</script>` ended
    the element and turned the rest into live HTML.
  * `divi/18-headless.md` passed WordPress `content.rendered` to the same sink in its
    Good Example, while `security/11-xss.md` and `frontend/14-security.md` both list
    that exact thing as a mistake. The pattern is defensible; going unsaid was not.

So the rule is procedural: an occurrence either reads as a warning from its
surroundings, or it is recorded in `scripts/data/sinks-baseline.json` as reviewed.
Anything else is new and unreviewed, and fails. Keys are content hashes, so editing a
reviewed line brings it back.

Exit code 0 = clean, 1 = an unreviewed occurrence.

Usage:
    python3 scripts/check-dangerous-sinks.py
    python3 scripts/check-dangerous-sinks.py --update-baseline
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KB = ROOT / "knowledge"
BASELINE = ROOT / "scripts" / "data" / "sinks-baseline.json"

# Constructs that execute, inject, or switch off a protection. Each is legitimate
# somewhere; none is legitimate unexamined.
SINKS: dict[str, str] = {
    r"dangerouslySetInnerHTML": "HTML injection sink",
    r"\bv-html\b": "HTML injection sink (Vue)",
    r"\.innerHTML\s*=": "HTML injection sink",
    r"document\.write\s*\(": "HTML injection sink",
    # Bare `eval(` only. `redis.eval(` is Redis' Lua entry point and has nothing
    # to do with JavaScript evaluation.
    r"(?<![.\w])eval\s*\(": "arbitrary evaluation",
    r"new Function\s*\(": "arbitrary evaluation",
    r"NODE_TLS_REJECT_UNAUTHORIZED\s*=\s*['\"]?0": "TLS verification off",
    r"rejectUnauthorized:\s*false": "TLS verification off",
    r"verify\s*=\s*False": "TLS verification off",
    r"--disable-web-security|--no-sandbox": "browser sandbox off",
    r"'unsafe-eval'": "CSP allows eval",
    r"privileged:\s*true": "privileged container",
    r"chmod\s+777": "world-writable permissions",
    r"curl\s+[^\n|]*\|\s*(sudo\s+)?(ba)?sh": "pipe download to shell",
    r"rm\s+-rf\s+/(?:\s|$)": "recursive delete of /",
    r"DROP\s+(DATABASE|SCHEMA)\b": "drops a database",
    r"--no-verify\b": "skips git hooks",
    r"push\s+--force(?!-with-lease)": "force push without lease",
}

# A document that is warning about the construct reads as a warning. Checked against
# the lines around the occurrence, not the whole file: one "Bad Example" heading must
# not excuse a sink four hundred lines further down.
WARNING = re.compile(
    r"bad example|anti-?pattern|common mistakes|never|❌|do not|don't|wrong|avoid|"
    r"insecure|unsafe|vulnerab|leak|attack|exploit|CVE|sanitiz|sink|trust boundary|"
    r"escape|allowlist|mistake",
    re.IGNORECASE,
)
CONTEXT_BEFORE, CONTEXT_AFTER = 14, 4


def main(argv: list[str]) -> int:
    baseline: dict[str, str] = (
        json.loads(BASELINE.read_text(encoding="utf-8")) if BASELINE.exists() else {}
    )
    compiled = [(re.compile(pattern), label) for pattern, label in SINKS.items()]

    found: dict[str, str] = {}
    problems: list[str] = []
    for path in sorted(KB.rglob("*.md")):
        rel = path.relative_to(KB).as_posix()
        lines = path.read_text(encoding="utf-8", errors="replace").split("\n")
        # `tags` and `when_to_use` name these constructs so an agent searching for
        # them arrives at the document that explains them. They are retrieval keys,
        # not code, and cannot ship.
        body_starts = 0
        if lines and lines[0].strip() == "---":
            for number, line in enumerate(lines[1:], start=1):
                if line.strip() == "---":
                    body_starts = number + 1
                    break
        for index, line in enumerate(lines):
            if index < body_starts:
                continue
            for pattern, label in compiled:
                if not pattern.search(line):
                    continue
                context = "\n".join(
                    lines[max(0, index - CONTEXT_BEFORE) : index + CONTEXT_AFTER]
                )
                if WARNING.search(context):
                    continue
                key = hashlib.sha1(f"{rel}:{line.strip()}".encode()).hexdigest()[:10]
                found[key] = f"{rel}:{index + 1}"
                if key in baseline:
                    continue
                problems.append(
                    f"{rel}:{index + 1}: {label}, with nothing nearby marking it as "
                    f"deliberate\n      {line.strip()[:100]}"
                )

    if "--update-baseline" in argv:
        BASELINE.write_text(
            json.dumps(found, indent=1, sort_keys=True) + "\n", encoding="utf-8"
        )
        print(f"baseline updated: {len(found)} reviewed occurrences recorded.")
        return 0

    for key in sorted(set(baseline) - set(found)):
        problems.append(
            f"baseline: {baseline[key]} is recorded as reviewed but no longer matches. "
            f"Run --update-baseline."
        )

    if problems:
        print(f"FAIL: {len(problems)} occurrence(s) need a decision\n")
        for problem in problems:
            print(f"  {problem}")
        print(
            "\nAn agent copies from this base, so each of these ships. Either say next "
            "to it why\nit is safe — the sanitizer, the trust boundary, the escaping — "
            "or, if it is already\nreviewed and the wording simply changed, record it "
            "with --update-baseline."
        )
        return 1

    print(f"OK: every executing or injecting construct is either warned about in place "
          f"or reviewed ({len(baseline)} recorded).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
