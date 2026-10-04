---
type: pitfall
title: Catalogue order differs between the memory and PostgreSQL stores
description: MemoryJokeStore preserves insertion order, with JOKES first and later additions appended; PostgresJokeStore lists alphabetically by name.
tags: [jokes, postgres, ordering]
status: stable
generated: { by: knockknock-architect/gpt-5.6-terra, at: 2026-10-04T00:32:13Z }
sources:
  - { id: mem, resource: "https://github.com/chfields/knock-knock-jokes/blob/6e3aafb6e0ace0132522c3cdca6c0bf1c1893887/knockknock/joke_store.py#L46-L48" }
  - { id: pg, resource: "https://github.com/chfields/knock-knock-jokes/blob/6e3aafb6e0ace0132522c3cdca6c0bf1c1893887/knockknock/joke_store.py#L154-L158" }
wardby:
  schema: 1
  roles: [builder, reviewer]
  affects: ["knockknock/joke_store.py", "knockknock/web.py", "web/src/**"]
  citations:
    - { id: mem, repo: github:chfields/knock-knock-jokes, path: knockknock/joke_store.py, lines: [46, 48], symbol: MemoryJokeStore.list, sha: 6e3aafb6e0ace0132522c3cdca6c0bf1c1893887, spanHash: sha256:a0fb076ce4407048bfaf516fb35dc9615244e3cdff42f82cbb2b60857f1b2aa0 }
    - { id: pg, repo: github:chfields/knock-knock-jokes, path: knockknock/joke_store.py, lines: [154, 158], symbol: PostgresJokeStore.list, sha: 6e3aafb6e0ace0132522c3cdca6c0bf1c1893887, spanHash: sha256:d83301e34e8aca7b20a069cb704541f0da12217b9f8dfce4d3a4f9acd1266365 }
  confidence: high
---

`JokeStore.list()` promises "display order", but the two implementations disagree:
the in-memory store preserves insertion order (built-ins from `JOKES`, followed by
additions),[^mem] while the PostgreSQL store
runs `ORDER BY name`.[^pg] Tests use the memory store, so anything that depends on
position — numbering, "first"/"next" joke, pagination — can pass locally and behave
differently on the deployed site.

**What to do:** don't rely on list position unless the change makes both stores
agree, and test ordering against both.

[^mem]: knockknock/joke_store.py, MemoryJokeStore.list
[^pg]: knockknock/joke_store.py, PostgresJokeStore.list
