# Agent compliance trial v1

This is the reproducible A/B test for whether repository guidance changes an agent's
work. The prompt and fixture are committed; generated runs are not.

```bash
python3 scripts/agent-compliance.py prepare /tmp/ai-kit-trial
python3 scripts/agent-compliance.py run /tmp/ai-kit-trial --model <exact-model-id> --repeats 5
python3 scripts/agent-compliance.py grade /tmp/ai-kit-trial
```

`prepare` creates two isolated Git repositories with the same `eval/` fixture. The
base arm contains this kit and automatically loads `AGENTS.md`; the control arm does
not. `run` invokes the same Codex CLI/model/config for both, saves JSONL traces, final
messages, CLI/model/version/time metadata, and token usage. `grade` checks output and
process: scoped files, immutable workflow inputs, token-checked Redis release,
lock-bounded PostgreSQL validation, whether the base arm queried the index and read
the expected documents, and whether it consulted the required checklists.

Do not replace the prompt after seeing a result. Add a versioned scenario instead.
Report every repetition, not only the best run.
