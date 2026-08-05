---
id: tools/25-editor-setup
topic: tools
slug: editor-setup
title: "Editor Setup"
type: doc
order: 25
status: ready
tags: [tools, editor-setup]
related: [tools/05-prettier, tools/04-eslint, tools/21-debuggers, tools/26-ai-coding-tools, tools/30-engineering-principles, tools/16-git-hooks]
when_to_use: "Read before committing editor configuration — deciding what to enforce for the whole team, what to recommend, and what to leave personal."
---
# Editor Setup

## Purpose

This document defines which editor configuration belongs in the repository: the settings that
must be identical for everyone, the extensions worth recommending, and the personal
preferences that should never be imposed.

## Why It Matters

Editor configuration is the difference between a formatter that runs automatically and one
that runs occasionally. When settings live only in individual machines, whitespace-only diffs
appear in pull requests, and each one costs review attention and creates merge conflicts.

The line to hold is between *project* configuration and *personal* configuration. Committing
someone's font size or colour theme is an imposition; committing the formatter binding is the
job.

## Core Principles

- **Enforce behavior, not appearance.** Formatter, line endings, and indentation are project
  decisions. Themes, fonts, and keybindings are not.
- **`.editorconfig` first.** It works in every editor, including those without plugins.
- **Recommend extensions; do not require them.** A recommendation list is helpful; a hard
  dependency on one editor is not.
- **The editor must not be the only place a check runs.** Everything enforced here also runs in
  the hook and in CI — see [Git Hooks](16-git-hooks.md).

## `.editorconfig`

The baseline every editor understands, and the one file that should exist in every repository:

```ini
# .editorconfig
root = true

[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true
indent_style = space
indent_size = 2

[*.{php,inc}]
indent_style = tab           # WordPress Coding Standards
indent_size = 4

[*.md]
trim_trailing_whitespace = false   # two trailing spaces are a hard line break

[Makefile]
indent_style = tab           # required by make itself

[*.{yml,yaml}]
indent_size = 2
```

Pair it with `.gitattributes` so line endings are normalized regardless of platform:

```gitattributes
* text=auto eol=lf
*.png binary
*.jpg binary
```

Without that pair, a Windows contributor's first commit rewrites every line of every file.

## VS Code

```json
// .vscode/settings.json — committed: project behavior only
{
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": "explicit"
  },

  "[php]": { "editor.defaultFormatter": "wongjn.php-sniffer" },
  "[markdown]": { "editor.formatOnSave": false },

  "typescript.tsdk": "node_modules/typescript/lib",   // the project's TS, not the editor's
  "typescript.enablePromptUseWorkspaceTsdk": true,

  "eslint.useFlatConfig": true,
  "eslint.workingDirectories": [{ "mode": "auto" }],  // correct resolution in a monorepo

  "search.exclude": {
    "**/node_modules": true,
    "**/dist": true,
    "**/coverage": true
  },
  "files.watcherExclude": {
    "**/node_modules/**": true,
    "**/dist/**": true
  }
}
```

```json
// .vscode/extensions.json — recommendations, shown on clone
{
  "recommendations": [
    "esbenp.prettier-vscode",
    "dbaeumer.vscode-eslint",
    "bmewburn.vscode-intelephense-client",
    "xdebug.php-debug",
    "stylelint.vscode-stylelint",
    "editorconfig.editorconfig"
  ],
  "unwantedRecommendations": [
    "hookyqr.beautify",        // conflicts with Prettier
    "ms-vscode.vscode-typescript-tslint-plugin"
  ]
}
```

`typescript.tsdk` deserves particular attention: without it the editor uses its bundled
TypeScript version, so the editor and CI disagree about whether the code compiles.

## What Not to Commit

```json
// Personal — belongs in user settings, not the repository
{
  "workbench.colorTheme": "One Dark Pro",
  "editor.fontSize": 13,
  "editor.fontFamily": "JetBrains Mono",
  "vim.useSystemClipboard": true,
  "editor.minimap.enabled": false
}
```

Committing these produces a pull request comment war and teaches people to gitignore the
`.vscode` directory entirely — losing the settings that did matter.

## Examples

**Good Example** — the whole setup working on clone

```bash
git clone git@github.com:acme/site.git && cd site
pnpm install          # `prepare` installs git hooks
code .                # VS Code prompts to install recommended extensions
# formatOnSave works, ESLint reports inline, the debugger has a launch config,
# and the editor uses the project's TypeScript version
```

Nothing to configure, nothing to ask, nothing that can diverge.

**Bad Example** — configuration by tribal knowledge

```
README:
"Install the Prettier extension and enable Format on Save.
 Also disable the built-in formatter, or you'll get conflicts.
 Ask in #dev if your ESLint isn't picking up the config."
```

Every instruction here is a setting that could have been committed.

## Common Mistakes

- No `.editorconfig`, so indentation depends on the editor.
- No `.gitattributes` normalization, producing whole-file diffs from Windows contributors.
- Personal preferences committed to project settings.
- Editor-only enforcement, so anyone using a different editor bypasses every check.
- The editor's bundled TypeScript used instead of the project's.
- Two formatters active, each undoing the other on save.
- `.vscode/` gitignored entirely, discarding useful shared configuration.
- Extension recommendations that conflict with the project's tooling.

## Production Tips

- Keep committed settings minimal — the smaller the file, the less objection it attracts and
  the longer it survives.
- Use `unwantedRecommendations` to name extensions that actively conflict; it prevents a
  recurring class of "formatting keeps changing" reports.
- For a monorepo, set `eslint.workingDirectories` and per-folder TypeScript SDK paths, or the
  editor resolves configs from the wrong package.
- If the team uses several editors, put behavior in `.editorconfig` and the hooks, and treat
  editor-specific files as convenience only.
- Devcontainers (`.devcontainer/devcontainer.json`) take this further, pinning the toolchain
  itself — worth it when onboarding is frequent or the stack is unusual. See
  [Local Environments](20-local-environments.md).

## AI Review Checklist

- Does `.editorconfig` exist and cover every language in the repository?
- Is `.gitattributes` normalizing line endings?
- Are committed editor settings limited to project behavior?
- Is the workspace TypeScript version used rather than the editor's?
- Are extension recommendations present, including conflicting ones marked unwanted?
- Does every editor-enforced rule also run in a hook and in CI?

## Related


- `knowledge/tools/05-prettier.md`
- `knowledge/tools/04-eslint.md`
- `knowledge/tools/21-debuggers.md`
- `knowledge/tools/26-ai-coding-tools.md`
- `knowledge/tools/30-engineering-principles.md`
- `knowledge/tools/16-git-hooks.md`
