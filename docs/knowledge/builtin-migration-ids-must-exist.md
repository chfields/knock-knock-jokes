---
type: invariant
title: Built-in migration IDs must remain in JOKES
description: Every ID named by a built-in catalogue migration must resolve in the current JOKES tuple, or PostgreSQL catalogue initialization fails before the migration can be recorded.
tags: [jokes, postgres, migrations, deployment]
status: stable
generated: { by: knockknock-architect/gpt-5.6-terra, at: 2026-11-16T06:02:53Z }
sources:
  - { id: migrations, resource: "https://github.com/chfields/knock-knock-jokes/blob/163e30946ad01bef01eeb963b578a42b81787c75/knockknock/joke_store.py#L9-L12" }
  - { id: apply, resource: "https://github.com/chfields/knock-knock-jokes/blob/163e30946ad01bef01eeb963b578a42b81787c75/knockknock/joke_store.py#L128-L153" }
wardby:
  schema: 1
  roles: [builder, reviewer, planner]
  affects: ["knockknock/jokes.py", "knockknock/joke_store.py", "tests/test_web.py"]
  citations:
    - { id: migrations, repo: github:chfields/knock-knock-jokes, path: knockknock/joke_store.py, lines: [9, 12], symbol: BUILTIN_JOKE_MIGRATIONS, sha: 163e30946ad01bef01eeb963b578a42b81787c75, spanHash: sha256:fae53c831ec6fad6d0e1bbb8dbeb2e05abc29024e20c6ce96b2d28363609f5d7 }
    - { id: apply, repo: github:chfields/knock-knock-jokes, path: knockknock/joke_store.py, lines: [128, 153], symbol: PostgresJokeStore._apply_builtin_joke_migrations, sha: 163e30946ad01bef01eeb963b578a42b81787c75, spanHash: sha256:b777770160fe5d62ae06bcaaf61cd1bf9c84e1728474437af415475e1960a00e }
  confidence: high
---

The migration tuples name catalogue IDs,[^migrations] then the PostgreSQL
initialization code indexes `jokes_by_id` directly for each one before inserting
and recording the migration.[^apply] Renaming or removing a migrated built-in
therefore raises `KeyError` during initialization while that migration remains
unrecorded.

**What to do:** keep previously migrated IDs in `JOKES`. For a rename or removal,
add a deliberate migration path rather than changing the referenced ID silently.

[^migrations]: knockknock/joke_store.py, BUILTIN_JOKE_MIGRATIONS
[^apply]: knockknock/joke_store.py, PostgresJokeStore._apply_builtin_joke_migrations
