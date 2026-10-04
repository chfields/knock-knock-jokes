---
type: pitfall
title: Built-in jokes are seeded into PostgreSQL only once
description: Built-in additions need a one-time catalogue migration; re-seeding resurrects deletions.
tags: [jokes, postgres, deployment]
status: stable
generated: { by: knockknock-architect/gpt-5.6-terra, at: 2026-10-03T21:28:18Z }
sources:
  - { id: seed, resource: "https://github.com/chfields/knock-knock-jokes/blob/6e3aafb6e0ace0132522c3cdca6c0bf1c1893887/knockknock/joke_store.py#L112-L125" }
  - { id: migration, resource: "https://github.com/chfields/knock-knock-jokes/blob/6e3aafb6e0ace0132522c3cdca6c0bf1c1893887/knockknock/joke_store.py#L127-L152" }
  - { id: select, resource: "https://github.com/chfields/knock-knock-jokes/blob/3333698bdcaa149060a79d0392042fd68dd996f4/knockknock/web.py#L130-L138" }
wardby:
  schema: 1
  roles: [builder, reviewer, planner]
  affects: ["knockknock/jokes.py", "knockknock/joke_store.py"]
  citations:
    - { id: seed, repo: github:chfields/knock-knock-jokes, path: knockknock/joke_store.py, lines: [112, 125], symbol: PostgresJokeStore._seed, sha: 6e3aafb6e0ace0132522c3cdca6c0bf1c1893887, spanHash: sha256:52acecc228a6274974fd0cbb986480cad4c4c1666c943d1f94b4ed557c4ab44b }
    - { id: migration, repo: github:chfields/knock-knock-jokes, path: knockknock/joke_store.py, lines: [127, 152], symbol: PostgresJokeStore._apply_builtin_joke_migrations, sha: 6e3aafb6e0ace0132522c3cdca6c0bf1c1893887, spanHash: sha256:b777770160fe5d62ae06bcaaf61cd1bf9c84e1728474437af415475e1960a00e }
    - { id: select, repo: github:chfields/knock-knock-jokes, path: knockknock/web.py, lines: [130, 138], symbol: create_app, sha: 3333698bdcaa149060a79d0392042fd68dd996f4, spanHash: sha256:7eb25a3a5b55a04e6c1d6f0b75c211c7ab9883855ccabc7ed90b0e414e6b9206 }
  confidence: high
---

When `DATABASE_URL` is set (the deployed site), the web catalogue comes from the
`jokes` table, not from `JOKES`.[^select] `PostgresJokeStore._seed` copies `JOKES`
in **only when the table is empty**.[^seed] Therefore a built-in addition must also
have a one-time entry in `BUILTIN_JOKE_MIGRATIONS`, which records its application in
`builtin_joke_migrations` and adds it to existing deployments.[^migration]

**Why it is this way:** jokes deleted through the web UI must stay deleted. Changing
`_seed` to insert missing built-ins on every start would bring deleted jokes back.

**What to do:** for a new built-in joke, add its ID to a new uniquely named
`BUILTIN_JOKE_MIGRATIONS` entry and test it against PostgreSQL. Never re-seed all
built-ins: that would resurrect deleted jokes. Editing a previously deployed
built-in's text still requires a dedicated migration.

[^seed]: knockknock/joke_store.py, PostgresJokeStore._seed
[^migration]: knockknock/joke_store.py, PostgresJokeStore._apply_builtin_joke_migrations
[^select]: knockknock/web.py, create_app store selection
