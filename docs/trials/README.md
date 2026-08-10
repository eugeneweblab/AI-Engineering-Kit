# Does an agent actually use this, and does it change the code?

Nine passes of guardrails measured proxies: whether a document parses, whether the
retrieval scorer lands on it, whether an example compiles. None of them measured the
thing the base exists for — an agent, given a task, writing better code.

This is that trial. Two agents, same five tasks, same model. One was told the
repository exists and to read `AGENTS.md`; the other was told nothing about it.
Both wrote to a directory. Grading is mechanical: `scripts/trial-grade.py` plus the
vendors' own tools.

The five tasks were chosen where the base states a rule that is version-specific
enough that a model answering from memory is likely to miss it, and mechanical
enough that grading needs no opinion.

## Result

| | with the base | without |
| --- | --- | --- |
| Mechanical rules (5) | 5/5 | 4/5 |
| Rules checked afterwards but not graded (8) | 8/8 | 6/8 |
| Tokens spent | 109k | 32k |

Three differences, all real:

- **Prisma 7 schema.** The control put `url` in the `datasource` block. Prisma's own
  `prisma validate` rejects it: *"The datasource property `url` is no longer
  supported in schema files."* The schema written with the base validates. This is
  the failure mode worth noting — the control did not forget the field, it
  *reasoned* its way to keeping it, commenting "so the schema is self-describing for
  `prisma validate`", which is the exact tool that refuses it. Confident, coherent,
  and wrong.
- **PodDisruptionBudget.** Present with the base, absent without. Three replicas
  without one are still evictable together during a node drain.
- **HTTP→HTTPS redirect** on the ALB. Present with the base, absent without.

Everything else the control got right unaided: `updateTag` over a one-argument
`revalidateTag`, `spec.selector`, `create_before_destroy`, escaping `<` in JSON-LD,
non-root containers, TLS policy, schema validation in the Server Action. Both
manifests pass kubeconform; both Terraform files are clean under tflint.

So the honest size of the effect: on a strong current model, the base changed three
of thirteen checked points, one of which was the difference between code that runs
and code that does not — at 3.4× the tokens.

## Did the agent follow the protocol?

`2026-08-10-protocol-log.md` is the log it kept. It did, without prompting beyond
"read AGENTS.md": symbol lookups in `SIGNALS.json` first, `status: ready` confirmed
in `INDEX.json`, `when_to_use` used to choose between candidates, `defers_to`
checked for overlaps (there were none in `kubernetes/`, and it said so), documents
read in full only after being chosen, then self-verification against each topic's
`98`/`99`/`100` checklists.

It also grepped rather than loaded, which only became the documented instruction
hours before this ran. Before that fix `AGENTS.md` said "Open `knowledge/INDEX.json`"
— 310k tokens.

## Repeating it

```bash
python3 scripts/trial-grade.py /tmp/trial/base /tmp/trial/nobase
```

The task prompts are in the git history of this file. When a framework moves a
major, rerun it: the tasks are exactly the places where memory goes stale.
