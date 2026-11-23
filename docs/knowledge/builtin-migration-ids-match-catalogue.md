---
type: invariant
title: Built-in migration IDs must exist in the current catalogue
description: Every joke ID listed by a built-in catalogue migration must be present in JOKES; a missing ID aborts PostgreSQL store initialization.
tags: [jokes, postgres, migrations, deployment]
status: stable
generated: { by: knockknock-architect/gpt-5.6-terra, at: 2026-11-23T06:03:34Z }
sources:
  - { id: migration, resource: "https://github.com/chfields/knock-knock-jokes/blob/163e30946ad01bef01eeb963b578a42b81787c75/knockknock/joke_store.py#L128-L153" }
wardby:
  schema: 1
  roles: [builder, reviewer, planner]
  affects: ["knockknock/jokes.py", "knockknock/joke_store.py", "tests/test_web.py"]
  citations:
    - { id: migration, repo: github:chfields/knock-knock-jokes, path: knockknock/joke_store.py, lines: [128, 153], symbol: PostgresJokeStore._apply_builtin_joke_migrations, sha: 163e30946ad01bef01eeb963b578a42b81787c75, spanHash: sha256:b777770160fe5d62ae06bcaaf61cd1bf9c84e1728474437af415475e1960a00e }
  confidence: high
---

`_apply_builtin_joke_migrations()` builds its lookup from the supplied current
catalogue, then directly indexes it for each ID in every unapplied migration.[^migration]
Consequently, removing or renaming a built-in that an older migration still
lists raises `KeyError` while the PostgreSQL store is starting.

**What to do:** keep migrated built-in IDs stable in `JOKES`. When retiring one,
preserve a compatible catalogue entry or change the migration strategy, and test
store initialization against an existing database.

[^migration]: knockknock/joke_store.py, PostgresJokeStore._apply_builtin_joke_migrations
