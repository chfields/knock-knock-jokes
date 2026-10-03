---
type: pitfall
title: Trusted proxy count controls the fallback voter identity
description: The IP-hash fallback trusts forwarded addresses only when KNOCKKNOCK_TRUSTED_PROXIES matches the deployed proxy chain.
tags: [ratings, privacy, deployment, proxy]
status: stable
generated: { by: knockknock-architect/gpt-5.6-terra, at: 2026-10-03T19:22:19Z }
sources:
  - { id: voter-key, resource: "https://github.com/chfields/knock-knock-jokes/blob/db6e4fa032e52c80670a86918faead2c7fe790bc/knockknock/web.py#L89-L100" }
  - { id: proxy, resource: "https://github.com/chfields/knock-knock-jokes/blob/db6e4fa032e52c80670a86918faead2c7fe790bc/knockknock/web.py#L111-L118" }
wardby:
  schema: 1
  roles: [builder, reviewer, planner]
  affects: ["knockknock/web.py", "tests/test_web.py", "app.py", "vercel.json"]
  citations:
    - { id: voter-key, repo: github:chfields/knock-knock-jokes, path: knockknock/web.py, lines: [89, 100], symbol: _voter_key, sha: db6e4fa032e52c80670a86918faead2c7fe790bc, spanHash: sha256:ee61b7ad45722b99ac5da6107a3bc366d05302b4e16a49de4a9afbfa4c5d1b42 }
    - { id: proxy, repo: github:chfields/knock-knock-jokes, path: knockknock/web.py, lines: [111, 118], symbol: create_app, sha: db6e4fa032e52c80670a86918faead2c7fe790bc, spanHash: sha256:727727122d3ef860e4b721bcc8eed9785c58fd25ff24760dc1ff16c7eb128afa }
  confidence: high
---

For visitors without a valid signed cookie, `_voter_key()` derives the one-vote
identity from `request.remote_addr`.[^voter-key] `create_app()` applies
`ProxyFix` only when `KNOCKKNOCK_TRUSTED_PROXIES` is positive, and trusts exactly
that many `X-Forwarded-*` hops.[^proxy] A deployment change must set this number
to the actual trusted reverse-proxy chain: too low collapses visitors to the
proxy address, while too high lets untrusted forwarded-address values affect the
fallback identity.

**What to do:** update `KNOCKKNOCK_TRUSTED_PROXIES` with proxy topology changes
and retain tests for both direct and proxied request handling.

[^voter-key]: knockknock/web.py, _voter_key
[^proxy]: knockknock/web.py, create_app proxy configuration
