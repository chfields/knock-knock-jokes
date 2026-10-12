---
type: pitfall
title: Local catalogue mutations are ephemeral while ratings persist
description: Without DATABASE_URL, a process uses a fresh in-memory catalogue but a JSONL rating store, so added or deleted web jokes disappear at restart while their ratings remain.
tags: [jokes, ratings, persistence, web]
status: stable
generated: { by: knockknock-architect/gpt-5.6-terra, at: 2026-10-12T06:03:33Z }
sources:
  - { id: selection, resource: "https://github.com/chfields/knock-knock-jokes/blob/1ed17ef7e564a1024358afaec6a8f7b20ead7c68/knockknock/web.py#L104-L138" }
wardby:
  schema: 1
  roles: [builder, reviewer, planner]
  affects: ["knockknock/web.py", "knockknock/joke_store.py", "knockknock/ratings.py", "tests/test_web.py"]
  citations:
    - { id: selection, repo: github:chfields/knock-knock-jokes, path: knockknock/web.py, lines: [104, 138], symbol: create_app, sha: 1ed17ef7e564a1024358afaec6a8f7b20ead7c68, spanHash: sha256:595f29873638a8c81c7e2af6db016e08445249281d506b23274fc0189c68325b }
  confidence: high
---

When neither store is injected and `DATABASE_URL` is absent, `create_app()`
selects `JsonlRatingStore` for ratings but constructs `MemoryJokeStore(JOKES)`
for the catalogue.[^selection] A new application process therefore restores the
built-in catalogue, discarding web-created entries and restoring deleted ones,
while the JSONL ratings file retains ratings by joke ID. The README documents
the two backend choices but not this differing restart behavior.

**What to do:** use PostgreSQL when web catalogue changes must survive a
restart. Treat local web mutations as temporary during development, and do not
interpret persisted local ratings as evidence that their catalogue changes also
persisted.

[^selection]: knockknock/web.py, create_app backend selection
