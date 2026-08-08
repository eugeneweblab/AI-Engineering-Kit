#!/usr/bin/env python3
"""Self-test: inject a defect per rule and assert the guardrail reports it.

A check that passes is only evidence when it can fail. Twice in this repository a
check reported success while doing nothing — `html-validate` writing its report to a
stdout pipe Node truncated at 64 KiB, and a missing parser returning the same value
as "no problem found". Neither was visible from a green run.

This copies the base, introduces one defect per rule, and fails if any of them goes
unreported. Every rule and every block language has a case; each case lands in its
own document, so all of them can be injected at once and verified in two runs — the
guardrail is slow enough that one run per case would take an hour.

Usage:
    python3 scripts/selftest-guardrails.py            # every case
    python3 scripts/selftest-guardrails.py sql html   # only matching names
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHECKER = ROOT / "scripts" / "check-knowledge.py"


def replace(path: str, old: str, new: str):
    def apply(kb: Path) -> None:
        target = kb / path
        text = target.read_text(encoding="utf-8")
        if old not in text:
            raise AssertionError(f"anchor missing in {path}: {old[:60]!r}")
        target.write_text(text.replace(old, new, 1), encoding="utf-8")
    apply.path = path
    return apply


def in_fence(path: str, tag: str, line: str):
    """Inject as the first line inside the document's first ```tag block."""
    return replace(path, f"```{tag}\n", f"```{tag}\n{line}\n")


def set_field(path: str, field: str, value: str):
    """Replace a frontmatter line wholesale — a partial edit can leave the old value
    in place, which is how the first `when_to_use` case silently tested nothing."""
    def apply(kb: Path) -> None:
        target = kb / path
        text = target.read_text(encoding="utf-8")
        new, count = re.subn(rf"^{field}:.*$", f"{field}: {value}", text,
                             count=1, flags=re.MULTILINE)
        if count != 1:
            raise AssertionError(f"no `{field}:` line in {path}")
        target.write_text(new, encoding="utf-8")
    apply.path = path
    return apply


def drop(path: str):
    def apply(kb: Path) -> None:
        (kb / path).unlink()
    apply.path = path
    return apply


def strip_rules(path: str):
    def apply(kb: Path) -> None:
        target = kb / path
        target.write_text(
            re.sub(r"^\*\*Rules:\*\* .*\n\n", "", target.read_text(encoding="utf-8"),
                   flags=re.MULTILINE),
            encoding="utf-8",
        )
    apply.path = path
    return apply


# Cases runnable without php / npx / hadolint / sqlfluff — one fast pass.
FAST: list[tuple[str, object, str]] = [
    ("structure/missing-98", drop("redis/98-production-checklist.md"),
     "no document with order 98"),
    ("frontmatter/id", replace("mysql/04-indexes.md", "id: mysql/04-indexes", "id: mysql/oops"),
     "id is"),
    ("frontmatter/topic", replace("linux/05-permissions.md", "topic: linux", "topic: unix"),
     "topic is"),
    ("frontmatter/order", replace("git/04-commits.md", "order: 4", "order: 40"),
     "order is"),
    ("frontmatter/status", replace("css/07-grid.md", "status: ready", "status: maybe"),
     "status is"),
    ("frontmatter/when_to_use", set_field("html/06-lists.md", "when_to_use", '""'),
     "when_to_use is empty"),
    ("frontmatter/type", replace("seo/03-indexing.md", "type: doc", "type: reference"),
     "type is"),
    ("frontmatter/title-vs-h1", replace("sql/05-joins.md", "# Joins", "# SQL Joins"),
     "but the H1 is"),
    ("frontmatter/duplicate-title",
     replace("docker/04-containers.md", 'title: "Docker Containers"', 'title: "Docker Images"'),
     "is already used by"),
    ("frontmatter/applies_to",
     replace("nextjs/10-caching.md", "applies_to: [app-router]", "applies_to: [pages-dir]"),
     "is not a known variant"),
    ("frontmatter/defers_to",
     replace("tools/16-git-hooks.md", "defers_to: git/20-hooks", "defers_to: git/99-nope"),
     "defers_to -> git/99-nope does not exist"),
    ("links/markdown",
     replace("prisma/07-crud.md", "## Related", "See [gone](99-gone.md).\n\n## Related"),
     "broken link"),
    ("links/related-id", replace("redis/03-strings.md", "related: [", "related: [redis/99-nope, "),
     "redis/99-nope does not exist"),
    ("fences/unbalanced", replace("github/06-pull-requests.md", "## Purpose", "## Purpose\n\n```ts"),
     "unbalanced"),
    ("fences/zero-width", replace("testing/09-assertions.md", "## Purpose", "## Purpose​"),
     "zero-width"),
    ("tables/unescaped-pipe",
     replace("ai/06-self-verification.md", r"'console\.log\|debugger", r"'console\.log|debugger"),
     "unescaped `|`"),
    ("pointers/rules-removed", strip_rules("redis/99-ai-review-checklist.md"),
     "`**Rules:**` pointer"),
    ("lang/python", in_fence("aws/14-cloudwatch.md", "python", "def broken(:"),
     "```python does not parse"),
    ("lang/json", in_fence("tools/18-monorepo-tools.md", "json", "{ broken: }"),
     "does not parse"),
    ("lang/yaml", in_fence("docker/12-docker-compose.md", "yaml", "a: [1, 2"),
     "```yaml does not parse"),
    ("lang/xml", in_fence("seo/07-sitemaps.md", "xml", "<!-- before the declaration -->"),
     "```xml does not parse"),
    ("lang/nginx", in_fence("nginx/03-server-blocks.md", "nginx", "server { listen 80"),
     "```nginx does not parse"),
    ("lang/hcl", in_fence("aws/20-ecr.md", "hcl", 'resource "x" "y" { a = , }'),
     "```hcl does not parse"),
    ("lang/ini", in_fence("php/27-production.md", "ini", "[unclosed\nkey = 1"),
     "```ini does not parse"),
    ("lang/graphql", in_fence("graphql/02-schema.md", "graphql", "type Broken { field: }"),
     "```graphql does not parse"),
    ("lang/http", in_fence("rest-api/01-http.md", "http", "PSOT /v1/orders HTTP/1.1"),
     "```http does not parse"),
    ("lang/diff", in_fence("ai/04-code-modification.md", "diff", "line without a prefix"),
     "```diff does not parse"),
    ("lang/cron", in_fence("linux/14-cron.md", "cron", "99 * * * * /bin/true"),
     "```cron does not parse"),
    ("lang/makefile", in_fence("tools/19-task-runners.md", "makefile", "build:\n    echo spaces"),
     "```makefile does not parse"),
    ("lang/redis", in_fence("redis/02-data-types.md", "redis", "SADDD key value"),
     "```redis does not parse"),
    ("lang/shell", in_fence("linux/03-bash.md", "bash", "if [ -f x ; then"),
     "shell block does not parse"),
]

# `check-versions.py` reads the whole base and its own snapshot, so its cases run
# against the real tree rather than the sandbox the other cases share.
VERSION_CASES: list[tuple[str, object, str]] = [
    ("versions/eol-runtime",
     replace("docker/08-dockerfile.md", "FROM node:24-slim", "FROM node:20-slim"),
     "reached end of life"),
    ("versions/stale-snapshot", "snapshot",
     "snapshot is"),
    ("manifests/k8s-no-selector",
     replace("kubernetes/05-deployments.md",
             "  selector: { matchLabels: { app: web } }\n", ""),
     "missing property 'selector'"),
    ("manifests/workflow-no-runs-on",
     replace("testing/21-cicd.md", "    runs-on: ubuntu-latest\n", ""),
     '"runs-on" section is missing'),
    ("sinks/unreviewed",
     replace("react/03-jsx.md", "## Purpose",
             "## Purpose\n\n```tsx\nconst Bio = ({ html }) => "
             "<div dangerouslySetInnerHTML={{ __html: html }} />;\n```\n"),
     "with nothing nearby marking it as deliberate"),
]

# Cases needing an external parser — one full pass.
SLOW: list[tuple[str, object, str]] = [
    ("lang/dockerfile",
     replace("docker/11-multi-stage-builds.md", "COPY go.mod go.sum ./",
             "COPY go.mod go.sum ./   # a mid-line # is an argument, not a comment"),
     "dockerfile block does not parse"),
    ("lang/go", in_fence("devops/13-observability.md", "go", "func broken( {\n}"),
     "go block does not parse"),
    ("lang/lua", in_fence("redis/11-lua-scripting.md", "lua", "if then end"),
     "lua block does not parse"),
    ("lang/sql", in_fence("sql/12-ddl.md", "sql", "SELEKT * FROM t;"),
     "sql block does not parse"),
    ("lang/html", replace("html/08-forms.md", '    id="email"\n', '    id="email"  <!-- c -->\n'),
     "html block does not parse"),
    ("lang/css", in_fence("css/06-flexbox.md", "css", ".broken { display: flex;"),
     "css block does not parse"),
    ("lang/php", in_fence("wordpress/08-hooks.md", "php", "function broken( { }"),
     "php block does not parse"),
    ("lang/js", in_fence("react/12-performance.md", "tsx", "const = ;"),
     "js block does not parse"),
]


def run_batch(cases: list[tuple[str, object, str]], extra: list[str]) -> dict[str, str]:
    """Inject every case into one sandbox, run once, report which went unnoticed."""
    verdicts: dict[str, str] = {}
    with tempfile.TemporaryDirectory() as tmp:
        sandbox = Path(tmp)
        shutil.copytree(ROOT / "knowledge", sandbox / "knowledge")
        shutil.copytree(ROOT / "docs", sandbox / "docs")

        seen: dict[str, str] = {}
        for name, defect, _ in cases:
            path = getattr(defect, "path", None)
            if path in seen:
                verdicts[name] = f"shares {path} with {seen[path]} — give it its own document"
                continue
            seen[path] = name
            try:
                defect(sandbox / "knowledge")
            except AssertionError as exc:
                verdicts[name] = f"could not inject: {exc}"

        proc = subprocess.run(
            [sys.executable, str(CHECKER), str(sandbox / "knowledge"), *extra],
            capture_output=True, text=True,
        )
        output = proc.stdout + proc.stderr
        # A language the guardrail could not check has not been proved wrong; saying
        # "not reported" would blame the rule for a missing parser. It still is not
        # clean — an unproved case fails, it just fails with the true reason.
        skipped = {
            family: tool
            for tool, family in re.findall(
                r"note: `([^`]+)` not found — (\w+) blocks were not checked", output)
        }
        for name, _, _ in cases:
            family = name.split("/", 1)[1] if name.startswith("lang/") else None
            if family in skipped:
                verdicts[name] = f"not proved: `{skipped[family]}` is unavailable here"

        if proc.returncode == 0:
            for name, _, _ in cases:
                verdicts.setdefault(name, "the guardrail reported success")
            return verdicts

        for name, _, expected in cases:
            if name in verdicts:
                continue
            if expected not in output:
                verdicts[name] = "not reported"
    return verdicts


def run_version_cases(cases: list[tuple[str, object, str]]) -> dict[str, str]:
    """Each case gets its own copy: the checker resolves paths from the tree root."""
    verdicts: dict[str, str] = {}
    for name, defect, expected in cases:
        with tempfile.TemporaryDirectory() as tmp:
            sandbox = Path(tmp) / "kit"
            shutil.copytree(ROOT / "knowledge", sandbox / "knowledge")
            shutil.copytree(ROOT / "scripts", sandbox / "scripts")
            if defect == "snapshot":
                data = sandbox / "scripts" / "data" / "eol.json"
                payload = json.loads(data.read_text(encoding="utf-8"))
                payload["fetched"] = "2020-01-01"
                data.write_text(json.dumps(payload), encoding="utf-8")
            else:
                defect(sandbox / "knowledge")
            script = ("check-versions.py" if name.startswith("versions/")
                      else "check-manifests.py" if name.startswith("manifests/")
                      else "check-dangerous-sinks.py")
            proc = subprocess.run(
                [sys.executable, str(sandbox / "scripts" / script)],
                capture_output=True, text=True,
            )
            output = proc.stdout + proc.stderr
            if proc.returncode == 0:
                verdicts[name] = "the guardrail reported success"
            elif expected not in output:
                verdicts[name] = "not reported"
    return verdicts


def main(argv: list[str]) -> int:
    wanted = argv[1:]
    fast = [c for c in FAST if not wanted or any(w in c[0] for w in wanted)]
    slow = [c for c in SLOW if not wanted or any(w in c[0] for w in wanted)]
    versions = [c for c in VERSION_CASES if not wanted or any(w in c[0] for w in wanted)]
    if not fast and not slow and not versions:
        print(f"no case matches {wanted}")
        return 2

    verdicts: dict[str, str] = {}
    if fast:
        verdicts |= run_batch(fast, ["--skip-external"])
    if slow:
        verdicts |= run_batch(slow, [])
    if versions:
        verdicts |= run_version_cases(versions)

    failures = []
    for name, _, _ in fast + slow + versions:
        problem = verdicts.get(name)
        if problem and problem.startswith("not proved"):
            print(f"  ????  {name}  — {problem}")
            failures.append(name)
            continue
        print(f"  {'ok  ' if not problem else 'FAIL'}  {name}"
              + (f"  — {problem}" if problem else ""))
        if problem:
            failures.append(name)

    unproved = [n for n in failures if verdicts[n].startswith("not proved")]
    print()
    if failures:
        missed = len(failures) - len(unproved)
        parts = []
        if missed:
            parts.append(f"{missed} injected defects went unreported")
        if unproved:
            parts.append(f"{len(unproved)} could not be proved for want of a parser")
        print(f"FAIL: of {len(fast) + len(slow) + len(versions)} cases, " + " and ".join(parts))
        print("A rule that cannot fail is not a check. Fix the rule, not this test.")
        return 1
    print(f"OK: all {len(fast) + len(slow) + len(versions)} injected defects were reported.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
