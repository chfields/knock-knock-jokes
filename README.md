# Knock-knock jokes

A small Python package and command-line program for telling classic knock-knock jokes.

## Install

From this repository, install the package in editable mode:

```bash
python -m pip install -e .
```

The core command-line app has no required third-party dependencies.

## Usage

Tell a random joke:

```bash
python -m knockknock
```

List the available jokes:

```bash
python -m knockknock --list
```

Tell a joke by its zero-based index or setup name:

```bash
python -m knockknock --joke 0
python -m knockknock --joke Lettuce
```

An optional JSON configuration file can be supplied at startup:

```bash
python -m knockknock --config config.json --rate
```

The supported setting is `rating_store`, which is overridden by an explicit
`--rating-store` argument. The config path must exist and refer to a file.

Ratings are optional. Enable the interactive prompt with `--rate`; press Enter
to skip, or enter a number from 1 to 5. In an interactive CLI, the prompt also
skips automatically after 10 seconds with no input. In a non-interactive CLI,
rating collection is skipped by default without prompting. Invalid input gets
one retry and is then skipped.
Set `KNOCK_KNOCK_RATING_SKIP_SECONDS` to change the interactive prompt timeout.
You can override it for one invocation with `--skip-seconds`, for example
`python -m knockknock --rate --skip-seconds 3`.
To persist this setting across sessions, add it to your shell's configuration
file, such as `~/.profile`.
Ratings are appended to
`~/.local/share/knockknock/ratings.jsonl` (or a path supplied with
`--rating-store`) and are never requested by default or by `--list`. The file
is local append-only history; remove it when ratings should be discarded.

The same functionality is available through the installed `knockknock` command.

## Optional web front end

Install the web extra to use the Flask application:

```bash
python -m pip install -e '.[web]'
```

Build it with `knockknock.web.create_app()`. Set `RATING_STORE_PATH` to an
explicit writable path when deploying it. The default JSONL file is local,
append-only rating history; it is intended for a trusted local environment,
and concurrent web workers need an operationally appropriate store before
production use.

Set `KNOCKKNOCK_SECRET_KEY` to a private, stable value in deployed web
applications. Flask uses it for sessions and the application uses it to sign
voter-identity cookies; changing it invalidates existing voter cookies.

Set `DATABASE_URL` to use PostgreSQL for ratings and the web catalogue. The
first connection seeds the built-in jokes; jokes added through the web UI and
deletions are persisted there. If the application is behind reverse proxies,
set `KNOCKKNOCK_TRUSTED_PROXIES` to the number of trusted proxy hops so Flask
uses `X-Forwarded-For` for the client address. It defaults to `0`, which leaves
forwarded addresses untrusted.

PostgreSQL-backed ratings also require the `postgres` extra:

```bash
python -m pip install 'knock-knock-jokes[postgres]'
```

PostgreSQL strictly guarantees one vote per voter. The JSONL fallback checks
for duplicate votes, but that check is not atomic across concurrent writers,
so concurrent requests may record duplicate votes.

Build the React frontend from `web/` with:

```bash
npm ci && npm run build
```

The build is written to `web/dist`, which the Flask application serves.

## Deploying to Vercel

The repository deploys to [Vercel](https://vercel.com) as a single Python
function. `app.py` is the entrypoint; `vercel.json` builds `web/` first, and
the build output in `web/dist` ships with the function. Runtime dependencies
are listed in `requirements.txt`: Vercel installs only the base dependencies
from `pyproject.toml`, which are empty, so the build command installs
`requirements.txt` into Vercel's build environment before building `web/`.

With the Vercel project connected to this repository, every pull request gets
a preview deployment and every merge to `main` deploys to production. Set
these environment variables on the Vercel project:

- `DATABASE_URL` — PostgreSQL connection string. Use a pooled connection
  (for example, Neon's pooled URL), because each function instance opens its
  own connection pools.
- `KNOCKKNOCK_SECRET_KEY` — required; the entrypoint refuses to start
  without it.
- `KNOCKKNOCK_TRUSTED_PROXIES` — set to `1` so Flask reads the client address
  from Vercel's `X-Forwarded-For` header.

Without `DATABASE_URL` the app falls back to the local JSONL rating file,
which a Vercel function cannot write to, so ratings fail to save.

## Development

Run the test suite with `pytest`:

```bash
pytest
```
