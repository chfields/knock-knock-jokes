---
type: risk
title: Catalogue mutations have no authorization boundary
description: Any caller that can reach the web API can create or delete catalogue entries.
tags: [jokes, web, security]
status: stable
generated: { by: knockknock-architect/gpt-5.6-terra, at: 2026-10-03T21:28:18Z }
sources:
  - { id: create, resource: "https://github.com/chfields/knock-knock-jokes/blob/3333698bdcaa149060a79d0392042fd68dd996f4/knockknock/web.py#L185-L200" }
  - { id: delete, resource: "https://github.com/chfields/knock-knock-jokes/blob/3333698bdcaa149060a79d0392042fd68dd996f4/knockknock/web.py#L220-L224" }
wardby:
  schema: 1
  roles: [builder, reviewer, planner]
  affects: ["knockknock/web.py", "knockknock/joke_store.py", "web/src/**"]
  citations:
    - { id: create, repo: github:chfields/knock-knock-jokes, path: knockknock/web.py, lines: [185, 200], symbol: create_app.api_create_joke, sha: 3333698bdcaa149060a79d0392042fd68dd996f4, spanHash: sha256:16264bcdea6854dd53207c415f3a1a54390d718548247f8ee362bba77a634a5b }
    - { id: delete, repo: github:chfields/knock-knock-jokes, path: knockknock/web.py, lines: [220, 224], symbol: create_app.api_delete_joke, sha: 3333698bdcaa149060a79d0392042fd68dd996f4, spanHash: sha256:b46ff855c8670b2a16a2d6aba41f881056a730a86a07132535e753310e78d81a }
  confidence: high
---

The create route validates fields and persists the request, but has no caller
authorization check.[^create] The delete route likewise removes an entry directly
for any request that supplies an existing ID.[^delete] Deploying this API where
untrusted users can reach it therefore grants them catalogue-write access.

**What to do:** put an authorization boundary in front of these routes before
exposing them to untrusted users, and apply the same policy to both mutations.

[^create]: knockknock/web.py, create_app.api_create_joke
[^delete]: knockknock/web.py, create_app.api_delete_joke
