---
type: pitfall
title: Catalogue order differs between the memory and PostgreSQL stores
description: MemoryJokeStore lists jokes in JOKES order; PostgresJokeStore lists them alphabetically by name.
tags: [jokes, postgres, ordering]
status: stable
generated: { by: knockknock-architect/gpt-5.6-terra, at: 2026-10-03T19:22:19Z }
sources:
  - { id: mem, resource: "https://github.com/chfields/knock-knock-jokes/blob/db6e4fa032e52c80670a86918faead2c7fe790bc/knockknock/joke_store.py#L43-L47" }
  - { id: pg, resource: "https://github.com/chfields/knock-knock-jokes/blob/db6e4fa032e52c80670a86918faead2c7fe790bc/knockknock/joke_store.py#L153-L157" }
wardby:
  schema: 1
  roles: [builder, reviewer]
  affects: ["knockknock/joke_store.py", "knockknock/web.py", "web/src/**"]
  citations:
    - { id: mem, repo: github:chfields/knock-knock-jokes, path: knockknock/joke_store.py, lines: [43, 47], symbol: MemoryJokeStore.list, sha: db6e4fa032e52c80670a86918faead2c7fe790bc, spanHash: sha256:36a3c69cef477aacd78fe91477a2488ac570cd1c5e064a511d38ba7c4ba87c40 }
    - { id: pg, repo: github:chfields/knock-knock-jokes, path: knockknock/joke_store.py, lines: [153, 157], symbol: PostgresJokeStore.list, sha: db6e4fa032e52c80670a86918faead2c7fe790bc, spanHash: sha256:d83301e34e8aca7b20a069cb704541f0da12217b9f8dfce4d3a4f9acd1266365 }
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
