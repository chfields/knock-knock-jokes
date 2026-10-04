---
type: risk
title: Every web response provisions a persistent voter cookie
description: A request without a valid voter cookie receives a signed, one-year cookie even when it does not view or submit a rating.
tags: [ratings, privacy, cookies, web]
status: stable
generated: { by: knockknock-architect/gpt-5.6-terra, at: 2026-10-03T21:28:18Z }
sources:
  - { id: create, resource: "https://github.com/chfields/knock-knock-jokes/blob/3333698bdcaa149060a79d0392042fd68dd996f4/knockknock/web.py#L67-L86" }
  - { id: response, resource: "https://github.com/chfields/knock-knock-jokes/blob/3333698bdcaa149060a79d0392042fd68dd996f4/knockknock/web.py#L140-L152" }
wardby:
  schema: 1
  roles: [builder, reviewer, planner]
  affects: ["knockknock/web.py", "tests/test_web.py", "README.md"]
  citations:
    - { id: create, repo: github:chfields/knock-knock-jokes, path: knockknock/web.py, lines: [67, 86], symbol: _voter_id, sha: 3333698bdcaa149060a79d0392042fd68dd996f4, spanHash: sha256:2bdb6c923a884647a2fc9a81e9cdda3c4211dc6ffc25f2cbfd5fc94692022cb5 }
    - { id: response, repo: github:chfields/knock-knock-jokes, path: knockknock/web.py, lines: [140, 152], symbol: create_app.set_voter_cookie, sha: 3333698bdcaa149060a79d0392042fd68dd996f4, spanHash: sha256:17b8f0266845e5d5d115f0af369d31745ec724fca11970cd0a5d82ae112ce5a4 }
  confidence: high
---

`set_voter_cookie()` runs after every request and calls `_voter_id()` even when
the route did not read or write rating data.[^response] Without a valid cookie,
`_voter_id()` creates a random ID and marks it for persistence.[^create] The
response then sends its signed cookie for one year; `HttpOnly`, `SameSite=Lax`,
and conditional `Secure` flags limit exposure but do not make issuance opt-in.

**What to do:** treat ordinary browsing as persistent-identifier issuance in
privacy and consent decisions. If passive visitors must remain cookieless,
create the voter ID only on rating-related flows and test the resulting
first-vote behavior.

[^create]: knockknock/web.py, _voter_id
[^response]: knockknock/web.py, create_app.set_voter_cookie
