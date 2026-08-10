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
    python3 scripts/check-lint.py --refresh-env       # install PHPStan + WP/WC stubs
    python3 scripts/check-lint.py --update-baseline
"""
from __future__ import annotations

import json
import os
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

# PHPStan analyses a whole tree at once, so PHP is handled as a batch rather than
# block by block: 445 separate invocations would cost minutes of process startup.
PHP_SANDBOX = Path(os.environ.get("KB_PHP_SANDBOX", "/tmp/kb-php"))
PHP_FENCE = re.compile(r"^```php\s*$\n(.*?)^```\s*$", re.DOTALL | re.MULTILINE)
PHP_COMPOSER = {
    "name": "kb/phpcheck",
    "require-dev": {
        "phpstan/phpstan": "^2.0",
        "php-stubs/wordpress-stubs": "^7.0",
        "php-stubs/woocommerce-stubs": "^11.0",
    },
}
PHP_CONFIG = """parameters:
  level: 0
  paths: [clean]
  scanFiles:
    - vendor/php-stubs/wordpress-stubs/wordpress-stubs.php
    - vendor/php-stubs/woocommerce-stubs/woocommerce-stubs.php
"""


def refresh_php_env() -> int:
    PHP_SANDBOX.mkdir(parents=True, exist_ok=True)
    (PHP_SANDBOX / "composer.json").write_text(
        json.dumps(PHP_COMPOSER, indent=2) + "\n", encoding="utf-8"
    )
    proc = subprocess.run(
        ["composer", "update", "--quiet", "--no-interaction"],
        cwd=PHP_SANDBOX, capture_output=True, text=True,
    )
    if proc.returncode != 0:
        print(proc.stdout[-1500:], proc.stderr[-1500:])
        return 1
    versions = {}
    for package in ("php-stubs/wordpress-stubs", "php-stubs/woocommerce-stubs",
                    "phpstan/phpstan"):
        manifest = PHP_SANDBOX / "vendor" / package / "composer.json"
        if manifest.exists():
            versions[package] = json.loads(manifest.read_text(encoding="utf-8")).get(
                "version", "installed"
            )
    print(f"PHP sandbox ready at {PHP_SANDBOX}: "
          f"{', '.join(sorted(versions)) or 'packages installed'}.")
    return 0


def lint_php_batch() -> tuple[int, list[tuple[str, str, str]]]:
    """Returns (blocks analysed, [(document, code, message)])."""
    clean = PHP_SANDBOX / "clean"
    shutil.rmtree(clean, ignore_errors=True)
    clean.mkdir(parents=True)

    origin: dict[str, str] = {}
    written = 0
    for path in sorted(KB.rglob("*.md")):
        for source in PHP_FENCE.findall(path.read_text(encoding="utf-8", errors="replace")):
            body = source if source.lstrip().startswith("<?php") else "<?php\n" + source
            written += 1
            candidate = clean / f"b{written:04d}.php"
            candidate.write_text(body, encoding="utf-8")
            # A block that is a class body or an array literal cannot be parsed on its
            # own. Feeding one to PHPStan makes it call the whole run incomplete and
            # silently stop applying rules — which is how an earlier version of this
            # reported zero errors while checking nothing.
            if subprocess.run(["php", "-l", str(candidate)],
                              capture_output=True).returncode != 0:
                candidate.unlink()
                continue
            origin[candidate.name] = path.relative_to(KB).as_posix()

    (PHP_SANDBOX / "phpstan.neon").write_text(PHP_CONFIG, encoding="utf-8")
    proc = subprocess.run(
        ["./vendor/bin/phpstan", "analyse", "--no-progress", "--memory-limit=4G",
         "--error-format=json"],
        cwd=PHP_SANDBOX, capture_output=True, text=True,
    )
    start = proc.stdout.find("{")
    if start < 0:
        return len(origin), [("(phpstan)", "PHPSTAN", proc.stderr[:200] or "no report")]
    report = json.loads(proc.stdout[start:])
    findings = []
    for path, info in report.get("files", {}).items():
        document = origin.get(os.path.basename(path), os.path.basename(path))
        for item in info["messages"]:
            findings.append((document, "PHPSTAN", item["message"]))
    return len(origin), findings

FENCE = re.compile(
    r"^```(" + "|".join(sorted(LINTERS)) + r")\s*$\n(.*?)^```\s*$",
    re.DOTALL | re.MULTILINE,
)


def main(argv: list[str]) -> int:
    if "--refresh-env" in argv:
        return refresh_php_env()

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

    if shutil.which("phpstan") or (PHP_SANDBOX / "vendor" / "bin" / "phpstan").exists():
        analysed, findings = lint_php_batch()
        counted += analysed
        for document, code, message in findings:
            shape = re.sub(r"'[^']*'", "'…'", message)[:150]
            key = f"{document}|{code}|{shape}"
            found[key] = found.get(key, 0) + 1
            where[key] = document
            sample.setdefault(key, message)
    else:
        SKIPPED["php"] = "phpstan (run --refresh-env)"

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
