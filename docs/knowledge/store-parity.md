---
type: invariant
title: Shared store behavior lands in both backends
description: JokeStore and RatingStore each have a local implementation and a PostgreSQL one; shared public behavior changes go into both, with tests for both.
tags: [jokes, ratings, postgres]
status: stable
generated: { by: knockknock-architect/gpt-5.6-terra, at: 2026-10-04T00:32:13Z }
sources:
  - { id: jmemory, resource: "https://github.com/chfields/knock-knock-jokes/blob/6e3aafb6e0ace0132522c3cdca6c0bf1c1893887/knockknock/joke_store.py#L40-L69" }
  - { id: jpostgres, resource: "https://github.com/chfields/knock-knock-jokes/blob/6e3aafb6e0ace0132522c3cdca6c0bf1c1893887/knockknock/joke_store.py#L72-L196" }
  - { id: rjsonl, resource: "https://github.com/chfields/knock-knock-jokes/blob/3333698bdcaa149060a79d0392042fd68dd996f4/knockknock/ratings.py#L81-L100" }
  - { id: rpostgres, resource: "https://github.com/chfields/knock-knock-jokes/blob/3333698bdcaa149060a79d0392042fd68dd996f4/knockknock/ratings.py#L133-L155" }
wardby:
  schema: 1
  roles: [builder, reviewer]
  affects: ["knockknock/joke_store.py", "knockknock/ratings.py", "tests/**"]
  citations:
    - { id: jmemory, repo: github:chfields/knock-knock-jokes, path: knockknock/joke_store.py, lines: [40, 69], symbol: MemoryJokeStore, sha: 6e3aafb6e0ace0132522c3cdca6c0bf1c1893887, spanHash: sha256:1c9993f0162bf582f455976c26a4ed6ea77b0b0f96692f449b43a19de13217f5 }
    - { id: jpostgres, repo: github:chfields/knock-knock-jokes, path: knockknock/joke_store.py, lines: [72, 196], symbol: PostgresJokeStore, sha: 6e3aafb6e0ace0132522c3cdca6c0bf1c1893887, spanHash: sha256:33e7e4b9d5e9ab17007958dd009b42a8534b23cc0d35cbea2ef3eb40657b9842 }
    - { id: rjsonl, repo: github:chfields/knock-knock-jokes, path: knockknock/ratings.py, lines: [81, 100], symbol: JsonlRatingStore, sha: 3333698bdcaa149060a79d0392042fd68dd996f4, spanHash: sha256:2ae7a6989e47febd6847f25d56ef833df8d4cbd5d72adaeafcf52ea510815075 }
    - { id: rpostgres, repo: github:chfields/knock-knock-jokes, path: knockknock/ratings.py, lines: [133, 155], symbol: PostgresRatingStore, sha: 3333698bdcaa149060a79d0392042fd68dd996f4, spanHash: sha256:ea514ade0804ba3177d0d7c034a2d5e4456a2847f869c8067b12e747269fc588 }
  confidence: high
---

`JokeStore` has `MemoryJokeStore`[^jmemory] and `PostgresJokeStore`[^jpostgres]
implementations; `RatingStore` has `JsonlRatingStore`[^rjsonl] and
`PostgresRatingStore`.[^rpostgres] A shared public method or behavior added to one
must be added to its sibling, with a test for each; otherwise storage behavior
diverges by deployment choice. Backend-specific implementation details, such as
PostgreSQL's durable built-in-catalogue migrations, need not be mirrored locally.

**What to do:** implement and test every shared storage behavior in both backends;
keep backend-specific durability mechanisms scoped to the backend that needs them.

[^jmemory]: knockknock/joke_store.py, MemoryJokeStore
[^jpostgres]: knockknock/joke_store.py, PostgresJokeStore
[^rjsonl]: knockknock/ratings.py, JsonlRatingStore
[^rpostgres]: knockknock/ratings.py, PostgresRatingStore
