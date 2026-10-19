---
type: risk
title: React catalogue deletion is immediate
description: The catalogue Delete button sends the destructive request immediately, with no confirmation or undo path.
tags: [jokes, web, deletion, frontend]
status: stable
generated: { by: knockknock-architect/gpt-5.6-terra, at: 2026-10-19T06:02:56Z }
sources:
  - { id: catalogue, resource: "https://github.com/chfields/knock-knock-jokes/blob/163e30946ad01bef01eeb963b578a42b81787c75/web/src/App.tsx#L120-L130" }
wardby:
  schema: 1
  roles: [builder, reviewer, planner]
  affects: ["web/src/App.tsx", "web/src/api.ts", "web/src/App.test.tsx", "knockknock/web.py"]
  citations:
    - { id: catalogue, repo: github:chfields/knock-knock-jokes, path: web/src/App.tsx, lines: [120, 130], symbol: Catalogue, sha: 163e30946ad01bef01eeb963b578a42b81787c75, spanHash: sha256:c13b090f6e1a5e70716834684559229c770588b1d5fc3cece2185f7ee50a8439 }
  confidence: high
---

`Catalogue` wires each Delete button directly to `remove()`, which calls
`deleteJoke()` and removes the item from local state after a successful
response.[^catalogue] There is no confirmation state, undo action, or recovery
link. A mistaken click therefore immediately performs a permanent catalogue
deletion; retained ratings can then attach to a later replacement with the
same ID.

**What to do:** add an explicit confirmation or an undo/recovery flow before
making deletion available to users, and test that the request is deferred until
the destructive action is confirmed.

[^catalogue]: web/src/App.tsx, Catalogue
