# scripts

Maintenance scripts for the knowledge base. Run from the repo root.

## `inject-frontmatter.py`

Backfills the required YAML frontmatter into every `knowledge/<topic>/*.md` that is
missing it. Idempotent — files that already start with `---` are skipped. `status` is
set to `draft` when the body is an empty scaffold (nothing beyond the `# Title`),
otherwise `ready`.

```bash
python3 scripts/inject-frontmatter.py
```

## `build-index.py`

Reads the frontmatter of every doc and regenerates:

- `knowledge/INDEX.json` — machine-readable index (the agent entrypoint).
- `knowledge/INDEX.md` — human-readable index.

Run it after adding, renaming, or re-statusing any document.

```bash
python3 scripts/build-index.py
```

Both are safe to re-run; they only touch frontmatter and the two INDEX files.

## `build-signals.py`

Generates `knowledge/SIGNALS.json`, which answers the question an agent has *before*
"which document" — namely "which rules apply to this repository at all":

- **`stack`** — a curated list mapping a file or directory to the stack or variant it
  identifies and the documents that govern it. `app/**/page.tsx` means App Router;
  `pages/_app.tsx` means the legacy Pages Router; a theme with `theme.json` is a block
  theme, the same theme without one is classic. Which files mean which variant is
  judgement, so this list is hand-maintained here rather than derived.
- **`symbols`** — generated from every document's `tags`: an API name in a diff
  (`revalidateTag`, `switch_to_blog`, `autovacuum_freeze_max_age`) resolves to the
  documents that state its rules. READMEs, `00` overviews, and the `98`/`99`
  checklists are excluded — they index or verify rules rather than state them.

```bash
python3 scripts/build-signals.py
```

The build fails if a curated signal points at a document that does not exist, and CI
fails if the committed file is stale.

## `check-ready-not-stub.py`

Guardrail linter (read-only). Fails if any doc marked `status: ready` is actually a
stub — it contains a TODO/placeholder marker, or its body is too thin to be real
content, or it is a `type: index` doc that is thin and links nowhere. This prevents the
regression the quality audit found: empty topics marked `ready` that route agents
(which filter `INDEX.json` for ready docs) to dead ends.

```bash
python3 scripts/check-ready-not-stub.py knowledge   # exit 0 = clean, 1 = violations
```

## `check-knowledge.py`

Guardrail linter (read-only). Covers the defect classes that are not visible by
inspection:

| Check | What fails the build |
|---|---|
| structure | a standard topic missing `README`/`00`/`98`/`99`/`100`, or a gap in `01`–`30` |
| frontmatter | `id`/`topic`/`order` disagreeing with the path; empty `status`/`title`/`when_to_use`; an unknown `type`, `applies_to` variant, or a `defers_to` target that does not exist or is missing from `related` |
| duplicates | a repeated `id`, a repeated `title`, or two docs claiming the same `order` inside a topic |
| links | a markdown link, a `related:` id, or a `` `knowledge/…md` `` path that does not resolve |
| fences | an unclosed ``` fence |
| code blocks | a block that does not parse as the language its fence claims |
| tables | an unescaped `|` inside a table cell, which splits the row and misaligns the table |
| pointers | a `98`/`99` checklist that lost its `**Rules:**` section pointers |
| plan | `docs/structure/` no longer describing the tree: a topic missing from the root tree, a topic with no part in the file list, or a file listed/present without its counterpart |

Blocks are handed to the real parser for their language:

| Language | Parser | Needs |
|---|---|---|
| Python | `ast.parse` | — |
| JSON / JSONC | comment-tolerant decoder | — |
| YAML | PyYAML | `pip install pyyaml` |
| XML | ElementTree | — |
| shell | `bash -n` | — |
| PHP | `php -l` | `php` |
| JS / TS / JSX / TSX | esbuild | `npx` |
| nginx / conf | crossplane, context checks off | `pip install crossplane` |
| HCL / Terraform | python-hcl2 | `pip install python-hcl2` |
| INI | `configparser` with a synthetic section | — |
| GraphQL | graphql-core | `pip install graphql-core` |
| Dockerfile | hadolint, build-breaking codes only | `hadolint` binary |
| Go | `gofmt -e`, fragments wrapped | `go` toolchain |
| Lua | `luac -p` | `lua5.4` |
| HTTP | request/status lines, methods, status range | — |
| diff | every line carries a patch prefix | — |
| cron | five schedule fields in range, plus a command | — |
| Makefile | recipe lines indented with a tab | — |
| Redis | first token is a real Redis command | — |
| SQL | `sqlfluff lint --rules PRS` | `pip install sqlfluff` |
| HTML | html-validate (syntax rules only) | `npx` |
| CSS / SCSS | stylelint with no rules enabled | `npx` |

A language whose tool is unavailable is reported as a skip, never passed silently.
SQL uses the `postgres` dialect except in MySQL-family topics (`mysql`, `wordpress`,
`woocommerce`, `divi`), and HTML applies only the syntax rules — a Bad Example is
often invalid on purpose, but never unparseable.

```bash
python3 scripts/check-knowledge.py knowledge                  # exit 0 = clean, 1 = violations
python3 scripts/check-knowledge.py knowledge --require-tools  # a missing parser fails
python3 scripts/check-knowledge.py --skip-external            # structure/links only
```

**`--require-tools` is what CI runs.** Without it a language whose parser is missing is
skipped with a printed note and the run still exits 0 — so a silently failed install
would leave the build green while eight languages went unchecked. With it, a skip is a
failure.

### `codeblock-baseline.json`

Documentation legitimately contains code *fragments* — class-method excerpts, NestJS
parameter decorators, Bad/Good pairs that reuse a name, lists of sibling JSX elements
or function signatures. These never parse standalone and are not defects, so the PHP
and JS/TS checks ignore the blocks listed in this baseline and fail only on a *new*
failure. After intentionally adding or removing such a fragment:

```bash
python3 scripts/check-knowledge.py --update-baseline
```

Review the diff before committing: a baseline that grows without a matching fragment
is a real defect being silenced.

## `check-agent-instructions.py`

Guardrail linter (read-only) for the contract *on top of* the knowledge — the files an
agent reads first. It verifies that every entrypoint (`CLAUDE.md`, `GEMINI.md`,
`.clinerules`, Copilot, Cursor) redirects to `AGENTS.md`; that every path, link, and
`python3 scripts/…` command they name exists; that every frontmatter field they tell an
agent to match on is actually exposed in `INDEX.json`; that the metadata contract in
`AGENTS.md` lists exactly the fields documents carry; and that the documented lookups
resolve — a representative repository file reaches a document through `SIGNALS.stack`,
and a representative API name through `SIGNALS.symbols`.

This is the check that would have caught the instructions telling agents to match on
`topic` and follow `related` while `INDEX.json` exposed neither.

```bash
python3 scripts/check-agent-instructions.py
```

---

## `check-versions.py`

Fails the build when a document recommends a runtime that has reached end of life.

This is the only defect class here that appears without anyone editing a file — the
document is fine, the calendar moved. Three separate audits each found it by hand:
"Redis 7.x is the current stable line as of 2026" after 8.x shipped, "target PHP 8.1+"
after 8.1 died, `node:20` and `golang:1.23` in the examples an agent copies. Nothing
structural is wrong with any of them.

End-of-life data comes from a committed snapshot (`scripts/data/eol.json`), so runs
are deterministic and need no network. The snapshot going stale is itself a failure —
old data finds nothing and would read as a clean run.

A reference that is dated on purpose — a `node:18` showing a broken dev/prod pair — is
exempted by content hash in `scripts/data/eol-baseline.json`. Editing the line
brings it back for review.

```bash
python3 scripts/check-versions.py                   # exit 0 = clean, 1 = something dead
python3 scripts/check-versions.py --refresh         # re-fetch the snapshot (needs network)
python3 scripts/check-versions.py --update-baseline # accept the current exceptions
```

---

## `check-dangerous-sinks.py`

Fails when a construct that executes or injects appears with nothing nearby saying why
it is safe.

An agent copies from this base, so a `dangerouslySetInnerHTML` in a document labelled
"Good Example" ships as production code. This does not judge whether a use is correct —
judging is what found the two cases that prompted it, and the heuristic was right twice
out of twenty-eight. It enforces something procedural instead: an occurrence either
reads as a warning from its surroundings, or it is recorded as reviewed in
`scripts/data/sinks-baseline.json`. Anything else is new and unexamined.

The two it was built from:

- `nextjs/19-seo.md` fed `JSON.stringify(jsonLd)` into a `<script>` through
  `dangerouslySetInnerHTML` and called it Good. `JSON.stringify` escapes neither `<` nor
  `/`, and script content is raw text, so a post title containing `</script>` closed the
  element and made the rest live HTML.
- `divi/18-headless.md` passed WordPress `content.rendered` to the same sink in its Good
  Example, while `security/11-xss.md` and `frontend/14-security.md` both list that exact
  thing as a mistake. The pattern is defensible for trusted editors; leaving it unsaid
  was not.

```bash
python3 scripts/check-dangerous-sinks.py                   # exit 0 = clean
python3 scripts/check-dangerous-sinks.py --update-baseline # record reviewed occurrences
```

---

## `check-manifests.py`

Validates every YAML example against the tool that would actually consume it.

`check-knowledge.py` proves 244 YAML blocks are YAML, which is a much weaker claim
than it looks. A Kubernetes Deployment without `spec.selector` is valid YAML and is
rejected by the API server. A workflow job without `runs-on` is valid YAML and fails
to load. Both parse without complaint.

Both were in the base. Thirteen Deployments across five topics had no `selector` —
including in `kubernetes/`, whose own `05-deployments.md` shows it correctly — so
every one would have failed `kubectl apply`. A release workflow declared no `runs-on`
on either job and forwarded no `outputs` from the job computing the version, so
`needs.release.outputs.release_created` was always empty and the deploy job would
never have run: a green pipeline that ships nothing.

| Kind | Tool | What it catches |
| --- | --- | --- |
| Kubernetes | `kubeconform -strict` | missing required fields, unknown properties |
| Workflows | `actionlint` | syntax, expression types, required action inputs |
| Compose | `docker compose config` | schema, references to undefined services |

Workflow examples usually omit `on:` to keep the point in view. Requiring it meant
they were classified as nothing and checked by nothing — closing that hole turned 23
checked workflows into 49 and surfaced seven more defects. The validator supplies a
minimal trigger for those blocks; the documents are untouched.

Deliberately-partial blocks — a `compose.override.yaml` has no `image` because it
merges over a base file — are recorded in `scripts/data/manifests-baseline.json`.

```bash
python3 scripts/check-manifests.py                   # exit 0 = clean
python3 scripts/check-manifests.py --require-tools    # a missing validator fails
python3 scripts/check-manifests.py --update-baseline  # accept partial blocks
```

Needs `kubeconform`, `actionlint`, and `docker` on PATH; each missing one is reported
rather than silently skipped.

---

## `check-types.py`

Compiles the base's TypeScript examples against the real libraries they import.

`check-knowledge.py` parses 1707 JS/TS blocks with esbuild, which proves syntax and
nothing else. `revalidateTag('posts')` parses. So does `new PrismaClient()`. Both are
compile errors against the libraries the base teaches — the first found by hand during
the Next.js 16 migration, the second by this check, which is what surfaced the whole
Prisma 6 to 7 migration.

The difficulty is not compiling; it is that most blocks are excerpts referencing a
`logger`, a `db`, a model from the reader's own project. Those produce TS2304 and
TS2307 by the hundred, and filtering by error code also discards real findings — a
missing `await` on `cookies()` arrives as TS2339, which is also what an undefined local
produces.

So nothing is filtered by cleverness. Every diagnostic is recorded in
`scripts/data/types-baseline.json`, keyed by document and message shape, and only
unreviewed ones fail. A new type error gets exactly one review — the same contract as
`check-dangerous-sinks.py`, for the same reason.

Library versions are pinned in `scripts/data/types-env.json`, so a run is reproducible
and a deliberate upgrade is a visible commit. That file is also the tripwire for the
next framework migration: when a pinned library moves a major, this check is what says
which examples stopped compiling.

```bash
python3 scripts/check-types.py --refresh-env           # rebuild from the pinned lock
python3 scripts/check-types.py --refresh-env --upgrade # move the lock to latest
python3 scripts/check-types.py                    # exit 0 = clean
python3 scripts/check-types.py --update-baseline   # accept current excerpts
```

---

## `check-lint.py`

Runs each language's real linter over the examples, not just its parser.

`bash -n` proves a shell block parses. So does `for f in $(ls *.log)`, which breaks on
the first filename with a space — and which this base teaches as an antipattern in
three separate documents. A document can state a rule and break it two hundred lines
away, and until now nothing noticed.

Two defects of exactly that shape, both in Good Examples:

- `playbooks/02-failed-deployment.md` chose the rollback target with
  `ls -1dt … | sed -n 2p`, while `linux/01`, `linux/28` and `snippets/03` all say
  never to parse `ls` output. A rollback playbook is the worst place to pick the
  wrong release.
- `linux/19-debugging.md` took `pid=$(pgrep -f my-service)` and used `$pid` unquoted
  in six following commands. `pgrep` returns several PIDs whenever the pattern is at
  all ambiguous, and every one of those commands then breaks.

A third finding was about the rule rather than the code: `linux/03` said "Quote
everything" flatly, while twenty-five Good Examples across the base are command
transcripts nobody quotes. The rule now says where it binds, and names `shellcheck`
as the arbiter.

Diagnostics are recorded in `scripts/data/lint-baseline.json` as a **count** per
document, code and message shape. The count matters: the first version keyed on the
shape alone, and a second `SC2086` in a document that already had one passed unseen.
Injection caught it, and the same hole was then found and fixed in `check-types.py`,
which had been shipped one commit earlier with the same keying.

Every tool version is pinned — shellcheck in the workflow, PHPStan and the stubs in
`scripts/data/lint-env.json`. CI caught this the hard way: an unpinned shellcheck on
the runner emitted an `SC2002` the laptop's did not, and the baseline is a record of
what someone reviewed, not of what one machine happened to report that day.

```bash
python3 scripts/check-lint.py                        # exit 0 = clean
python3 scripts/check-lint.py --refresh-env          # rebuild PHP sandbox from the lock
python3 scripts/check-lint.py --refresh-env --upgrade # move the lock to latest
python3 scripts/check-lint.py --require-tools         # a missing linter fails
python3 scripts/check-lint.py --update-baseline       # accept current diagnostics
```

PHP is handled too, as a batch: PHPStan over the 445 parseable blocks with
`php-stubs/wordpress-stubs` 7 and `php-stubs/woocommerce-stubs` 11, which answers
"does this WordPress API exist" for the base's largest topic. It found nothing —
every `wp_*`, `WP_*` and `wc_*` symbol in 445 blocks is real on the current major.

Getting to that answer took three false starts, each of which reported clean while
checking nothing:

- `bootstrapFiles` for the stubs instead of `scanFiles` — the stubs were never used
  for symbol discovery.
- A run that exceeded PHPStan's memory limit inside a parallel worker still emitted
  `{"totals": {"file_errors": 0}}`.
- Worst of the three: a single unparseable fragment makes PHPStan declare the whole
  run incomplete and stop applying rules, so 445 files reported zero errors. Blocks
  are now pre-filtered with `php -l`, and the 36 that are class bodies or bare array
  literals never reach PHPStan. That change alone took the report from 0 to 193
  diagnostics.

Each of those was caught by injecting a call to a function that does not exist and
noticing the run stayed green. None would have been visible from the output.

The linter registry is keyed by fence tag, so adding ESLint for the React blocks is
a table entry rather than a new script.

---

## `selftest-guardrails.py`

Proves the linters can fail. It copies the base, injects one real defect per rule and
per block language — 39 in all, each in its own document — and reports any that goes
unnoticed.

This exists because a green run is not evidence on its own. Two checks here reported
success while doing nothing: `html-validate` wrote its report to a stdout pipe that
Node truncated at 64 KiB, so the JSON never parsed; and a missing parser returned the
same value as "no problem found". Neither was visible from the outside.

A case whose parser is not installed is reported as **not proved** rather than as a
missing rule, and still fails the run — an unchecked language must not read as clean.

```bash
python3 scripts/selftest-guardrails.py            # every case (~70 s)
python3 scripts/selftest-guardrails.py sql html   # only matching names
```

---

## `selftest-retrieval.py`

Answers a different question: not "is the base well-formed" but "does an agent
following [`AGENTS.md`](../AGENTS.md) actually land on the right rule". It runs 41
realistic questions — at least one per language and framework in the base — through
the documented protocol: detect the stack from `SIGNALS.stack`, resolve symbols
through `SIGNALS.symbols`, then rank `ready` documents by `when_to_use`, `tags`,
slug and title.

Every miss is a metadata defect, and fixing it means fixing the base. Real ones this
found: `errexit` and `nounset` appeared nowhere in the base, so the document teaching
`set -euo pipefail` was unreachable by the names of its own options; `AssumeRole` was
in a checklist but not in `aws/02-iam`; and terms of art that live in prose — `LCP`,
`CLS`, `IAM`, `JWT` — were not indexed at all, because only code and inline spans
were.

```bash
python3 scripts/selftest-retrieval.py            # pass/fail per question
python3 scripts/selftest-retrieval.py --why      # which evidence carried each answer
python3 scripts/selftest-retrieval.py --ablate   # what each source of evidence is worth
```

`--ablate` is the honesty check: it disables one source at a time and counts how many
questions still reach their rule. If a source can be removed with no effect, it is not
doing the work its weight claims.

---

## Angles tried that found nothing

Recorded so they are not re-run blind. Each was measured, not guessed at.

| Angle | Result |
| --- | --- |
| Building GraphQL SDL blocks as schemas rather than parsing them | 16 of 20 flagged, all legitimate excerpt references to types a project defines elsewhere (`DateTime`, `User`, `Post`) |
| hadolint's full rule set on the 53 Dockerfile blocks | 89 findings: deliberate Bad Examples, fragment artifacts, and a DL3025 false positive on `HEALTHCHECK CMD … \|\| exit 1`, which is the only legal shell form there |
| Prose citing `key: value` that the adjacent code contradicts | 55 candidates, 0 real. Prose that names a value almost always names the one to *avoid*; the code then correctly shows the opposite |
| The inverse — code using a value the adjacent prose forbids | 1 candidate, a mis-attributed negation. 0 real |
| Constants compared across documents (bcrypt cost, HSTS max-age, pool limits) | Consistent. Every HSTS instance is `max-age=63072000`; the `max-age=60` is a labelled Bad Example; differing `connection_limit` values are contextual and explained in place |
| Running each document's SQL against a real PostgreSQL 17 | Errors were all excerpt, concatenation, or psql artifacts — `:input` is a driver placeholder psql reads as its own variable |
| Contradictory directives about the same identifier | 161 candidates, 0 real. The polarity heuristic fires on any mention, so "`any` used to silence an error instead of `unknown`" reads as both |
| Whether a `**Rules:**` pointer is topically relevant | 416 of 511 flagged — a broken metric, not a finding: "Structure and Semantics" → `03-semantic-html` fails word overlap and is obviously right |

The one angle that paid was compiling against real libraries, and it is now
`check-types.py`.

---

All eleven checks run in CI via `.github/workflows/knowledge-guardrails.yml`, which also
fails the build if `INDEX.json`/`INDEX.md` or `SIGNALS.json` are out of sync with the
frontmatter.
