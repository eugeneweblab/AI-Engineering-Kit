#!/usr/bin/env python3
"""Build knowledge/SIGNALS.json — what to read based on what the repository contains.

INDEX.json answers "which documents exist". This answers the question an agent has
*before* that one: given this repository and this diff, which rules apply at all?

Two lookups:

  stack   a file or directory that identifies a stack or a variant within it —
          `app/` vs `pages/`, a theme with `theme.json` vs one without. Curated
          below, because "which files mean which variant" is judgement, not data.

  symbols an inverted index of every doc's `tags`, so a symbol appearing in a diff
          (`revalidateTag`, `switch_to_blog`, `autovacuum_freeze_max_age`) resolves
          to the documents that state the rules for it.

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
    {"when": "app/**/page.tsx", "means": "Next.js App Router — the current model",
     "docs": ["nextjs/03-app-router", "nextjs/06-server-components", "nextjs/10-caching"]},
    {"when": "pages/_app.tsx", "means": "Next.js Pages Router — legacy; do not extend it",
     "docs": ["nextjs/30-migration-guide", "nextjs/03-app-router"]},
    {"when": "nest-cli.json", "means": "NestJS service",
     "docs": ["nestjs/01-architecture", "nestjs/02-modules"]},
    {"when": "prisma/schema.prisma", "means": "Prisma is the ORM",
     "docs": ["prisma/02-schema", "prisma/06-client", "prisma/05-migrations"]},
    {"when": "ormconfig.*|**/*.entity.ts", "means": "TypeORM is the ORM",
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
    {"when": "wp-content/themes/*/theme.json", "means": "WordPress block theme",
     "docs": ["wordpress/17-block-themes", "wordpress/16-block-editor"]},
    {"when": "wp-content/themes/*/functions.php", "absent": "wp-content/themes/*/theme.json",
     "means": "WordPress classic theme — the template hierarchy governs",
     "docs": ["wordpress/13-template-hierarchy", "wordpress/14-theme-development"]},
    {"when": "wp-content/plugins/woocommerce/", "means": "WooCommerce store",
     "docs": ["woocommerce/01-architecture", "woocommerce/16-security"]},
    {"when": "wp-content/themes/Divi/|wp-content/themes/*/style.css:Template: Divi",
     "means": "Divi builder — assumes a classic theme",
     "docs": ["divi/01-architecture", "divi/04-custom-modules"]},

    # --- Infrastructure and delivery ----------------------------------------
    {"when": "Dockerfile", "means": "container image is built here",
     "docs": ["docker/08-dockerfile", "docker/11-multi-stage-builds", "docker/18-security"]},
    {"when": "docker-compose.y*ml", "means": "Compose-orchestrated services",
     "docs": ["docker/12-docker-compose", "docker/13-environment-variables"]},
    {"when": "**/kustomization.yaml|**/Chart.yaml|k8s/**/*.yaml",
     "means": "Kubernetes workloads",
     "docs": ["kubernetes/05-deployments", "kubernetes/19-resource-management",
              "kubernetes/22-security"]},
    {"when": ".github/workflows/*.y*ml", "means": "GitHub Actions pipeline",
     "docs": ["github/08-actions", "cicd/02-pipeline-design", "cicd/06-security-scanning"]},
    {"when": ".gitlab-ci.yml", "means": "GitLab CI pipeline",
     "docs": ["cicd/18-gitlab-ci", "cicd/02-pipeline-design"]},
    {"when": "**/*.tf", "means": "Terraform — infrastructure as code",
     "docs": ["devops/08-infrastructure-as-code", "devops/09-configuration-management"]},
    {"when": "nginx.conf|**/sites-available/*", "means": "Nginx configuration",
     "docs": ["nginx/03-server-blocks", "nginx/05-reverse-proxy", "nginx/13-security"]},

    # --- Data and APIs ------------------------------------------------------
    {"when": "**/*.graphql|**/schema.gql", "means": "GraphQL schema",
     "docs": ["graphql/02-schema", "graphql/17-security", "graphql/15-n1-problem"]},
    {"when": "**/openapi.y*ml|**/swagger.y*ml", "means": "documented HTTP API",
     "docs": ["rest-api/21-openapi", "rest-api/03-resource-design"]},
    {"when": "**/migrations/*", "means": "versioned schema changes",
     "docs": ["databases/17-migrations", "sql/12-ddl"]},

    # --- Cross-cutting ------------------------------------------------------
    {"when": ".env|.env.example", "means": "environment-based configuration",
     "docs": ["security/16-secrets-management", "nodejs/15-configuration"]},
    {"when": "**/*.test.ts|**/*.spec.ts|tests/**", "means": "a test suite exists",
     "docs": ["testing/28-testing-strategy", "testing/22-flaky-tests"]},
]


def frontmatter(path: Path) -> dict[str, str]:
    m = FRONTMATTER_RE.match(path.read_text(encoding="utf-8", errors="replace"))
    if not m:
        return {}
    return {
        k: v.strip()
        for k, v in re.findall(r"^([a-z_]+):\s*(.*)$", m.group(1), re.MULTILINE)
    }


def main() -> int:
    symbols: dict[str, list[str]] = {}
    doc_count = 0

    for path in sorted(KB.rglob("*.md")):
        fm = frontmatter(path)
        if not fm or fm.get("status") != "ready":
            continue
        # Only documents that state a rule. READMEs and `00` are indexes; `98`/`99`
        # are verification lists already reachable through their **Rules:** pointers.
        if path.name == "README.md" or path.name.startswith(("00-", "98-", "99-")):
            continue
        doc_count += 1
        doc_id = fm.get("id", "")
        raw = fm.get("tags", "")
        if not (raw.startswith("[") and raw.endswith("]")):
            continue
        items = [x.strip().strip("\"'") for x in raw[1:-1].split(",") if x.strip()]
        topic, slug = fm.get("topic", ""), fm.get("slug", "")
        for tag in items:
            if tag in (topic, slug):        # already reachable via topic/slug
                continue
            symbols.setdefault(tag, []).append(doc_id)

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
            "`symbols`. Both point at document ids in INDEX.json."
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
