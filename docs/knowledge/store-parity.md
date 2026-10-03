---
type: invariant
title: Every store change lands in both backends
description: JokeStore and RatingStore each have a local implementation and a PostgreSQL one; behavior changes go into both, with tests for both.
tags: [jokes, ratings, postgres]
status: stable
generated: { by: knockknock-architect/gpt-5.6-terra, at: 2026-10-03T21:28:18Z }
sources:
  - { id: jmemory, resource: "https://github.com/chfields/knock-knock-jokes/blob/3333698bdcaa149060a79d0392042fd68dd996f4/knockknock/joke_store.py#L40-L47" }
  - { id: jpostgres, resource: "https://github.com/chfields/knock-knock-jokes/blob/3333698bdcaa149060a79d0392042fd68dd996f4/knockknock/joke_store.py#L71-L86" }
  - { id: rjsonl, resource: "https://github.com/chfields/knock-knock-jokes/blob/3333698bdcaa149060a79d0392042fd68dd996f4/knockknock/ratings.py#L81-L100" }
  - { id: rpostgres, resource: "https://github.com/chfields/knock-knock-jokes/blob/3333698bdcaa149060a79d0392042fd68dd996f4/knockknock/ratings.py#L133-L155" }
wardby:
  schema: 1
  roles: [builder, reviewer]
  affects: ["knockknock/joke_store.py", "knockknock/ratings.py", "tests/**"]
  citations:
    - { id: jmemory, repo: github:chfields/knock-knock-jokes, path: knockknock/joke_store.py, lines: [40, 47], symbol: MemoryJokeStore, sha: 3333698bdcaa149060a79d0392042fd68dd996f4, spanHash: sha256:358cd28536dde3a946e6092ba20be02ba0834795ae4ce1b1d6565652a69d42a9 }
    - { id: jpostgres, repo: github:chfields/knock-knock-jokes, path: knockknock/joke_store.py, lines: [71, 86], symbol: PostgresJokeStore, sha: 3333698bdcaa149060a79d0392042fd68dd996f4, spanHash: sha256:62f2883713ad7d7e08caa82c06bd062a25c1c6ffa2451cc507b2ebebb558b45b }
    - { id: rjsonl, repo: github:chfields/knock-knock-jokes, path: knockknock/ratings.py, lines: [81, 100], symbol: JsonlRatingStore, sha: 3333698bdcaa149060a79d0392042fd68dd996f4, spanHash: sha256:2ae7a6989e47febd6847f25d56ef833df8d4cbd5d72adaeafcf52ea510815075 }
    - { id: rpostgres, repo: github:chfields/knock-knock-jokes, path: knockknock/ratings.py, lines: [133, 155], symbol: PostgresRatingStore, sha: 3333698bdcaa149060a79d0392042fd68dd996f4, spanHash: sha256:ea514ade0804ba3177d0d7c034a2d5e4456a2847f869c8067b12e747269fc588 }
  confidence: high
---

`JokeStore` has `MemoryJokeStore`[^jmemory] and `PostgresJokeStore`[^jpostgres]
implementations; `RatingStore` has `JsonlRatingStore`[^rjsonl] and
`PostgresRatingStore`.[^rpostgres] A method or behavior added to one must be
added to its sibling, with a test for each; otherwise storage behavior diverges
by deployment choice.

**What to do:** implement and test every storage behavior in both backends.

[^jmemory]: knockknock/joke_store.py, MemoryJokeStore
[^jpostgres]: knockknock/joke_store.py, PostgresJokeStore
[^rjsonl]: knockknock/ratings.py, JsonlRatingStore
[^rpostgres]: knockknock/ratings.py, PostgresRatingStore
