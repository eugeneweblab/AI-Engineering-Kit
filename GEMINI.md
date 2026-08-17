# GEMINI.md

Agent instructions for this repository live in [`AGENTS.md`](AGENTS.md). Read it first.
Resolve the Git root and run every lookup under `knowledge/` from there; the current
working directory may be nested.

Entrypoint for finding knowledge: [`knowledge/INDEX.json`](knowledge/INDEX.json).
Filter to `status: "ready"`, then match: `when_to_use` states when a document applies,
`tags` and `topic` narrow it. Read the doc at its `path`.

[`knowledge/SIGNALS.json`](knowledge/SIGNALS.json) works from the code instead of the
task description: `stack` maps a file such as `app/page.tsx` or `wp-config.php` to the
documents that govern that stack, and `symbols` maps an API name such as `revalidateTag`
or `argon2` to the documents that state its rules.

Skip a document whose `applies_to` names a variant `SIGNALS.stack` did not match in this
repository, including when no variant matched. Do not cite `draft` stubs as sources.
