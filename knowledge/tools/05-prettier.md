---
id: tools/05-prettier
topic: tools
slug: prettier
title: "Prettier"
type: doc
order: 5
status: ready
tags: [tools, prettier]
related: [tools/04-eslint, tools/16-git-hooks, tools/25-editor-setup, tools/06-stylelint, tools/30-engineering-principles]
when_to_use: "Read before adding or configuring a formatter — setting options, integrating with ESLint, or introducing formatting to an existing codebase without destroying git blame."
---
# Prettier

## Purpose

This document defines how to use Prettier: which options to set (few), how it divides
responsibility with the linter, and how to adopt it in an existing codebase without ruining
`git blame` for everyone.

## Why It Matters

Formatting debates consume review time and produce nothing. A formatter ends them by removing
the decision — not by choosing well, but by choosing consistently. That is the entire value
proposition, and it only holds if the formatter runs automatically and its output is never
discussed.

The second-order benefit matters more in practice: diffs shrink to actual changes, so review
attention goes to logic instead of whitespace.

## Core Principles

- **Configure almost nothing.** Every option added is a decision the team has to make and
  maintain. The defaults are fine; consistency is the point, not the specific style.
- **The formatter and the linter must not overlap.** `eslint-config-prettier` disables every
  rule Prettier owns.
- **Format automatically**, in the editor on save and on commit for staged files. Manual
  formatting is formatting that does not happen.
- **Check, do not format, in CI.** `--check` fails on unformatted code; running `--write` in
  CI hides the fact that someone's setup is broken.

## Best Practices

```json
// .prettierrc — deliberately small
{
  "singleQuote": true,
  "trailingComma": "all",
  "printWidth": 100,
  "plugins": ["prettier-plugin-tailwindcss"]
}
```

```gitignore
# .prettierignore
dist/
coverage/
pnpm-lock.yaml
*.min.js
CHANGELOG.md
```

```json
{
  "scripts": {
    "format": "prettier --write .",
    "format:check": "prettier --check ."
  }
}
```

The Tailwind plugin is worth calling out: it sorts utility classes into the canonical order
automatically, which removes an entire category of review comment. See
[Tailwind](../tailwind/26-best-practices.md).

## Adopting It in an Existing Codebase

Reformatting a mature repository rewrites every line, and `git blame` then attributes all of
it to that commit. The fix is a single, isolated commit plus a blame-ignore file:

```bash
# 1. Formatting ONLY — no other change in this commit.
npx prettier --write .
git commit -am "style: apply prettier to the whole codebase"

# 2. Record the commit so blame skips it.
git rev-parse HEAD >> .git-blame-ignore-revs
git commit -am "chore: ignore the prettier commit in git blame"
```

```gitconfig
# Make it apply for everyone (also honored by GitHub automatically).
git config blame.ignoreRevsFile .git-blame-ignore-revs
```

Doing this in the same commit as a feature change is the mistake to avoid: the real change
becomes unreviewable inside thousands of formatting lines.

## Examples

**Good Example** — automatic, non-overlapping, verified in CI

```json
// .vscode/settings.json — committed, so every editor behaves the same
{
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": { "source.fixAll.eslint": "explicit" }
}
```

```json
// package.json — staged files only, so the hook stays fast
{
  "lint-staged": {
    "*.{ts,tsx,js,jsx,css,md,json}": ["prettier --write"],
    "*.{ts,tsx}": ["eslint --fix --max-warnings 0"]
  }
}
```

```yaml
# CI verifies rather than fixes
- run: pnpm format:check
```

**Bad Example** — the two tools fighting

```js
// eslint.config.js
export default [
  {
    plugins: { prettier: prettierPlugin },
    rules: {
      'prettier/prettier': 'error',   // runs Prettier as a lint rule: slow, noisy errors
      semi: ['error', 'never'],       // and directly contradicts Prettier's output
    },
  },
];
```

Every save now produces a lint error, and fixing it produces a formatting change that
re-triggers the error.

## Common Mistakes

- Formatting rules left enabled in ESLint, so the two tools disagree.
- `eslint-plugin-prettier` instead of `eslint-config-prettier` — formatting differences become
  lint errors and every file must be parsed twice.
- A large formatting commit mixed with real changes.
- No `.git-blame-ignore-revs` after adopting the formatter.
- `--write` in CI instead of `--check`, masking developers whose setup is broken.
- Formatting lockfiles, generated code, or vendored files.
- A heavily customized `.prettierrc` that reintroduces the debate the tool was adopted to end.
- Editor settings not committed, so formatting depends on who saved the file last.

## Production Tips

- Commit `.vscode/settings.json` and `.vscode/extensions.json` so a new developer gets correct
  behavior on clone; keep enforced settings minimal and machine-agnostic.
- Add `.editorconfig` as well — it covers editors without a Prettier plugin, and Prettier
  reads it for `indent_style`, `indent_size`, and `end_of_line`.
- Set `endOfLine: "lf"` (the default) and pair it with `* text=auto eol=lf` in
  `.gitattributes` to keep Windows contributors from producing whole-file diffs.
- Pin the Prettier version. Minor releases occasionally change output, which would otherwise
  reformat the codebase on someone's machine and not another's.

## AI Review Checklist

- Is `eslint-config-prettier` in use, with no formatting rules left in ESLint?
- Does CI run `prettier --check` rather than `--write`?
- Is formatting applied automatically on save and on staged files?
- Was the initial formatting commit isolated and recorded in `.git-blame-ignore-revs`?
- Are generated files, lockfiles, and build output ignored?
- Is the Prettier version pinned?
- Is the configuration minimal, with every non-default option justified?

## Related

- `knowledge/tools/04-eslint.md`
- `knowledge/tools/16-git-hooks.md`
- `knowledge/tools/25-editor-setup.md`
- `knowledge/tools/06-stylelint.md`
- `knowledge/tools/30-engineering-principles.md`
