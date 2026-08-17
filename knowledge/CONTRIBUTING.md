# Contributing

An agent copies from this base and ships the result. That is the difference between
this repository and most documentation: a wrong rule here does not confuse a reader,
it becomes production code. Everything below follows from that.

This guide covers **what must not break** and **why**. The other three sources of
truth are unchanged:

- [`engineering/WRITING_STANDARD.md`](engineering/WRITING_STANDARD.md) — how to write.
- [`TEMPLATE.md`](TEMPLATE.md) — required frontmatter and section order.
- [`../AGENTS.md`](../AGENTS.md) — how agents consume this base.
- [`../scripts/README.md`](../scripts/README.md) — what each guardrail checks and what it caught.

---

## The invariants

Thirteen checks run on every push. They exist because each one is a defect class that
already shipped here at least once and was invisible to inspection.

### Enforced: a document is findable

An unreachable rule is the same as a missing rule, and this is the failure mode that
does not announce itself — the document is well-written, complete, and nobody's query
ever reaches it.

| Invariant | Broken when |
|---|---|
| `status: ready` means real content | a stub, TODO, or empty index doc claims `ready`; agents filter on this field and land on a dead end |
| Maturity claims have evidence | `reviewed`/`validated` is missing sources, checked version, or review dates |
| `INDEX.json`, `INDEX.md`, `SIGNALS.json` match the frontmatter | you edited frontmatter and did not rerun the generators |
| Every rule is reachable | a document ranks for nothing, is in no symbol index, and its title does not isolate it in `INDEX.md` |
| Agent instructions are executable | an entrypoint names a field, path, or command that does not exist |

`when_to_use` is the field that carries this. Ablation over all 1439 documents prices
it at **−284** — remove it and 284 documents stop being found. Nothing checks that it
is *good*, only that it is non-empty. Write it as the situation a reader is in
("Read before building modals, drawers, route transitions"), not as a restatement of
the title. That phrasing is deliberate throughout the base and it is why the base
answers "I am doing X" better than "tell me about Y".

Ranking the top five is zero-sum. A longer `when_to_use` wins queries a sibling then
loses, and the scorer weights every matching word equally — `prisma` counts for exactly
as much as `code`. When you widen one, run `check-reachability.py` and look at what
moved before committing.

### Enforced: an example is real

| Invariant | Checked by |
|---|---|
| Every fenced block parses as the language its fence claims | `check-knowledge.py` — each block handed to the real parser for its language |
| TypeScript compiles against the libraries it imports | `check-types.py`, versions pinned in `types-env.json` |
| Examples pass their language's linter | `check-lint.py` — shellcheck, ruff, PHPStan with WordPress stubs, ESLint, stylelint |
| YAML manifests satisfy the tool that consumes them | `check-manifests.py` — kubeconform, actionlint, `docker compose config` |
| No document recommends an end-of-life runtime | `check-versions.py` against a committed snapshot |
| Anything that executes or injects is warned about or reviewed | `check-dangerous-sinks.py` |

Valid YAML is a much weaker claim than a valid manifest: thirteen Kubernetes
Deployments here parsed cleanly and had no `spec.selector`, so every one would have
failed `kubectl apply`. `revalidateTag('posts')` parses too, and is a compile error
against the library this base teaches.

### Enforced: structure

Canonical filenames and numbering come from
[`../docs/structure/canonical-file-list.md`](../docs/structure/canonical-file-list.md).
A standard topic has `README`, `00`, `01`–`30` without gaps, then `98`, `99`, `100`.
`id`, `topic`, and `order` must agree with the path; ids, titles, and orders are unique
within a topic; every markdown link, every `related:` id, and every bare path pointing
into the base resolves; a `defers_to` target must exist and appear in `related`.

That last one is stricter than it sounds, and it applies to this file too: an earlier
draft of this section wrote a path as an illustration, in backticks, and the check
rejected it as a link to a file that does not exist. Write patterns so they cannot be
read as paths.

Order documents by the `order` field, never by filename — `100` sorts before `11`.

### Not enforced by anything

Say so in review, because no script will:

- **Whether the rule is true.** Nothing verifies that the advice is correct, only that
  the code demonstrating it parses, compiles, and lints.
- **Whether the prose is current.** `check-versions.py` catches a dead runtime. It does
  not catch a rule that stopped being best practice.
- **Whether two documents contradict each other.** This was measured four separate
  ways — prose against adjacent code, the inverse, constants across documents,
  contradictory directives about one identifier — and produced 0 real findings from
  217 counted candidates. The heuristics do not work; a reader is still the only
  detector.
- **Whether a Good Example is correct in every semantic dimension.** The checker now
  rejects silently mutable Actions/runners in labelled workflow examples, and the sink
  checker covers known injection APIs; broader engineering correctness still requires review.

---

## Baselines: when adding is honest, and when it is silencing

Seven files record "a human looked at this and decided". They are the mechanism that
lets a guardrail be strict without drowning in legitimate exceptions — and the easiest
place in this repository to hide a real defect.

| File | Records | Entries |
|---|---|---|
| `lint-baseline.json` | linter diagnostics, keyed by document, code and **count** | 531 |
| `types-baseline.json` | `tsc` diagnostics, keyed by document and message shape | 136 |
| `codeblock-baseline.json` | blocks that are fragments and never parse standalone | 133 |
| `reachability-baseline.json` | documents reachable by symbol or grep but not by rank | 308 |
| `sinks-baseline.json` | reviewed uses of a construct that executes or injects | 8 |
| `eol-baseline.json` | a dated runtime shown on purpose | 5 |
| `manifests-baseline.json` | deliberately partial manifests | 2 |

**Adding an entry is justified when the diagnostic is an artifact of the example's
shape, not of its content:** a class-method excerpt that cannot parse standalone, a
`logger` the reader supplies, a `compose.override.yaml` with no `image` because it
merges over a base, a `node:18` deliberately shown as the broken half of a pair.

**Adding an entry is silencing a defect when the diagnostic is about the code the
reader would copy.** An unquoted variable, a missing `await`, a manifest field the API
server requires. Fix the example.

Rules that follow from this:

1. **A growing baseline needs a reason in the commit message.** `git diff` the baseline
   before committing. A baseline that grows without a matching new fragment is a real
   defect being silenced, and nothing else will tell you.
2. **Never run `--update-baseline` to make a red build green.** Run it after you have
   read what changed and can say why each new entry is an artifact.
3. **Counts matter, not just shapes.** `lint-baseline.json` keys on a count for a
   reason: the first version keyed on the message shape alone, and a second `SC2086` in
   a document that already had one passed unseen. The same hole existed in
   `check-types.py`, shipped one commit earlier.
4. **Pin the tool.** An unpinned shellcheck on the CI runner emitted a diagnostic the
   laptop's did not. A baseline is a record of what someone reviewed, not of what one
   machine happened to report that day. Versions live in `lint-env.json` and
   `types-env.json`; a deliberate upgrade is a visible commit.

---

## Adding or editing a document

1. **Prefer filling an existing stub over creating a file.** Most of the structure
   already exists as `draft`. Keep the canonical filename and numeric prefix — the
   prefix *is* the document's `order` and must be unique within its topic.
2. Start from [`TEMPLATE.md`](TEMPLATE.md). The frontmatter block is mandatory.
3. Write per `WRITING_STANDARD.md`. One subject per document. Explain why, and name the
   trade-off.
4. Set `when_to_use` to the situation, and `related` to the documents a reader will
   want next. If two topics cover one subject, set `defers_to` on the one that does not
   own the rule and add the owner to `related`.
5. Flip `status: draft → ready` only when the Definition of Done is met. `ready` is a
   promise that an agent may generate code from it unsupervised.
6. Regenerate and commit both generated files:

   ```bash
   python3 scripts/build-index.py     # INDEX.json + INDEX.md
   python3 scripts/build-signals.py   # SIGNALS.json
   ```

7. Verify before you finish:

   ```bash
   python3 scripts/check-knowledge.py knowledge   # structure, links, every code block
   python3 scripts/check-reachability.py          # your document is findable
   ```

   The rest run in CI. To reproduce a CI failure locally, `scripts/README.md` documents
   each check's flags and what it needs installed.

### Writing rules that stay true

- Write in English.
- Do not duplicate a rule that another document owns — cross-reference it. Two copies
  drift, and then the base contradicts itself with no check to notice.
- Name the variant a rule is specific to in `applies_to`. App Router caching rules are
  not "mostly right" on the Pages Router, they are wrong.
- Prefer updating an existing document over adding one.
- Keep tool-specific and vendor-specific material out. This should read the same in
  five years; integration notes belong under `agents/`.

---

## Adding a guardrail

A check that has never failed is not evidence. Two checks in this repository reported
success while doing nothing: `html-validate` wrote its report to a stdout pipe Node
truncated at 64 KiB, so the JSON never parsed; and a missing parser returned the same
value as "no problem found". Neither was visible from the outside.

So a new check ships with proof it can fail — a case in
[`../scripts/selftest-guardrails.py`](../scripts/selftest-guardrails.py), or its own
`--selftest`. A language whose tool is missing must be reported as *not proved* and
fail the run, never skipped silently: `--require-tools` is what CI passes, because
without it a failed install leaves the build green while eight languages go unchecked.

Record the angles that found nothing, too. `scripts/README.md` has a table of eight
measured approaches that produced no real findings — it is there so nobody re-runs them
blind.

---

## Related documents

- [`README.md`](README.md) — knowledge directory overview
- [`../scripts/README.md`](../scripts/README.md) — every guardrail, what it caught, how to run it
- [`../docs/trials/README.md`](../docs/trials/README.md) — whether an agent actually uses this, measured
