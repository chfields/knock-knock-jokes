---
type: invariant
title: Per-voter data is keyed by _voter_key(), never raw identity
description: Ratings are keyed by a signed-cookie id or a SHA-256 of the client IP; raw IPs and cookie values are never stored or returned.
tags: [ratings, privacy]
status: stable
generated: { by: human:chfields-spike, at: 2026-10-03T00:00:00Z }
sources:
  - { id: key, resource: "https://github.com/chfields/knock-knock-jokes/blob/b92f0a0606448cf4d1163b0420644fac997e2c05/knockknock/web.py#L89-L100" }
wardby:
  schema: 1
  roles: [builder, reviewer]
  affects: ["knockknock/web.py", "knockknock/ratings.py"]
  citations:
    - { id: key, repo: github:chfields/knock-knock-jokes, path: knockknock/web.py, lines: [89, 100], symbol: _voter_key, sha: b92f0a0606448cf4d1163b0420644fac997e2c05, spanHash: sha256:ee61b7ad45722b99ac5da6107a3bc366d05302b4e16a49de4a9afbfa4c5d1b42 }
  confidence: high
---

Anything stored or looked up per voter uses `_voter_key()`:[^key] `cookie:<id>` from
the signed voter cookie, else `ip:<sha256 of client address>`. Never persist, log,
or return a raw IP address or the cookie value. Note a first-time visitor has no
cookie yet, so their first vote is keyed by IP hash.

[^key]: knockknock/web.py, _voter_key
