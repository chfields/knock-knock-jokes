---
type: risk
title: Deleting a joke leaves ratings that can attach to a replacement
description: Deleting a catalogue entry does not remove its ratings; recreating the same setup can reuse its ID and expose its prior scores and per-voter vote history.
tags: [jokes, ratings, deletion, data-retention]
status: stable
generated: { by: knockknock-architect/gpt-5.6-terra, at: 2026-10-05T06:03:13Z }
sources:
  - { id: endpoint, resource: "https://github.com/chfields/knock-knock-jokes/blob/8e2e7a2b7826cc6e5ec233e53b439f9792d88da4/knockknock/web.py#L220-L224" }
  - { id: memory, resource: "https://github.com/chfields/knock-knock-jokes/blob/8e2e7a2b7826cc6e5ec233e53b439f9792d88da4/knockknock/joke_store.py#L53-L69" }
  - { id: postgres, resource: "https://github.com/chfields/knock-knock-jokes/blob/8e2e7a2b7826cc6e5ec233e53b439f9792d88da4/knockknock/joke_store.py#L167-L196" }
  - { id: ratings, resource: "https://github.com/chfields/knock-knock-jokes/blob/8e2e7a2b7826cc6e5ec233e53b439f9792d88da4/knockknock/ratings.py#L111-L121" }
  - { id: votes, resource: "https://github.com/chfields/knock-knock-jokes/blob/8e2e7a2b7826cc6e5ec233e53b439f9792d88da4/knockknock/ratings.py#L81-L100" }
  - { id: postgres-ratings, resource: "https://github.com/chfields/knock-knock-jokes/blob/8e2e7a2b7826cc6e5ec233e53b439f9792d88da4/knockknock/ratings.py#L171-L184" }
  - { id: postgres-summary, resource: "https://github.com/chfields/knock-knock-jokes/blob/8e2e7a2b7826cc6e5ec233e53b439f9792d88da4/knockknock/ratings.py#L220-L234" }
wardby:
  schema: 1
  roles: [builder, reviewer, planner]
  affects: ["knockknock/web.py", "knockknock/joke_store.py", "knockknock/ratings.py", "tests/test_web.py"]
  citations:
    - { id: endpoint, repo: github:chfields/knock-knock-jokes, path: knockknock/web.py, lines: [220, 224], symbol: create_app.api_delete_joke, sha: 8e2e7a2b7826cc6e5ec233e53b439f9792d88da4, spanHash: sha256:b46ff855c8670b2a16a2d6aba41f881056a730a86a07132535e753310e78d81a }
    - { id: memory, repo: github:chfields/knock-knock-jokes, path: knockknock/joke_store.py, lines: [53, 69], symbol: "MemoryJokeStore.create and delete", sha: 8e2e7a2b7826cc6e5ec233e53b439f9792d88da4, spanHash: sha256:132173a992525ef4c09711fd76fcb5976a2aa801e6d0a6d080b0b6785199e1e2 }
    - { id: postgres, repo: github:chfields/knock-knock-jokes, path: knockknock/joke_store.py, lines: [167, 196], symbol: "PostgresJokeStore.create and delete", sha: 8e2e7a2b7826cc6e5ec233e53b439f9792d88da4, spanHash: sha256:cbe619cbde491784c9e5681c9a7348b98e2d63b02c66f8f8c1c3bfaad9264904 }
    - { id: ratings, repo: github:chfields/knock-knock-jokes, path: knockknock/ratings.py, lines: [111, 121], symbol: JsonlRatingStore.summaries, sha: 8e2e7a2b7826cc6e5ec233e53b439f9792d88da4, spanHash: sha256:af7d9cfe3fa140f57807dd1b626161b0702fc6845b7f92e11f8a003bc18a678c }
    - { id: votes, repo: github:chfields/knock-knock-jokes, path: knockknock/ratings.py, lines: [81, 100], symbol: JsonlRatingStore.save, sha: 8e2e7a2b7826cc6e5ec233e53b439f9792d88da4, spanHash: sha256:2ae7a6989e47febd6847f25d56ef833df8d4cbd5d72adaeafcf52ea510815075 }
    - { id: postgres-ratings, repo: github:chfields/knock-knock-jokes, path: knockknock/ratings.py, lines: [171, 184], symbol: PostgresRatingStore._create_schema, sha: 8e2e7a2b7826cc6e5ec233e53b439f9792d88da4, spanHash: sha256:8869229763dc97738b274f5efa82ce3f07e9d1847ac6d725bed8427e21e2a7a7 }
    - { id: postgres-summary, repo: github:chfields/knock-knock-jokes, path: knockknock/ratings.py, lines: [220, 234], symbol: PostgresRatingStore.summaries, sha: 8e2e7a2b7826cc6e5ec233e53b439f9792d88da4, spanHash: sha256:a3aaf3e352993dd9ec40af59fb033f486e52c53fef3a81505967b9aff771928a }
  confidence: high
---

The delete endpoint only deletes from the catalogue store; it never asks the
rating store to remove data.[^endpoint] Both catalogue stores derive a new
entry's base ID from its setup and make that base ID available again after
deletion.[^memory][^postgres] Both rating stores continue to aggregate records
by `joke_id`, so a replacement with that ID inherits the deleted entry's
scores; their stored voter keys also make old voters appear to have already
rated it.[^ratings][^votes][^postgres-ratings][^postgres-summary]

**What to do:** decide whether deletion is archival or permanent. For permanent
deletion, remove ratings for the ID atomically with the catalogue entry. For
archival deletion, retain a non-reusable identity or make the retained ratings
explicit in the product and deletion UI.

[^endpoint]: knockknock/web.py, create_app.api_delete_joke
[^memory]: knockknock/joke_store.py, MemoryJokeStore.create and delete
[^postgres]: knockknock/joke_store.py, PostgresJokeStore.create and delete
[^ratings]: knockknock/ratings.py, JsonlRatingStore.summaries
[^votes]: knockknock/ratings.py, JsonlRatingStore.save
[^postgres-ratings]: knockknock/ratings.py, PostgresRatingStore._create_schema
[^postgres-summary]: knockknock/ratings.py, PostgresRatingStore.summaries
