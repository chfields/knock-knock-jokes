---
type: invariant
title: Every store change lands in both backends
description: JokeStore and RatingStore each have a local implementation and a PostgreSQL one; behavior changes go into both, with tests for both.
tags: [jokes, ratings, postgres]
status: stable
generated: { by: human:chfields-spike, at: 2026-10-03T00:00:00Z }
sources:
  - { id: jproto, resource: "https://github.com/chfields/knock-knock-jokes/blob/b92f0a0606448cf4d1163b0420644fac997e2c05/knockknock/joke_store.py#L14-L27" }
  - { id: rproto, resource: "https://github.com/chfields/knock-knock-jokes/blob/b92f0a0606448cf4d1163b0420644fac997e2c05/knockknock/ratings.py#L51-L62" }
wardby:
  schema: 1
  roles: [builder, reviewer]
  affects: ["knockknock/joke_store.py", "knockknock/ratings.py", "tests/**"]
  citations:
    - { id: jproto, repo: github:chfields/knock-knock-jokes, path: knockknock/joke_store.py, lines: [14, 27], symbol: JokeStore, sha: b92f0a0606448cf4d1163b0420644fac997e2c05, spanHash: sha256:e98cd29335ddbb769221e7a3a90e3129b2036c1c7cc6ddf3a4ceabd8ad083a61 }
    - { id: rproto, repo: github:chfields/knock-knock-jokes, path: knockknock/ratings.py, lines: [51, 62], symbol: RatingStore, sha: b92f0a0606448cf4d1163b0420644fac997e2c05, spanHash: sha256:22d935cf4aa99110afbd7d0387a4f24a937303cd697250b4e58d830f901f2ce9 }
  confidence: high
---

`JokeStore`[^jproto] is implemented by `MemoryJokeStore` and `PostgresJokeStore`;
`RatingStore`[^rproto] by `JsonlRatingStore` and `PostgresRatingStore`. The deployed
site runs only the PostgreSQL ones, local runs and most tests only the others.
A method or behavior added to one must be added to its sibling, with a test for
each. PostgreSQL tests skip unless `DATABASE_URL` is set — wardby coding runs
provide a PostgreSQL service, so run them there.

[^jproto]: knockknock/joke_store.py, JokeStore
[^rproto]: knockknock/ratings.py, RatingStore
