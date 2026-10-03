---
type: invariant
title: Per-voter data uses verified cookie IDs or IP hashes
description: Ratings receive a verified cookie ID or a SHA-256 client-IP fallback, never the signed cookie string or raw address.
tags: [ratings, privacy]
status: stable
generated: { by: knockknock-architect/gpt-5.6-terra, at: 2026-10-03T21:28:18Z }
sources:
  - { id: key, resource: "https://github.com/chfields/knock-knock-jokes/blob/3333698bdcaa149060a79d0392042fd68dd996f4/knockknock/web.py#L89-L100" }
  - { id: lookup, resource: "https://github.com/chfields/knock-knock-jokes/blob/3333698bdcaa149060a79d0392042fd68dd996f4/knockknock/web.py#L207-L218" }
  - { id: save, resource: "https://github.com/chfields/knock-knock-jokes/blob/3333698bdcaa149060a79d0392042fd68dd996f4/knockknock/web.py#L226-L241" }
wardby:
  schema: 1
  roles: [builder, reviewer]
  affects: ["knockknock/web.py", "knockknock/ratings.py"]
  citations:
    - { id: key, repo: github:chfields/knock-knock-jokes, path: knockknock/web.py, lines: [89, 100], symbol: _voter_key, sha: 3333698bdcaa149060a79d0392042fd68dd996f4, spanHash: sha256:ee61b7ad45722b99ac5da6107a3bc366d05302b4e16a49de4a9afbfa4c5d1b42 }
    - { id: lookup, repo: github:chfields/knock-knock-jokes, path: knockknock/web.py, lines: [207, 218], symbol: create_app.api_random_joke, sha: 3333698bdcaa149060a79d0392042fd68dd996f4, spanHash: sha256:be13c0c4fa738ef0982be78ee935b4d8f68891776876cdd71b9a990c5a6e9d8d }
    - { id: save, repo: github:chfields/knock-knock-jokes, path: knockknock/web.py, lines: [226, 241], symbol: create_app.api_rate_joke, sha: 3333698bdcaa149060a79d0392042fd68dd996f4, spanHash: sha256:86ddc8335886d9db60120c8b35eed9f56cb3657aa814fb5656d9f8a65ff1f33c }
  confidence: high
---

Anything stored or looked up per voter uses `_voter_key()`:[^key] a verified
`cookie:<id>` value from the signed voter cookie, else `ip:<sha256 of client
address>`. The signed cookie string and raw client address are not passed to the
rating store: API reads use the key for lookup[^lookup] and rating submissions use
it for persistence.[^save] A first-time visitor has no cookie yet, so their first
vote is keyed by IP hash.

**What to do:** pass `_voter_key()` to per-voter storage and lookup calls; do not
substitute an unverified cookie value or raw client address.

[^key]: knockknock/web.py, _voter_key
[^lookup]: knockknock/web.py, create_app.api_random_joke
[^save]: knockknock/web.py, create_app.api_rate_joke
