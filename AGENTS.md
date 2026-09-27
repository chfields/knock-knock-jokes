# Working in this repository

Directions for coding agents (Codex, Claude Code, wardby) and for people.
Keep this file current: a change that moves code, adds a command, or changes
how something is built or tested updates this file in the same pull request.

## Layout

- `knockknock/` — the Python package (Python 3.9+; its core has no required
  third-party dependencies, with optional PostgreSQL support via psycopg):
  - `jokes.py` — the joke catalogue (`JOKES`) and lookup (`get_joke`)
  - `ratings.py` — joke ratings and their storage
  - `sequence.py` — the knock-knock exchange
  - `__main__.py` — the command-line program (`python -m knockknock`)
  - `web.py` — the Flask app and its JSON API (`/api/...`); `templates/` holds
    the server-rendered fallback pages
- `tests/` — pytest tests for the package, the CLI and the Flask app
- `web/` — the front end: React 19 + TypeScript + Vite, HeroUI 3 and
  Tailwind 4, tested with Vitest and Testing Library. It is the only npm
  project in the repository.
  - `web/src/api.ts` — every call to the Flask API goes through here
  - `web/src/App.tsx` — the app; `web/src/App.test.tsx` — its tests
- `docs/` — design notes and plans

## Python

Run from the repository root (pytest imports `knockknock` from there; no
editable install is needed):

```bash
python -m venv --system-site-packages .venv
.venv/bin/python -m pip install flask pytest ruff
.venv/bin/python -m pytest
.venv/bin/python -m ruff check .
```

CI also runs bandit and pip-audit (`pip install ".[lint]"`), on Python 3.9
and 3.12. Code must
run on 3.9: no `match`, and no `X | Y` type unions at runtime without
`from __future__ import annotations`.

PostgreSQL-backed ratings need the optional extra:

```bash
python -m pip install 'knock-knock-jokes[postgres]'
```

Only the PostgreSQL store strictly guarantees one vote per voter. The JSONL
fallback checks for duplicates but is not atomic across concurrent writers, so
concurrent requests may record duplicate votes.

## Front end

Run npm only in a directory that already has the `package.json` you are
working on — here, `web/`. Never run npm at the repository root, and never
create a new `package.json` or lockfile unless the task asks for a new
JavaScript project.

```bash
cd web
npm ci            # or npm install <pkg> when adding a dependency
npm test
npm run build     # tsc --noEmit, then vite build
```

Commit `web/package-lock.json` with any dependency change. `node_modules/`
and `dist/` are never committed.

## Conventions

- Reuse what exists: joke lookup is `get_joke()` in `knockknock/jokes.py`,
  not re-implemented in `web.py` or the CLI; front-end API calls belong in
  `web/src/api.ts`.
- Keep functions, modules and components small and focused; keep business
  logic out of Flask views and out of React components that render.
- Every change comes with tests: new behavior, edge cases, and a regression
  test for every bug fix. Front-end changes need both `npm test` and
  `npm run build` to pass.
- Follow the existing style: dataclasses, type hints and docstrings in
  Python; the existing data format for jokes.
- Do not change `.github/`, `CODEOWNERS`, or dependency manifests unless the
  task asks for it.
