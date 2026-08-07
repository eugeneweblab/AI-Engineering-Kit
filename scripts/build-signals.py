#!/usr/bin/env python3
"""Build knowledge/SIGNALS.json — what to read based on what the repository contains.

INDEX.json answers "which documents exist". This answers the question an agent has
*before* that one: given this repository and this diff, which rules apply at all?

Two lookups:

  stack   a file or directory that identifies a stack or a variant within it —
          `app/` vs `pages/`, a theme with `theme.json` vs one without. Curated
          below, because "which files mean which variant" is judgement, not data.

  symbols an inverted index of every API name, directive, and configuration key
          appearing in a document's code, so a symbol in a diff (`revalidateTag`,
          `switch_to_blog`, `argon2`) resolves to the documents that govern it.

          Built from the documents themselves rather than from their `tags`: `tags`
          carries a handful of headline symbols for a human, and indexing only those
          left most of the base unreachable — `argon2` appears in seven documents and
          resolved to none.

Run from repo root:  python3 scripts/build-signals.py
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KB = ROOT / "knowledge"
FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)

# Each entry: what to look for, what it means, and which documents govern it.
# `absent` narrows a match — the same file means different things with and without
# a sibling, which is exactly the variant question an agent needs answered.
STACK_SIGNALS: list[dict] = [
    # --- JavaScript / TypeScript applications -------------------------------
    {"when": "next.config.*", "means": "Next.js application",
     "docs": ["nextjs/01-architecture", "nextjs/28-best-practices"]},
    {"when": "app/page.tsx|app/**/page.tsx", "variant": "app-router", "means": "Next.js App Router — the current model",
     "docs": ["nextjs/03-app-router", "nextjs/06-server-components", "nextjs/10-caching"]},
    {"when": "pages/_app.tsx", "variant": "pages-router", "means": "Next.js Pages Router — legacy; do not extend it",
     "docs": ["nextjs/30-migration-guide", "nextjs/03-app-router"]},
    # `middleware.ts` is the deprecated spelling of the same file. Both point at
    # the same rules, which is where the rename is explained.
    {"when": "proxy.ts|proxy.js|src/proxy.ts|src/proxy.js|middleware.ts|middleware.js|src/middleware.ts|src/middleware.js",
     "means": "Next.js Proxy (formerly Middleware) — runs in front of every matched route",
     "docs": ["nextjs/13-proxy", "nextjs/14-authentication"]},
    {"when": "nest-cli.json", "means": "NestJS service",
     "docs": ["nestjs/01-architecture", "nestjs/02-modules"]},
    {"when": "prisma/schema.prisma", "variant": "prisma", "means": "Prisma is the ORM",
     "docs": ["prisma/02-schema", "prisma/06-client", "prisma/05-migrations"]},
    {"when": "ormconfig.*|*.entity.ts|**/*.entity.ts", "variant": "typeorm", "means": "TypeORM is the ORM",
     "docs": ["nestjs/17-database", "nestjs/06-repositories"]},
    {"when": "tsconfig.json", "means": "TypeScript project",
     "docs": ["typescript/16-configuration", "typescript/02-type-system"]},
    {"when": "tailwind.config.*", "means": "Tailwind CSS",
     "docs": ["tailwind/16-theme", "tailwind/21-design-system"]},
    {"when": "vite.config.*", "means": "Vite build",
     "docs": ["tools/09-vite"]},
    {"when": "webpack.config.*", "means": "Webpack build",
     "docs": ["tools/10-webpack"]},
    {"when": "playwright.config.*", "means": "Playwright end-to-end tests",
     "docs": ["tools/14-playwright", "testing/04-e2e-testing"]},
    {"when": "vitest.config.*|jest.config.*", "means": "unit test runner",
     "docs": ["tools/13-test-runners", "testing/02-unit-testing"]},
    {"when": "pnpm-workspace.yaml|turbo.json|nx.json", "means": "monorepo",
     "docs": ["tools/18-monorepo-tools", "git/24-monorepo"]},

    # --- PHP / WordPress ----------------------------------------------------
    {"when": "composer.json", "means": "PHP project",
     "docs": ["php/07-composer", "php/24-psr-standards"]},
    {"when": "wp-config.php", "means": "WordPress site",
     "docs": ["wordpress/01-wordpress-architecture", "wordpress/03-best-practices"]},
    {"when": "wp-content/themes/*/theme.json", "variant": "block-theme", "means": "WordPress block theme",
     "docs": ["wordpress/17-block-themes", "wordpress/16-block-editor"]},
    {"when": "wp-content/themes/*/functions.php", "absent": "wp-content/themes/*/theme.json",
     "variant": "classic-theme",
     "means": "WordPress classic theme — the template hierarchy governs",
     "docs": ["wordpress/13-template-hierarchy", "wordpress/14-theme-development"]},
    {"when": "wp-content/plugins/woocommerce/", "means": "WooCommerce store",
     "docs": ["woocommerce/01-architecture", "woocommerce/16-security"]},
    {"when": "wp-content/themes/Divi/|wp-content/themes/*/style.css:Template: Divi",
     "variant": "classic-theme",
     "means": "Divi builder — assumes a classic theme",
     "docs": ["divi/01-architecture", "divi/04-custom-modules"]},

    # --- Infrastructure and delivery ----------------------------------------
    {"when": "Dockerfile", "means": "container image is built here",
     "docs": ["docker/08-dockerfile", "docker/11-multi-stage-builds", "docker/18-security"]},
    {"when": "docker-compose.y*ml", "means": "Compose-orchestrated services",
     "docs": ["docker/12-docker-compose", "docker/13-environment-variables"]},
    {"when": "kustomization.yaml|**/kustomization.yaml|Chart.yaml|**/Chart.yaml|k8s/*.y*ml|k8s/**/*.y*ml|**/k8s/*.y*ml",
     "means": "Kubernetes workloads",
     "docs": ["kubernetes/05-deployments", "kubernetes/19-resource-management",
              "kubernetes/22-security"]},
    {"when": ".github/workflows/*.y*ml", "means": "GitHub Actions pipeline",
     "docs": ["github/08-actions", "cicd/02-pipeline-design", "cicd/06-security-scanning"]},
    {"when": ".gitlab-ci.yml", "means": "GitLab CI pipeline",
     "docs": ["cicd/18-gitlab-ci", "cicd/02-pipeline-design"]},
    {"when": "*.tf|**/*.tf", "means": "Terraform — infrastructure as code",
     "docs": ["devops/08-infrastructure-as-code", "devops/09-configuration-management"]},
    {"when": "nginx.conf|**/nginx.conf|**/sites-available/*|**/conf.d/*.conf", "means": "Nginx configuration",
     "docs": ["nginx/03-server-blocks", "nginx/05-reverse-proxy", "nginx/13-security"]},

    # --- Data and APIs ------------------------------------------------------
    {"when": "*.graphql|**/*.graphql|schema.gql|**/schema.gql", "means": "GraphQL schema",
     "docs": ["graphql/02-schema", "graphql/17-security", "graphql/15-n1-problem"]},
    {"when": "openapi.y*ml|**/openapi.y*ml|swagger.y*ml|**/swagger.y*ml", "means": "documented HTTP API",
     "docs": ["rest-api/21-openapi", "rest-api/03-resource-design"]},
    {"when": "migrations/*|**/migrations/*", "means": "versioned schema changes",
     "docs": ["databases/17-migrations", "sql/12-ddl"]},

    # --- Cross-cutting ------------------------------------------------------
    {"when": ".env|.env.example", "means": "environment-based configuration",
     "docs": ["security/16-secrets-management", "nodejs/15-configuration"]},
    {"when": "*.test.ts|**/*.test.ts|*.spec.ts|**/*.spec.ts|tests/**", "means": "a test suite exists",
     "docs": ["testing/28-testing-strategy", "testing/22-flaky-tests"]},
]


# Representative paths each signal must recognise. `**/x` matches only when there is
# a directory in between, so a pattern written that way silently misses the root-level
# layout — `app/page.tsx` and `main.tf` matched nothing until this table was added.
PROBES: list[tuple[str, str]] = [
    ("proxy.ts", "Next.js Proxy"),
    ("src/middleware.ts", "Next.js Proxy (deprecated spelling)"),
    ("app/page.tsx", "app-router"),
    ("app/products/[id]/page.tsx", "app-router"),
    ("pages/_app.tsx", "pages-router"),
    ("main.tf", "Terraform"),
    ("infra/modules/main.tf", "Terraform"),
    ("k8s/deployment.yaml", "Kubernetes"),
    ("k8s/base/deployment.yaml", "Kubernetes"),
    ("deploy/k8s/app.yaml", "Kubernetes"),
    ("migrations/001_init.sql", "schema changes"),
    ("db/migrations/001_init.sql", "schema changes"),
    ("schema.graphql", "GraphQL"),
    ("src/schema.graphql", "GraphQL"),
    ("openapi.yaml", "HTTP API"),
    ("docs/openapi.yaml", "HTTP API"),
    ("src/user.entity.ts", "TypeORM"),
    ("wp-content/themes/acme/theme.json", "block theme"),
    ("Dockerfile", "container image"),
    (".github/workflows/ci.yml", "GitHub Actions"),
]


def unmatched_probes() -> list[str]:
    import fnmatch
    out = []
    for path, what in PROBES:
        if not any(
            fnmatch.fnmatch(path, pattern)
            for signal in STACK_SIGNALS
            for pattern in signal["when"].split("|")
        ):
            out.append(f"{path}  ({what})")
    return out


def frontmatter(path: Path) -> dict[str, str]:
    m = FRONTMATTER_RE.match(path.read_text(encoding="utf-8", errors="replace"))
    if not m:
        return {}
    return {
        k: v.strip()
        for k, v in re.findall(r"^([a-z_]+):\s*(.*)$", m.group(1), re.MULTILINE)
    }


SYMBOL_STOP = set("""
if else for while return function const let var new class extends import from export
default try catch finally throw await async this true false null undefined typeof
public private protected static void string number boolean any type interface enum
echo print array foreach endforeach endif isset empty require include use namespace
fn match case switch break continue do in of as is not and or the a an it its with
select insert update delete where group order by join on values create drop alter
then fi done esac elif local read source exit cd ls cp mv rm mkdir cat grep sed awk
head tail sort uniq wc find xargs npm npx node run build start dev main index src
lib app dist out tmp foo bar baz example acme myplugin data value item items result
results name title id key path file line text html body head div span error log call
console warn info debug map filter reduce find push slice split replace trim length
size count render process env args options config params props state children status
code message request response next user users order orders product products post
posts page pages event events row report handler callback helper util temp thing
""".split())

CALL_RE = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]{2,})\s*\(")
DECORATOR_RE = re.compile(r"@([A-Z][A-Za-z0-9_]{2,})")
CLASS_RE = re.compile(r"\b([A-Z][A-Za-z0-9]*(?:_[A-Z][A-Za-z0-9]*)+|[A-Z][a-z0-9]+[A-Z][A-Za-z0-9]*)\b")
CONST_RE = re.compile(r"\b([A-Z][A-Z0-9_]{3,})\b")
KEY_RE = re.compile(r"^\s*([a-z][a-z0-9_.-]{3,})\s*[:=]", re.MULTILINE)
CSS_AT_RE = re.compile(r"(@[a-z-]{3,})")
INLINE_RE = re.compile(r"`([A-Za-z_][A-Za-z0-9_.:$-]{2,})`")
# The package a document imports is itself a signal: a diff that pulls in `argon2`
# or `jose` should reach the document that governs it.
IMPORT_RE = re.compile(
    r"""(?:from|require\(|import)\s*\(?\s*['"]([@\w][\w@/.-]{2,})['"]"""
)
RECEIVER_RE = re.compile(r"\b([a-z][a-zA-Z0-9_]{2,})\.[a-zA-Z_]")
# Terms of art live in prose, not in code: LCP, CLS, IAM, JWT, CSP, OOM. They are
# what a person types, and indexing only code left every one of them resolving to
# nothing. A mention threshold keeps the index pointing at the documents a term is
# actually about rather than every document that names it once.
ACRONYM_RE = re.compile(r"\b([A-Z][A-Z0-9]{1,7})\b")
ACRONYM_MENTIONS = 3
ACRONYM_STOP = {"AND", "OR", "NOT", "THE", "FOR", "ALL", "ANY", "NEW", "GET", "SET",
                "PUT", "ADD", "RUN", "USE", "TODO", "FIXME", "NOTE", "OK", "NO",
                "YES", "ID", "URL", "URI", "API", "APIS", "CI", "CD", "UI", "UX",
                "HTTP", "HTTPS", "JSON", "YAML", "XML", "HTML", "CSS", "SQL", "PHP",
                "AWS", "GET", "POST", "PATCH", "HEAD", "BAD", "GOOD", "WHY"}
# A person asks about "Largest Contentful Paint", not `LCP`. The base already glosses
# its acronyms on first use, so the expansions can be read out of the corpus itself
# rather than kept as a hand-written list that would drift. The initials check is what
# keeps this honest: only a phrase whose trailing words spell the acronym is accepted.
GLOSS_RE = re.compile(
    r"\b((?:[A-Z][\w-]*|to|of|the|and|for|in|on)"
    r"(?:[ -](?:[A-Z][\w-]*|to|of|the|and|for|in|on)){1,5})\s+\(([A-Z]{2,6})s?\)"
)
FENCE_RE = re.compile(r"^```[a-zA-Z0-9_+.-]*\s*$\n(.*?)^```\s*$", re.DOTALL | re.MULTILINE)
BAD_AT_RE = re.compile(
    r"^@(param|return|returns|var|throws|see|since|deprecated|example|inheritdoc|"
    r"nestjs|apollo|types|testing-library|playwright|prisma|acme|wordpress)$", re.IGNORECASE
)


def glossary(bodies: list[str]) -> dict[str, str]:
    """Acronym -> spelled-out term, harvested from the base's own first-use glosses."""
    found: dict[str, str] = {}
    for body in bodies:
        prose = re.sub(r"```.*?```", " ", body, flags=re.DOTALL)
        for phrase, acronym in GLOSS_RE.findall(prose):
            words = [w for w in re.split(r"[ -]", phrase) if w]
            # Which suffix of the phrase is the term, and whether a connector counts
            # toward the acronym, both vary: "Time to First Byte" is TTFB but
            # "Interaction to Next Paint" is INP. Accept the shortest suffix that
            # spells the acronym under either reading.
            for start in range(len(words) - 1, -1, -1):
                tail = words[start:]
                spelled = "".join(w[0] for w in tail).upper()
                kept = "".join(w[0] for w in tail if w[0].isupper()).upper()
                if acronym in (spelled, kept):
                    found.setdefault(acronym, " ".join(tail).lower())
                    break
    return found


def document_symbols(body: str, expansions: dict[str, str] | None = None) -> set[str]:
    """Every identifier a document's code actually names."""
    code = "\n".join(FENCE_RE.findall(body))
    prose = re.sub(r"```.*?```", " ", body, flags=re.DOTALL)
    found: set[str] = set()
    for pattern in (CALL_RE, DECORATOR_RE, CLASS_RE, CONST_RE, KEY_RE, RECEIVER_RE):
        found.update(pattern.findall(code))
    for module in IMPORT_RE.findall(code):
        found.add(module)
        found.add(module.rsplit("/", 1)[-1])   # `@nestjs/common` -> `common`
    found.update(s for s in CSS_AT_RE.findall(code) if not BAD_AT_RE.match(s))
    found.update(INLINE_RE.findall(prose))

    mentions: dict[str, int] = {}
    for acronym in ACRONYM_RE.findall(prose):
        mentions[acronym] = mentions.get(acronym, 0) + 1
    found.update(
        a for a, count in mentions.items()
        if count >= ACRONYM_MENTIONS and a not in ACRONYM_STOP
    )

    if expansions:
        lowered = prose.lower()
        for acronym, phrase in expansions.items():
            # The spelled-out term earns its place the same way the acronym does:
            # by being what the document is about, not by being named once in an
            # aside. Mentions of either form count toward the one threshold.
            if lowered.count(phrase) + mentions.get(acronym, 0) >= ACRONYM_MENTIONS:
                found.add(phrase)

    return {
        s for s in found
        if len(s) >= 3 and s.lower() not in SYMBOL_STOP and not s.isdigit()
    }


def main() -> int:
    symbols: dict[str, list[str]] = {}

    indexable: list[tuple[str, str, str, str]] = []
    for path in sorted(KB.rglob("*.md")):
        fm = frontmatter(path)
        if not fm or fm.get("status") != "ready":
            continue
        # Only documents that state a rule. READMEs and `00` are indexes; `98`/`99`
        # are verification lists already reachable through their **Rules:** pointers.
        if path.name == "README.md" or path.name.startswith(("00-", "98-", "99-")):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        indexable.append((
            fm.get("id", ""), FRONTMATTER_RE.sub("", text, count=1),
            fm.get("topic", ""), fm.get("slug", ""),
        ))
    doc_count = len(indexable)
    expansions = glossary([body for _, body, _, _ in indexable])

    for doc_id, body, topic, slug in indexable:
        for symbol in document_symbols(body, expansions):
            if symbol in (topic, slug):     # already reachable via topic/slug
                continue
            symbols.setdefault(symbol, []).append(doc_id)

    # A symbol present across a large share of the base identifies nothing in
    # particular. Keep the ones that point somewhere.
    ceiling = max(12, doc_count // 12)
    symbols = {s: ids for s, ids in symbols.items() if len(set(ids)) <= ceiling}

    unmatched = unmatched_probes()
    if unmatched:
        print("error: a stack signal does not recognise a representative path:")
        for u in unmatched:
            print(f"  {u}")
        return 1

    missing = [
        f"{s['when']} -> {d}"
        for s in STACK_SIGNALS for d in s["docs"]
        if not (KB / f"{d}.md").exists()
    ]
    if missing:
        print("error: stack signal points at a document that does not exist:")
        for m in missing:
            print(f"  {m}")
        return 1

    out = {
        "schema": "ai-engineering-kit/signals@1",
        "note": (
            "Detect the stack from `stack`, then resolve any symbol in the diff via "
            "`symbols`. Both point at document ids in INDEX.json. In `when`, `|` "
            "separates alternatives and `**` matches any number of directories; a "
            "pattern is written to match both the root-level and the nested layout."
        ),
        "stats": {
            "stack_signals": len(STACK_SIGNALS),
            "symbols": len(symbols),
            "docs_indexed": doc_count,
        },
        "stack": STACK_SIGNALS,
        "symbols": {k: sorted(set(v)) for k, v in sorted(symbols.items())},
    }
    (KB / "SIGNALS.json").write_text(
        json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(
        f"SIGNALS.json: {len(STACK_SIGNALS)} stack signals, "
        f"{len(symbols)} symbols from {doc_count} docs."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
