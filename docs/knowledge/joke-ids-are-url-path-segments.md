---
type: invariant
title: Joke IDs are single URL path segments
description: "Web-facing joke IDs must not contain slashes: the domain accepts any nonempty ID, while routes address a joke through one path segment."
tags: [jokes, web, routing]
status: stable
generated: { by: knockknock-architect/gpt-5.6-terra, at: 2026-10-26T06:04:15Z }
sources:
  - { id: validation, resource: "https://github.com/chfields/knock-knock-jokes/blob/163e30946ad01bef01eeb963b578a42b81787c75/knockknock/jokes.py#L9-L20" }
  - { id: generated-id, resource: "https://github.com/chfields/knock-knock-jokes/blob/163e30946ad01bef01eeb963b578a42b81787c75/knockknock/joke_store.py#L35-L38" }
  - { id: route, resource: "https://github.com/chfields/knock-knock-jokes/blob/163e30946ad01bef01eeb963b578a42b81787c75/knockknock/web.py#L215-L218" }
wardby:
  schema: 1
  roles: [builder, reviewer, planner]
  affects: ["knockknock/jokes.py", "knockknock/joke_store.py", "knockknock/web.py", "web/src/api.ts"]
  citations:
    - { id: validation, repo: github:chfields/knock-knock-jokes, path: knockknock/jokes.py, lines: [9, 20], symbol: Joke.__post_init__, sha: 163e30946ad01bef01eeb963b578a42b81787c75, spanHash: sha256:d6090149b9b6e1f23b537b6606befccd370f39d3e9cb52c22344be216c01019b }
    - { id: generated-id, repo: github:chfields/knock-knock-jokes, path: knockknock/joke_store.py, lines: [35, 38], symbol: _joke_id, sha: 163e30946ad01bef01eeb963b578a42b81787c75, spanHash: sha256:28e6289cdc5b08c493e3fc26fa708d53bf725a239add70810bcfcf7dd506a259 }
    - { id: route, repo: github:chfields/knock-knock-jokes, path: knockknock/web.py, lines: [215, 218], symbol: create_app.api_joke_detail, sha: 163e30946ad01bef01eeb963b578a42b81787c75, spanHash: sha256:bc200f58de2c6042a2cca7f7bc004d1552c4488d3eba743cb3d6364986a050f9 }
  confidence: high
---

`Joke` only rejects an empty ID, so a built-in or imported catalogue can supply
an ID that is not safe to place in a URL.[^validation] The web detail endpoint
uses the default Flask `<joke_id>` path converter, which accepts one segment
only.[^route] User-created IDs pass through `_joke_id()`, which already reduces
them to lower-case letters, digits, and hyphens.[^generated-id]

**What to do:** keep every built-in or imported ID to one URL-safe path segment,
or change the route and client URL construction together before allowing other
characters.

[^validation]: knockknock/jokes.py, Joke.__post_init__
[^generated-id]: knockknock/joke_store.py, _joke_id
[^route]: knockknock/web.py, create_app.api_joke_detail
