---
id: github/23-cli
topic: github
slug: cli
title: "GitHub CLI"
type: doc
order: 23
status: ready
tags: [github, cli, GH_TOKEN, GITHUB_TOKEN, scripting, tasks, inside]
related: [github/22-api, github/26-automation, github/08-actions, github/06-pull-requests, github/21-permissions]
when_to_use: "Read before scripting with the gh CLI, automating GitHub tasks in shell, or using gh inside Actions."
---
# GitHub CLI

## Purpose

This document defines how to use the GitHub **CLI** (`gh`) to script GitHub operations —
pull requests, issues, releases, and raw [API](22-api.md) calls — reliably from a shell.
It is written so an agent can write automation that is deterministic, machine-parseable,
and safe to run unattended in CI.

`gh` is a thin, authenticated wrapper over the API with high-level commands (`gh pr`,
`gh issue`, `gh release`) and a raw escape hatch (`gh api`). It handles auth, pagination,
and JSON output so scripts do not have to reimplement them.

## Why It Matters

CLI one-liners graduate into CI pipelines, and a script that "worked on my machine"
breaks unattended in ways a human would have caught: it parses human-formatted output
that changes format, it reads only the first page of results, or it prompts for
confirmation and hangs a job forever. Because `gh` runs with a real token, a careless
script also carries that token's [permissions](21-permissions.md). Treat CLI automation
with the same rigor as API code — it *is* API code with a friendlier surface.

## Core Principles

- **Parse JSON, never human output.** Use `--json <fields>` (and `--jq`) for structured,
  stable output. Scraping the default pretty output breaks when formatting changes.
- **Make it non-interactive.** In scripts and CI, pass every answer as a flag and add
  `--yes`/`-y` where destructive prompts exist. An unexpected prompt hangs the job.
- **Authenticate explicitly and least-privilege.** In CI, set `GH_TOKEN`
  (`GITHUB_TOKEN`) from a secret; locally, `gh auth login`. Scope the token to the task.
- **Reach for `gh api` when a subcommand cannot.** It gives full REST/GraphQL access with
  auth handled, including `--paginate` to fetch all pages.
- **Fail loudly.** `gh` exits non-zero on error; run with `set -euo pipefail` so a failed
  call stops the script instead of continuing on stale data.

## Best Practices

- Emit structured data with `--json` and filter with `--jq` in one call, so parsing is
  robust and no second process is needed.
- In pipelines set `GH_TOKEN` from a secret and pin behavior with env vars
  (`GH_PROMPT_DISABLED=1` / `--no-prompt` patterns) so nothing blocks on input.
- Use `gh api --paginate` for list endpoints; the plain command returns one page and will
  silently undercount, just like a naive [API](22-api.md) client.
- Prefer high-level commands (`gh pr create`, `gh release create`) for readability; drop
  to `gh api` only for what they do not cover.
- Pin the `gh` version in CI (or use the runner's provided version deliberately) so a CLI
  upgrade does not change flag behavior mid-pipeline.
- Package repeated logic as a **`gh extension`** rather than copy-pasting shell across
  repos.

## Examples

**Good Example** — non-interactive, JSON-parsed, paginated

```bash
set -euo pipefail                 # any failed gh call aborts the script
export GH_TOKEN="$CI_GITHUB_TOKEN"  # scoped token from CI secret, not interactive login

# Structured output + jq filter: stable regardless of gh's pretty formatting.
open_count=$(gh pr list --repo acme/billing --state open \
  --json number --jq 'length')
echo "open PRs: $open_count"

# --paginate fetches ALL pages of a raw API list, not just the first.
gh api --paginate /repos/acme/billing/issues \
  --jq '.[] | select(.labels[].name=="bug") | .number'
```

**Bad Example** — interactive, scrapes text, one page only

```bash
# No token set → gh may prompt for login and hang the CI job.
# Grepping human output: breaks the moment gh changes its table format.
gh pr list --repo acme/billing | grep -c OPEN     # counts a formatting word, not PRs

# Missing --paginate: silently returns only the first page of issues.
gh api /repos/acme/billing/issues | jq 'length'   # undercounts, no error raised

gh release delete v1.2.3                           # prompts for confirmation → hangs
```

## Common Mistakes

- Grepping or `awk`-ing the human-readable output instead of using `--json`/`--jq`.
- Forgetting `--paginate` on `gh api` list calls and processing only the first page.
- Running destructive commands without `--yes`, so CI hangs on a confirmation prompt.
- Not setting `GH_TOKEN` in CI, causing an interactive login prompt or an auth failure.
- Omitting `set -euo pipefail`, so a failed `gh` call is ignored and the script proceeds
  on empty or stale data.
- Reimplementing API pagination and retry in shell when `gh api --paginate` already does it.

## Production Tips

- In GitHub Actions, `gh` is preinstalled and reads `GH_TOKEN` from `env` — pass the
  workflow's scoped `secrets.GITHUB_TOKEN`, not a personal PAT.
- Use `gh api --method` with `-f`/`-F` for typed fields when a subcommand is missing;
  `-F` sends non-string types and reads `@file` bodies.
- Log the `gh --version` at the top of CI jobs so behavior changes are traceable.

## AI Review Checklist

- Does the script parse `--json`/`--jq` output rather than scraping human text?
- Are all interactive prompts suppressed with flags/`--yes` for unattended runs?
- Is `GH_TOKEN` set from a scoped secret in CI, not an interactive login?
- Do `gh api` list calls use `--paginate` to fetch every page?
- Is the script run under `set -euo pipefail` so failed calls abort it?
- Is the `gh` version pinned or deliberately chosen for stable flag behavior?

## Related

- `knowledge/github/22-api.md`
- `knowledge/github/26-automation.md`
- `knowledge/github/08-actions.md`
- `knowledge/github/06-pull-requests.md`
- `knowledge/github/21-permissions.md`
