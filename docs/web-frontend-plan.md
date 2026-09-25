# Web front-end implementation plan

## Goal and boundaries

Add a React single-page web UI for browsing and telling the jokes already
provided by this package. A visitor should be able to open a page, receive a
random joke, choose a joke from the catalogue, see the same five-line
call-and-response sequence as the CLI, and optionally submit a 1–5 rating.
The web layer should be a presentation and request-handling layer; the joke
catalogue and wording remain owned by the package.

The current design gives the front end a useful seam to build on:

- `knockknock/jokes.py` defines the frozen `Joke` value object, the ordered
  `JOKES` tuple, and case-insensitive `get_joke()` lookup.
- `knockknock/sequence.py` defines `tell(joke)`, which returns the canonical
  five strings to display.
- `knockknock/ratings.py` defines validation in `Rating`, timestamp creation in
  `Rating.now()`, the `RatingStore` protocol, and append-only persistence in
  `JsonlRatingStore`.
- `knockknock/__main__.py` should remain CLI-specific. In particular,
  `_collect_rating()` depends on TTY input and `select`, so it is not a web
  request handler.

Do not copy the joke text or five-line formatting into templates. Templates
should receive `Joke` data and the list returned by `tell()`.

## Framework recommendation

Use Flask for the first web implementation, as an optional runtime dependency
(`flask` should not become a mandatory dependency for users who only install
the CLI). Flask is small, supports Python 3.9, has straightforward route and
test-client APIs, and fits this repository's existing synchronous,
standard-library-sized design. It also allows the front end to be added as a
separate module without changing `main()` or the package exports.

Flask remains the small server boundary, while React and HeroUI provide the
client-side application. Flask exposes the small JSON API and serves the Vite
build, keeping deployment simple without adding a second server.

## Proposed implementation shape

Add a web module (for example, `knockknock/web.py`) and keep application
construction in a factory such as `create_app(config=None)`. The factory
should accept a rating-store path and testing configuration rather than read
process-global state during import. Add templates and static assets only as
needed by the chosen Flask layout; this plan does not authorize implementing
them now.

Use the existing objects as follows:

1. For the random page, choose an element from `JOKES` and pass it to
   `tell()`. This is the web equivalent of the default branch in `main()`;
   it must not create a second catalogue or second sequence formatter.
2. For a selected joke, resolve a URL-safe stable identifier from the
   existing `Joke.id` values (`cow-says`, `lettuce`, and so on). The resolver
   should reject unknown IDs with a 404. If a reusable ID lookup is needed,
   add it next to `get_joke()` in the domain module rather than embedding
   catalogue-specific matching rules in a route.
3. Pass the selected `Joke` and `tell(joke)` result to the template. The
   template may present the five lines as a list or a conversational layout,
   but the words must come from `tell()`.
4. On rating submission, validate through `Rating.now(joke.id, value)` and
   persist through an injected `RatingStore` (the default being
   `JsonlRatingStore`). Do not call `_collect_rating()` and do not duplicate
   the 1–5 validation. The web handler should return a useful error page or
   redisplay the form for invalid input, while treating storage failures as a
   controlled server error.

Keep the default store path configurable. The existing CLI default is
`~/.local/share/knockknock/ratings.jsonl`; a deployed web process should be
given an explicit writable path rather than assuming a user home directory.
Document that the JSONL file is local append-only history and that concurrent
web workers need an operationally appropriate store before production use.

## Routes and pages

Implement the smallest useful set of routes:

- `GET /` — show a random joke, using the same five-line sequence, with links
  to the catalogue and to another random joke.
- `GET /jokes` — show every entry in `JOKES` in catalogue order, linking by
  stable `Joke.id`.
- `GET /jokes/<joke_id>` — show one selected joke; unknown IDs return 404.
- `POST /jokes/<joke_id>/ratings` — accept a form value from 1 through 5,
  create a `Rating` with `Rating.now()`, save it through the configured store,
  then redirect back to the joke page with a success message.

Use POST/redirect/GET for ratings so browser refresh does not submit the same
form again. Include a CSRF strategy before exposing the app beyond a trusted
local environment; for a local-only v1, at minimum restrict the documented
deployment and avoid claiming production security. Escape all displayed
catalogue values through the template engine and do not turn user-submitted
rating values into HTML.

There is currently no rating-reader API: `ratings.py` can save ratings and
compute aggregates only when given an iterable of `Rating` objects. Therefore
the initial page can confirm that a rating was saved but should not promise an
average or count unless a deliberate JSONL reader/service is added and tested.

## Test plan

Retain the existing pytest suite and add web tests in a new module such as
`tests/test_web.py`. Use Flask's test client and an in-memory fake implementing
the existing `RatingStore` protocol, so tests do not write to the developer's
home directory.

Cover at least:

- `GET /` returns 200, includes the five lines produced by `tell()`, and uses
  a deterministic selection when randomness is patched.
- `GET /jokes` contains every `JOKES` name exactly once and links to the
  corresponding IDs.
- `GET /jokes/<id>` renders the expected `Joke` and all `tell(joke)` lines;
  an unknown ID returns 404 without a traceback.
- `POST /jokes/<id>/ratings` accepts each boundary value 1 and 5, stores a
  `Rating` with the selected joke's ID, and redirects back to the detail page.
- Missing, non-integer, boolean-like, and out-of-range form values do not get
  persisted and produce a client error or validation message. Test a store
  `OSError` as a controlled failure as well.
- Templates do not introduce a second copy of the sequence wording; assert
  against values returned by the domain functions where practical.
- Existing CLI behavior remains unchanged by running the full suite, including
  `tests/test_cli.py`, `tests/test_jokes.py`, `tests/test_sequence.py`,
  `tests/test_ratings.py`, and `tests/test_rating_prompt.py`.

Run `pytest` (and the repository's configured Ruff/security checks when the
optional development tools are installed). Add a focused dependency/install
check for the optional web extra and a smoke test for `create_app()` so a
missing or incompatible Flask dependency fails clearly.

## Deliberate v1 exclusions

Leave these out of the first implementation:

- user accounts, login, moderation, admin screens, and per-user rating
  history;
- editing, deleting, or remotely synchronizing the built-in catalogue;
- WebSockets, async processing, or a second backend service;
- average-rating displays until the append-only JSONL file has a supported
  reader and concurrency behavior;
- rating deduplication, analytics, pagination, search, and localization;
- production deployment files, reverse-proxy configuration, and CI changes;
- changes to the CLI, `__main__.py`, existing source modules, or CODEOWNERS.

The implementation should be delivered as a separately testable optional web
surface, with the existing package API and command-line contract continuing to
work when Flask is not installed.
