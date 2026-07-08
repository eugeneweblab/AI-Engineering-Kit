---
id: react/03-jsx
topic: react
slug: jsx
title: "JSX"
type: doc
order: 3
status: ready
tags: [react, jsx]
related: [react/04-components, react/05-props, react/11-rendering, react/20-accessibility, react/25-security]
when_to_use: "Read before writing or reviewing any JSX markup, lists, conditionals, or dangerouslySetInnerHTML."
---
# JSX

## Purpose

This document defines how to write JSX — the XML-like syntax React uses to describe
UI. JSX compiles to plain function calls (`React.createElement` / the automatic JSX
runtime), so every JSX expression is just JavaScript that returns a React element. The
goal here is markup that is correct, readable, safe from injection, and cheap to render.

## Why It Matters

JSX looks like HTML but is not HTML, and that gap is where bugs live. Attribute names
differ (`className`, `htmlFor`), `{}` embeds arbitrary JavaScript that runs on every
render, and list keys silently control whether React reuses or recreates DOM nodes. A
wrong key loses input focus and component state; a stray expression re-runs work each
render; `dangerouslySetInnerHTML` opens an XSS hole. These are invisible in review unless
you know the rules.

## Core Principles

- **JSX is an expression, not a template.** Everything inside `{}` is real JavaScript
  evaluated during render. Keep it cheap and side-effect-free.
- **JSX auto-escapes text.** Any string inside `{}` is escaped, so interpolated user data
  cannot inject markup. The only way to bypass this is `dangerouslySetInnerHTML` — treat
  it as a red flag.
- **Keys identify list items across renders.** They must be stable, unique among siblings,
  and derived from the data's identity — never the array index for dynamic lists.
- **A component returns one root.** Wrap siblings in a real element or a Fragment
  (`<>...</>`); do not add wrapper `<div>`s that break layout.

## Best Practices

- Use `className` (not `class`) and `htmlFor` (not `for`); style with an object:
  `style={{ marginTop: 8 }}`, values camelCased.
- Render lists with `.map` and give each item a stable `key` from a domain id.
- Express conditionals with ternaries or short-circuit `&&`, but guard `&&` against
  falsy-but-renderable values (`0` renders as "0"); use `count > 0 && ...`.
- Keep logic out of JSX. Compute values above the `return`; JSX should read declaratively.
- Prefer Fragments over wrapper elements to avoid polluting the DOM and CSS.
- Self-close void elements (`<img />`, `<br />`) — JSX requires it.
- Never build markup by string concatenation; never pass unsanitized HTML to
  `dangerouslySetInnerHTML`. See [security](25-security.md).

## Examples

**Good Example** — stable keys, guarded condition, escaped text

```jsx
function TodoList({ todos }) {
  return (
    <ul>
      {todos.map((todo) => (
        // key is the todo's stable id, so React matches items across reorders
        <li key={todo.id}>
          {todo.title} {/* auto-escaped: safe even if title contains <script> */}
          {todo.overdue && <span className="badge">Overdue</span>}
        </li>
      ))}
    </ul>
  );
}
```

**Bad Example** — index key, unguarded `&&`, unsafe HTML

```jsx
function TodoList({ todos, note }) {
  return (
    <ul>
      {todos.map((todo, i) => (
        // index key: deleting an item shifts keys, corrupting per-row state and focus
        <li key={i}>
          {todo.count && <span>{todo.count} left</span>} {/* renders "0" when count is 0 */}
          {/* injects raw HTML from user input → XSS */}
          <div dangerouslySetInnerHTML={{ __html: note }} />
        </li>
      ))}
    </ul>
  );
}
```

## Common Mistakes

- Using the array index as `key` in a list that can reorder, insert, or delete.
- `{value && <X />}` where `value` can be `0` or `""`, printing the falsy value.
- Writing `class` or `for` instead of `className` / `htmlFor` (silently ignored).
- Putting expensive computation or side effects inside JSX `{}` — it re-runs every render.
- Passing user-controlled strings to `dangerouslySetInnerHTML` without sanitization.
- Returning multiple sibling elements without a Fragment wrapper.

## Production Tips

- Enable `eslint-plugin-react` and `jsx-a11y` to catch missing keys, bad `&&` guards, and
  accessibility gaps at build time.
- If you must render trusted HTML, sanitize it first (e.g. DOMPurify) and centralize that
  in one reviewed helper, not scattered across components.

## AI Review Checklist

- Does every list item have a stable, unique `key` that is not the array index?
- Are `&&` conditions guarded so falsy values (`0`, `""`) do not render?
- Are DOM attributes JSX-correct (`className`, `htmlFor`, camelCased `style`)?
- Is all interpolated data left to JSX's auto-escaping, with no raw HTML injection?
- Is any `dangerouslySetInnerHTML` fed only sanitized, trusted content?
- Is heavy logic computed above the `return` rather than inside JSX?

## Related

- `knowledge/react/04-components.md`
- `knowledge/react/05-props.md`
- `knowledge/react/11-rendering.md`
- `knowledge/react/20-accessibility.md`
- `knowledge/react/25-security.md`
