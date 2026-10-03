---
type: pitfall
title: Built-in jokes are seeded into PostgreSQL only once
description: Built-in additions need a one-time catalogue migration; re-seeding resurrects deletions.
tags: [jokes, postgres, deployment]
status: stable
generated: { by: human:chfields-spike, at: 2026-10-03T00:00:00Z }
sources:
  - { id: seed, resource: "https://github.com/chfields/knock-knock-jokes/blob/b92f0a0606448cf4d1163b0420644fac997e2c05/knockknock/joke_store.py#L99-L112" }
  - { id: select, resource: "https://github.com/chfields/knock-knock-jokes/blob/b92f0a0606448cf4d1163b0420644fac997e2c05/knockknock/web.py#L130-L138" }
wardby:
  schema: 1
  roles: [builder, reviewer, planner]
  affects: ["knockknock/jokes.py", "knockknock/joke_store.py"]
  citations:
    - { id: seed, repo: github:chfields/knock-knock-jokes, path: knockknock/joke_store.py, lines: [99, 112], symbol: PostgresJokeStore._seed, sha: b92f0a0606448cf4d1163b0420644fac997e2c05, spanHash: sha256:52acecc228a6274974fd0cbb986480cad4c4c1666c943d1f94b4ed557c4ab44b }
    - { id: select, repo: github:chfields/knock-knock-jokes, path: knockknock/web.py, lines: [120, 138], symbol: create_app, sha: b92f0a0606448cf4d1163b0420644fac997e2c05, spanHash: sha256:cb01667100806c5e2ed306a5a70436a13338b10e908b5d245b592c14040614cd }
  confidence: high
---

When `DATABASE_URL` is set (the deployed site), the web catalogue comes from the
`jokes` table, not from `JOKES`.[^select] `PostgresJokeStore._seed` copies `JOKES`
in **only when the table is empty**.[^seed] Therefore a built-in addition must also
have a one-time entry in `BUILTIN_JOKE_MIGRATIONS`, which records its application in
`builtin_joke_migrations` and adds it to existing deployments.

**Why it is this way:** jokes deleted through the web UI must stay deleted. Changing
`_seed` to insert missing built-ins on every start would bring deleted jokes back.

**What to do:** for a new built-in joke, add its ID to a new uniquely named
`BUILTIN_JOKE_MIGRATIONS` entry and test it against PostgreSQL. Never re-seed all
built-ins: that would resurrect deleted jokes. Editing a previously deployed
built-in's text still requires a dedicated migration.

[^seed]: knockknock/joke_store.py, PostgresJokeStore._seed
[^select]: knockknock/web.py, create_app store selection
