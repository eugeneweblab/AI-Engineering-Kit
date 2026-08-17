# codex integration

This tool follows the shared instructions in [`../../AGENTS.md`](../../AGENTS.md).

Codex automatically loaded the root `AGENTS.md` in the 2026-08-17 compliance trial.
The trial also proved that lookups fail when instructions assume the current working
directory is the repository root; the shared protocol now resolves the Git root first.
Re-run the versioned trial after material CLI discovery changes.
