#!/usr/bin/env python3
"""Self-test: run the retrieval protocol and assert it reaches the right rules.

AGENTS.md tells an agent how to find knowledge. This executes that procedure
literally — detect the stack from repository files via `SIGNALS.stack`, resolve
symbols from the diff via `SIGNALS.symbols`, filter `INDEX.json` to `status: ready`,
match on `when_to_use` / `topic` / `tags`, drop anything whose `applies_to` names
another variant — and checks that a realistic question about each language lands on
the document that states the rule.

It is the counterpart to selftest-guardrails.py: that one proves the checks can
fail, this one proves the instructions can be followed. Both exist because a green
run is not evidence on its own.

Usage:
    python3 scripts/selftest-retrieval.py           # every case
    python3 scripts/selftest-retrieval.py php sql   # only matching names
"""
from __future__ import annotations

import collections
import fnmatch
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOP_N = 5

STOPWORDS = set(
    "a an the for with of to in on and or is are read before when any this that it its "
    "use using new my our i we how do does can should".split()
)


def tokens(text: str) -> set[str]:
    """Words, plus a naive singular so `join` matches `joins`."""
    out: set[str] = set()
    for word in re.split(r"[^a-z0-9]+", text.lower()):
        if not word or word in STOPWORDS or len(word) <= 2:
            continue
        out.add(word)
        if word.endswith("s") and len(word) > 3:
            out.add(word[:-1])
    return out


class Protocol:
    """The lookup AGENTS.md describes, and nothing beyond it."""

    def __init__(self) -> None:
        index = json.loads((ROOT / "knowledge" / "INDEX.json").read_text(encoding="utf-8"))
        self.signals = json.loads((ROOT / "knowledge" / "SIGNALS.json").read_text(encoding="utf-8"))
        self.docs = [
            d for topic in index["topics"].values() for d in topic["docs"]
            if d["status"] == "ready"
        ]
        # Multi-word terms of art, longest first: "core web vitals" should win over
        # "web vitals" when both are present.
        self.phrases = sorted(
            (s for s in self.signals["symbols"] if " " in s), key=len, reverse=True
        )
        # `IAM` is indexed, `iam` is what someone types. Fold case, but only where it
        # is unambiguous — `set` and `SET` are different things.
        collisions = {s.lower() for s in self.signals["symbols"]}
        seen: dict[str, list[str]] = {}
        for name, ids in self.signals["symbols"].items():
            seen.setdefault(name.lower(), []).extend(ids)
        self.folded = {k: v for k, v in seen.items() if k in collisions}

    def stack(self, files: list[str]) -> list[dict]:
        hits = []
        for entry in self.signals["stack"]:
            patterns = entry["when"].split("|")
            if not any(fnmatch.fnmatch(f, p) for f in files for p in patterns):
                continue
            absent = entry.get("absent")
            if absent and any(fnmatch.fnmatch(f, absent) for f in files):
                continue
            hits.append(entry)
        return hits

    def lookup_symbol(self, symbol: str) -> list[list[str]]:
        """A diff yields `LEFT JOIN` and `set -euo pipefail` as well as bare names.
        Try the phrase, then the same phrase in the case the index holds, then each
        word in it — which is what a reader would do.

        Each resolved term is returned as its own group. Merging them into one list
        loses the thing that matters: in `set -euo pipefail`, `pipefail` names one
        document and `set` names forty-seven, and a merged list weights the precise
        term as if it were the vague one."""
        hit = self.signals["symbols"].get(symbol) or self.folded.get(symbol.lower())
        if hit:
            return [hit]
        groups: list[list[str]] = []
        for word in re.split(r"[^A-Za-z0-9_.-]+", symbol):
            if len(word) > 2:
                found = self.signals["symbols"].get(word) or self.folded.get(word.lower())
                if found:
                    groups.append(found)
        return groups

    def terms_in(self, task: str) -> list[str]:
        """The question itself names things. "Largest Contentful Paint regressed"
        carries the term; so does "Pods are OOM killed". A reader spots a term of art
        and looks it up — treat that as a signal rather than as loose word overlap."""
        lowered = task.lower()
        found = [p for p in self.phrases if p in lowered]
        found += [
            word for word in re.findall(r"\b[A-Z][A-Z0-9]{1,7}\b", task)
            if word in self.signals["symbols"]
        ]
        return found

    def retrieve(self, task: str, files: list[str], symbols: list[str],
                 without: str = "", assume_variants: list[str] | None = None) -> list[str]:
        """`without` blanks one source of evidence, so a caller can ask which one
        was actually carrying the result. A test that cannot be made to fail proves
        nothing; ablation is how this one shows its answers are not coincidental.

        `assume_variants` is for reachability probes that have no repository files:
        they still have to measure a variant-specific document in a repo where it
        applies, not skip it as if the repo were a different variant."""
        if without == "stack":
            files = []
        if without == "symbols":
            symbols = []
        # Weights follow the precedence AGENTS.md states: a signal outranks
        # `when_to_use`, which outranks tags, which outranks a word in a title.
        score: collections.Counter[str] = collections.Counter()

        stack = self.stack(files)
        variants = {e["variant"] for e in stack if "variant" in e}
        if assume_variants:
            variants |= set(assume_variants)
        stack_topics: set[str] = set()
        for entry in stack:
            for doc_id in entry["docs"]:
                score[doc_id] += 20
                stack_topics.add(doc_id.split("/")[0])

        # A symbol is worth what it narrows. `revalidateTag` names two documents and
        # settles the question; `revert` names a git document, a CSS keyword and a
        # deploy step, and settles nothing — weighting them alike lets the vague one
        # outrank `when_to_use`.
        # A resolved term establishes the subject the way a stack signal establishes
        # the stack: it says which topic, not which document. Treat it the same.
        term_topics: set[str] = set()
        named = [] if without == "terms" else self.terms_in(task)
        for symbol in list(symbols) + named:
            for targets in self.lookup_symbol(symbol):
                weight = 30 / max(1, len(set(targets)))
                for doc_id in targets:
                    score[doc_id] += weight
                    term_topics.add(doc_id.split("/")[0])

        query = tokens(task) if without != "task" else set()
        for doc in self.docs:
            applies = doc.get("applies_to")
            if applies and not (set(applies) & variants):
                continue                     # a rule for a variant this repo does not use
            points = (
                8 * len(query & tokens(doc.get("when_to_use", "")
                                       if without != "when_to_use" else ""))
                + 4 * len(query & ({t.lower() for t in doc["tags"]}
                                   if without != "tags" else set()))
                + 1 * len(query & tokens(doc["slug"]))
                + 1 * len(query & tokens(doc["title"]))
            )
            if doc["topic"] in stack_topics or doc["topic"] in term_topics:
                points += 6          # the signal says which topic, not which document
            if points:
                score[doc["id"]] += points

        return [doc_id for doc_id, _ in score.most_common(TOP_N)]


# One realistic question per language, with what a repository and a diff would show.
# `expect` is satisfied when any of its documents is in the top five.
CASES: list[dict] = [
    {"name": "typescript", "task": "Turn on strict type checking for the whole project",
     "files": ["tsconfig.json"], "symbols": ["strict", "noUncheckedIndexedAccess"],
     "expect": ["typescript/16-configuration", "typescript/02-type-system"]},
    {"name": "javascript", "task": "An unhandled promise rejection crashes the process",
     "files": ["package.json"], "symbols": ["unhandledRejection"],
     "expect": ["javascript/09-promises", "nodejs/16-error-handling",
                "javascript/14-error-handling"]},
    {"name": "react", "task": "The list re-renders on every keystroke",
     "files": [], "symbols": ["useCallback", "memo"],
     "expect": ["react/12-performance", "react/11-rendering"]},
    {"name": "nextjs", "task": "Cache the product page and revalidate it after a write",
     "files": ["next.config.ts", "app/page.tsx"], "symbols": ["revalidateTag"],
     "expect": ["nextjs/10-caching"]},
    {"name": "nodejs", "task": "The service stops accepting connections under CPU load",
     "files": ["package.json"], "symbols": ["worker_threads"],
     "expect": ["nodejs/02-event-loop", "nodejs/12-worker-threads", "nodejs/19-performance"]},
    {"name": "nestjs", "task": "The API response leaks database entity fields",
     "files": ["nest-cli.json"], "symbols": ["ClassSerializerInterceptor"],
     "expect": ["nestjs/07-dto"]},
    {"name": "django", "task": "Upgrade Django without crossing an unsupported Python version",
     "files": ["manage.py", "config/settings/base.py"], "symbols": ["Django"],
     "expect": ["django/01-version-support", "django/10-upgrades"]},
    {"name": "django-n1", "task": "Stop N+1 queries when listing invoices with their owners",
     "files": ["manage.py"], "symbols": ["select_related"],
     "expect": ["django/05-querysets-and-transactions"]},
    {"name": "wagtail", "task": "Upgrade Wagtail and confirm the Django compatibility matrix",
     "files": ["manage.py", "cms/wagtail_hooks.py"], "symbols": ["Wagtail"],
     "expect": ["wagtail/01-version-compatibility", "wagtail/11-upgrades"]},
    {"name": "wagtail-publish", "task": "Publish a page from a management command",
     "files": ["manage.py", "home/templates/home/home_page.html"], "symbols": ["save_revision"],
     "expect": ["wagtail/05-revisions-and-workflows"]},
    {"name": "php", "task": "Escape user input before rendering it in a template",
     "files": ["composer.json"], "symbols": ["htmlspecialchars"],
     "expect": ["php/13-security", "security/10-output-encoding"]},
    {"name": "wordpress", "task": "A scheduled job sends the same email twice",
     "files": ["wp-config.php"], "symbols": ["wp_schedule_event"],
     "expect": ["wordpress/22-cron-and-background-tasks"]},
    {"name": "woocommerce", "task": "Add a fee at checkout without breaking tax totals",
     "files": ["wp-content/plugins/woocommerce/"], "symbols": ["woocommerce_cart_calculate_fees"],
     "expect": ["woocommerce/07-checkout", "woocommerce/10-taxes", "woocommerce/12-hooks"]},
    {"name": "divi", "task": "Style a Divi module without editing the parent theme",
     "files": ["wp-content/themes/Divi/"], "symbols": ["et_pb_section"],
     "expect": ["divi/09-custom-css", "divi/01-architecture", "divi/04-custom-modules"]},
    {"name": "sql", "task": "The join returns duplicate rows after adding a table",
     "files": [], "symbols": ["LEFT JOIN", "GROUP BY"],
     "expect": ["sql/05-joins", "sql/04-grouping"]},
    {"name": "postgresql", "task": "Autovacuum is not keeping up on a large table",
     "files": [], "symbols": ["autovacuum_freeze_max_age"],
     "expect": ["postgresql/20-vacuum"]},
    {"name": "mysql", "task": "Choose a storage engine and character set for a new table",
     "files": [], "symbols": ["InnoDB", "utf8mb4"],
     "expect": ["mysql/08-storage-engines", "mysql/03-data-types", "mysql/02-configuration"]},
    {"name": "prisma", "task": "Connection pool exhausted in a serverless deployment",
     "files": ["prisma/schema.prisma"], "symbols": ["PrismaClient"],
     "expect": ["prisma/06-client", "prisma/25-production"]},
    {"name": "redis", "task": "Two workers process the same job at once",
     "files": [], "symbols": ["SETNX", "EVAL"],
     "expect": ["redis/17-distributed-locks", "redis/11-lua-scripting"]},
    {"name": "graphql", "task": "One query fires a database call per item in a list",
     "files": ["schema.graphql"], "symbols": ["DataLoader"],
     "expect": ["graphql/16-dataloader", "graphql/15-n1-problem"]},
    {"name": "rest-api", "task": "Which status code should a create endpoint return",
     "files": ["openapi.yaml"], "symbols": ["Location"],
     "expect": ["rest-api/07-status-codes", "rest-api/03-resource-design"]},
    {"name": "html", "task": "Mark up a form so the labels are announced",
     "files": [], "symbols": ["autocomplete", "fieldset"],
     "expect": ["html/08-forms", "accessibility/08-forms"]},
    {"name": "css", "task": "An override keeps losing to another rule",
     "files": [], "symbols": ["specificity", "!important"],
     "expect": ["css/03-specificity", "css/02-selectors"]},
    {"name": "tailwind", "task": "Support dark mode without duplicating every class",
     "files": ["tailwind.config.ts"], "symbols": ["prefers-color-scheme"],
     "expect": ["tailwind/12-dark-mode", "tailwind/16-theme"]},
    {"name": "docker", "task": "The image is 1 GB and ships the compiler",
     "files": ["Dockerfile"], "symbols": ["HEALTHCHECK"],
     "expect": ["docker/11-multi-stage-builds", "docker/09-image-optimization",
                "docker/08-dockerfile"]},
    {"name": "kubernetes", "task": "Pods are OOM killed under load",
     "files": ["k8s/deployment.yaml"], "symbols": ["OOMKilled"],
     "expect": ["kubernetes/19-resource-management", "kubernetes/20-autoscaling"]},
    {"name": "nginx", "task": "Requests to the upstream time out behind the proxy",
     "files": ["nginx.conf"], "symbols": ["proxy_pass", "proxy_read_timeout"],
     "expect": ["nginx/05-reverse-proxy", "nginx/19-proxying-applications"]},
    {"name": "linux", "task": "A shell script keeps running after a command fails",
     "files": [], "symbols": ["set -euo pipefail"],
     "expect": ["linux/03-bash", "linux/24-scripting"]},
    {"name": "terraform", "task": "Terraform wants to replace the load balancer",
     "files": ["main.tf"], "symbols": ["aws_lb_target_group"],
     "expect": ["devops/08-infrastructure-as-code", "aws/10-elastic-load-balancer"]},
    {"name": "aws", "task": "Give a service the least IAM permission it needs",
     "files": [], "symbols": ["AssumeRole", "iam"],
     "expect": ["aws/02-iam", "aws/25-security"]},
    {"name": "proxy", "task": "Redirect unauthenticated requests before the route renders",
     "files": ["proxy.ts", "app/page.tsx"], "symbols": ["NextResponse.redirect", "matcher"],
     "expect": ["nextjs/13-proxy", "nextjs/14-authentication"]},
    # Topics an agent reaches by task shape rather than by stack: process, playbooks,
    # templates, and the worked examples. Without these ten, a fifth of the base was
    # never exercised by any probe.
    {"name": "ai", "task": "The generated code works but does not look like the rest of the codebase",
     "files": [], "symbols": [],
     "expect": ["ai/03-code-generation", "ai/01-context-gathering"]},
    {"name": "checklists", "task": "We put this in front of real users next week — what must be verified first",
     "files": [], "symbols": [],
     "expect": ["checklists/01-pre-launch"]},
    {"name": "engineering", "task": "The defect reproduces but I cannot find where it originates",
     "files": [], "symbols": [],
     "expect": ["engineering/03-debugging-methodology"]},
    {"name": "examples", "task": "Implement a REST endpoint end to end: contract, validation, service, tests",
     "files": [], "symbols": [],
     "expect": ["examples/01-rest-endpoint"]},
    {"name": "figma", "task": "Turn this Figma frame into a component that holds up across breakpoints",
     "files": [], "symbols": ["Auto Layout"],
     "expect": ["figma/05-responsive-analysis", "figma/01-figma-analysis", "figma/02-layout-analysis"]},
    {"name": "playbooks", "task": "The application is unreachable and returning 502 for everyone",
     "files": [], "symbols": [],
     "expect": ["playbooks/01-site-down"]},
    {"name": "prompts", "task": "Draft the instruction to give an assistant that is reviewing a diff",
     "files": [], "symbols": [],
     "expect": ["prompts/01-code-review"]},
    {"name": "snippets", "task": "Format money for display without floating point rounding error",
     "files": [], "symbols": ["Intl.NumberFormat"],
     "expect": ["snippets/01-typescript-utilities"]},
    {"name": "templates", "task": "Record a decision that is expensive to reverse so it is not relitigated",
     "files": [], "symbols": [],
     "expect": ["templates/02-architecture-decision-record", "architecture/26-architecture-decision-records"]},
    {"name": "tools", "task": "Pin the Node version so CI and a laptop build the same thing",
     "files": [".nvmrc"], "symbols": ["engines"],
     "expect": ["tools/02-version-management", "tools/01-package-managers"]},
    {"name": "cicd", "task": "Block the merge when tests fail",
     "files": [".github/workflows/ci.yml"], "symbols": [],
     "expect": ["cicd/05-quality-gates", "github/08-actions", "github/09-workflows",
                "cicd/17-github-actions"]},
    {"name": "github-workflows", "task": "Pin Actions, bound the job, and cancel superseded runs",
     "files": [".github/workflows/ci.yml"], "symbols": ["timeout-minutes", "cancel-in-progress"],
     "expect": ["github/09-workflows", "cicd/17-github-actions", "github/08-actions"]},
    {"name": "pg-migration", "task": "Add a required status column on a large write-heavy PostgreSQL table without a blocking validation",
     "files": ["migrations/001_orders_status.sql"], "symbols": ["NOT VALID", "lock_timeout"],
     "expect": ["postgresql/22-migrations", "databases/17-migrations"]},
    {"name": "nextjs-pages", "task": "Keep the Pages Router app running while planning the App Router move",
     "files": ["pages/_app.tsx"], "symbols": [],
     "expect": ["nextjs/30-migration-guide"]},
    {"name": "redis-lock-file", "task": "Worker A deletes Worker B's Redis lock after its lease expires",
     "files": ["src/lock.ts"], "symbols": ["randomUUID", "eval"],
     "expect": ["redis/17-distributed-locks"]},
    {"name": "git", "task": "Undo a commit that is already pushed",
     "files": [], "symbols": ["git revert", "reflog"],
     "expect": ["git/10-revert", "git/19-reflog", "git/09-reset"]},
    {"name": "testing", "task": "A test passes locally and fails in CI at random",
     "files": ["tests/app.spec.ts"], "symbols": ["useFakeTimers"],
     "expect": ["testing/22-flaky-tests"]},
    {"name": "security", "task": "Store user passwords for a new login endpoint",
     "files": [], "symbols": ["argon2"],
     "expect": ["security/05-password-security", "security/03-authentication",
                "nestjs/15-authentication", "nextjs/14-authentication"]},
    {"name": "accessibility", "task": "A screen reader does not announce the error message",
     "files": [], "symbols": ["aria-describedby", "role"],
     "expect": ["accessibility/18-error-messages", "accessibility/07-aria",
                "accessibility/08-forms"]},
    {"name": "performance", "task": "Largest Contentful Paint regressed after a release",
     "files": [], "symbols": ["fetchpriority"],
     "expect": ["performance/18-web-vitals", "performance/11-images",
                "performance/07-loading"]},
    # No repository files and no diff: the term named in the question is the only
    # evidence there is. Without a case like this the term lookup is machinery that
    # never has to work.
    {"name": "csp", "task": "The Content Security Policy blocks an inline script",
     "files": [], "symbols": [],
     "expect": ["security/20-csp", "security/22-security-headers", "frontend/14-security"]},
    {"name": "seo", "task": "Product pages dropped out of the index",
     "files": [], "symbols": ["robots.txt", "canonical"],
     "expect": ["seo/03-indexing", "seo/08-robots-txt", "seo/06-canonicalization"]},
    {"name": "python", "task": "Structure logging for a service so failures are searchable",
     "files": [], "symbols": ["structlog", "logging"],
     "expect": ["devops/14-logging", "nodejs/17-logging", "aws/14-cloudwatch"]},
    {"name": "go", "task": "The trace ends at the database call instead of continuing",
     "files": [], "symbols": ["context.Background", "tracer"],
     "expect": ["devops/13-observability", "architecture/18-observability"]},
    {"name": "lua", "task": "Make a check-and-set on Redis atomic",
     "files": [], "symbols": ["EVAL", "redis.call"],
     "expect": ["redis/11-lua-scripting", "redis/17-distributed-locks"]},
    {"name": "frontend", "task": "Where should form state live in the component tree",
     "files": [], "symbols": ["useState"],
     "expect": ["frontend/04-state-management", "react/06-state", "react/15-forms"]},
    {"name": "backend", "task": "Two writes must both succeed or neither",
     "files": [], "symbols": ["transaction"],
     "expect": ["backend/17-transactions", "databases/09-transactions",
                "nestjs/18-transactions"]},
    {"name": "architecture", "task": "Split a monolith without distributing the database",
     "files": [], "symbols": [],
     "expect": ["architecture/10-modular-monolith", "architecture/09-microservices"]},
    {"name": "workflow", "task": "How do I investigate a production bug end to end",
     "files": [], "symbols": [],
     "expect": ["workflows/06-investigate-production-bug", "workflows/02-fix-a-bug"]},
]


def main(argv: list[str]) -> int:
    explain = "--why" in argv[1:]
    wanted = [a for a in argv[1:] if not a.startswith("-")]
    cases = [c for c in CASES if not wanted or any(w in c["name"] for w in wanted)]
    if not cases:
        print(f"no case matches {wanted}")
        return 2

    protocol = Protocol()
    misses = []
    for case in cases:
        found = protocol.retrieve(case["task"], case["files"], case["symbols"])
        hit = set(case["expect"]) & set(found)
        print(f"  {'ok  ' if hit else 'MISS'}  {case['name']:<14} {case['task'][:48]}")
        if hit and explain:
            carried = [
                source for source in ("stack", "symbols", "terms", "when_to_use",
                                      "tags", "task")
                if not set(case["expect"]) & set(protocol.retrieve(
                    case["task"], case["files"], case["symbols"], without=source))
            ]
            print(f"          via    : {', '.join(carried) or 'nothing — redundant evidence'}"
                  f"  ->  {sorted(set(case['expect']) & set(found))[0]}")
        if not hit:
            print(f"          reached: {', '.join(found) or '(nothing)'}")
            print(f"          wanted : {', '.join(case['expect'])}")
            misses.append(case["name"])

    if "--ablate" in argv[1:]:
        print("\n  How much each source of evidence is worth, across all "
              f"{len(cases)} questions:\n")
        for source in ("stack", "symbols", "terms", "when_to_use", "tags", "task"):
            kept = sum(
                bool(set(c["expect"]) & set(protocol.retrieve(
                    c["task"], c["files"], c["symbols"], without=source)))
                for c in cases
            )
            print(f"    without {source:<12} {kept}/{len(cases)} still reach the rule"
                  f"   (-{len(cases) - kept})")

    print()
    if misses:
        print(f"MISS: {len(misses)} of {len(cases)} questions did not reach their rule")
        print("The protocol is what agents follow — fix the metadata, not this test.")
        return 1
    print(f"OK: all {len(cases)} questions reached a document that states the rule.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
