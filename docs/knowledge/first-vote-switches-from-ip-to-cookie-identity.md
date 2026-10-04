---
type: risk
title: A first direct vote switches from IP to cookie identity
description: A visitor who first submits a rating without a valid voter cookie can rate that joke once by IP hash and again by the newly issued cookie identity.
tags: [ratings, voters, cookies, privacy]
status: stable
generated: { by: knockknock-architect/gpt-5.6-terra, at: 2026-10-03T21:34:30Z }
sources:
  - { id: key, resource: "https://github.com/chfields/knock-knock-jokes/blob/197a5d64ac0143c4180130045d4a5419e42c7af6/knockknock/web.py#L89-L100" }
  - { id: response, resource: "https://github.com/chfields/knock-knock-jokes/blob/197a5d64ac0143c4180130045d4a5419e42c7af6/knockknock/web.py#L140-L152" }
  - { id: save, resource: "https://github.com/chfields/knock-knock-jokes/blob/197a5d64ac0143c4180130045d4a5419e42c7af6/knockknock/web.py#L226-L241" }
wardby:
  schema: 1
  roles: [builder, reviewer, planner]
  affects: ["knockknock/web.py", "knockknock/ratings.py", "tests/test_web.py"]
  citations:
    - { id: key, repo: github:chfields/knock-knock-jokes, path: knockknock/web.py, lines: [89, 100], symbol: _voter_key, sha: 197a5d64ac0143c4180130045d4a5419e42c7af6, spanHash: sha256:ee61b7ad45722b99ac5da6107a3bc366d05302b4e16a49de4a9afbfa4c5d1b42 }
    - { id: response, repo: github:chfields/knock-knock-jokes, path: knockknock/web.py, lines: [140, 152], symbol: create_app.set_voter_cookie, sha: 197a5d64ac0143c4180130045d4a5419e42c7af6, spanHash: sha256:17b8f0266845e5d5d115f0af369d31745ec724fca11970cd0a5d82ae112ce5a4 }
    - { id: save, repo: github:chfields/knock-knock-jokes, path: knockknock/web.py, lines: [226, 241], symbol: create_app.api_rate_joke, sha: 197a5d64ac0143c4180130045d4a5419e42c7af6, spanHash: sha256:86ddc8335886d9db60120c8b35eed9f56cb3657aa814fb5656d9f8a65ff1f33c }
  confidence: high
---

`api_rate_joke()` saves the rating under `_voter_key()` before the response is
sent.[^save] With no valid request cookie, that key is an IP hash rather than
the generated voter ID.[^key] The after-request handler then creates and sends
a voter cookie, so the next request uses `cookie:<id>` instead.[^response]
Neither backend treats those two keys as the same voter, allowing a second
rating for the same joke when the first request was a direct vote rather than a
prior page or API visit.

**What to do:** keep the key stable across the initial rating response and its
later requests (for example, derive it from `_voter_id()`), and add a regression
test that directly posts twice with the same client.

[^key]: knockknock/web.py, _voter_key
[^response]: knockknock/web.py, create_app.set_voter_cookie
[^save]: knockknock/web.py, create_app.api_rate_joke
