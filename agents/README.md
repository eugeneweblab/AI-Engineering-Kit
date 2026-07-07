# Agents

Tool-specific integration notes for AI coding assistants.

**The single source of truth is [`../AGENTS.md`](../AGENTS.md).** Every file here just
tells a specific tool how to load it. Each tool also has a native entrypoint at the
repo root or in `.github` / `.cursor` that points back to `AGENTS.md`:

| Tool | Native entrypoint | Notes |
|------|-------------------|-------|
| Claude Code | `CLAUDE.md`, `AGENTS.md` | Auto-loaded from repo root. |
| Cursor | `.cursor/rules/*.mdc`, `AGENTS.md` | `alwaysApply` rule redirects here. |
| Codex | `AGENTS.md` | Reads `AGENTS.md` directly. |
| GitHub Copilot | `.github/copilot-instructions.md` | Auto-loaded by Copilot. |
| Gemini CLI | `GEMINI.md` | Reads `GEMINI.md` from root. |
| Cline | `.clinerules`, `AGENTS.md` | Redirects here. |

Keep engineering knowledge in `knowledge/`. Only genuinely tool-specific configuration
belongs under `agents/`.
