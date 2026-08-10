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
import tempfile
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


def lint_python(source: str) -> list[tuple[str, str]]:
    """ruff, restricted to the rule families that mean a bug rather than a style
    preference: E9 (syntax/runtime), F (pyflakes — undefined names, dead bindings)
    and B (bugbear — mutable defaults, silent `zip` truncation)."""
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as handle:
        handle.write(source)
        path = handle.name
    try:
        proc = subprocess.run(
            [sys.executable, "-m", "ruff", "check", path, "--select=E9,F,B",
             "--output-format=json", "--no-cache"],
            capture_output=True, text=True,
        )
        try:
            report = json.loads(proc.stdout or "[]")
        except json.JSONDecodeError:
            return [("RUFF", (proc.stderr or "ruff produced no report")[:200])]
        return [(item["code"] or "RUFF", item["message"]) for item in report]
    finally:
        os.unlink(path)


# language tags -> (tool that must be on PATH, function returning [(code, message)])
LINTERS: dict[str, tuple[str, object]] = {
    "bash": ("shellcheck", lint_shell),
    "sh": ("shellcheck", lint_shell),
    "shell": ("shellcheck", lint_shell),
    "zsh": ("shellcheck", lint_shell),
    "python": (sys.executable, lint_python),
}

# PHPStan analyses a whole tree at once, so PHP is handled as a batch rather than
# block by block: 445 separate invocations would cost minutes of process startup.
PHP_SANDBOX = Path(os.environ.get("KB_PHP_SANDBOX", "/tmp/kb-php"))
PHP_FENCE = re.compile(r"^```php\s*$\n(.*?)^```\s*$", re.DOTALL | re.MULTILINE)
ES_SANDBOX = Path(os.environ.get("KB_ES_SANDBOX", "/tmp/kb-eslint"))
ES_FENCE = re.compile(r"^```(ts|tsx|js|jsx)\s*$\n(.*?)^```\s*$", re.DOTALL | re.MULTILINE)
ES_PACKAGES = ["eslint", "eslint-plugin-react-hooks", "@typescript-eslint/parser"]
ES_CONFIG = """import reactHooks from "eslint-plugin-react-hooks";
import tsParser from "@typescript-eslint/parser";
export default [
  {
    files: ["blocks/**/*.{ts,tsx}"],
    languageOptions: {
      parser: tsParser,
      parserOptions: {
        ecmaVersion: "latest", sourceType: "module", ecmaFeatures: { jsx: true },
      },
    },
    plugins: { "react-hooks": reactHooks },
    rules: {
      // The two rules this base teaches by name. Everything else eslint offers is
      // style, and style findings on excerpts are noise.
      "react-hooks/rules-of-hooks": "error",
      "react-hooks/exhaustive-deps": "warn",
    },
  },
];
"""


def refresh_es_env(pinned: dict) -> dict:
    ES_SANDBOX.mkdir(parents=True, exist_ok=True)
    (ES_SANDBOX / "package.json").write_text(
        json.dumps({"name": "kb-eslint", "private": True, "type": "module"}) + "\n",
        encoding="utf-8",
    )
    wanted = [f"{name}@{pinned[name]}" if name in pinned else name for name in ES_PACKAGES]
    subprocess.run(["npm", "install", "--silent", "--no-audit", "--no-fund", *wanted],
                   cwd=ES_SANDBOX, capture_output=True, text=True)
    versions = {}
    for name in ES_PACKAGES:
        manifest = ES_SANDBOX / "node_modules" / name / "package.json"
        if manifest.exists():
            versions[name] = json.loads(manifest.read_text(encoding="utf-8"))["version"]
    return versions


def lint_js_batch() -> tuple[int, list[tuple[str, str, str]]]:
    """ESLint over every ts/tsx/js/jsx block, checking only the React hook rules."""
    blocks = ES_SANDBOX / "blocks"
    shutil.rmtree(blocks, ignore_errors=True)
    blocks.mkdir(parents=True)

    origin: dict[str, str] = {}
    written = 0
    for path in sorted(KB.rglob("*.md")):
        for tag, source in ES_FENCE.findall(path.read_text(encoding="utf-8", errors="replace")):
            written += 1
            name = f"b{written:04d}." + ("tsx" if tag in ("tsx", "jsx") else "ts")
            (blocks / name).write_text(source, encoding="utf-8")
            origin[name] = path.relative_to(KB).as_posix()

    (ES_SANDBOX / "eslint.config.js").write_text(ES_CONFIG, encoding="utf-8")
    proc = subprocess.run(["npx", "eslint", "blocks", "--format", "json"],
                          cwd=ES_SANDBOX, capture_output=True, text=True)
    start = proc.stdout.find("[")
    if start < 0:
        return len(origin), [("(eslint)", "ESLINT", proc.stderr[:200] or "no report")]
    findings = []
    for entry in json.loads(proc.stdout[start:]):
        document = origin.get(os.path.basename(entry["filePath"]), entry["filePath"])
        for item in entry["messages"]:
            rule = item.get("ruleId")
            if not rule:
                continue          # a parse failure is an excerpt, and check-knowledge owns syntax
            findings.append((document, rule.split("/")[-1], item["message"]))
    return len(origin), findings


# CSS and HTML go through npx, which resolves a pinned version on demand, so they
# need no sandbox of their own — only a config that turns on the rules that mean a
# defect. `check-knowledge.py` already runs both with rules off, for syntax alone.
WEB_SANDBOX = Path(os.environ.get("KB_WEB_SANDBOX", "/tmp/kb-web"))
CSS_FENCE = re.compile(r"^```css\s*$\n(.*?)^```\s*$", re.DOTALL | re.MULTILINE)
HTML_FENCE = re.compile(r"^```html\s*$\n(.*?)^```\s*$", re.DOTALL | re.MULTILINE)
STYLELINT_CONFIG = {"rules": {
    "property-no-unknown": True,
    "declaration-property-value-no-unknown": True,
    "unit-no-unknown": True,
    "function-no-unknown": True,
    "at-rule-no-unknown": [True, {"ignoreAtRules": [
        "tailwind", "apply", "screen", "layer", "variants", "responsive", "theme",
        "utility", "custom-variant", "plugin", "config", "source"]}],
    "selector-pseudo-class-no-unknown": True,
    "selector-pseudo-element-no-unknown": True,
    "no-duplicate-selectors": True,
    "declaration-block-no-duplicate-properties": [
        True, {"ignore": ["consecutive-duplicates-with-different-values"]}],
}}
HTMLVALIDATE_CONFIG = {
    "extends": ["html-validate:recommended"],
    "rules": {
        # Off: presentation choices an excerpt cannot satisfy.
        "void-style": "off", "no-trailing-whitespace": "off", "attr-quotes": "off",
        "element-required-content": "off", "long-title": "off",
        "require-sri": "off", "no-inline-style": "off", "unique-landmark": "off",
        # On: the accessibility rules this base has a whole topic about.
        "wcag/h30": "error", "wcag/h32": "error", "wcag/h36": "error",
        "wcag/h37": "error", "wcag/h63": "error", "wcag/h67": "error",
        "wcag/h71": "error", "input-missing-label": "error",
        "form-dup-name": "error", "heading-level": "error", "empty-heading": "error",
        "attribute-misuse": "error", "no-dup-id": "error",
    },
}


def lint_web_batch() -> tuple[int, list[tuple[str, str, str]]]:
    """stylelint and html-validate with real rules, over every css/html block."""
    findings: list[tuple[str, str, str]] = []
    total = 0
    for kind, fence, config_name, config, pattern, argv in (
        ("css", CSS_FENCE, ".stylelintrc.json", STYLELINT_CONFIG, "*.css",
         ["npx", "--yes", "stylelint@16"]),
        ("html", HTML_FENCE, ".htmlvalidate.json", HTMLVALIDATE_CONFIG, "*.html",
         ["npx", "--yes", "html-validate@8"]),
    ):
        work = WEB_SANDBOX / kind
        shutil.rmtree(work, ignore_errors=True)
        work.mkdir(parents=True)
        (work / config_name).write_text(json.dumps(config), encoding="utf-8")
        origin: dict[str, str] = {}
        written = 0
        for path in sorted(KB.rglob("*.md")):
            for source in fence.findall(path.read_text(encoding="utf-8", errors="replace")):
                written += 1
                name = f"b{written:04d}.{kind}"
                (work / name).write_text(source, encoding="utf-8")
                origin[name] = path.relative_to(KB).as_posix()
        total += written
        report = work / "report.json"
        # Both write to a file rather than stdout: Node truncates a large pipe on
        # exit, which once made a checker parse half a document and report success.
        if kind == "css":
            subprocess.run([*argv, pattern, "--formatter", "json",
                            "--output-file", str(report)],
                           cwd=work, capture_output=True, text=True)
        else:
            subprocess.run([*argv, pattern, "--formatter", f"json={report.name}"],
                           cwd=work, capture_output=True, text=True)
        if not report.exists():
            findings.append((f"({kind})", "TOOL", "linter produced no report"))
            continue
        data = json.loads(report.read_text(encoding="utf-8"))
        for entry in data:
            key = "source" if kind == "css" else "filePath"
            document = origin.get(os.path.basename(entry[key]), entry[key])
            items = entry["warnings"] if kind == "css" else entry["messages"]
            for item in items:
                rule = item.get("rule") or item.get("ruleId") or kind.upper()
                text = item.get("text") or item.get("message") or ""
                findings.append((document, rule, text))
    return total, findings


PHP_LOCK = ROOT / "scripts" / "data" / "lint-env.json"
PHP_PACKAGES = {
    "phpstan/phpstan": "^2.0",
    "php-stubs/wordpress-stubs": "^7.0",
    "php-stubs/woocommerce-stubs": "^11.0",
}
PHP_CONFIG = """parameters:
  level: 0
  paths: [clean]
  scanFiles:
    - vendor/php-stubs/wordpress-stubs/wordpress-stubs.php
    - vendor/php-stubs/woocommerce-stubs/woocommerce-stubs.php
"""


def refresh_php_env() -> int:
    # Exact versions from the lock unless asked to move them: a stub release changes
    # which symbols exist, and the baseline should record a review, not a Tuesday.
    pinned = json.loads(PHP_LOCK.read_text(encoding="utf-8")) if PHP_LOCK.exists() else {}
    upgrade = "--upgrade" in sys.argv
    require = {
        name: (constraint if upgrade or name not in pinned else pinned[name])
        for name, constraint in PHP_PACKAGES.items()
    }
    PHP_SANDBOX.mkdir(parents=True, exist_ok=True)
    (PHP_SANDBOX / "composer.json").write_text(
        json.dumps({"name": "kb/phpcheck", "require-dev": require}, indent=2) + "\n",
        encoding="utf-8",
    )
    proc = subprocess.run(
        ["composer", "update", "--quiet", "--no-interaction"],
        cwd=PHP_SANDBOX, capture_output=True, text=True,
    )
    if proc.returncode != 0:
        print(proc.stdout[-1500:], proc.stderr[-1500:])
        return 1
    installed = subprocess.run(
        ["composer", "show", "--format=json"], cwd=PHP_SANDBOX,
        capture_output=True, text=True,
    )
    versions = {}
    try:
        for entry in json.loads(installed.stdout).get("installed", []):
            if entry["name"] in PHP_PACKAGES:
                versions[entry["name"]] = entry["version"].lstrip("v")
    except (json.JSONDecodeError, KeyError):
        pass
    if versions:
        PHP_LOCK.write_text(json.dumps(versions, indent=1, sort_keys=True) + "\n",
                            encoding="utf-8")
    print(f"PHP sandbox ready at {PHP_SANDBOX}: "
          + ", ".join(f"{n} {v}" for n, v in sorted(versions.items())))
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
        pinned = json.loads(PHP_LOCK.read_text(encoding="utf-8")) if PHP_LOCK.exists() else {}
        node_versions = refresh_es_env({} if "--upgrade" in argv else pinned)
        code = refresh_php_env()
        if node_versions:
            lock = json.loads(PHP_LOCK.read_text(encoding="utf-8")) if PHP_LOCK.exists() else {}
            lock.update(node_versions)
            PHP_LOCK.write_text(json.dumps(lock, indent=1, sort_keys=True) + "\n",
                                encoding="utf-8")
            print("  eslint: " + ", ".join(f"{n} {v}" for n, v in sorted(node_versions.items())))
        return code

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

    if shutil.which("npx"):
        analysed, findings = lint_web_batch()
        counted += analysed
        for document, code, message in findings:
            shape = re.sub(r"'[^']*'", "'…'", re.sub(r'"[^"]*"', '"…"', message))[:150]
            key = f"{document}|{code}|{shape}"
            found[key] = found.get(key, 0) + 1
            where[key] = document
            sample.setdefault(key, message)
    else:
        SKIPPED["css/html"] = "npx"

    if (ES_SANDBOX / "node_modules").exists():
        analysed, findings = lint_js_batch()
        counted += analysed
        for document, code, message in findings:
            shape = re.sub(r"'[^']*'", "'…'", message)[:150]
            key = f"{document}|{code}|{shape}"
            found[key] = found.get(key, 0) + 1
            where[key] = document
            sample.setdefault(key, message)
    else:
        SKIPPED["ts/tsx/js/jsx"] = "eslint (run --refresh-env)"

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
