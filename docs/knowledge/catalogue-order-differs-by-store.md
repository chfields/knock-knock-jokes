---
type: pitfall
title: Catalogue order differs between the memory and PostgreSQL stores
description: MemoryJokeStore lists jokes in JOKES order; PostgresJokeStore lists them alphabetically by name.
tags: [jokes, postgres, ordering]
status: stable
generated: { by: human:chfields-spike, at: 2026-10-03T00:00:00Z }
sources:
  - { id: mem, resource: "https://github.com/chfields/knock-knock-jokes/blob/b92f0a0606448cf4d1163b0420644fac997e2c05/knockknock/joke_store.py#L42-L43" }
  - { id: pg, resource: "https://github.com/chfields/knock-knock-jokes/blob/b92f0a0606448cf4d1163b0420644fac997e2c05/knockknock/joke_store.py#L114-L118" }
wardby:
  schema: 1
  roles: [builder, reviewer]
  affects: ["knockknock/joke_store.py", "knockknock/web.py", "web/src/**"]
  citations:
    - { id: mem, repo: github:chfields/knock-knock-jokes, path: knockknock/joke_store.py, lines: [42, 43], symbol: MemoryJokeStore.list, sha: b92f0a0606448cf4d1163b0420644fac997e2c05, spanHash: sha256:a22d3aa4f645e2d12baa197f6b94439fffcec9c6b69e93d642c4cc1809debbd1 }
    - { id: pg, repo: github:chfields/knock-knock-jokes, path: knockknock/joke_store.py, lines: [114, 118], symbol: PostgresJokeStore.list, sha: b92f0a0606448cf4d1163b0420644fac997e2c05, spanHash: sha256:d83301e34e8aca7b20a069cb704541f0da12217b9f8dfce4d3a4f9acd1266365 }
  confidence: high
---

`JokeStore.list()` promises "display order", but the two implementations disagree:
the in-memory store keeps `JOKES` (insertion) order,[^mem] while the PostgreSQL store
runs `ORDER BY name`.[^pg] Tests use the memory store, so anything that depends on
position — numbering, "first"/"next" joke, pagination — can pass locally and behave
differently on the deployed site.

**What to do:** don't rely on list position unless the change makes both stores
agree, and test ordering against both.

[^mem]: knockknock/joke_store.py, MemoryJokeStore.list
[^pg]: knockknock/joke_store.py, PostgresJokeStore.list
