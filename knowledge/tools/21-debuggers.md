---
id: tools/21-debuggers
topic: tools
slug: debuggers
title: "Debuggers"
type: doc
order: 21
status: ready
tags: [tools, debuggers]
related: [tools/22-profilers, tools/20-local-environments, tools/25-editor-setup, tools/29-observability-tools, tools/30-engineering-principles]
when_to_use: "Read before debugging beyond print statements — attaching a debugger to Node, PHP, or the browser, and setting breakpoints that actually help."
---
# Debuggers

## Purpose

This document defines how to use a real debugger: attaching to Node and PHP processes,
configuring Xdebug and the editor, and the breakpoint techniques that answer questions
`console.log` cannot.

## Why It Matters

Print debugging works until the question becomes "what is the state of these eight variables
at the moment this condition first becomes true, three hundred iterations in". At that point
each additional print is a rebuild and a re-run, while a conditional breakpoint answers it in
one pass.

The reason people persist with prints is setup friction: a debugger that requires ten minutes
of configuration is not used during an incident. Committing that configuration to the
repository is what makes the tool available when it matters.

## Core Principles

- **Commit the debugger configuration.** `.vscode/launch.json` in the repository means the
  debugger works on clone.
- **Reach for it when state is complex**, not for every bug. A single wrong value is faster to
  find with a log line.
- **Conditional and logpoint breakpoints beat re-runs.** Both remove the edit-rebuild cycle
  entirely.
- **Debug the running environment.** If the bug only appears in Docker, attach to the process
  in Docker rather than reproducing approximately on the host.

## Node

```json
// .vscode/launch.json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Debug: current test file",
      "type": "node",
      "request": "launch",
      "program": "${workspaceFolder}/node_modules/vitest/vitest.mjs",
      "args": ["run", "${relativeFile}"],
      "console": "integratedTerminal",
      "skipFiles": ["<node_internals>/**", "**/node_modules/**"]
    },
    {
      "name": "Attach: server in Docker",
      "type": "node",
      "request": "attach",
      "port": 9229,
      "address": "localhost",
      "localRoot": "${workspaceFolder}",
      "remoteRoot": "/app",              // path mapping: host ↔ container
      "skipFiles": ["<node_internals>/**"]
    }
  ]
}
```

```yaml
# compose.yaml — expose the inspector from the container
services:
  app:
    command: node --inspect=0.0.0.0:9229 dist/server.js
    ports: ['3000:3000', '9229:9229']
```

`skipFiles` matters more than it appears: without it, stepping through code lands repeatedly
inside framework internals and the session becomes unusable.

## PHP and Xdebug

```ini
; php.ini / docker-php-ext-xdebug.ini
zend_extension=xdebug

xdebug.mode=debug
xdebug.start_with_request=trigger      ; only when triggered — no cost on normal requests
xdebug.client_host=host.docker.internal
xdebug.client_port=9003
xdebug.idekey=VSCODE
```

```json
// .vscode/launch.json
{
  "name": "Listen for Xdebug",
  "type": "php",
  "request": "launch",
  "port": 9003,
  "pathMappings": {
    "/var/www/html": "${workspaceFolder}"   // container path → local path
  }
}
```

Trigger a debugged request with a cookie or query parameter:

```bash
curl 'http://localhost:8080/wp-admin/admin-ajax.php?XDEBUG_TRIGGER=1&action=acme_sync'
```

Two settings decide whether Xdebug is usable: `start_with_request=trigger` keeps the
performance cost off normal requests (`xdebug.mode=debug` with `start_with_request=yes` slows
every request substantially), and `pathMappings` is what makes breakpoints bind at all — a
wrong mapping produces the familiar "breakpoints are grey and never hit".

For WP-CLI and other CLI scripts:

```bash
XDEBUG_TRIGGER=1 wp acme signups recount
```

## Breakpoint Techniques

```js
// Conditional: stop only on the case that fails.
// Right-click the breakpoint → Expression: order.total < 0
```

```js
// Logpoint: prints without modifying the file, so no rebuild and nothing to remove later.
// Expression: `order ${order.id}: total=${order.total}, items=${order.items.length}`
```

```js
// Programmatic break, useful in generated or minified code where clicking a line is hard.
if (order.total < 0) {
  debugger;    // ignored unless devtools/inspector is attached
}
```

Other techniques worth knowing: **caught/uncaught exception breakpoints** to stop at the throw
site with the stack intact, **DOM breakpoints** in the browser to catch which script mutates a
node, and **XHR/fetch breakpoints** to stop when a specific request is issued.

## Examples

**Good Example** — a question a debugger answers in one run

```
"The cart total is wrong, but only for orders with a percentage coupon and
 a shipping override — roughly one in two hundred."
```

A conditional breakpoint on `coupon.type === 'percent' && order.shipping.overridden` stops on
the first matching case with the full object graph available. Print debugging this means
logging every order and reading two hundred entries.

**Bad Example** — debugging that ships

```ts
console.log('>>> HERE 1', order);
console.log('>>> HERE 2', JSON.stringify(cart, null, 2));
debugger;
```

All three reach production if the review is inattentive: the logs leak order data into the
browser console, and `debugger` freezes any developer with devtools open. Lint against them —
`no-console` and `no-debugger` exist for this.

## Common Mistakes

- No committed launch configuration, so everyone reconfigures from scratch.
- Xdebug in `develop,debug` mode always on, making local development several times slower.
- Wrong `pathMappings`, producing breakpoints that never bind.
- Debugging the host process when the bug lives in the container.
- Missing `skipFiles`, so stepping ends up inside framework internals.
- Source maps missing, leaving the debugger in minified output.
- `console.log` and `debugger` committed.
- Re-running the whole flow instead of setting a conditional breakpoint.

## Production Tips

- Never attach a debugger to production. Use structured logging and an error tracker with
  captured context instead — see [Observability Tools](29-observability-tools.md).
- Ensure sourcemaps are generated and uploaded, so production stack traces map to real
  filenames.
- For an intermittent bug, a logpoint plus a structured log line beats a breakpoint: it
  captures every occurrence rather than stopping on one.
- Keep a second Xdebug profile with `xdebug.mode=profile` for performance work — see
  [Profilers](22-profilers.md).
- In the browser, the Sources panel debugs application code and the Network panel answers
  "did the request even go out"; check the second before assuming the first.

## AI Review Checklist

- Is a debugger configuration committed to the repository?
- Does it map container paths to workspace paths correctly?
- Is Xdebug trigger-based rather than always on?
- Are sourcemaps available in the environment being debugged?
- Are `console.log` and `debugger` statements linted against?
- Does the setup attach to the environment where the bug reproduces?

## Related

- `knowledge/tools/22-profilers.md`
- `knowledge/tools/25-editor-setup.md`
- `knowledge/tools/29-observability-tools.md`
- `knowledge/engineering/03-debugging-methodology.md`
