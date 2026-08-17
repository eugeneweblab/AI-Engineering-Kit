# Agents

Tool-specific integration notes for AI coding assistants.

**The single source of truth is [`../AGENTS.md`](../AGENTS.md).** Every file here just
tells a specific tool how to load it. Each tool also has a native entrypoint at the
repo root or in `.github` / `.cursor` that points back to `AGENTS.md`:

| Tool | Native entrypoint | Verification status |
|------|-------------------|---------------------|
| Claude Code | `CLAUDE.md`, `AGENTS.md` | Adapter present; live compliance trial not yet recorded. |
| Cursor | `.cursor/rules/*.mdc`, `AGENTS.md` | `alwaysApply` adapter present; live protocol execution and output grading 13/13 on 2026-08-17 (n=1, no control arm). |
| Codex | `AGENTS.md` | Automatic load and document retrieval verified 2026-08-17. |
| GitHub Copilot | `.github/copilot-instructions.md` | Adapter present; live agent-mode trial not yet recorded. |
| Gemini CLI | `GEMINI.md` | Adapter present; live compliance trial not yet recorded. |
| Cline | `.clinerules`, `AGENTS.md` | Adapter present; live compliance trial not yet recorded. |

Do not convert “adapter present” into “tool follows every rule”. Run the versioned
scenario under `docs/trials/agent-compliance-v1/`, save the trace and tool version,
then update this table with the dated result.

Keep engineering knowledge in `knowledge/`. Only genuinely tool-specific configuration
belongs under `agents/`.
