---
type: risk
title: The Flask factory's default secret makes direct deployments forgeable
description: A deployment that calls create_app without KNOCKKNOCK_SECRET_KEY uses a public signing key, allowing forged voter cookies and Flask sessions.
tags: [web, security, deployment, cookies]
status: stable
generated: { by: knockknock-architect/gpt-5.6-terra, at: 2026-11-02T06:03:36Z }
sources:
  - { id: factory, resource: "https://github.com/chfields/knock-knock-jokes/blob/163e30946ad01bef01eeb963b578a42b81787c75/knockknock/web.py#L103-L114" }
  - { id: serializer, resource: "https://github.com/chfields/knock-knock-jokes/blob/163e30946ad01bef01eeb963b578a42b81787c75/knockknock/web.py#L62-L64" }
  - { id: vercel-entrypoint, resource: "https://github.com/chfields/knock-knock-jokes/blob/163e30946ad01bef01eeb963b578a42b81787c75/app.py#L5-L10" }
wardby:
  schema: 1
  roles: [builder, reviewer, planner]
  affects: ["knockknock/web.py", "app.py", "README.md", "tests/test_vercel_entrypoint.py"]
  citations:
    - { id: factory, repo: github:chfields/knock-knock-jokes, path: knockknock/web.py, lines: [103, 114], symbol: create_app, sha: 163e30946ad01bef01eeb963b578a42b81787c75, spanHash: sha256:471bcd9999f909cd3174882efee2427184beecf2e89132eee385944b3f6cfcdc }
    - { id: serializer, repo: github:chfields/knock-knock-jokes, path: knockknock/web.py, lines: [62, 64], symbol: _voter_serializer, sha: 163e30946ad01bef01eeb963b578a42b81787c75, spanHash: sha256:a63f2ae341b4ad184f2de52f879ab2b1c633e0107e6ac1d6f1fa309d71630364 }
    - { id: vercel-entrypoint, repo: github:chfields/knock-knock-jokes, path: app.py, lines: [5, 10], symbol: app, sha: 163e30946ad01bef01eeb963b578a42b81787c75, spanHash: sha256:d61d3f2b7b05930c5eb26e26855d7e198ded0c1157de79017fe0e745be34b040 }
  confidence: high
---

create_app() uses the literal knockknock-local-web secret when the environment
variable is absent.[^factory] Flask uses that secret for its sessions, and the
voter-cookie serializer uses the same application secret.[^serializer] Anyone
can therefore mint a cookie for a chosen voter ID in a direct deployment that
relies on the fallback, defeating the per-voter vote check as well as session
integrity. The Vercel entrypoint rejects a missing environment secret, but that
protection is not part of the factory.[^vercel-entrypoint]

**What to do:** every production entrypoint that invokes create_app() must
require a private, stable KNOCKKNOCK_SECRET_KEY; consider making the factory
reject the fallback outside explicitly configured local development and tests.

[^factory]: knockknock/web.py, create_app
[^serializer]: knockknock/web.py, _voter_serializer
[^vercel-entrypoint]: app.py, application entrypoint
